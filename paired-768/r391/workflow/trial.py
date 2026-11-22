"""Compare exact profile rebuilding and delta equations on three frozen R391 IDs."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from time import perf_counter_ns

PINS = {
    "price/check.py": "5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    "price/receipt.json": "19a4795048fb16016801f17c8be6ad9d38715af8a3bd941ae2b44d8c5de43b06",
    "audit/receipt.json": "55a7693e59aa46d80e19adf91bfaaf300a29ce949af5b1cab9732e5ed21f5904",
}
SHIFTS = (0, 7, 8)
H1, H2, H3 = 8192, 129414, 524395
TICK = 10**21


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--round", type=Path, required=True)
    args = parser.parse_args()
    start = perf_counter_ns()
    for path, digest in PINS.items():
        assert sha256((args.round / path).read_bytes()).hexdigest() == digest, path
    scope = run_path(str(args.round / "price/check.py"))
    primary = json.loads((args.round / "price/receipt.json").read_bytes())
    independent = json.loads((args.round / "audit/receipt.json").read_bytes())
    io_ns = perf_counter_ns() - start

    eta, binary = scope["ETA"], scope["BINARY"]
    target = Q(primary["target_kappa"])
    margin_units = Q(5, 10**18)
    gaussian = target + Q(primary["gaussian_margin"])

    def rebuild():
        caps = {}
        for shift in SHIFTS:
            _, cap = scope["funding"]((H1, H2 - shift, H3 + shift))
            caps[shift] = min(cap - margin_units, gaussian)
        return caps

    def delta():
        prior, cap3 = scope["funding"]((H1, H2, H3))
        cap2 = (249 * (binary - Q(11, 8 * H2)) + prior[0]) / 250
        assert cap2 < eta and cap3 < eta
        caps = {}
        for shift in SHIFTS:
            new2 = cap2 + Q(249*11, 250*8) * (Q(1,H2) - Q(1,H2-shift))
            assert new2 < eta
            booked2 = Q(int(new2*TICK) - 1, TICK)
            new3 = cap3 + Q(249*11, 250*8) * (Q(1,H3) - Q(1,H3+shift)) + (booked2-prior[1])/250
            assert new3 < eta
            caps[shift] = min(new3 - margin_units, gaussian)
        return caps

    start = perf_counter_ns()
    first = rebuild()
    rebuild_ns = perf_counter_ns() - start
    start = perf_counter_ns()
    second = delta()
    delta_ns = perf_counter_ns() - start
    start = perf_counter_ns()
    answers = [Q(primary[key]) for key in (
        "actual_prior_installed_cap", "seven_level_installed_cap", "candidate_installed_cap")]
    assert list(first.values()) == list(second.values()) == answers
    assert [x > target for x in answers] == [False, False, True]
    assert str(Q(primary["ordinary_margin"])) in json.dumps(independent)
    assert str(Q(primary["gaussian_margin"])) in json.dumps(independent)
    compare_ns = perf_counter_ns() - start
    print(json.dumps({"inputs": PINS, "caps": {str(k): str(v) for k,v in first.items()},
                      "passing": [8], "rebuild_ns": rebuild_ns, "delta_ns": delta_ns,
                      "matched_receipt_comparison_ns": compare_ns, "authentication_ns": io_ns},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
