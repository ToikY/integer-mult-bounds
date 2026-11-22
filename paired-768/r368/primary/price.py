"""Bound one Gaussian half-rank split reduction on exact #8053."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from collections import Counter
import importlib
import json
import runpy
import subprocess
import sys
import tempfile
import time

PINS = {
    "bootstrap.py": "e7609488216e31baf99d3a9b6acaba0e45b1a4c97288d563c43bb414fd0eb183",
    "unpowered_price.py": "c273f2bcd46a114595ee669021aa6cd7223488f87cee0fe10bd762bc92177424",
    "retimed_supplier.py": "4bd969e3f1cfdcdf26c36e5fa7ab64c8e72904f516a51af6b2a29524e1cf8eb2",
    "installations.py": "c68d55d1719068eb627dabc99bfa3d19beb601aa3b5e7d0b33f354a8be2cc5dd",
    "outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "RESULT.json": "3d85ccaf415b33702951ceb14b78fa1f7f0964ba3f201bf07b9e8a6e96882220",
}
WRAPPER_PINS = {
    "verify.py": "513229ad495efab7a738644d291eb19f84bc751d6a606e84183229d4549549ab",
    "PEER-SOURCE.json": "91e965d76ef4d72aa68422c382c8be25fce47b16d610783a5e3872f82953cffc",
    "RESULT.json": PINS["RESULT.json"],
}
OLD = Q(".0038981721342")
C0 = Q(1071523491, 2**38)
H = 20_000_000
D = 10**18
SCALE = 2**50


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def hashed_json(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def restore_fixed_carrier(wrapper, destination):
    for name, expected in WRAPPER_PINS.items():
        assert digest(wrapper / name) == expected, f"Fixed-carrier source differs at {name}"
    code = runpy.run_path(str(wrapper / "verify.py"))
    destination.mkdir()
    code["restore"](destination)
    code["edit_installation"](destination)
    return destination


def log_bounds(x):
    z = (x - 1) / (x + 1)
    low = 2 * sum(z**(2*i+1)/(2*i+1) for i in range(24))
    return low, low + 2*z**49/(49*(1-z*z))


def logarithm(rank):
    dlo, dhi = log_bounds(Q(2))
    if rank == Q(1, 2):
        return -dhi, -dlo
    exponent = int(rank).bit_length() - 1
    lo, hi = log_bounds(Q(rank, 2**exponent))
    return lo + exponent*dlo, hi + exponent*dhi


def explore(pkg, work):
    for name, sha in PINS.items():
        assert digest(pkg / name) == sha, f"Source differs at {name}"
    sys.path.insert(0, str(pkg))
    bootstrap = importlib.import_module("bootstrap")
    bootstrap.install(work)
    sys.path.insert(0, str(work))
    price = importlib.import_module("unpowered_price")
    source = importlib.import_module("retimed_supplier")
    outer = importlib.import_module("outer_budget")
    check = importlib.import_module("check_complete")
    profile = importlib.import_module("installations")
    assert source.SMALL_SPLITS == 1008
    assert profile.EXTENDED.kappa == OLD and profile.GAUSSIAN_C == C0
    assert (profile.EXTENDED.complex_log, profile.EXTENDED.positive_stop_denominator) == (H, D)

    native = source.word(*price.load_changed(work / "inputs"))
    targets_seq, paid_seq = source.source_ranks(native)
    t = Counter(targets_seq)
    old_paid = Counter(paid_seq)
    assert (t, old_paid) == price.ranks()
    assert (len(targets_seq), len(paid_seq), t[1]) == (105216, 564144, 1008)

    unit_cuts = [(i, label.tag) for i, label in enumerate(native.paid) if label.rank == 1]
    old_margin, old_cells = price.certify(C0, (t, old_paid))
    assert old_margin > 0 and len(old_cells) == 54 and old_cells[448,1032] == 1

    left = int((OLD + Q(39,256*H) + Q(5,D)) * SCALE)
    right = (SCALE + 249) // 250  # Cover all admissible C < 0.004, even off-grid.
    assert Q(left, SCALE) <= C0
    binary_ceil = Q(check.profile_row(profile.EXTENDED)["stage_rates"][-1])
    assert binary_ceil == OLD + Q(5, D)
    assert profile.BINARY_C < Q(right, SCALE)

    def interval_at(signed, c):
        result = [0, 0]
        for r, n in signed.items():
            lo, hi = price.intervals(r, 1-c)
            result[0] += n * (lo if n >= 0 else hi)
            result[1] += n * (hi if n >= 0 else lo)
        return tuple(Q(v, price.UNIT) for v in result)

    def derivative(signed):
        bound = Q(0)
        for r, n in signed.items():
            exp1, exp2 = 1-Q(left,SCALE), 1-Q(right,SCALE)
            if r >= 1:
                exp1, exp2 = exp2, exp1
            log_bounds = logarithm(r)
            low = price.intervals(r, exp1)[0]
            high = price.intervals(r, exp2)[1]
            bound += max(-n * x * y for x in log_bounds for y in (low,high))/price.UNIT
        upper = Q(-((-bound * 100)//1), 100)
        assert upper < 0
        return upper

    def crossing(signed):
        slope = derivative(signed)
        lo, hi = left, right
        assert interval_at(signed, Q(lo,SCALE))[0] > 0
        assert interval_at(signed, Q(hi,SCALE))[1] < 0
        for _ in range(42):
            if hi-lo == 1:
                break
            cut = (hi+lo)//2
            lower, upper = interval_at(signed, Q(cut,SCALE))
            if lower > 0:
                lo = cut
            elif upper < 0:
                hi = cut
            else:
                raise ArithmeticError("Insufficient directed precision")
        assert hi-lo == 1
        return Q(lo,SCALE), Q(hi,SCALE), slope

    def difference(paid):
        signed = t.copy()
        signed.subtract(paid)
        return signed

    def tweak(splits):
        paid = old_paid.copy()
        restored = 1008-splits
        paid[Q(1,2)] -= 2*restored
        paid[1] += restored
        assert paid.total() == old_paid.total()-restored
        return paid

    old_lo, old_hi, old_slope = crossing(difference(old_paid))
    p5 = tweak(1005)
    restricted = Counter({rank:n for rank,n in t.items() if rank >= 2})
    restricted.subtract({rank:n for rank,n in p5.items() if rank >= 1})
    hall_low, hall_high = interval_at(restricted, Q(left,SCALE))
    assert hall_high < -Q(26,100)
    hall_slope = derivative(restricted)

    p6 = tweak(1006)
    lo, hi, slope = crossing(difference(p6))
    assert lo > old_hi
    trial = Q(int((lo+old_hi)*2**39), 2**40)
    assert old_hi < trial < lo
    rates = check.tariff(trial, (t, p6), 1224)
    margin, cells = price.certify(trial, (t,p6))
    assert rates["cells"] == len(cells) == 54 and cells[448,1032] == 1
    assert set(cells) == set(old_cells)
    restored_count = 1008-1006
    for s, unit_rank in unit_cuts[1006:1008]:
        assert native.paid[s].rank == 1 and native.paid[s].tag == unit_rank
    assert len(unit_cuts[1006:1008]) == restored_count

    debit = Q(39,256*H)
    pos = trial-debit
    k = Q(int((pos-Q(1,10**13))*10**13),10**13)
    assert k > old_hi-debit-Q(5,D)
    negative = interval_at(difference(old_paid), trial)[1]
    assert negative < 0
    g = Q(1,D)
    old_fixed_cap = C0-debit-5*g
    candidate = profile.Profile((60000,960000), H, profile.EXTENDED.eta, k, D)
    # Independently evaluate the installed #8053 bookkeeping with exactly
    # one bound changed, restoring its module variable before return.
    check.GAUSSIAN_C = trial
    try:
        row = check.profile_row(candidate)
    finally:
        check.GAUSSIAN_C = C0
    verify = outer.qualify(k,g,k+5*g,pos)
    assert row["signed_gate"] == verify
    rho = 1-margin
    half_lower = p6[Q(1,2)] * price.intervals(Q(1,2), 1-trial)[0]
    assert Q(half_lower,price.UNIT) >= rho * t[1]
    all_cells = [[str(r),k,str(v)] for (r,k),v in sorted(cells.items())]
    trimmed = lambda q: str(Q(-((-q*10**14)//1),10**14))
    return {
        "comparator": "e25494616bf149217644ce08d949181ea3600e13",
        "scope": [1005,1006,1008],
        "pins": PINS,
        "raw_bracket_1008": [str(v) for v in (old_lo,old_hi,old_slope)],
        "raw_bracket_1006": [str(v) for v in (lo,hi,slope)],
        "1005_hall_deficit_upper": trimmed(hall_high),
        "1005_hall_derivative_upper": str(hall_slope),
        "1005_cut_left": str(Q(left,SCALE)),
        "relevant_cut_right": str(Q(right,SCALE)),
        "1006_literal_touched_paid_clock_and_tag": unit_cuts[1006:1008],
        "1006_fixed_c": str(trial), "1006_kappa_candidate": str(k),
        "1006_kappa_decimal": f"{float(k):.13f}",
        "1006_gain_vs_8053": str(k-OLD),
        "1006_gain_vs_8053_fixed_price_cap": str(k-old_fixed_cap),
        "1006_gain_vs_1008_best_relaxed_with_same_debit": str(k-(old_hi-debit-5*g)),
        "1008_negative_at_new_trial_margin_upper": trimmed(negative),
        "1006_payment_saving_at_trial_lower": str(
            2*(2*Q(price.intervals(Q(1,2),1-trial)[0],price.UNIT)-1)
        ),
        "1006_canonical_cells_sha256": hashed_json(all_cells),
        "1006_recomputed_cells": all_cells,
        "1006_changing_shares": sum(cells[key]!=old_cells[key] for key in cells),
        "1006_tariff": rates, "1006_extended_profile": row,
        "source_targets": [[str(r),n] for r,n in sorted(t.items())],
        "source_paid": [[str(r),n] for r,n in sorted(old_paid.items())],
        "status": "PRICE_SURVIVOR_PRE_BUILD",
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--package", type=Path)
    source.add_argument("--fixed-carrier", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        with tempfile.TemporaryDirectory(prefix="split-price-") as root:
            work = Path(root)
            package = (
                restore_fixed_carrier(args.fixed_carrier.resolve(), work/"source")
                if args.fixed_carrier else args.package.resolve()
            )
            result = explore(package, work/"installed")
        with args.out.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        start = time.monotonic()
        proc = subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=45)
        print(f"exit={proc.returncode} elapsed={time.monotonic()-start:.3f}s")
        raise SystemExit(proc.returncode)
