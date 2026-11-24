"""Test one exact minimum-rank child tariff on #8097's complete booked factor."""

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
    "peer/RESULT.json": "f3ff96fb44169735871b27c1a22dd3f499e20a77401896fe53845f546aa1c9f5",
    "peer/prepare.py": "5c54f3b1f1156eb4710038b1d0124d83db9241c80cb06c59abe1f0d132f8a55b",
    "handoff/r431/check_tariff.py": "f5e258d3fe81b2a220e4458846c733649dd607fa3d0b07d1c1d4ff2a57d3cc8f",
    "handoff/r427/check_fringe.py": "63c8b56140e5f42f504ac98bb4824934e90e4a5ff26fa3065fe10c8e199640c4",
}


def read_pinned(peer, handoff, key):
    root, name = key.split("/", 1)
    data = ({"peer": peer, "handoff": handoff}[root] / name).read_bytes()
    assert sha256(data).hexdigest() == PINS[key], key
    return data


def check(peer, handoff):
    inputs = {key: read_pinned(peer, handoff, key) for key in PINS}
    original = json.loads(inputs["peer/RESULT.json"])
    source = inputs["peer/prepare.py"].decode()
    assert "assert tape_factor_periodic(134, BINARY_C, ORDINARY_FLOOR, paid, bit_cells) * CHILD_TARIFF < ordinary_upper" in source
    assert "Q(256, 255)" in source and "assert Q(75, 32) / CHILD_TARIFF == Q(2400, 2401)" in source
    raw = source.split("RAW_FLOOR_PATCH =", 1)[1].split("def replace", 1)[0]
    edits = [line for line in raw.splitlines() if line[:1] in ("+", "-") and not line.startswith(("+++", "---"))]
    call = "    return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C"
    assert edits == ["-" + call + ")", "+" + call + ", level_floor=1156)"]

    ordinary = runpy.run_path(str(handoff / "r431/check_tariff.py"))["checked_ordinary"]
    power = runpy.run_path(str(handoff / "r427/check_fringe.py"))["power_of_two"]
    tariff_old = Q(original["ordinary_child_tariff"])
    debit_old = Q(original["ordinary_finite_debit"])
    assert tariff_old == Q(2401, 1024) and debit_old == Q(1418665, 2**20)
    assert original["ordinary_child_geometric_sum"] == 2401
    contraction = Q(2390, 2391)
    tariff = Q(22965, 9841) / contraction
    ratio = tariff / tariff_old
    drop = Q(4096, 2**20)
    assert ratio * (1 + drop) < 1
    for bits in (112, 192):
        lower, upper = power(drop, bits)
        assert lower > 1 and ratio * upper < 1
    assert 1 / (1 - contraction) == 2391 < original["ordinary_child_geometric_sum"]
    debit = debit_old - drop

    terminal = original["terminal"]
    old = Q(terminal["kappa"])
    stop = Q(1, 10**18)
    heights = terminal["ordinary_H"]
    assert heights == [8192, 63614, 1005821, 15903360, 251454111, 268435455]
    old_ordinary, new_ordinary = (ordinary(value, heights, stop) for value in (debit_old, debit))
    gaussian = Q(original["gaussian"]["trial"]) - Q(original["gaussian"]["finite_loss"]["debit"]) / terminal["numerical_H"] - 5 * stop
    ceiling = min(new_ordinary, gaussian)
    projected = Q(ceil(10**15 * ceiling) - 1, 10**15)
    assert old == Q("0.003900862325217") and old < old_ordinary < projected < ceiling
    exponent = terminal["stock"]["public_exponent_A"]
    entry = original["entry"]
    conversion = ceil((projected - Q(entry["kappa"])) * exponent)
    recurring = 1 + max(entry["log2_C"] + conversion, terminal["log2_C"])
    assert (exponent, conversion, recurring) == (536923552, 242079, 171810078109)
    return {
        "scope": "One fixed 28-bit six-stage source and price screen, no native build",
        "inputs_sha256": PINS,
        "proposed_tariff": str(tariff),
        "whole_factor_ratio": str(ratio),
        "kept_ordinary_reserve": "256/255",
        "old_geometric_budget": 2401,
        "proved_new_geometric_sum": 2391,
        "tested_debit": str(debit),
        "directed_precisions": [112, 192],
        "old_ordinary_cap": str(old_ordinary),
        "new_ordinary_cap": str(new_ordinary),
        "gaussian_cap": str(gaussian),
        "binding": "ordinary" if new_ordinary <= gaussian else "Gaussian",
        "projected_kappa": str(projected),
        "projected_delta": str(projected - old),
        "complete_log2_C": recurring,
    }


if __name__ == "__main__":
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--peer-package", type=Path, required=True)
    parser.add_argument("--handoff-root", type=Path, required=True)
    args = parser.parse_args()
    signal.alarm(45)
    try:
        print(json.dumps(check(args.peer_package, args.handoff_root), indent=2))
    finally:
        signal.alarm(0)
