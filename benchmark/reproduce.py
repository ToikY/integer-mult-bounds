"""From a fresh directory, reproduce the pinned producer and independent consumer."""
from pathlib import Path,PurePosixPath
from hashlib import sha1,sha256
import shutil,subprocess,sys,tarfile
from urllib.request import urlopen

if sys.version_info[:2]!=(3,12) or len(sys.argv)!=2:
    raise SystemExit("python3.12 -IB reproduce.py NEW_DIRECTORY")
w=Path(sys.argv[1]).resolve()
w.mkdir(parents=True,exist_ok=False)
base='https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/'
pins=[
    ('replay.tar.gz','ac3df5d5c8889f464f575e32dfea43714abf08ca','research/p104-round6-independent-proof-replay','bffb02e833d8253c693ea3e679fdc1a737a5a45f81089255848d9ee9a7d3487d','aba392f96d42b042944c9235c7f8bb8be5d3209c'),
    ('source7863.tar.gz','b3e4412fe01f07dc58305616fabf96345f49a781','research/p104-bit-451-factor-schedule','5f9d9c378a1bddccb2e42ac6453716fa950f19bd71f6181a9606f5eb68b022b3','43577b87651ba39f339e30d0782c7bc9a77cf195')]
for name,head,path,sha,blob in pins:
    raw=urlopen(base+head+'/'+path+'/replay.tar.gz',timeout=60).read()
    assert sha256(raw).hexdigest()==sha
    assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
    (w/name).write_bytes(raw)
    with tarfile.open(w/name) as tar:
        members=tar.getmembers()
        assert len({m.name for m in members})==len(members)
        assert sum(m.size for m in members)<2**29
        for m in members:
            p=PurePosixPath(m.name)
            assert not p.is_absolute() and '..' not in p.parts and (m.isdir() or m.isfile())
        if name=='replay.tar.gz':
            tar.extractall(w/'extract',filter='data')
        else:
            producer_files=[m for m in members if m.isfile()]
            assert len(producer_files)==204
            for m in producer_files:
                p=PurePosixPath(m.name).relative_to('package-sanitized')
                assert (w/'extract/451-consumer'/p).read_bytes()==tar.extractfile(m).read()
for prg in ('run.py','producer.py'):
    shutil.copyfile(Path(__file__).with_name(prg),w/prg)
    subprocess.run([sys.executable,'-IB',w/prg],check=True)
