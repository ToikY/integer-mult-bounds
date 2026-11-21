"""Replay the two exact paid-moment proofs and bind their signed consumer applications."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
HEAD = "6dd295cb133c35e7ea14d744644ca77d8ffaa6ed"
PUBLIC_HEAD = "156137f70e7819cca8d86a1925d4c2873c77552e"
PACKAGE = "research/bit-451-carrier-cover/"
ARCHIVE = "5f9d9c378a1bddccb2e42ac6453716fa950f19bd71f6181a9606f5eb68b022b3"
VERIFIER = "0ace528fee828f6016e80bc283867513d02ff485ec7a89682be60def1170da6a"

def check(flag, message):
    if not flag:
        raise ValueError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(items):
    result = dict(items)
    check(len(result) == len(items), "duplicate manifest key")
    return result

def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)

def run(script, *args):
    subprocess.run([sys.executable, "-IB", script, *args], check=True, timeout=45)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scientific-checkout", required=True, type=Path)
    parser.add_argument("--public-source", action="store_true", help="use the published R339 source archive even when the R344 scientific commit is present")
    parser.add_argument("--full-signed", action="store_true", help="also recompute the two full signed consumers")
    args = parser.parse_args()
    check(sys.implementation.name == "cpython" and sys.version_info[:2] == (3,12) and __debug__, "use CPython 3.12 with assertions")
    manifest = read(HERE / "manifest.json")
    check(set(manifest) == {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file() and p != HERE/"manifest.json" and "__pycache__" not in p.parts}, "bundle census")
    for name, wanted in manifest.items():
        check(digest(HERE / name) == wanted, name)
    with tempfile.TemporaryDirectory(prefix="paid-proof-") as work:
        root = Path(work)
        shutil.copytree(HERE/"evidence", root, dirs_exist_ok=True)
        source_head = HEAD
        if args.public_source or subprocess.run(["git","-C",args.scientific_checkout,"cat-file","-e",HEAD+"^{commit}"],
                                                stderr=subprocess.DEVNULL).returncode:
            source_head = PUBLIC_HEAD
        for name, expected in (("verify.py", VERIFIER), ("source7863.tar.gz", ARCHIVE)):
            if source_head == PUBLIC_HEAD and name == "verify.py":
                data = (HERE/"evidence/scientific-verifier.py").read_bytes()
            else:
                data = subprocess.check_output(["git","-C",args.scientific_checkout,"show",source_head+":"+PACKAGE+name])
            path = root / name
            path.write_bytes(data)
            check(digest(path) == expected, name)
        lib = runpy.run_path(str(root/"verify.py"))
        producer = lib["extract"](root)
        bit = root/"round321/benchmark/producer/BIT-451.json"
        bit.parent.mkdir(parents=True)
        shutil.copyfile(producer/"BIT-451.json", bit)
        for n, old in ((344,342),(345,344)):
            at = root/f"round{n}/independent"
            before = root/f"round{old}/independent"
            signed = root/f"round{n}/consumer/run"
            control = root/f"round{old}/consumer/run"
            component, outer = root/f"supplier{n}.json", root/f"outer{n}.json"
            run(at/"audit.py", root, component)
            check(digest(component) == digest(at/"receipt.json"), "source reconstruction")
            run(at/"bind.py","--component",component,"--consumer",signed,"--old",before/"receipt.json",
                "--old-consumer",control,"--out",outer)
            check(digest(outer) == digest(at/"outer-verified.json"), "complete signed binding")
            shutil.copyfile(component, at/"receipt.json")
            shutil.copyfile(outer, at/"outer-verified.json")
            if args.full_signed:
                obj, receipt = read(component), read(signed/"receipt.json")
                app = {name:receipt["output_sha256"][name] for name in ("APPLICATION.json","AUDIT.json","adapter/binary/FINITE.json")}
                lib["consumer"](producer,root/f"fresh{n}",
                    {"installed":obj["cap"],"old_fixed_loss_ceiling":str(Fraction(obj["old_relaxed_ceiling"]))},
                    cap=obj["cap"],expected_claim=receipt["claim"],expected_hashes=app)
            print(f"R{n}: paid proof and signed binding passed" + ("; fresh signed computation passed" if args.full_signed else " (archived signed computation)"),flush=True)

if __name__ == "__main__":
    main()
