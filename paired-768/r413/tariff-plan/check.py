"""Authenticate one physical receiver bound and check the local tariff invoice."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import runpy
import signal


PINS = {
    "RECEIVER.md": "f31089b6304fc5352feb9aa8a963cc5a950a828165d3426e16e8a973529d814e",
    "ORDINARY-CLOCK.md": "4694db0b2218796e348c1128271cebb3fc779151a639b0e0fb5bbecf9f3ccb94",
    "8094-prepare.py": "bc401e5c47d275617f3c7d162d56ea4c604ef3d4c6637ab2a8aa8627a570a9f6",
    "8094-RESULT.json": "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
    "matched_price_support.py": "4964fb80e4f2a449decbd35044808b3cc235c44405bfa926f6b12f95e9213c33",
}


def authenticated(path, pin):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == PINS[pin], pin
    return data


def settled_debit(price, old_tick, power):
    def classify(tick):
        low, high = (2 * x for x in power(2, Q(tick, 2**20) - 1))
        if price[1] < low:
            return True
        if high < price[0]:
            return False
        raise ArithmeticError("Insufficient directed precision at this debit")

    lo, hi = 2**20 + 1, old_tick
    assert not classify(lo) and classify(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if classify(mid):
            hi = mid
        else:
            lo = mid
    return lo, hi


def check(args):
    receiver = authenticated(args.proof_root / "RECEIVER.md", "RECEIVER.md").decode()
    clock = authenticated(args.proof_root / "ORDINARY-CLOCK.md", "ORDINARY-CLOCK.md").decode()
    prepare = authenticated(args.prepare, "8094-prepare.py").decode()
    profile = json.loads(authenticated(args.profile, "8094-RESULT.json"))
    authenticated(args.power_source, "matched_price_support.py")
    power = runpy.run_path(str(args.power_source))["rooted_power"]

    assert "same byte volume and high cardinality" in receiver
    assert "(21x+3)/D" in receiver
    assert "complete mean is below 75/32" in receiver
    assert "A direct frame always has one same-stage child" in clock
    assert "Each child width is floor(c/N)" in clock
    assert "at s=t and s=1" in clock
    assert "child_tariff = Q(2401, 1024)" in prepare
    assert "128 + 3 * len(heights) + 320 * sum(heights)" in prepare
    assert "40 + 22 + 16384 * sum(heights) + sum(additions)" in prepare

    tiers = {tier: profile[tier]["ordinary_H"] for tier in ("entry", "terminal")}
    assert [len(heights) for heights in tiers.values()] == [2, 5]
    assert all(height >= 4 for heights in tiers.values() for height in heights)

    def quotient_mean(n):
        x = 3 ** (n - 2)
        return Q(21 * x + 3, 9 * x - 1)

    # Cross-multiplication gives 6x >= 5462, monotone for x >= 1.
    upper = Q(2390, 1024)
    assert quotient_mean(8) > upper > quotient_mean(9) > 1
    assert 6 * 3**7 > 5462 > 6 * 3**6
    coarse, previous, proposed = Q(75, 32), Q(2401, 1024), Q(2391, 1024)
    assert coarse / proposed > 1  # The proposed tariff cannot use the old bound.
    q = upper / proposed
    booking = 1 / (1 - q)
    assert q == Q(2390, 2391) and booking == 2391
    assert booking < 2401 and booking < 8 * 376
    assert (Q(7, 10) * booking) ** 2 < 2**22

    l = 4474
    delta = Q(1, 2**128)
    suffix = Q(186, 25)
    c = Q(4391986206293, 2**50)
    factors = power(1024 * 134 * l, c)
    common = Q(4097, 4096) * Q(1028, 1024)
    common *= (1 + suffix / l + delta) / ((1 - Q(10, l)) * (1 - delta)**3)
    old_tick = 1420718
    assert Q(profile["ordinary_finite_debit"]) == Q(old_tick, 2**20)
    old_price = tuple(previous * common * v for v in factors)
    new_price = tuple(proposed * common * v for v in factors)
    old_fail, old_pass = settled_debit(old_price, old_tick, power)
    new_fail, new_pass = settled_debit(new_price, old_tick, power)
    assert (old_fail, old_pass) == (old_tick - 1, old_tick)
    assert new_pass + 1 < old_pass

    return {
        "scope": "One unchanged physical receiver and #8094 ordinary price substitution only.",
        "hashes": PINS,
        "ordinary_heights": tiers,
        "smallest_rank_covered": 9,
        "quotient_mean_at_9": quotient_mean(9),
        "paid_child_mean_upper": upper,
        "proposed_tariff": proposed,
        "same_stage_contraction_upper": q,
        "child_depth_sum_upper": booking,
        "entry_clock_exponent_allowance": 22,
        "terminal_added_bits_kept_per_stage": 3,
        "ordinary_grid_denominator": 2**20,
        "old_adjacent_debits_fail_pass": [old_fail, old_pass],
        "proposed_adjacent_debits_fail_pass": [new_fail, new_pass],
        "ordinary_debit_saving_ticks": old_pass - new_pass,
        "controls": {"rank_8_excluded": True, "old_child_bound_breaks_new_tariff": True},
    }


def capped(_signal, _frame):
    raise TimeoutError("30-second ordinary component cap reached")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("proof-root", "prepare", "profile", "power-source"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    assert __debug__
    signal.signal(signal.SIGALRM, capped)
    signal.alarm(30)
    try:
        print(json.dumps(check(args), indent=2, default=str))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
