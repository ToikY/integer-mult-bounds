"""Test the best limiting mean at the first lower debit on the exact current invoice."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
import os
from pathlib import Path
from runpy import run_path
import sys
from tempfile import TemporaryDirectory, gettempdir


HEAD = "517eac577bc12a1519eaf346a6816ad91bc9df90"
PINS = {
    "package/verify.py": "66ef63d6a7e89d0424641c63afa23149b7f8259d29333dc4b745ec612b4358f6",
    "package/INPUTS.json": "be77a83e9b702928c3b8e16554fae12aefb635b99bfb01c5a175e9105f440c09",
    "package/RESULT.json": "4ae4c5332a66396a63c0732c5fb1f797f96ebae0e397665de382a3ea31861fa6",
    "package/source/domain/ASSEMBLY.json": "1f7d6217d3212147c01ba84b56772b1a6709325cfc16ce4ba2e047553c654908",
    "assembled/receipt.py": "16c045b4907770da8974db9a96d4c9fc5606648473be95519edf317e2ea484e0",
    "assembled/independent_price.py": "d2d956a03099c6ea580e9076e5c4847fe609e7e1feb04863c9d7179ef6e7237e",
    "runtime/installations.py": "83c9616cadecbb6da76a0c4e0d909abe62490d48f35c47c08c68d879c65e13c7",
    "handoff/round438/check_minimal_debit.py": "34c82423ef62ec15eae6ba1f68b0a9be8ca1a54e43fdd34cd46e3a2acfddf9e4",
}
LOWER_DEBIT = Q(1411928, 2**20)
CURRENT_DEBIT = Q(1411929, 2**20)
CURRENT_TARIFF = Q(15009853977, 6430103800)
CONTRACTION = Q(2390, 2391)
LIMIT_TARIFF = Q(7, 3) / CONTRACTION


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Duplicate input key {name!r}")
        result[name] = value
    return result


def read_pinned(path, key):
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f"Pinned input differs at {key}")
    return data


def band(pair, bits):
    scale = 1 << bits
    return [floor(scale*pair[0]), ceil(scale*pair[1])]


def check(package, helper):
    for name in ("verify.py", "INPUTS.json", "source/domain/ASSEMBLY.json"):
        read_pinned(package / name, f"package/{name}")
    read_pinned(helper, "handoff/round438/check_minimal_debit.py")
    data = json.loads(read_pinned(package / "RESULT.json", "package/RESULT.json"), object_pairs_hook=unique_object)
    assert Q(data["terminal"]["kappa"]) == Q(".003900862349161")
    assert Q(data["ordinary_finite_debit"]) == CURRENT_DEBIT
    assert Q(data["ordinary_child_tariff"]) == CURRENT_TARIFF
    assert Q(data["ordinary_child_contraction"]) == CONTRACTION
    assert data["ordinary_child_geometric_budget"] == 2401 and data["ordinary_reserve"] == "256/255"
    # Subtracting 7/3 from (21*x+3)/(9*x-1) leaves the positive remainder below.
    assert (3*21 - 7*9, 3*3 + 7) == (0, 16)
    assert CURRENT_TARIFF * CONTRACTION == Q(7, 3) + Q(16, 3*(9*3**14 - 1))
    assert LIMIT_TARIFF == Q(5579, 2390) < CURRENT_TARIFF

    loader = run_path(str(package / "verify.py"))
    loader["authenticate"]()
    tools = run_path(str(helper))
    loader["reserve"](Path(gettempdir()))
    with TemporaryDirectory(prefix="limiting-quotient-mean-") as temporary:
        scratch = Path(temporary).resolve()
        env = dict(os.environ, **loader["THREAD_ENV"], TMPDIR=str(scratch))
        peer = loader["prepare"](scratch, env)
        receipt, independent = peer / "receipt.py", peer / "independent_price.py"
        read_pinned(receipt, "assembled/receipt.py")
        read_pinned(independent, "assembled/independent_price.py")
        runtime = scratch / "runtime"
        loader["install"](peer, runtime, env)
        read_pinned(runtime / "installations.py", "runtime/installations.py")
        previous = sys.argv
        try:
            sys.argv = [str(receipt), str(runtime)]
            source = run_path(str(receipt))
        finally:
            sys.argv = previous
        target, paid = source["raw_moments"](source["graph"](), source["caller"]())
        rate, lower = source["BINARY_C"], source["ORDINARY_FLOOR"]
        margin, cells = source["certify"](rate, (target, paid))
        assert margin > 0 and lower == data["ordinary_floor"] == 1156
        assert (sum(target.values()), sum(paid.values()), len(cells)) == (18906, 104652, 24)
        power, unit = source["power_interval"], source["UNIT"]
        assert unit == 2**112

        def power112(base, exponent):
            assert Q(base).denominator == 1
            return tuple(Q(value, unit) for value in power(int(base), exponent))

        def ratio112(n, d, exponent):
            assert Q(n).denominator == Q(d).denominator == 1
            n_lo, n_hi = power(int(n), exponent)
            d_lo, d_hi = power(int(d), exponent)
            return Q(n_lo, d_hi), Q(n_hi, d_lo)

        power192 = tools["get_powers"](independent)

        def ratio192(n, d, exponent):
            return power192(Q(n, d), exponent)

        bounds = {}
        for bits, powers, ratio in ((112, power112, ratio112), (192, power192, ratio192)):
            lo, hi = tools["full_envelope"](rate, lower, paid, cells, powers, ratio)
            if bits == 112:
                direct = source["tape_factor_periodic"]
                assert (lo, hi) == (direct(134, rate, lower, paid, cells, upper=False),
                                    direct(134, rate, lower, paid, cells))
            charge = band((lo*LIMIT_TARIFF, hi*LIMIT_TARIFF), bits)
            allowance = band(tuple(2*x for x in powers(2, LOWER_DEBIT - 1)), bits)
            bounds[str(bits)] = {"limiting_charge": charge, "lower_debit_allowance": allowance,
                                 "lower_charge_minus_upper_allowance": charge[0] - allowance[1]}
    excludes = all(row["lower_charge_minus_upper_allowance"] > 0 for row in bounds.values())
    limit_funds = all(row["limiting_charge"][1] < row["lower_debit_allowance"][0]
                      for row in bounds.values())
    assert not (excludes and limit_funds)
    if excludes:
        decision = "Stop fixed-envelope domain refinements"
    elif limit_funds:
        decision = "Test one finite-domain bound before any build"
    else:
        decision = "Unresolved directed comparison"
    return {"scope": "Fixed periodic envelope, contraction, reserve and geometry. Quotient-domain bound only.",
            "head": HEAD, "pinned_inputs": PINS, "minimum_limiting_child_mean": "7/3",
            "mean_minus_limit": "16/(3*(9*x-1)) for x=3^(N-2)", "limiting_tariff": str(LIMIT_TARIFF),
            "tested_lower_debit": str(LOWER_DEBIT), "booked_debit": str(CURRENT_DEBIT),
            "dyadic_interval_numerators": bounds, "excluded_at_both_precisions": excludes,
            "limit_funds_at_both_precisions": limit_funds, "decision": decision}


if __name__ == "__main__":
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--helper", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.package.resolve(), args.helper.resolve()), indent=2))
