"""Authenticate, construct and independently replay the chart-120 result.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
from hashlib import sha1, sha256
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from composition import checked, dump, load, read
from construct import construct
from physical_check import run as check_physical

def extract_peer(root):
    pins = read(HERE / "INPUTS.json")
    checked(pins["head"] == "ee4a05f9c926cf85904c81b768d73acaf9e44b54" and
            pins["tree"] == "1accfb5a4299b9631fcac19e95f0f07996956070", "Exact #7116 head and package tree")
    archive = (HERE / "pr7116.tar.gz").read_bytes()
    checked(sha256(archive).hexdigest() == pins["archive_sha256"], "Exact compressed source bundle")
    entries = {e["path"]: e for e in pins["files"]}
    checked(len(entries) == len(pins["files"]) == 17, "Full predecessor package")
    members = {}
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(archive))) as bundle:
        for item in bundle:
            path = root / item.name
            checked(item.isfile() and path.resolve().is_relative_to(root.resolve()) and
                    item.name in entries and item.name not in members, "Unique regular source member")
            data = bundle.extractfile(item).read()
            pin = entries[item.name]
            blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            checked(len(data) == pin["size"] and sha256(data).hexdigest() == pin["sha256"] and
                    blob == pin["git_blob"] and item.mode == int(pin["mode"], 8) & 0o777, "Exact member hash and mode")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            members[item.name] = (pin["mode"], blob)
    checked(members.keys() == entries.keys(), "Complete predecessor closure")
    def git_tree(names):
        records = []
        for name, value in names.items():
            if isinstance(value, dict):
                mode, digest = "40000", git_tree(value)
            else:
                mode, digest = value
            raw_name = name.encode()
            records.append((raw_name + (b"/" if isinstance(value, dict) else b""),
                            mode.encode() + b" " + raw_name + b"\0" + bytes.fromhex(digest)))
        payload = b"".join(record for _, record in sorted(records))
        return sha1(b"tree " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
    dirs = {}
    for name, metadata in members.items():
        location = dirs
        parts = name.split("/")
        for part in parts[:-1]:
            location = location.setdefault(part, {})
        location[parts[-1]] = metadata
    checked(git_tree(dirs) == pins["tree"], "Predecessor Git tree reconstructed")
    return root

def run(root, phase):
    peer = extract_peer(root / "peer")
    pin = load("peer7116_inputs", peer / "inputs.py")
    candidate = root / "WORD.json.gz"
    with pin.sources() as (source, _):
        build = construct(source[7115], HERE / "WITNESS.json", candidate)
        dump(root / "CONSTRUCTION.json", build)
        print("PASS_CHART120_CONSTRUCTION", flush=True)
        if phase == "physical":
            receipt = check_physical(source[7115], candidate)
            dump(root / "PHYSICAL.json", receipt)
            return "PHYSICAL.json"
    from composition import run as run_composition
    run_composition(root, peer, candidate)
    return "RESULT.json"

if __name__ == "__main__":
    checked(__debug__, "Replay requires assertions")
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("physical", "composition"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="p104-chart120-") as temp:
        root = args.out.resolve() if args.out else Path(temp)
        root.mkdir(parents=True, exist_ok=True)
        receipt = run(root, args.phase)
        expected = HERE / receipt
        if expected.exists():
            checked((root / receipt).read_bytes() == expected.read_bytes(), "Frozen receipt replay")
        else:
            checked(args.out is not None, "Missing frozen package receipt")
        print("PASS_CHART120_" + args.phase.upper(), flush=True)
