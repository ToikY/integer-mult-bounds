"""Price one stronger uniform child-mean bound for the exact #8098 profile."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil
from pathlib import Path
import runpy
import signal
import sys


PINS = {
    "package/RESULT.json": "30f83c4820557c0ca3461928c5000da6a0c9fc4b98b3bf6539df8bdb18fb0d93",
    "package/source/transfer/ASSEMBLY.json": "457ee19688c033bea32fcdb5a61a5cc5bd7bba97227799e09f220ae85e60d8df",
    "package/source/transfer/edits.py": "622ce1c5018e294d693c0621b0ccae70b88e0b923009ec81fa8420256205d290",
    "handoff/r427/check_fringe.py": "63c8b56140e5f42f504ac98bb4824934e90e4a5ff26fa3065fe10c8e199640c4",
    "handoff/r431/check_tariff.py": "f5e258d3fe81b2a220e4458846c733649dd607fa3d0b07d1c1d4ff2a57d3cc8f",
}
BASE = "c7d4441c5e4406bff4a79576cf6b2ce0a596390a"


def unique_object(pairs):
    value = {}
    for key, child in pairs:
        if key in value:
            raise ValueError(f"Duplicate source key {key!r}")
        value[key] = child
    return value


def check(package, handoff):
    roots = {"package": package, "handoff": handoff}
    inputs = {}
    for key, digest in PINS.items():
        prefix, name = key.split("/", 1)
        data = (roots[prefix] / name).read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f"Pinned file differs at {key}")
        inputs[key] = data

    result = json.loads(inputs["package/RESULT.json"], object_pairs_hook=unique_object)
    source = json.loads(inputs["package/source/transfer/ASSEMBLY.json"], object_pairs_hook=unique_object)
    assert source["candidate_installation_sha256"] == "d34b860c4c35aeb302767216bf58dd9da627fe2b1b2b646fd70d6a544563648e"
    assert b"assert all(height >= 4 for profile in (ENTRY, TERMINAL)" in inputs["package/source/transfer/edits.py"]
    assert b"full_factor = tape_factor_periodic(" in inputs["package/source/transfer/edits.py"]
    assert b"ORDINARY_DEBIT = Q(1418665, 2**20)" in inputs["package/source/transfer/edits.py"]
    checked_ordinary = runpy.run_path(str(handoff / "r431/check_tariff.py"))["checked_ordinary"]
    power = runpy.run_path(str(handoff / "r427/check_fringe.py"))["power_of_two"]

    entry, terminal = result["entry"], result["terminal"]
    heights = tuple(terminal["ordinary_H"])
    old_rate = Q(terminal["kappa"])
    assert old_rate == Q(".003900862339776")
    assert [min(entry["ordinary_H"]), min(heights)] == [3000, 8192]
    assert heights == (8192, 63614, 1005821, 15903360, 251454111, 268435455)
    contraction = Q(result["ordinary_child_contraction"])
    old_tariff = Q(result["ordinary_child_tariff"])
    assert contraction == Q(2390, 2391)
    assert old_tariff * contraction == Q(22965, 9841)
    assert 1 / (1 - contraction) == result["ordinary_child_geometric_sum"] == 2391
    assert result["ordinary_child_geometric_budget"] == 2401

    # The same mean decreases with x, and the priced stages have N=2**H>=16.
    n = 16
    x = 3 ** (n - 2)
    assert 21 * (-1) - 9 * 3 == -48
    mean = Q(21 * x + 3, 9 * x - 1)
    assert 1 < Q(7, 3) < mean < old_tariff * contraction
    tariff = mean / contraction
    ratio = tariff / old_tariff
    drop = Q(128, 2**20)
    for precision in (112, 192):
        low, high = power(drop, precision)
        assert 1 < low <= high and ratio * high < 1

    stop = Q(1, 10**18)
    old_debit = Q(result["ordinary_finite_debit"])
    assert old_debit == Q(1414569, 2**20)
    new_debit = old_debit - drop
    # Transfer the authenticated #8097 allowance using #8098's existing tariff.
    # Convexity bounds 2**(4224/2**20) by 1+4224/2**20.
    current_ratio = old_tariff / Q(2401, 1024)
    comparison = current_ratio * (1 + Q(1418665, 2**20) - new_debit)
    assert comparison == Q(12903689025, 12907770512) < 1
    old_cap, new_cap = (checked_ordinary(debit, heights, stop) for debit in (old_debit, new_debit))
    gaussian = result["gaussian"]
    gaussian_cap = Q(gaussian["trial"]) - Q(gaussian["finite_loss"]["debit"]) / terminal["numerical_H"] - 5 * stop
    updated_rate = Q(ceil(10**15 * new_cap) - 1, 10**15)
    assert old_rate < old_cap < updated_rate < new_cap < gaussian_cap
    assert new_cap <= updated_rate + Q(1, 10**15)
    activation = terminal["stock"]["public_exponent_A"]
    premium = ceil((updated_rate - Q(entry["kappa"])) * activation)
    recurring = 1 + max(entry["log2_C"] + premium, terminal["log2_C"])
    assert (activation, premium, recurring) == (536923552, 242079, 171810078109)
    return {
        "scope": "One exact ordinary price on the installed domain. Signed replay and selector edit remain unrun.",
        "base_commit": BASE,
        "inputs_sha256": PINS,
        "minimum_priced_H": min(*entry["ordinary_H"], *heights),
        "used_domain_floor_N": n,
        "uniform_child_mean_upper": str(mean),
        "candidate_tariff": str(tariff),
        "charged_geometric_budget": 2401,
        "kept_reserve": "256/255",
        "whole_factor_ratio": str(ratio),
        "directed_precisions": [112, 192],
        "candidate_debit": str(new_debit),
        "existing_tariff_also_funds_this_debit": True,
        "existing_tariff_directed_chord_control": str(comparison),
        "old_crossing": str(old_cap),
        "candidate_crossing": str(new_cap),
        "gaussian_crossing": str(gaussian_cap),
        "provisional_kappa": str(updated_rate),
        "provisional_delta": str(updated_rate - old_rate),
        "complete_log2_C": recurring,
    }


if __name__ == "__main__":
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--handoff-root", type=Path, required=True)
    args = parser.parse_args()
    signal.alarm(45)
    try:
        print(json.dumps(check(args.package.resolve(), args.handoff_root.resolve()), indent=2))
    finally:
        signal.alarm(0)
