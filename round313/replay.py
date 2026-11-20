"""Run the Round 313 screen and independent control using CPython 3.12."""
import hashlib
from pathlib import Path
import runpy
import subprocess
import sys
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
if len(sys.argv) != 2 or sys.version_info[:2] != (3,12):
    raise SystemExit('usage: python3.12 -IB replay.py WORK-DIRECTORY')
root=Path(sys.argv[1]).resolve()
root.mkdir(parents=True,exist_ok=True)
pins=runpy.run_path(str(HERE/'pairs.py'))['PINS']
urlroot='https://raw.githubusercontent.com/'
sources = {
    'inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py':
        'aliromman/integer-mult-bounds/4f7c67ae387cc91580f469aeda4d508b372b9ec1/research/p104-dual-supplier-lift/bit_native.py',
    'inputs/cache/parent/binary/independent/price.py':
        'Clear1nsight/integer-mult-bounds/913fb6febe28cc3ccad1c16de8e45b8bce0da063/research/p104-subdivided-helper-births/binary/independent/price.py',
    'inputs/cache/parent/binary/independent/literal.py':
        'Clear1nsight/integer-mult-bounds/913fb6febe28cc3ccad1c16de8e45b8bce0da063/research/p104-subdivided-helper-births/binary/independent/literal.py',
    'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz':
        'Clear1nsight/integer-mult-bounds/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/binary/WORD.json.gz',
}
assert pins.keys()==sources.keys()
for path,remote in sources.items():
    dest=root/path
    data=dest.read_bytes() if dest.exists() else urlopen(urlroot+remote,timeout=30).read()
    if hashlib.sha256(data).hexdigest()!=pins[path]:
        raise ValueError('source mismatch: '+path)
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
out=root/'round313-replay'
out.mkdir(exist_ok=True)
word=root/'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz'
receipt=out/'receipt.json'
subprocess.run([sys.executable,'-IB',HERE/'pairs.py',root,receipt],check=True)
subprocess.run([sys.executable,'-IB',HERE/'check.py',word,receipt,out/'independent.json'],check=True)
