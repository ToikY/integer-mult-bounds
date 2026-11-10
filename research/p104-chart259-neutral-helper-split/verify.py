"""Authenticate, construct and independently replay the chart-259 result.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha1, sha256
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from composition import checked, dump, read
from construct import construct

def extract_peer(root):
    pins = read(HERE / "INPUTS.json")
    checked(pins["head"] == "b3d68cf1db9bf493ded2d8f4cb922939edc0ef95" and
            pins["tree"] == "c480f8103238a3bd5c06c4b71c266edcb2a5baf8", "Exact #7120 head and package tree")
    frozen = HERE / "predecessor"
    entries = {e["path"]: e for e in pins["files"]}
    checked(len(entries) == len(pins["files"]) == 26, "Full predecessor package")
    members = {}
    files = {p.relative_to(frozen).as_posix() for p in frozen.rglob("*") if p.is_file()}
    checked(files == entries.keys(), "Complete predecessor closure")
    for name, pin in entries.items():
        path = frozen / name
        target = root / name
        checked(path.is_file() and path.resolve().is_relative_to(frozen.resolve()) and
                target.resolve().is_relative_to(root.resolve()), "Safe regular predecessor source")
        data = path.read_bytes()
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        checked(len(data) == pin["size"] and sha256(data).hexdigest() == pin["sha256"] and
                blob == pin["git_blob"], "Exact predecessor Git blob and SHA256")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        members[name] = (pin["mode"], blob)
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
    candidate = root / "WORD.json.gz"
    build = construct(peer / "WORD.json.gz", HERE / "WITNESS.json", candidate)
    checked(build["word_sha256"] == "0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc",
            "Exact constructed chart-259 word")
    dump(root / "CONSTRUCTION.json", build)
    print("PASS_CHART259_CONSTRUCTION", flush=True)
    if phase == "physical":
        from physical_check import run as check_physical
        receipt = check_physical(peer, candidate)
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
    with tempfile.TemporaryDirectory(prefix="p104-chart259-") as temp:
        root = args.out.resolve() if args.out else Path(temp)
        root.mkdir(parents=True, exist_ok=True)
        receipt = run(root, args.phase)
        expected = HERE / receipt
        if expected.exists():
            checked((root / receipt).read_bytes() == expected.read_bytes(), "Frozen receipt replay")
        else:
            checked(args.out is not None, "Missing frozen package receipt")
        print("PASS_CHART259_" + args.phase.upper(), flush=True)
