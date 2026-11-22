"""Compare one exact #8055 retuning through the signed entry and terminal geometry."""

from argparse import ArgumentParser
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import runpy

PINS = {
    "installations.py": "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df",
    "receipt.py": "3d0219eb2262ea64ccf2dc8da4d2877e32c519c4670d99577703f8bfc236ba61",
    "CLOCK.md": "cf71e4a3216df23eb7e4fa8a8d9de3735e6257c65ca8a60a5085d9f3c90c4ecb",
    "RESULT.json": "661e16fcb533b69b97ad2dc91ab81bed79c44e7fdce01306ce573cb6f0ed7fa7",
    "source/activation.py": "6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b",
    "source/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "source/outer_clock.py": "63363c3da673365f3ac5e1b7e318c6938005f1e9c9896799504cc598efbf96fa",
}
KAPPA = Q(".003898202")
COMPARATOR = Q(".0038982016137")
NEW_H = (35327, 559462)
H_M = 680000
G = Q(1, 10**18)


def ceiling(r):
    x = Q(r)
    return -(-x.numerator // x.denominator)


def independent_geometry(heights, numerical):
    cuts = []
    for h in heights:
        short = ceiling(Q(250, 249) * (h + 64))
        cuts.append(max(short, h + 64 + cuts[-1]) if cuts else short)
    target = numerical + cuts[-1] + 102
    k = target.bit_length()
    s = target + 7 * k
    if s > 2**k:
        k += 1
        s = target + 7 * k
    assert (s - 1).bit_length() == k and s - 7 * k == target
    assert (s - 1) - 7 * (s - 2).bit_length() < target
    jump = (1 << k) + 1 - 7 * (k + 1) - target
    assert jump >= 0
    width = 128 * (4 * (s + 1) + 6)
    q = (6 * width - 1).bit_length()
    axis_log = s - 1 - q
    side = ceiling(Q((1 << q), 6))
    offset = (-(1 << (s - 1))) % 6
    assert offset in (2, 4)
    assert ((1 << (s - 1)) + offset - 6).bit_length() == s - 1
    assert ((1 << (s - 1)) + offset).bit_length() == s
    return {
        "binary_cuts": cuts,
        "terminal_A": s - 1,
        "controller_s": s,
        "first_header_offset": offset,
        "next_jump_slack": jump,
        "minimum_window": width,
        "log2_axes": axis_log,
        "largest_axis_width": side,
        "private_geometry_log2": 1024 * (side + s + 67) + s,
        "dense_root_rows_log2": 2 * side,
    }


def ordinary(profile, b):
    prior = Q()
    rates = []
    margins = []
    for index, h in enumerate(profile.rank_logs):
        uncapped = (249 * (b - Q(11, 8 * h)) + prior) / 250
        cap = min(profile.eta, uncapped)
        rate = profile.ordinary if index + 1 == len(profile.rank_logs) else Q(
            int(cap * 10**21) - 1, 10**21
        )
        assert prior < rate < cap
        margins.append(cap - rate)
        rates.append(rate)
        prior = rate
    return rates, margins


def check(package, raw_trial):
    for name, expected in PINS.items():
        assert sha256((package / name).read_bytes()).hexdigest() == expected, name
    installation = runpy.run_path(str(package / "installations.py"))
    active = runpy.run_path(str(package / "source/activation.py"))["resource_receipt"]
    inherited_prefix = runpy.run_path(str(package / "source/outer_clock.py"))["financial_checks"]
    signed = runpy.run_path(str(package / "source/outer_budget.py"))["qualify"]
    base_receipt = json.loads((package / "RESULT.json").read_bytes())
    early = installation["ENTRY"]
    old = installation["TERMINAL"]
    new = replace(old, rank_logs=NEW_H, kappa=KAPPA)
    old_geom = independent_geometry(old.rank_logs, old.complex_log)
    geom = independent_geometry(new.rank_logs, new.complex_log)
    assert old_geom["terminal_A"] == base_receipt["terminal"]["stock"]["public_exponent_A"]
    stock = active(new)
    assert geom["terminal_A"] == stock["public_exponent_A"]
    assert geom["first_header_offset"] == stock["first_public_offset"]
    assert geom["binary_cuts"] == stock["binary_cuts"]
    assert min(new.rank_logs) >= 8192 and 2_660_000 * 32 < (1 << 30)
    assert inherited_prefix() == base_receipt["prefix"]
    entry_stock = active(early)
    assert json.loads(json.dumps(entry_stock)) == base_receipt["entry"]["stock"]
    B = installation["BINARY_C"]
    old_rates, _ = ordinary(old, B)
    assert list(map(str, old_rates)) == base_receipt["terminal"]["rates"]
    rates, margins = ordinary(new, B)
    assert G == Q(1, new.positive_stop_denominator)
    raw_requirement = KAPPA + 5 * G + Q(43, 256 * H_M)
    old_gaussian = installation["GAUSSIAN_C"]
    assert old_gaussian < raw_requirement
    previous_old = old_rates[-1]
    assert signed(old.kappa, G, previous_old, old_gaussian - Q(43, 256 * H_M)) == (
        base_receipt["terminal"]["signed"]
    )
    log_b = 128 + 320 * sum(NEW_H)
    log_c = max(84_500_001, 1602 + 220 * H_M + log_b)
    early_premium = ceiling((KAPPA - early.kappa) * geom["terminal_A"])
    entry_log = base_receipt["entry"]["log2_C"] + early_premium
    combined = max(entry_log, log_c) + 1
    result = {
        "peer_source": "7b48187d99525ad59f560de3921ec7e48382484c",
        "exact_comparator": "c5cbef6e558542d6e809aabb6ead89b9e51f7b1c",
        "target_kappa": str(KAPPA),
        "comparator_kappa": str(COMPARATOR),
        "comparator_gain_if_verified": str(KAPPA - COMPARATOR),
        "pins": PINS,
        "ordinary_stage_rates": list(map(str, rates)),
        "ordinary_stage_margins": list(map(str, margins)),
        "eta": str(new.eta),
        "terminal_width_logs": [92 * h for h in (*NEW_H, H_M)],
        "terminal_geometry": geom,
        "terminal_stock": stock,
        "entry_rate_conversion_bits": early_premium,
        "entry_log2_C_after_conversion": entry_log,
        "terminal_log2_B": log_b,
        "terminal_log2_C": log_c,
        "total_log2_C": combined,
        "delta_log2_C_vs_peer": combined - base_receipt["complete_log2_C"],
        "old_gaussian_price_shortfall": str(raw_requirement - old_gaussian),
        "strict_raw_requirement": str(raw_requirement),
        "currency": "analytic retuning only, literal Gaussian replacement still required",
    }
    if raw_trial is not None:
        assert raw_trial > raw_requirement
        positive = raw_trial - Q(43, 256 * H_M)
        result["booking_test_given_raw_trial"] = signed(KAPPA, G, rates[-1], positive)
        result["candidate_raw_trial"] = str(raw_trial)
        result["warning_on_trial"] = "the provided Gaussian trial needs independent literal proof"
    return result


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--package", required=True, type=Path)
    p.add_argument("--raw-trial", type=Q)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = check(args.package, args.raw_trial)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
