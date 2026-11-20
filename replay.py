"""Reproduce the bounded screens on pinned public inputs with CPython 3.12."""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
pa = ArgumentParser()
pa.add_argument("work", type=Path)
pa.add_argument("--round", type=int, action="append", dest="rounds")
pa.add_argument("--input-root", type=Path, help="reuse a previously authenticated input tree")
a = pa.parse_args()
if sys.version_info[:2] != (3,12):
    raise SystemExit("CPython 3.12 required")
out=a.work.resolve()
out.mkdir(parents=True,exist_ok=True)
root=(a.input_root or (out/"inputs-cache")).resolve()
def unique(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("duplicate key "+k)
        result[k]=v
    return result
for key,pin in json.loads((HERE/"SOURCES.json").read_text(),object_pairs_hook=unique).items():
    f=root/key
    raw=f.read_bytes() if f.exists() else urlopen(pin["url"],timeout=30).read()
    if hashlib.sha256(raw).hexdigest()!=pin["sha256"]:
        raise ValueError("source mismatch: "+key)
    if not f.exists():
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(raw)
word=root/"inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz"
plan=json.loads((HERE/"TESTS.json").read_text())
for n, commands in plan.items():
    if a.rounds and int(n) not in a.rounds:
        continue
    dest=out/("round"+n)
    dest.mkdir(exist_ok=True)
    for cmd in commands:
        argv=[p.format(root=str(root),out=str(dest),word=str(word),here=str(HERE)) for p in cmd]
        subprocess.run([sys.executable,"-IB",*argv],check=True)
    import gzip
    for output_name,expected_name in json.loads((HERE/"RECEIPTS.json").read_text())[n].items():
        actual=json.loads((dest/output_name).read_bytes())
        ref=HERE/("round"+n)/expected_name
        raw=ref.read_bytes()
        expected=json.loads(gzip.decompress(raw) if ref.suffix==".gz" else raw)
        for key in ("seconds","scientific_elapsed_s","elapsed_s"):
            expected.pop(key,None)
            actual.pop(key,None)
        if actual!=expected:
            raise ValueError("scientific receipt differs in round "+n+": "+output_name)
    print("Matched saved scientific receipts for round "+n,flush=True)
