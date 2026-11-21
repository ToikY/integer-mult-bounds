"""Authenticate both peer archives and replay the sealed batch and provisional supplier."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def run(args, output, expected, timeout):
    command = [sys.executable, '-IB', *args]
    subprocess.run(command, check=True, timeout=timeout)
    got, old = (json.loads(path.read_bytes()) for path in (output, expected))
    for key in ('elapsed_seconds', 'seconds'):
        if key in old:
            del old[key], got[key]
    if got != old:
        raise ValueError(f'regenerated result differs from {expected.name}')


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit('CPython 3.12 with assertions enabled is required')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work', type=Path, help='new, empty replay output directory')
    parser.add_argument('--archives', type=Path, help='directory already holding the two exact source archives')
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    cscript = ROOT/'round328/consumer/replay.py'
    archive_root = args.archives.resolve() if args.archives else work
    for name, (head, package, pin) in runpy.run_path(str(cscript))['PINS'].items():
        target = archive_root/name
        if not args.archives:
            url = f'https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/{head}/research/{package}/replay.tar.gz'
            with urlopen(url, timeout=60) as response:
                target.write_bytes(response.read())
        if sha256(target.read_bytes()).hexdigest() != pin:
            raise ValueError(f'archive sha256 mismatch for {name}')
    word = work/'WORD.json.gz'
    with tarfile.open(archive_root/'source7863.tar.gz') as source:
        for name,out in (
            ('package-sanitized/BIT-451.json',work/'BIT-451.json'),
            ('package-sanitized/inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz',word),
        ):
            member = source.getmember(name)
            if not member.isfile():
                raise ValueError(f'expected a regular file: {name}')
            out.write_bytes(source.extractfile(member).read())
    r327 = ROOT/'round327'
    r328 = ROOT/'round328'
    primary = work/'327-primary.json'
    independent = work/'327-independent.json'
    compare = work/'327-comparison.json'
    run([ROOT/'round326/contract.py',word,primary,'--price-first','--skip-pairs','64'],
        primary,r327/'paid.json',65)
    second = r327/'independent/check_batch.py'
    run([second,'run',ROOT/'round326/independent/check_pair.py',word,independent],
        independent,r327/'independent/receipt.json',65)
    run([second,'compare',independent,primary,compare],compare,r327/'independent/comparison.json',15)
    arith = work/'328-arithmetic.json'
    run([r328/'arithmetic/screen.py',work,arith],arith,r328/'arithmetic/receipt.json',60)
    out = work/'consumer'
    run([cscript,'--archives',archive_root,'--out',out],out/'receipt.json',r328/'consumer/receipt.json',100)
    print('PASS R327 batch and R328 finite arithmetic plus supplied-cap consumer. Mixed-slab physical transfer remains open.')


if __name__ == '__main__':
    main()
