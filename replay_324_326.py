"""Fetch authenticated inputs and reproduce the graph and literal decisions for Rounds 324–326."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from pathlib import Path
import runpy
import subprocess
import sys


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("work",type=Path)
    parser.add_argument("--package",type=Path,help="offline path to the source-pinned #8022 package")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    args.work.mkdir(parents=True,exist_ok=True)
    python = [sys.executable,"-IB"]
    base = here / "round324/reproduce.py"
    args324 = ["--package", args.package] if args.package else []
    subprocess.run([*python,base,args.work,*args324],check=True,timeout=180)
    read = runpy.run_path(str(base))["read_json"]
    package = args.package or args.work / "package8022"
    word = package / "sources/WORD.json.gz"
    for n,pscript,pinputs,iscript in (
        (325,"midpoint.py",[package,here/"round322/split.py"],"replay.py"),
        (326,"contract.py",[word],"check_pair.py"),
    ):
        directory = here/f"round{n}"
        primary = args.work/f"{n}-primary.json"
        independent = args.work/f"{n}-independent.json"
        iinputs = [package,primary] if n == 325 else [word]
        for program,inputs,output,expected in (
            (directory/pscript,pinputs,primary,directory/"receipt.json"),
            (directory/"independent"/iscript,iinputs,independent,directory/"independent/receipt.json"),
        ):
            subprocess.run([*python,program,*inputs,output],check=True,timeout=65)
            measured,sealed = read(output),read(expected)
            key = "elapsed_seconds" if "elapsed_seconds" in sealed else "seconds"
            del measured[key],sealed[key]
            assert measured == sealed, expected
    a,b = read(primary),read(independent)
    assert a["status"] == "sample-exhausted" and b["status"] == "case-cap"
    assert b["ranked_pairs"][:64] == [row[1:] for row in a["roster"]]
    assert a["pool"] == b["total_pairs"] and len(a["cases"]) == 576
    assert 20**100 > 8*19**100
    interval_signs = 0
    for x,y in zip(a["cases"],b["cases"],strict=True):
        assert x[:3] == [*y["pair"],y["dimension"]]
        assert (x[3] != "infeasible") == y["feasible"]
        if not y["feasible"]:
            continue
        hist = Counter({int(k):v for k,v in y["old_paid"].items()})
        hist.subtract({int(k):v for k,v in y["new_paid"].items()})
        assert {k:v for k,v in hist.items() if v} == dict(x[4])
        lo,hi = map(Fraction,y["raw_saving_36"])
        assert max(lo,Fraction(x[5][0],a["price_scale"])) <= min(hi,Fraction(x[5][1],a["price_scale"])) < 0
        # For 0 <= k <= 1/100 we have 19r/20 <= r^(1-k) <= r for ranks 1..8.
        plus = sum(r*n for r,n in hist.items() if n>0)
        minus = sum(-r*n for r,n in hist.items() if n<0)
        interval_signs += (20*plus < 19*minus)
    print("Matched all six sealed receipts and all 576 pair-dimensions.")
    print("Strictly negative throughout 0 <= k <= 1/100:", interval_signs)
    priced = args.work/"326-price-first.json"
    subprocess.run([*python,here/"round326/contract.py",word,priced,"--price-first"],check=True,timeout=65)
    screening, sealed = read(priced), read(here/"round326/price-first-control.json")
    del screening["seconds"], sealed["seconds"]
    assert screening == sealed and screening["witness"] is None
    for x,y in zip(screening["cases"],b["cases"],strict=True):
        assert x[:3] == [*y["pair"],y["dimension"]]
        if x[3] == "excluded-by-price":
            assert Fraction(y["raw_saving_36"][1]) <= 0
        else:
            assert x[3] == "infeasible" and not y["feasible"]
    print("Price-first control reproduced the decision on the same 576 cases.")


if __name__ == "__main__":
    main()
