"""Exact fixed-height signed scalar price for the standalone tariff change."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from math import ceil, floor
from pathlib import Path
import json
import runpy
import signal

PINS = {
    "r411/audit/inputs/8094-RESULT.json": "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
    "r411/audit/inputs/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "r413/tariff-plan/RECEIPT.json": "885a7c76aed1a966b761823a12103b4315577680501efe9ebc8773cfb599bab5",
}
PROFILE = "r411/audit/inputs/8094-RESULT.json"
CALLER = "r411/audit/inputs/outer_budget.py"
TARIFF = "r413/tariff-plan/RECEIPT.json"
TRIAL_B = Fraction(4391986206293, 2**50)
GUARD = Fraction(1, 10**18)
DISPLAY = 10**15
INTERMEDIATE = 10**21


def duplicate_safe(pairs):
    result = dict(pairs)
    if len(pairs) != len(result):
        raise ValueError("Duplicate JSON key")
    return result


def read(root, name):
    data = (root / name).read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError(f"Digest mismatch for {name}")
    return data


def stage_steps(heights, debit, eta):
    previous = Fraction(0)
    internal = []
    for rank in heights[:-1]:
        funded = min(eta, (249 * (TRIAL_B - debit / rank) + previous) / 250)
        previous = Fraction(floor(funded * INTERMEDIATE) - 1, INTERMEDIATE)
        internal.append(previous)
    funded = min(eta, (249 * (TRIAL_B - debit / heights[-1]) + previous) / 250)
    return internal, funded


def check(root):
    profile = json.loads(read(root, PROFILE), object_pairs_hook=duplicate_safe)
    tariffs = json.loads(read(root, TARIFF), object_pairs_hook=duplicate_safe)
    read(root, CALLER)
    qualify = runpy.run_path(str(root / CALLER))["qualify"]
    enter, term = profile["entry"], profile["terminal"]
    eta = {"entry": Fraction(39, 10000), "terminal": Fraction(1, 256)}
    assert tariffs["ordinary_heights"] == {label: profile[label]["ordinary_H"] for label in eta}
    assert Fraction(tariffs["proposed_tariff"]) == Fraction(2391, 1024)
    assert Fraction(tariffs["paid_child_mean_upper"]) / Fraction(tariffs["proposed_tariff"]) == Fraction(2390, 2391)
    assert 1 / (1 - Fraction(tariffs["same_stage_contraction_upper"])) == Fraction(tariffs["child_depth_sum_upper"]) == 2391
    assert 8 * 376 > 2391 and (Fraction(7, 10) * 2391)**2 < 2**22
    assert tariffs["terminal_added_bits_kept_per_stage"] == 3
    assert tariffs["entry_clock_exponent_allowance"] == 22
    prior_debit = Fraction(profile["ordinary_finite_debit"])
    fail_debit, pass_debit = tariffs["proposed_adjacent_debits_fail_pass"]
    scale = tariffs["ordinary_grid_denominator"]
    assert (fail_debit, pass_debit, scale) == (1414403, 1414404, 2**20)
    debit = Fraction(pass_debit, scale)
    assert prior_debit - debit == Fraction(6314, 2**20)
    gauss_trial = Fraction(profile["gaussian"]["trial"])
    gauss_loss = Fraction(profile["gaussian"]["raw_loss"])
    g_terminal = term["numerical_H"]
    assert g_terminal == 208653
    gaussian = gauss_trial - gauss_loss / g_terminal
    _, old_bound = stage_steps(term["ordinary_H"], prior_debit, eta["terminal"])
    _, new_bound = stage_steps(term["ordinary_H"], debit, eta["terminal"])
    old_rate = Fraction(term["kappa"])
    old_limit, new_limit = old_bound - 5 * GUARD, new_bound - 5 * GUARD
    gaussian_limit = gaussian - 5 * GUARD
    rate = Fraction(ceil(min(new_limit, gaussian_limit) * DISPLAY) - 1, DISPLAY)
    higher_tick = rate + Fraction(1, DISPLAY)
    assert old_rate <= old_limit < rate < gaussian_limit < new_limit
    assert gaussian_limit < higher_tick < new_limit
    closed = {}
    for label in eta:
        row = profile[label]
        for d in (prior_debit, debit):
            kappa = Fraction(row["kappa"]) if label == "entry" or d == prior_debit else rate
            internals, max_ordinary = stage_steps(row["ordinary_H"], d, eta[label])
            paid = kappa + 5 * GUARD
            assert 0 < paid < max_ordinary
            rates = [*internals, paid]
            assert all(a < b for a, b in zip(rates, rates[1:]))
            raw_positive = gauss_trial - gauss_loss / row["numerical_H"]
            outer = qualify(kappa, GUARD, paid, raw_positive)
            assert outer["strict"] == 54 and outer["functional"] == 4
            if d == prior_debit:
                assert rates == [Fraction(v) for v in row["ordinary_rates"]]
                assert outer == row["signed"]
                continue
            if label == "entry":
                log_b = 40 + 22 + 2**14 * sum(row["ordinary_H"]) + sum(row["binary_surcharges"])
            else:
                log_b = 128 + 3 * len(row["ordinary_H"]) + 320 * sum(row["ordinary_H"])
            log_c = max(84_500_001, log_b + 220 * row["numerical_H"] + 1602)
            assert (log_b, log_c) == (row["log2_B"], row["log2_C"])
            closed[label] = {"rates": rates, "signed": outer, "log2_B": log_b, "log2_C": log_c}
    try:
        qualify(higher_tick, GUARD, higher_tick + 5 * GUARD, gaussian)
    except ArithmeticError:
        pass
    else:
        raise ValueError("The next display tick unexpectedly passed")
    g_lower_margin = gauss_trial - gauss_loss / (g_terminal - 1) - rate - 5 * GUARD
    try:
        qualify(rate, GUARD, rate + 5 * GUARD, gauss_trial - gauss_loss / (g_terminal - 1))
    except ArithmeticError:
        assert g_lower_margin < 0
    else:
        raise ValueError("The preceding Gaussian height unexpectedly passed")
    entry_kappa = Fraction(enter["kappa"])
    activation = term["stock"]["public_exponent_A"]
    surcharge = ceil((rate - entry_kappa) * activation)
    assert surcharge == ceil((old_rate - entry_kappa) * activation) == profile["entry_price_surcharge"]
    total = 1 + max(closed["entry"]["log2_C"] + surcharge, closed["terminal"]["log2_C"])
    assert total == profile["complete_log2_C"]
    return {
        "scope": "Exact signed scalar price at fixed #8094 heights; native receiver, source assembly, installed setup and signed replay open.",
        "profile_head": "c20a08dc0a79a989e3515068560d5da371c0a2a8",
        "profile_cases": 1,
        "binary_debit": debit,
        "gaussian_height": g_terminal,
        "old_booked_kappa": old_rate,
        "old_guarded_ordinary_crossing": old_limit,
        "new_guarded_ordinary_crossing": new_limit,
        "new_guarded_gaussian_crossing": gaussian_limit,
        "maximum_display_tick": rate,
        "delta_over_reported_8094": rate - old_rate,
        "delta_over_old_guarded_crossing": rate - old_limit,
        "ordinary_headroom_at_new_kappa": new_limit - rate,
        "positive_margin_at_new_kappa": gaussian_limit - rate,
        "next_display_tick": higher_tick,
        "next_tick_gaussian_margin": gaussian_limit - higher_tick,
        "gaussian_height_minus_one_margin": g_lower_margin,
        "entry_surcharge_bits": surcharge,
        "complete_recurring_log2_C": total,
        "tiers": closed,
        "inputs_sha256": PINS,
    }


def timeout(_signal, _frame):
    raise TimeoutError("30-second scalar cap")


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    try:
        print(json.dumps(check(args.root), indent=2, default=str))
    finally:
        signal.alarm(0)
