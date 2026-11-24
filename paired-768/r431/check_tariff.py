"""Check one precise ordinary child tariff at the pinned #8096 profile."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
import os
from pathlib import Path
import runpy
import signal
import sys
from tempfile import TemporaryDirectory


PINS = {
    "package/RESULT.json": "6894e85cec33111c46ca03a56ddad9a33cd913f267e4ec5c5d2ed95bc1adb8af",
    "assembled/receipt.py": "c39a9f0e754348849a210a291989b68d234e7639633977b18f7b4afc231b94fe",
    "handoff/round427/check_fringe.py": "63c8b56140e5f42f504ac98bb4824934e90e4a5ff26fa3065fe10c8e199640c4",
}


def authenticate(path, key):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == PINS[key], key
    return data


def checked_ordinary(debit, heights, stop):
    c = Q(4391986206293, 2**50)
    eta = Q(1, 256)
    previous = Q(0)
    for height in heights:
        ceiling = min(eta, (249 * (c - debit / height) + previous) / 250)
        previous = Q(floor(10**21 * ceiling) - 1, 10**21)
    return ceiling - 5 * stop


def price(result, power):
    prior_child = Q(2390, 1024)
    previous_tariff = Q(result["ordinary_child_tariff"])
    old_debit = Q(result["ordinary_finite_debit"])
    contraction = Q(result["ordinary_child_contraction"])
    assert previous_tariff == Q(2391, 1024) and old_debit == Q(1414404, 2**20)
    assert contraction == prior_child / previous_tariff == Q(2390, 2391)
    assert 1 / (1 - contraction) == result["ordinary_child_geometric_sum"] == 2391
    floor_x = 3**7
    exact_child = Q(21 * floor_x + 3, 9 * floor_x - 1)
    proposed_tariff = exact_child / contraction
    assert exact_child < prior_child and proposed_tariff < previous_tariff

    # The derivative numerator of (21*x+3)/(9*x-1) is negative.
    assert -21 - 9 * 3 == -48
    debit_drop = Q(128, 2**20)
    ratio = proposed_tariff / previous_tariff
    for bits in (112, 192):
        lower, upper = power(debit_drop, bits)
        assert lower > 1                       # unchanged tariff would fail
        assert ratio * upper < 1               # entire existing rounded factor
    new_debit = old_debit - debit_drop

    terminal = result["terminal"]
    stop = Q(1, 10**18)
    heights = terminal["ordinary_H"]
    assert heights == [31808, 502922, 7951907, 125730703, 134217727]
    old_ordinary = checked_ordinary(old_debit, heights, stop)
    new_ordinary = checked_ordinary(new_debit, heights, stop)
    g = result["gaussian"]
    gaussian = Q(g["trial"]) - Q(g["finite_loss"]["debit"]) / terminal["numerical_H"] - 5 * stop
    old = Q(terminal["kappa"])
    assert old < old_ordinary < gaussian < new_ordinary
    projected = Q(ceil(10**15 * gaussian) - 1, 10**15)
    assert old_ordinary < projected < gaussian <= projected + Q(1, 10**15)

    entry = result["entry"]
    exponent = terminal["stock"]["public_exponent_A"]
    conversion = ceil((projected - Q(entry["kappa"])) * exponent)
    recurring = 1 + max(entry["log2_C"] + conversion, terminal["log2_C"])
    assert (exponent, conversion, recurring) == (268644472, 121121, 85945126846)
    return {
        "scope": "One fixed profile, ordinary charge only, no native run",
        "inputs_sha256": PINS,
        "minimum_rank": 9,
        "worst_exact_child": str(exact_child),
        "previous_tariff": str(previous_tariff),
        "proposed_tariff": str(proposed_tariff),
        "factor_ratio": str(ratio),
        "geometric_sum": 2391,
        "old_ordinary_debit": str(old_debit),
        "tested_ordinary_debit": str(new_debit),
        "directed_precisions": [112, 192],
        "previous_tariff_fails_drop": True,
        "binding_after_drop": "Gaussian",
        "old_ordinary_guarded": str(old_ordinary),
        "new_ordinary_guarded": str(new_ordinary),
        "gaussian_guarded": str(gaussian),
        "projected_kappa": str(projected),
        "projected_delta": str(projected - old),
        "complete_log2_C": recurring,
    }


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--power-check", type=Path, required=True)
    args = parser.parse_args()
    signal.alarm(45)
    try:
        authenticate(args.power_check, "handoff/round427/check_fringe.py")
        power = runpy.run_path(str(args.power_check))["power_of_two"]
        driver = runpy.run_path(str(args.package.resolve() / "verify.py"))
        driver["authenticate"]()
        result = driver["read_json"](authenticate(args.package / "RESULT.json", "package/RESULT.json"))
        with TemporaryDirectory(prefix="croc-r431-tariff-") as directory:
            scratch = Path(directory).resolve()
            env = dict(os.environ, **driver["THREAD_ENV"], TMPDIR=str(scratch))
            prepared = driver["prepare"](scratch, env)
            source = authenticate(prepared / "receipt.py", "assembled/receipt.py").decode()
        assert "rank_guard = 3**7" in source
        assert "ordinary_upper = tape_factor(134, BINARY_C, 4474, Q(186, 25)) * Q(255, 256) * CHILD_TARIFF" in source
        assert "21 * rank_guard + 3 <= worst_child * (9 * rank_guard - 1)" in source
        print(json.dumps(price(result, power), indent=2))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
