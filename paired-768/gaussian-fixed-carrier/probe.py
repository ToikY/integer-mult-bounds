"""Bound the unpowered Gaussian moment and test one stricter fixed-carrier price."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import importlib
import json
import shutil
import sys
import tarfile
import tempfile

PINS = {
    "predecessor/predecessor-8030.tar.gz":
        "769d5a05cc1373fa22ed5956af636992fcd19d7e5c1753a32033a73c358cd31c",
    "unpowered_price.py":
        "c273f2bcd46a114595ee669021aa6cd7223488f87cee0fe10bd762bc92177424",
    "outer_budget.py":
        "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
}
C_OLD = Fraction(2092819, 2**29)
K_OLD = Fraction(".003898171")
H = 20_000_000
D = 10**18


def log_interval(rank, log_two=None):
    """Use 24 terms of the atanh series and an exact geometric tail."""
    if rank == Fraction(1, 2):
        lo, hi = log_two
        return -hi, -lo
    if log_two is None:
        power = 0
        x = rank
    else:
        power = int(rank).bit_length() - 1
        x = Fraction(rank, 2**power)
    z = (x - 1) / (x + 1)
    lo = 2 * sum(z**(2 * j + 1) / (2 * j + 1) for j in range(24))
    hi = lo + 2 * z**49 / (49 * (1 - z*z))
    if log_two is not None:
        lo += power * log_two[0]
        hi += power * log_two[1]
    return lo, hi


def evaluate(source, root):
    for name, expected in PINS.items():
        if sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Source differs at {name}")
    with tarfile.open(source / next(iter(PINS))) as archive:
        if not all(record.isfile() for record in archive):
            raise ValueError("Expected archived files only")
        archive.extractall(root, filter="data")
    for name in ("unpowered_price.py", "outer_budget.py"):
        shutil.copyfile(source / name, root / name)
    sys.path.insert(0, str(root))
    price = importlib.import_module("unpowered_price")
    outer = importlib.import_module("outer_budget")
    targets, paid = price.ranks()
    assert (sum(targets.values()), sum(paid.values())) == (105216, 564144)

    def moment(c):
        t = 1 - c
        lower = sum(n * price.intervals(r, t)[0] for r, n in targets.items())
        upper = sum(n * price.intervals(r, t)[1] for r, n in targets.items())
        return (
            lower - sum(n * price.intervals(r, t)[1] for r, n in paid.items()),
            upper - sum(n * price.intervals(r, t)[0] for r, n in paid.items()),
        )

    scale = 2**50
    left = int(C_OLD * scale)
    right = scale // 250
    ltwo = log_interval(Fraction(2))
    derivative_upper = Fraction(0)
    for rank in targets.keys() | paid.keys():
        log_lo, log_hi = log_interval(rank, ltwo)
        power_lo = price.intervals(rank, 1 - Fraction(right, scale))[0]
        power_hi = price.intervals(rank, 1 - C_OLD)[1]
        if rank < 1:
            power_lo = price.intervals(rank, 1 - C_OLD)[0]
            power_hi = price.intervals(rank, 1 - Fraction(right, scale))[1]
        coefficient = paid[rank] - targets[rank]
        derivative_upper += max(
            coefficient * log_value * power_value
            for log_value in (log_lo, log_hi)
            for power_value in (power_lo, power_hi)
        ) / price.UNIT
    assert derivative_upper < 0
    assert moment(Fraction(left, scale))[0] > 0
    assert moment(Fraction(right, scale))[1] < 0
    for _ in range(42):
        if right - left <= 1:
            break
        mid = (left + right) // 2
        lo, hi = moment(Fraction(mid, scale))
        if lo > 0:
            left = mid
        elif hi < 0:
            right = mid
        else:
            raise ArithmeticError("Raw price resolved only to the current interval")
    assert right == left + 1
    cap_low, cap_high = Fraction(left, scale), Fraction(right, scale)
    # Retain a simple 38-bit denominator and strict slack from the raw crossing.
    candidate = Fraction(int((C_OLD + cap_low) * 2**37), 2**38)
    margin, cells = price.certify(candidate, (targets, paid))
    _, previous_cells = price.certify(C_OLD, (targets, paid))
    assert cells.keys() == previous_cells.keys()
    changed_cells = sum(cells[key] != previous_cells[key] for key in cells)
    assert changed_cells
    assert len(cells) == 54 and cells[448, 1032] == 1
    assert min(cells.values()) / sum(targets.values()) > Fraction(1, 2**64)
    assert max(max(v.numerator.bit_length(), v.denominator.bit_length()) for v in cells.values()) < 512
    assert all(4 * k >= 5 * r for r, k in cells)
    unit = price.UNIT
    paid_lower = sum(n * price.intervals(r, 1 - candidate)[0] for r, n in paid.items())
    target_upper = sum(n * price.intervals(r, 1 - candidate)[1] for r, n in targets.items())
    assert paid_lower > 10 * unit and 100 * paid_lower > 99 * target_upper
    tick = Fraction(1, 2**128)
    upper = Fraction(price.intervals(1024 * 1224 * 32768, candidate)[1], unit)
    factor = (
        Fraction(256, 255) * Fraction(4097, 4096) * Fraction(1028, 1024) * upper
        * (1 + Fraction(64, 32768) + tick)
        / ((1 - Fraction(10, 32768)) * (1 - tick)**3)
    )
    assert factor**256 < 2**39
    assert Fraction(price.intervals(1032, candidate)[1], unit) < Fraction(106, 100)
    assert 1 - candidate > Fraction(996, 1000)
    pos = candidate - Fraction(39, 256 * H)
    old_priced_cap = C_OLD - Fraction(39, 256 * H) - Fraction(5, D)
    kappa = Fraction(int((pos - Fraction(1, 10**13)) * 10**13), 10**13)
    assert kappa > old_priced_cap
    b = Fraction(4391986206293, 2**50)
    first_limit = Fraction(249, 250) * (b - Fraction(11, 8 * 60_000))
    first = Fraction(int(first_limit * 10**21) - 1, 10**21)
    second = (249 * (b - Fraction(11, 8 * 960_000)) + first) / 250
    ordinary = kappa + Fraction(5, D)
    assert first < ordinary < min(second, Fraction(39, 10_000))
    profile = outer.qualify(kappa, Fraction(1, D), ordinary, pos)
    _, _, prior_positive_margin = outer.margins(
        kappa, Fraction(1, D), ordinary, C_OLD - Fraction(39, 256 * H)
    )
    assert prior_positive_margin < 0
    rendered = {}
    values = {
        "raw_gaussian_lower": cap_low, "raw_gaussian_upper": cap_high,
        "raw_margin_derivative_upper": Fraction(-((-100 * derivative_upper)//1), 100),
        "old_fixed_carrier_bound": old_priced_cap, "candidate_gaussian_c": candidate,
        "candidate_kappa": kappa, "gain_vs_reported": kappa - K_OLD,
        "gain_vs_fixed_certified_bound": kappa - old_priced_cap,
        "old_price_margin_on_new_profile": prior_positive_margin,
        "gaussian_margin": margin, "binary_second_stage_limit": second,
    }
    for k, v in values.items():
        rendered[k] = {"exact": str(v), "approx": f"{float(v):.18f}"}
    return {
        "ranks": {"target": {str(k): v for k, v in targets.items()},
                  "paid": {str(k): v for k, v in paid.items()}},
        "receipts": rendered, "profile": profile, "H": H, "D": D,
        "pins": PINS, "cells": len(cells), "changed_probability_shares": changed_cells
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--peer", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="gaussian-price-") as target:
        print(json.dumps(evaluate(args.peer.resolve(), Path(target)), indent=2, sort_keys=True))
