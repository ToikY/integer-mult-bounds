"""Reject literal fractional-axis quartiles on the production column parity."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import runpy

PINS = {
    "transport.py": "98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9",
    "retimed_supplier.py": "bdc5bf5e5228fe1179951a074508f59a90f6d2634f5af8e2d5a097329e484755",
    "installations.py": "983fdc1fd09ec8727d8c573ba171d52a0fc0200437f9233f249a2aa5e7be9503",
    "check_complete.py": "a73bb6819014f7e61b73ab95bf28ec74d1f1607c0a58ad60315d391ab82557c1",
    "check_positive_word.py": "a88de880627489764668f6a3ec34f4861f61bd49cc74d3547d3ef18ee017dbe4",
}


def allocations(plan, exponent, paid):
    return plan(
        2**32, (1, 1), paid, {(r, 1): Q(1) for r in paid}, exponent,
        32768, 32772, 2**50, 1, 2**32,
        delay_base=2,
    )


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    for name, expected in PINS.items():
        assert sha256((args.package / name).read_bytes()).hexdigest() == expected, name
    source = runpy.run_path(str(args.package / "transport.py"))
    profile = runpy.run_path(str(args.package / "installations.py"))
    H = profile["EXTENDED"].complex_log
    ambient = 1224
    even_bad = 32770
    columns = even_bad - 8
    cap = 2 * ((1 << H) // (2048 * ambient))
    assert H == 20_000_000 and cap > even_bad
    assert columns == 32762 and columns % 4 == 2
    exponent = 1 - profile["GAUSSIAN_C"]
    assert source["Measure"](exponent, 1, 256).mass(even_bad, even_bad + 2)[0] > 0

    # One actual compiler kernel. Restrict its two-frame test to this same bad production
    # residue with two targets and two paid pieces. It isolates the fractional size guard.
    old = allocations(source["Plan"], exponent, (Q(1, 2), Q(1, 2)))
    old_events = old.events()
    old_open = next(old_events)
    old_paid = next(old_events)
    assert old_open[0] == 0 and old_open[2] == columns and old_paid[3] == columns // 2

    bad = allocations(source["Plan"], exponent, (Q(1, 4), Q(3, 4)))
    bad_events = bad.events()
    bad_open = next(bad_events)
    assert bad_open[0] == 0 and bad_open[2] == columns
    try:
        next(bad_events)
    except ArithmeticError as e:
        assert str(e) == "The parent cannot cover the selected interval."
    else:
        raise AssertionError("The compiler accepted a fractional axis count")

    # A parity-aware successor may round the first length down and its complement up.
    # Test the two possible residues symbolically, since e is always even.
    for e in (32768, 32770):
        width = e - 8
        lengths = (width // 4, width - width // 4)
        for r, length in zip((Q(1, 4), Q(3, 4)), lengths):
            assert r * (e - 10) <= length and abs(length - r * width) <= Q(1, 2)
            # k >= 1 for every compatible target. The gap grows with k.
            assert 8 - 10 * r >= Q(1, 2)
    fringe_coefficient = Q(21, 2) * Q(106, 100) / (Q(996, 1000) * Q(99, 100) * Q(19, 100))
    assert fringe_coefficient < 64

    result = {
        "predecessor": "f6f4ecd5dd717ce2b155dd564469e9693ac90f6d",
        "pins": PINS,
        "fixed_literal_quarter_edit_valid": False,
        "first_bad_production_band": even_bad,
        "actual_columns": columns,
        "literal_quarter_sizes": [str(Q(columns, 4)), str(Q(3 * columns, 4))],
        "even_positive_control_paid_size": columns // 2,
        "actual_compiler_kernel_rejects": True,
        "proved_rounded_local_slack_at_least": "1/2",
        "rounded_fringe_coefficient_upper": str(fringe_coefficient),
        "unresolved_rounded_variant": True,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
