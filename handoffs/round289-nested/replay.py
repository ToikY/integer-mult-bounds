"""Reproduce the fixed nested Type B rank obstruction."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def run(script,*args):
    return subprocess.check_output([sys.executable, "-I", "-B", str(HERE / script), *map(str,args)],timeout=32)


def main():
    assert __debug__ and sys.version_info[:2] == (3,12) and len(sys.argv)==2
    root=Path(sys.argv[1]).resolve()
    primary=run("check_nested_idle.py",root/"inputs")
    expected=HERE/"expected/PRIMARY.jsonl"
    assert primary==expected.read_bytes()
    independent=json.loads(run("independent/check_nested_idle_reverse.py",root,expected,hashlib.sha256(primary).hexdigest()))
    saved=json.loads((HERE/"expected/INDEPENDENT.json").read_bytes())
    assert 0<=independent.pop("seconds")<30
    assert independent.pop("lead_sha256")==hashlib.sha256(primary).hexdigest()
    assert saved.pop("lead_sha256") is None
    assert independent==saved
    print("PASS_NESTED_IDLE_SQUARE_EXCLUSION")


if __name__=="__main__":
    main()
