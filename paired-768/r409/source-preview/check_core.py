"""Check the two prospective source files against the pinned arithmetic recipe."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
from types import ModuleType, SimpleNamespace
import ast
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
PRICE = HERE.parent/"price"


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("installed_runtime", type=Path)
    args = parser.parse_args()
    assert __debug__
    pins = json.loads((HERE/"SOURCE-PINS.json").read_bytes())
    for file, pin in pins.items():
        assert sha256((HERE/file).read_bytes()).hexdigest() == pin["prospective"]
    assert sha256((args.installed_runtime/"installations.py").read_bytes()).hexdigest() == pins["installations.py"]["before"]
    raw = (args.installed_runtime/"strict_moment.py").read_bytes()
    assert sha256(raw).hexdigest() == "f13c79ed45ce41c67a3f47c1767601be032ae65a908b9ee3a80643b0ac08689a"
    core = ModuleType("strict_moment")
    width = 1 << 112
    functions = [d for d in ast.parse(raw).body
                 if isinstance(d, ast.FunctionDef) and d.name in {"ceiling", "power_interval"}]
    assert [d.name for d in functions] == ["ceiling", "power_interval"]
    core.UNIT, core.isqrt = width, isqrt
    exec(compile(ast.Module(body=functions, type_ignores=[]), "strict_moment.py", "exec"), core.__dict__)
    sys.modules[core.__name__] = core
    grades = ModuleType("grades")
    grades.UPPER_DIVISOR = 1724
    sys.modules[grades.__name__] = grades
    pricer = ModuleType("unpowered_price")

    def intervals(rank, exponent):
        if rank == Q(1, 2):
            lower, upper = core.power_interval(2, exponent)
            return width**2 // upper, -(-width**2 // lower)
        return core.power_interval(int(rank), exponent)

    pricer.intervals = intervals
    sys.modules[pricer.__name__] = pricer

    for filename, digest in {
        "replay_grade_cut.py": "5b7eb70b4258de852a64045a7875fd79d1240ab6119e4c1d11ec8bdcea2f9daf",
        "R368-RANK-RECEIPT.json": "d26a1f9ea8fd78900f45bf83c29ee2b700d015c231a82eab1cad54283b4aec66",
        "PRICE.json": "9c06021a01749f560cc0d8b14167fa8b07f5d6771695939bd20e56f0d99bf4e6",
    }.items():
        assert sha256((PRICE/filename).read_bytes()).hexdigest() == digest
    census = runpy.run_path(str(PRICE/"replay_grade_cut.py"))
    rows = json.loads((PRICE/"R368-RANK-RECEIPT.json").read_bytes())
    record = json.loads((PRICE/"PRICE.json").read_bytes())
    profile = runpy.run_path(str(HERE/"installations.py"))["TERMINAL"]
    result = record["complete_projected_invoice"]
    assert tuple(result["native_heights"]) == profile.rank_logs
    assert result["gaussian_height"] == profile.complex_log
    assert Q(result["projected_kappa"]) == profile.kappa
    def native_rank(value):
        number = Q(value)
        return number.numerator if number.denominator == 1 else number

    cells = {(native_rank(r),native_rank(k)):Q(value) for (r,k),value in record["grade_rows"]}
    paid = census["weighted"](census["unmix"](rows["source_paid"]),1008)
    targets = census["weighted"](census["unmix"](rows["source_targets"]))
    provider = SimpleNamespace(trial=Q(17145637307,2**42), ambient=306, cells=cells,
                               paid=SimpleNamespace(histogram=paid),
                               targets=SimpleNamespace(histogram=targets))
    module = runpy.run_path(str(HERE/"positive_debit.py"))
    check = module["certify_loss"]
    output = check(provider,1874)
    assert Q(output["debit"]) == Q(record["debit"])
    assert Q(output["exterior_period_factor"]) == Q(22067,21981)
    check.__globals__["POSITIVE_DEBIT"] = Q(output["debit"])-Q(1,2**30)
    try:
        check(provider,1874)
    except AssertionError:
        print("PASS_ADJACENT_LOWER_DEBIT_REJECTED")
    else:
        raise ValueError("The lower debit unexpectedly passed")
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
