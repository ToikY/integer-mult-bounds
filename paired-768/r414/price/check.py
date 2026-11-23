"""Directed fixed-height price for one ordinary child-tariff change."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil
from pathlib import Path
import runpy
import signal

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "r411/audit/replay_scalar.py": "7805a516da11aded5595af0fe9f5c7843bf3dfd6a7822987c635e1bd361c9afa",
    "r410/bundle/overrides/matched_price_support.py": "4964fb80e4f2a449decbd35044808b3cc235c44405bfa926f6b12f95e9213c33",
    "r413/tariff-plan/RECEIPT.json": "885a7c76aed1a966b761823a12103b4315577680501efe9ebc8773cfb599bab5",
}
GRID = 10**15


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def finite_debit(power, cb):
    child, tariff = Q(2390, 1024), Q(2391, 1024)
    assert 21 * 3**7 + 3 <= child * (9 * 3**7 - 1)
    assert 21 * 3**6 + 3 > child * (9 * 3**6 - 1)
    assert 1 / (1 - child / tariff) == 2391 < 2401
    assert (Q(7, 10) * 2391)**2 < 2**22 and 2391 < 8 * 376
    assert Q(75, 32) / tariff > 1
    floor = 4474
    delta = Q(1, 2**128)
    common = (tariff * Q(4097, 4096) * Q(1028, 1024)
              * (1 + Q(186, 25 * floor) + delta)
              / ((1 - Q(10, floor)) * (1 - delta)**3))
    lo, hi = (common * v for v in power(1024 * 134 * floor, cb))
    debit = Q(1414404, 2**20)
    allow = 2 * power(2, debit - 1)[0]
    below = 2 * power(2, debit - 1 - Q(1, 2**20))[1]
    assert below < lo < hi < allow
    return debit, allow - hi, lo - below


def check(root):
    for relative, digest in PINS.items():
        assert sha(root / relative) == digest, relative
    old_path = root / "r411/audit/replay_scalar.py"
    old = runpy.run_path(str(old_path))
    power = runpy.run_path(str(root / "r410/bundle/overrides/matched_price_support.py"))["series_power"]
    for relative, digest in old["PINS"].items():
        assert sha(old_path.parent / relative) == digest
    source = json.loads((old_path.parent / "inputs/8094-RESULT.json").read_bytes())
    qualify = runpy.run_path(str(old_path.parent / "inputs/outer_budget.py"))["qualify"]
    debit, reserve, adjacent_shortfall = finite_debit(power, old["CB"])
    old_debit = Q(source["ordinary_finite_debit"])
    assert old_debit - debit == Q(6314, 2**20)

    entry, terminal = source["entry"], source["terminal"]
    eH, H = entry["ordinary_H"], terminal["ordinary_H"]
    eg, g = entry["numerical_H"], terminal["numerical_H"]
    assert g == 208653 and eg == 1024
    guard, cg, dg, ordinary = (old[key] for key in ("G", "CG", "DG", "ordinary"))
    gaussian = cg - dg / g - 5 * guard
    new_ordinary = ordinary(H, debit)[-1] - 5 * guard
    old_ordinary = ordinary(H, old_debit)[-1] - 5 * guard
    old_k = Q(terminal["kappa"])
    k = Q(ceil(min(gaussian, new_ordinary) * GRID) - 1, GRID)
    assert old_k <= old_ordinary < k < gaussian < new_ordinary
    assert k + Q(1, GRID) >= gaussian
    assert cg - dg / (g - 1) - 5 * guard < k
    assert k - old_k == Q(1364, GRID)

    paid = k + 5 * guard
    entry_rate = Q(entry["kappa"])
    entry_paid = entry_rate + 5 * guard
    assert ordinary(eH, debit)[-1] > entry_paid
    new_book = ordinary(H, debit, paid)
    exact_exp = terminal["stock"]["public_exponent_A"]
    entry_extra = ceil((k - entry_rate) * exact_exp)
    e_log_b = 40 + 22 + 16384 * sum(eH) + 25818582
    log_b = 128 + 3 * len(H) + 320 * sum(H)
    e_c = max(84500001, 1602 + 220 * eg + e_log_b)
    late_c = max(84500001, 1602 + 220 * g + log_b)
    complete = 1 + max(e_c + entry_extra, late_c)
    assert (e_log_b, log_b, e_c, late_c) == (entry["log2_B"], terminal["log2_B"], entry["log2_C"], terminal["log2_C"])
    assert (entry_extra, complete) == (121121, 85945126846)
    entry_controls = qualify(entry_rate, guard, entry_paid, cg - dg / eg)
    terminal_controls = qualify(k, guard, paid, cg - dg / g)
    for controls in (entry_controls, terminal_controls):
        assert (controls["strict"], controls["functional"]) == (54, 4)
    return {
        "scope": "one #8094 scalar invoice using the proven smaller child charge; physical signed replay not run",
        "debit": debit,
        "tariff": Q(2391, 1024),
        "child_sum": 2391,
        "debit_reserve": reserve,
        "lower_debit_shortfall": adjacent_shortfall,
        "projected_kappa": k,
        "old_kappa": old_k,
        "difference": k - old_k,
        "old_ordinary_ceiling": old_ordinary,
        "new_ordinary_ceiling": new_ordinary,
        "fixed_G_positive_ceiling": gaussian,
        "entry_premium": entry_extra,
        "full_recurring_log2_C": complete,
        "entry_signed_controls": entry_controls,
        "terminal_signed_controls": terminal_controls,
        "terminal_ordinary_booked": new_book,
    }


def timeout(_unused_signal, _unused_frame):
    raise TimeoutError("The one-profile price cap was reached")


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    try:
        print(json.dumps(check(parser.parse_args().root), indent=2, default=str))
    finally:
        signal.alarm(0)
