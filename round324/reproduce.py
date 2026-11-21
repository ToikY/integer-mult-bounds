"""Replay the one-packet intervention against pinned public sources with CPython 3.12."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen


def unique(pairs):
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError("duplicate key: " + key)
        fields[key] = value
    return fields


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def compare(actual, expected):
    measured, sealed = read_json(actual), read_json(expected)
    for record in (measured, sealed):
        del record["seconds"]
    if measured != sealed:
        raise ValueError(f"scientific receipt mismatch: {expected}")


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("CPython 3.12 required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    parser.add_argument("--package", type=Path, help="existing exact #8022 package for offline use")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    args.work.mkdir(exist_ok=True, parents=True)
    package = args.package or args.work / "package8022"
    sources = read_json(here.parent / "round323/SOURCES.json")
    for key in ("sources/WORD.json.gz", "sources/bit_native.py", "sources/binary_operator.py"):
        dest = package / key
        if dest.is_file() or args.package is not None:
            data = dest.read_bytes()
        else:
            with urlopen(sources[key]["url"], timeout=30) as response:
                data = response.read()
        if sha256(data).hexdigest() != sources[key]["sha256"]:
            raise ValueError("incorrect dependency: " + key)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    primary = args.work / "primary.json"
    independent = args.work / "independent.json"
    for script, inputs, result, expected in (
        (here / "cascade.py", [package], primary, here / "receipt.json"),
        (here / "independent/replay.py", [package, primary], independent, here / "independent/receipt.json"),
    ):
        subprocess.run([sys.executable, "-IB", script, *inputs, result], check=True, timeout=65)
        compare(result, expected)
    print("Matched both sealed scientific receipts.")


if __name__ == "__main__":
    main()
