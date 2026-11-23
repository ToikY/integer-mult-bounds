"""Check the one-tick ordinary composition without generating a native image."""
from fractions import Fraction as Q
from hashlib import sha256
from argparse import ArgumentParser
import json
from math import ceil, floor
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "r411/audit/replay_scalar.py": "7805a516da11aded5595af0fe9f5c7843bf3dfd6a7822987c635e1bd361c9afa",
    "r411/audit/ORDINARY-TICK.json": "9df422f8c3ac8c10b8d468724791b14ed888ed5903eeea01e4e3f529dc97117a",
    "r410/bundle/overrides/matched_price_support.py": "4964fb80e4f2a449decbd35044808b3cc235c44405bfa926f6b12f95e9213c33",
}


def check(base):
    for name, digest in PINS.items():
        assert sha256((base / name).read_bytes()).hexdigest() == digest, name

    scalar_file = base / "r411/audit/replay_scalar.py"
    scalar = runpy.run_path(str(scalar_file))
    fringe_file = base / "r411/audit/ORDINARY-TICK.json"
    fringe = json.loads(fringe_file.read_bytes())
    ordinary, guard, cb, cg, dg = (scalar[k] for k in ("ordinary", "G", "CB", "CG", "DG"))
    powers = base / "r410/bundle/overrides/matched_price_support.py"
    power = runpy.run_path(str(powers))["series_power"]
    receipt = json.loads((scalar_file.parent / "inputs/8094-RESULT.json").read_bytes())
    assert sha256((scalar_file.parent / "inputs/8094-RESULT.json").read_bytes()).hexdigest() == scalar["PINS"]["inputs/8094-RESULT.json"]
    outer_file = scalar_file.parent / "inputs/outer_budget.py"
    assert sha256(outer_file.read_bytes()).hexdigest() == scalar["PINS"]["inputs/outer_budget.py"]
    qualify = runpy.run_path(str(outer_file))["qualify"]

    charged_child = Q(2401, 1024)
    actual_child = Q(75, 32)
    q = actual_child / charged_child
    assert q == Q(2400, 2401) and 1 / (1 - q) == 2401
    assert Q(2401, 376) < 8
    assert 2**21 < (Q(7, 10) * 2401) ** 2 < 2**22
    # Negative control: a tariff equal to the actual maximum gives no
    # finite geometric majorant uniform in the same-stage tree depth.
    assert actual_child / actual_child == 1

    L = 4474
    delta = Q(1, 2**128)
    new_debit = Q(1420717, 2**20)
    old_debit = Q(receipt["ordinary_finite_debit"])
    assert old_debit - new_debit == Q(1, 2**20)
    assert Q(fringe["matched_fringe_upper"]) == Q(837, 125)
    assert fringe["grade_cells"] == 24 and fringe["phase_intervals"] == 1211
    bare_lo, bare_hi = power(1024 * 134 * L, cb)
    common = charged_child * Q(4097, 4096) * Q(1028, 1024)
    common /= (1 - Q(10, L)) * (1 - delta)**3
    priced = common * bare_hi * (1 + Q(fringe["matched_fringe_upper"]) / L + delta)
    new_allow, opposite_allow = (2 * x for x in power(2, new_debit - 1))
    full_old_reserve_bare = Q(256, 255) * common * bare_lo * (1 + delta)
    assert priced < new_allow < opposite_allow < full_old_reserve_bare

    term, entry = receipt["terminal"], receipt["entry"]
    h = term["ordinary_H"]
    old_crossing = ordinary(h, old_debit)[-1] - 5 * guard
    new_crossing = ordinary(h, new_debit)[-1] - 5 * guard
    old_kappa = Q(term["kappa"])
    kappa = Q(floor(new_crossing * 10**15), 10**15)
    assert old_kappa <= old_crossing < kappa < new_crossing
    assert kappa == Q("0.003900857267793") and kappa - old_kappa == Q(7, 10**15)
    g = term["numerical_H"]
    paid_kappa = kappa + 5 * guard
    gaussian = cg - dg / g
    assert cg - dg / (g - 1) < paid_kappa < gaussian
    ordinary_booked = ordinary(h, new_debit, paid_kappa)
    assert ordinary_booked[-1] == paid_kappa
    signed = qualify(kappa, guard, paid_kappa, gaussian)
    assert (signed["strict"], signed["functional"]) == (54, 4)
    log_b = 128 + 3 * len(h) + 320 * sum(h)
    term_cost = max(84500001, 1602 + 220 * g + log_b)
    entry_premium = ceil((kappa - Q(entry["kappa"])) * term["stock"]["public_exponent_A"])
    combined_cost = 1 + max(term_cost, entry["log2_C"] + entry_premium)
    assert (log_b, entry_premium, combined_cost) == (85899221583, 121121, 85945126846)

    return {
        "scope": "one exact ordinary tariff, linear/power moments and signed scalar book; no installed replay",
        "old_ordinary_dyadic_crossing": old_crossing,
        "new_ordinary_dyadic_crossing": new_crossing,
        "comparison_delta_over_reported_kappa": kappa - old_kappa,
        "projected_kappa": kappa,
        "clock_contraction": q,
        "clock_geometric_sum": 2401,
        "reserve_with_conservative_suffix": new_allow - priced,
        "negative_full_reserve_shortfall_at_zero_suffix": full_old_reserve_bare - opposite_allow,
        "recurring_log2_C": combined_cost,
        "entry_conversion_bits": entry_premium,
        "terminal_rates": ordinary_booked,
        "signed_budget": signed,
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    print(json.dumps(check(parser.parse_args().root), indent=2, default=str))
