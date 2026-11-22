"""Exclude the fixed #8055 compact profile with a Gaussian-only edit."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import runpy

PINS = {
    "installations.py": "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df",
    "receipt.py": "3d0219eb2262ea64ccf2dc8da4d2877e32c519c4670d99577703f8bfc236ba61",
    "NUMERICAL.md": "14b86724db522393981ed54b540a35f27bd952f3d95d6e6d14c5b23896811dc9",
    "runtime.patch": "6c93961841be2abc3629928074e2c7917d264e94187276fc88a33f922a3c62e4",
    "grades.py": "340684fdd5ca0e611836b0e7301f1c339282ba532bf9e3ec8055944d8981f3c8",
}
CAMPAIGN = Q(".0038982016137")


def ceil(x):
    return -(-x.numerator // x.denominator)


def check(package):
    for name, expected in PINS.items():
        assert sha256((package / name).read_bytes()).hexdigest() == expected, name
    profile = runpy.run_path(str(package / "installations.py"))
    entry, terminal = profile["ENTRY"], profile["TERMINAL"]
    assert entry.rank_logs == (3000, 3080) and entry.complex_log == 1024
    assert terminal.rank_logs == (35327, 559005) and terminal.complex_log == 680000
    assert terminal.positive_stop_denominator == 10**18
    assert terminal.kappa == Q(".0038982")
    b = Q(profile["BINARY_C"])
    a1, a2 = (b - Q(11, 8 * h) for h in terminal.rank_logs)
    first = Q(249, 250) * a1
    unfloored = (249 * a2 + first) / 250
    stop = Q(5, terminal.positive_stop_denominator)
    ordinary = unfloored - stop
    floored = Q(int(first * 10**21) - 1, 10**21)
    actual = (249 * a2 + floored) / 250 - stop
    assert terminal.kappa < actual <= ordinary < unfloored < CAMPAIGN

    ambient = 12087
    assert (79 * 153) == ambient
    virtual_ratio_bound = 4 * ambient
    assert virtual_ratio_bound < 1024 * ambient
    assert Q(106, 100)**250 > ambient
    fringe = Q(21, 2) * Q(106, 100) / (Q(996, 1000) * Q(99, 100) * Q(19, 100))
    assert fringe < 64
    assert 37 - 35 * entry.complex_log < -2

    # Base width w=e-8 stays even. For any bundle its residue decides whether
    # changing 8w to 79w activates these extra physical phases. Changing only
    # the low-copy cut lengths leaves the large native width untouched.
    phase = 48 * (3042 + 697 + 200)
    assert phase == 189072
    assert phase * 6 == 1134432
    phase_examples = []
    for w, bundle in ((32760, 1), (32762, 1), (32762, 2)):
        extra = phase if (w * bundle) % 4 == 2 else 0
        assert (79 * w * bundle) % 4 == (w * bundle) % 4
        phase_examples.append([w, bundle, extra, 6 * extra])

    entrance = 1274851
    old_finite_premium = ceil((terminal.kappa - entry.kappa) * entrance)
    campaign_finite_premium = ceil((CAMPAIGN - entry.kappa) * entrance)
    assert old_finite_premium == campaign_finite_premium == 572
    return {
        "peer": "7b48187d99525ad59f560de3921ec7e48382484c",
        "dependency_hashes_by_path": PINS,
        "campaign_comparator": str(CAMPAIGN),
        "peer_report": str(terminal.kappa),
        "ordinary_upper_no_stop_or_first_stage_floor": str(unfloored),
        "ordinary_upper_with_stop_but_no_first_stage_floor": str(ordinary),
        "ordinary_upper_actual_first_stage_floor": str(actual),
        "shortfall_even_before_stop": str(CAMPAIGN - unfloored),
        "shortfall_after_stop_but_no_first_stage_floor": str(CAMPAIGN - ordinary),
        "large_copy_phase_pass_extents": phase_examples,
        "coarse_ratio_bound_if_rounded": virtual_ratio_bound,
        "hypothetical_fringe_coefficient": str(fringe),
        "entry_rate_conversion_bits": old_finite_premium,
        "remaining_cases_in_fixed_compact_profile": 0,
        "status": "EXCLUDED_BY_UNCHANGED_ORDINARY_PRICE",
    }


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--package", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    data = check(args.package)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
