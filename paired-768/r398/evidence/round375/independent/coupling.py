"""Reprice the original 48-call 1-to-79 quarter inventory at one new dyadic."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import runpy

PEER_BASE = "round371/peer8055/research/tiered-native-multiplier"

PINS = {
    "round366/gaussian/receipt.json": "9e1206f26d124f9f788a96ff43453195c4ae8c9b679acbf8a0ca132c80a5b7a1",
    "round371/peer8055/research/tiered-native-multiplier/RESULT.json":
        "661e16fcb533b69b97ad2dc91ab81bed79c44e7fdce01306ce573cb6f0ed7fa7",
    "round371/peer8055/research/tiered-native-multiplier/source/outer_budget.py":
        "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "round371/peer8055/research/tiered-native-multiplier/installations.py":
        "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df",
    "round371/peer8055/research/tiered-native-multiplier/source/activation.py":
        "6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b",
    "round374/publish/research/p104-compact-rounded-partitions/RESULT.json":
        "0d20d4607fd2d68dfe0aaf84e063d986cb2c8e614a89dcd3a825135d62e075c6",
    "round375/independent/verified.json":
        "92a161b5c73f42c419d7a1c49e97729b6b5ac18724b9275fd8feca9cf7b0524e",
}
UNIT = 2**112
C = Q(1097317122991, 2**48)
K = Q(".00389821005")
B = Q(4391986206293, 2**50)
D = Q(339, 2048)
G = Q(1, 10**18)


def power_interval(rank, exponent):
    """Match the published fixed-point power rules, with exact quotient enclosures."""
    assert rank > 0 and exponent >= 0
    if rank.denominator > 1:
        lo, hi = power_interval(Q(rank.numerator), exponent)
        low, high = power_interval(Q(rank.denominator), exponent)
        return lo * UNIT // high, -(-hi * UNIT // low)
    whole, residue = divmod(exponent.numerator, exponent.denominator)
    depth = exponent.denominator.bit_length() - 1
    assert exponent.denominator == 2**depth
    a, b = rank.numerator * UNIT, rank.numerator * UNIT
    x, y = rank.numerator**whole * UNIT, rank.numerator**whole * UNIT
    for bit in range(depth - 1, -1, -1):
        a = isqrt(a * UNIT)
        b = 1 + isqrt(b * UNIT - 1)
        if (residue >> bit) & 1:
            x = x * a // UNIT
            y = -(-y * b // UNIT)
    return x, y


def base_copy(dual):
    """Invert H[r]=h[r]+h[r/8] on strictly increasing integer grades."""
    raw = Counter()
    for grade, count in sorted(dual.items()):
        assert grade.denominator == 1
        raw[grade] = count - raw[grade / 8]
        assert raw[grade] >= 0
    raw = +raw
    rebuilt = raw.copy()
    for grade, count in raw.items():
        rebuilt[8 * grade] += count
    assert rebuilt == dual
    return raw


def dual_copy(raw):
    result = raw.copy()
    for grade, count in raw.items():
        result[79 * grade] += count
    return result


def allocate(c, targets, paid):
    exponent = 1 - c
    t_mass = {k: n * power_interval(k, exponent)[0] for k, n in targets.items()}
    p_mass = {r: n * power_interval(r, exponent)[1] for r, n in paid.items()}
    total_t, total_p = sum(t_mass.values()), sum(p_mass.values())
    ratio = Q(total_p, total_t)
    cap = {k: v * ratio for k, v in t_mass.items()}
    inbound = cap.copy()
    cells = {}
    sorted_targets = sorted(targets, reverse=True)
    for r in sorted(paid, reverse=True):
        remainder = p_mass[r]
        for k in sorted_targets:
            if 5 * r > 4 * k or remainder <= 0:
                break
            take = min(remainder, cap[k])
            if take:
                cells[r, k] = Q(take, p_mass[r])
                cap[k] -= take
                remainder -= take
        assert remainder == 0, r
    assert not any(cap.values())
    for r in paid:
        assert sum(v for (r0, _), v in cells.items() if r0 == r) == 1
    for k in targets:
        assert sum(v * p_mass[r] for (r, k0), v in cells.items() if k0 == k) == inbound[k]
    return 1 - ratio, cells


def funding(signed, kappa, heights, hg):
    pre = Q()
    floors = []
    for i, h in enumerate(heights):
        cap = min(Q(".0039"), (249 * (B - Q(11, 8 * h)) + pre) / 250)
        new = kappa + 5 * G if i == 1 else Q(int(cap * 10**21) - 1, 10**21)
        assert pre < new < cap
        floors.append(str(cap - new))
        pre = new
    return {"ordinary_slack": floors, "signed": signed(kappa, G, pre, C - D / hg)}


def check(root):
    inputs = {}
    for path, digest in PINS.items():
        source = (root / path).read_bytes()
        assert sha256(source).hexdigest() == digest, path
        if path.endswith(".json"):
            inputs[path] = json.loads(source)
    signed = runpy.run_path(str(root / PEER_BASE / "source/outer_budget.py"))["qualify"]
    census, peer, predecessor, price = inputs.values()
    assert Q(price["one_price_followup"]["trial_kappa"]) == K
    assert Q(price["one_price_followup"]["gaussian_trial"]) == C

    signed_target, signed_paid = (Counter({Q(k): n for k, n in hist.items()}) for hist in (
        census["ranks"]["target"], census["ranks"]["paid"]
    ))
    halves = signed_paid.pop(Q(1, 2))
    assert halves == 2016
    signed_paid[1] += halves // 2
    t, p = (base_copy(hist) for hist in (signed_target, signed_paid))
    assert (t.total(), p.total()) == (52608, 281568)
    targets, original_paid = dual_copy(t), dual_copy(p)
    original_paid[1] -= 1008
    half = original_paid.copy()
    half[Q(1, 2)] = 2016
    quarter = original_paid.copy()
    quarter.update({Q(1, 4): 1008, Q(3, 4): 1008})
    assert (targets.total(), half.total(), quarter.total()) == (105216, 564144, 564144)
    old_margin, old_cells = allocate(Q(2143194013, 2**39), targets, half)
    current_margin, current_cells = allocate(Q(2143195807, 2**39), targets, quarter)
    assert old_margin == Q(peer["gaussian"]["margin"]) and len(old_cells) == 62
    assert current_margin == Q(predecessor["gaussian"]["margin"]) and len(current_cells) == 63

    margin, cells = allocate(C, targets, quarter)
    assert 0 < margin < current_margin
    assert len(cells) == 63 and cells.keys() == current_cells.keys()
    assert cells[4424, 10191] == 1 and targets[10191] == 624
    max_ratio = max(Q(k) / r for r, k in cells)
    assert max_ratio == 9
    min_share = min(cells.values()) / targets.total()
    max_bits = max(max(x.numerator.bit_length(), x.denominator.bit_length()) for x in cells.values())
    assert min_share > Q(1, 2**64) and max_bits < 512
    for r, k in cells:
        errors = (0, Q(-1, 2)) if r == Q(1, 4) else (0, Q(1, 2)) if r == Q(3, 4) else (0,)
        for error in errors:
            assert 8 * k - 10 * r + error >= 0
            assert 10 * k - 8 * r + error < 10 * k
            assert error <= 8 * r
    L, A, h = 32768, 12087, 1024
    assert 4 * A < 1024 * A
    assert 41 - 34 * h < -2
    assert Q(99, 100) <= 1 - margin < 1
    assert Q(power_interval(Q(max(targets)), C)[1], UNIT) < Q(106,100)
    assert 1 - C > Q(996,1000)
    d = Q(1, 2**128)
    factor = Q(256, 255) * Q(4097, 4096) * Q(1028, 1024)
    factor *= Q(power_interval(Q(1024 * A * L), C)[1], UNIT)
    factor *= (1 + Q(64, L) + d) / ((1-Q(10, L)) * (1 - d)**3)
    factor_upper = -(-factor.numerator * 10**6 // factor.denominator)
    assert factor ** D.denominator < 2 ** D.numerator

    assert 48 * (3042 + 697 + 200) == 189072
    assert 6 * 189072 == 1134432
    profile = runpy.run_path(str(root / PEER_BASE / "installations.py"))["Profile"]
    stock = runpy.run_path(str(root / PEER_BASE / "source/activation.py"))["resource_receipt"]
    terminal_stock = stock(profile((35327, 561325), 680000, K))
    entrance = terminal_stock["public_exponent_A"]
    finite_extra = (K - Q(".00345")) * entrance
    premium = -(-finite_extra.numerator // finite_extra.denominator)
    log_b = 128 + 320 * (35327 + 561325)
    log_c = 1 + max(peer["entry"]["log2_C"] + premium, 1602 + 220 * 680000 + log_b)
    assert (entrance, premium, log_c) == (1277171, 573, 340530371)
    return {
        "pins": PINS,
        "raw_trial": str(C),
        "kappa_if_complete_replay_passes": str(K),
        "cost_upper_without_claiming_literal_acceptance": str(C - D / 680000 - 5 * G),
        "raw_directed_relative_margin": str(margin),
        "lower_bound_on_cell_probability": str(min_share),
        "largest_reduced_cell_bits": max_bits,
        "transport_cells": [[str(r), str(k), str(p)] for (r, k), p in sorted(cells.items())],
        "changed_cell_fractions_vs_R374": sum(p != current_cells[r, k] for (r, k), p in cells.items()),
        "retimed_factor_upper_in_millionths": factor_upper,
        "gaussian_debit_units": str(D),
        "entry": funding(signed, Q(".00345"), (3000, 3080), 1024),
        "terminal": funding(signed, K, (35327, 561325), 680000),
        "terminal_stock": terminal_stock,
        "entry_premium_bits": premium,
        "recurring_clock_log2_upper": log_c,
        "accepted_exact_price_and_support": True,
        "remaining_gate": "new literal compiler, typed calendar, physical signed and full registered replay",
    }


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = check(args.inputs)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
