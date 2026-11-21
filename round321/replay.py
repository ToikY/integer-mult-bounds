"""Fetch three immutable sources and compare both scientific receipted outputs."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen
import gzip
import json
import shutil
import subprocess
import sys
if sys.version_info[:2] != (3,12):
    raise SystemExit("CPython 3.12 required")
p=ArgumentParser()
p.add_argument('work',type=Path)
p.add_argument('--input-root',type=Path,help='existing comparator sources; each is authenticated before use')
a=p.parse_args()
here=Path(__file__).resolve().parent
work=a.work.resolve()
root=work/'benchmark'
def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate key '+key)
        result[key]=value
    return result
pins=json.loads((here/'SOURCES.json').read_bytes(),object_pairs_hook=unique)
for key,spec in pins.items():
    dest=root/key
    source=(a.input_root/key) if a.input_root else dest
    raw=source.read_bytes() if source.is_file() else urlopen(spec['url'],timeout=30).read()
    if sha256(raw).hexdigest()!=spec['sha256']:
        raise ValueError('source mismatch '+key)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists() or dest.read_bytes()!=raw:
        dest.write_bytes(raw)
compat=work/'round320'
compat.mkdir(exist_ok=True)
shutil.copyfile(here/'pairs.py',compat/'pairs.py')
word=next(root/key for key in pins if key.endswith('WORD.json.gz'))
operator=next(root/key for key in pins if key.endswith('binary_operator.py'))
for runner,args,time_cap,name in [
    ('third.py',[root],60,'primary.json'),
    ('check.py',[word,operator],30,'independent.json'),
]:
    output=work/name
    subprocess.run([sys.executable,'-IB',here/runner,*args,output],check=True,timeout=time_cap)
    actual=json.loads(output.read_bytes(),object_pairs_hook=unique)
    raw=(here/name).read_bytes() if name=='primary.json' else gzip.decompress((here/(name+'.gz')).read_bytes())
    expected=json.loads(raw,object_pairs_hook=unique)
    actual.pop('seconds')
    expected.pop('seconds')
    if expected!=actual:
        raise ValueError('scientific receipt mismatch: '+name)
    print('Matched '+name)
