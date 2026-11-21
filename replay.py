"""Replay the three bounded screens on exact public sources with CPython 3.12."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

if sys.version_info[:2] != (3, 12) or len(sys.argv) != 2:
    raise SystemExit("usage: python3.12 -IB replay.py WORK_DIRECTORY")
here = Path(__file__).resolve().parent
work = Path(sys.argv[1]).resolve()
work.mkdir(parents=True, exist_ok=True)

def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate receipt key: " + key)
        result[key] = value
    return result

def run(script, *args):
    subprocess.run([sys.executable, "-IB", script, *args], check=True, timeout=90)

def match(file, expected):
    output = json.loads(file.read_bytes(), object_pairs_hook=unique)
    original = json.loads(expected.read_bytes(), object_pairs_hook=unique)
    output.pop("seconds")
    original.pop("seconds")
    if output != original:
        raise ValueError("scientific receipt mismatch: " + str(expected))
    print("Matched", expected.relative_to(here), flush=True)

run(here/"round321/replay.py", work/"r321")
package = work/"package8022"
for name, pin in json.loads((here/"round323/SOURCES.json").read_bytes(), object_pairs_hook=unique).items():
    target = package/name
    data = target.read_bytes() if target.exists() else urlopen(pin["url"], timeout=30).read()
    if sha256(data).hexdigest() != pin["sha256"]:
        raise ValueError("public source mismatch: " + name)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
for number, program, inputs in [(322, "split.py", work/"r321/benchmark"), (323, "exchange.py", package)]:
    original = here/("round"+str(number))
    dest = work/("r"+str(number))
    dest.mkdir(exist_ok=True)
    run(original/program, inputs, dest/"result.json")
    match(dest/"result.json", original/"result.json")
    run(original/"check.py", inputs, dest/"result.json", dest/"replay.json")
    match(dest/"replay.json", original/"replay.json")
