"""Check the exact raw-grade capacity cut and surviving Hall support on #8087."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from math import isqrt
from pathlib import Path
from subprocess import check_output
import json

HERE = Path(__file__).resolve().parent
HEAD = "aea1699415250d865f7a635f4df0b76f406c47b4"
BOOK = "research/p104-period-debit-25bit/RESULT-460.json"
PINS = {
    BOOK: "8c8b7cebbdea179329d225d828f31e37e2fddfcfd177750803ae81e39726def8",
    "R368-RANK-RECEIPT.json": "d26a1f9ea8fd78900f45bf83c29ee2b700d015c231a82eab1cad54283b4aec66",
}
UNIT = 1 << 112
HALF = Q(1, 2)
TRIAL = Q(17145637307, 2**42)
T = 1 - TRIAL


def pinned(root, name):
    data = (root / name).read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError(f"Pin mismatch at {name}")
    return json.loads(data)


def unmix(rows):
    counts = Counter({Q(rank): count for rank, count in rows})
    assert len(counts) == len(rows)
    if HALF in counts:
        assert counts.pop(HALF) == 2016
        counts[1] += 1008
    base = Counter()
    for rank in sorted(counts):
        amount = counts[rank] - base[rank / 8]
        assert amount >= 0
        if amount:
            base[rank] = amount
    assert base + Counter({8 * rank: count for rank, count in base.items()}) == counts
    return base


def weighted(base, s=0):
    counts = Counter({rank: 5 * count for rank, count in base.items()})
    counts.update({2 * rank: 451 * count for rank, count in base.items()})
    if s:
        assert counts[1] > 5 * s
        counts[1] -= 5 * s
        counts[HALF] = 10 * s
    return counts


@cache
def outward(rank):
    if rank == HALF:
        low, high = outward(Q(2))
        return UNIT**2 // high, -(-UNIT**2 // low)
    assert rank >= 1 and rank.denominator == 1
    root_lo = root_hi = int(rank) * UNIT
    lo = hi = UNIT
    for bit in range(T.denominator.bit_length() - 2, -1, -1):
        root_lo = isqrt(root_lo * UNIT)
        root_hi = 1 + isqrt(root_hi * UNIT - 1)
        if T.numerator >> bit & 1:
            lo = lo * root_lo // UNIT
            hi = -(-hi * root_hi // UNIT)
    return lo, hi


def mass(hist, endpoint):
    return {rank: count * outward(rank)[endpoint] for rank, count in hist.items()}


def upper_tail(hist, lower):
    return sum(value for rank, value in hist.items() if rank >= lower)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    args = parser.parse_args()
    assert __debug__
    root = args.baseline.resolve()
    assert check_output(["git", "-C", root, "rev-parse", "HEAD"]).decode().strip() == HEAD
    assert not check_output(["git", "-C", root, "status", "--porcelain"])
    signed = pinned(root, BOOK)["gaussian"]
    source = pinned(HERE, "R368-RANK-RECEIPT.json")
    assert source["1006_literal_touched_paid_clock_and_tag"][-2:] == [
        [1592, ["return", 9977, 0, 91990]], [1593, ["return", 9977, 0, 91966]],
    ]
    base_targets = unmix(source["source_targets"])
    base_paid = unmix(source["source_paid"])
    targets, paid = weighted(base_targets), weighted(base_paid, 1008)
    assert Q(signed["trial"]) == TRIAL and signed["weights"] == [5, 451]
    assert sum(base_targets.values()) == 52608 and sum(base_paid.values()) == 281568
    assert sum(targets.values()) == signed["weighted_targets"] == 23989248
    assert sum(paid.values()) == signed["weighted_loans"] == 128400048
    assert targets[1] == 5040 and min(targets) == 1 and min(paid) == HALF

    target_lower = mass(targets, 0)
    target_total = sum(target_lower.values())
    old_margin = 1 - Q(sum(mass(paid, 1).values()), target_total)
    assert old_margin == Q(signed["directed_margin"]) > 0

    compulsory = mass(weighted(base_paid, 1005), 0)
    shortage = Q(upper_tail(compulsory, 1) - upper_tail(mass(targets, 1), 2), UNIT)
    assert shortage > 0

    still_paid = mass(weighted(base_paid, 1006), 1)
    paid_total = sum(still_paid.values())
    assert paid_total < target_total
    capacity = {k: Q(value * paid_total, target_total) for k, value in target_lower.items()}
    slack = {r: (upper_tail(capacity, 5 * r / 4) - upper_tail(still_paid, r)) / UNIT
             for r in sorted(still_paid)}
    assert slack.pop(HALF) == 0 and len(slack) == 21 and min(slack.values()) > 0
    binding = min(slack, key=slack.get)
    h_lo, h_hi = outward(HALF)
    saving = [Q(10 * (2 * x - UNIT), UNIT) for x in (h_lo, h_hi)]
    print(json.dumps({
        "head": HEAD, "raw_trial": str(TRIAL),
        "reconstructed_directed_margin": str(old_margin),
        "weighted_grade_one_targets": 5040,
        "absolute_real_cut_shortage_at_1005": str(shortage),
        "removed_splits_excluded": [3, 1008],
        "proper_directed_capacity_cuts_at_1006": len(slack),
        "weakest_proper_source_grade": str(binding),
        "least_directed_proper_cut_slack_at_1006": str(slack[binding]),
        "gross_real_moment_saving_at_two_bounds": list(map(str, saving)),
    }, indent=2))


if __name__ == "__main__":
    main()
