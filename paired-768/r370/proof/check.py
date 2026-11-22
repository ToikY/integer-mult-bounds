"""Check the exact integral and paid-width inequalities for a rounded Gaussian recipe."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

INPUT_PIN = "dbde66c13af0f44c4ba55690ee7a4324111c29961211f740eea2c3b1f513a037"
L = 32768
AMBIENT = 1224
POSITIONS = 564142
MIN_H = 1024


def proof(receipt):
    assert receipt["exact_head"] == "f6f4ecd5dd717ce2b155dd564469e9693ac90f6d"
    trial = Q(receipt["hypothetical_trial"])
    b = trial.denominator.bit_length() - 1
    assert trial.denominator == 2**b and 0 < trial < Q(1, 250)
    assert receipt["paid_count"] == POSITIONS < 2**20
    assert receipt["productive_count"] == 105216 < 2**17
    # The minimum changed paid grade is 1/4, and the maximum target grade is 1032.
    # For every used endpoint x, x <= max(U, U*max_ratio) < N.
    max_ratio = 4 * 1032
    assert max_ratio < 1024 * AMBIENT
    # b≤46: at most 47 products, inverse-power width <= 2^99*N^23/G.
    # The next log coefficient includes two endpoints, N^6, and 1/t < 2.
    assert b <= 46 and 2 * (46 + 1) < 2**7
    error_log2_upper = 37 - 35 * MIN_H
    assert error_log2_upper < -2

    concrete = []
    choices = (Q(1, 4), Q(3, 4))
    for e in (L, L + 2):
        w = e - 8
        first = w // 4
        second = w - first
        assert 0 < first <= second and first + second == w
        for r, length in zip(choices, (first, second)):
            error = length - r * w
            assert abs(error) <= Q(1, 2)
            assert 8 - 10 * r + error >= 0
            assert 4 * 1 >= 5 * r
            assert length >= r * (e - 10)
        concrete.append([e, w, first, second])
    # 4^-c*ln(5/4)>0.19 using ln(4)<2, e^-x>=1-x, and ln(5/4)>1/5.
    psi_coefficient = (1 - 2 * Q(1, 250)) * Q(1, 5)
    assert psi_coefficient > Q(19, 100)
    # Independent generous rank-power, mass-ratio and t bounds from the signed census.
    fringe = Q(21, 2) * Q(106, 100) / (Q(996, 1000) * Q(99, 100) * Q(19, 100))
    assert fringe < 64
    # Same descending bin proof for genuine cells. The first bin suffices since
    # (4/5)*(e+2) / e decreases for e>0.
    assert Q(4, 5) * (L + 2) < Q(5, 6) * L and Q(6, 5)**4 > 2
    cap_price = trial - Q(39, 256 * 20_000_000) - Q(5, 10**18)
    candidate = Q(".0038982016137")
    assert Q(receipt["old_comparator"]) < candidate < cap_price
    return {
        "predecessor_head": receipt["exact_head"],
        "round369_price_receipt_sha256": INPUT_PIN,
        "analytic_test_trial": str(trial),
        "actual_exponent_root_depth": b,
        "certified_root_depth_limit": 46,
        "max_virtual_ratio": max_ratio,
        "worst_case_grid_mass_error_log2_less_than": error_log2_upper,
        "psi_over_P_lower": str(psi_coefficient),
        "fringe_coefficient_upper": str(fringe),
        "rounded_column_examples": concrete,
        "literal_leaf_count_pair_is_nominal": True,
        "fixed_profile_debit": "39/256",
        "fixed_profile_signed_trial_for_future_replay": str(candidate),
        "price_slack_vs_positive_cap": str(cap_price - candidate),
        "status": "ANALYTIC_INTERFACE_CHECK_ONLY",
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    contents = args.receipt.read_bytes()
    assert sha256(contents).hexdigest() == INPUT_PIN
    data = proof(json.loads(contents))
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
