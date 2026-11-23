"""Reprice the fixed profile using the literal four-aligned exterior period."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil
from pathlib import Path
import runpy
import signal

ROOT = Path(__file__).resolve().parents[2]
PEER = "r411/audit/inputs/8094-RESULT.json"
FROZEN = "r414/price/RECEIPT.json"
POWER = "r410/bundle/overrides/matched_price_support.py"
OUTER = "r411/audit/inputs/outer_budget.py"
PINS = {
    PEER: "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
    FROZEN: "b435820233afbc2c80d5203db0b448be2c10450e70508ea35bbcb335fd35d540",
    POWER: "4964fb80e4f2a449decbd35044808b3cc235c44405bfa926f6b12f95e9213c33",
    OUTER: "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
}


def check(root):
    for file, expected in PINS.items():
        assert sha256((root / file).read_bytes()).hexdigest() == expected, file
    peer = json.loads((root / PEER).read_bytes())
    frozen = json.loads((root / FROZEN).read_bytes())
    power = runpy.run_path(str(root / POWER))["rooted_power"]
    qualify = runpy.run_path(str(root / OUTER))["qualify"]
    factor = peer["gaussian"]["finite_loss"]
    assert factor["upper_divisor"] == 1724 and factor["upper_scale"] == 263772
    # size <= 258 * U, with U <= M / 263772. Both typed widths
    # use the same physical k chart grade in the emitted period.
    x0 = Q(263772, 4 * 258)
    period = Q(257, 256)
    assert 255 < x0 < 256 and Q(256) / x0 < period
    # For x > 256, set m=ceil(x)-1>=256. Then ceil(x)/x < 1+1/m.
    coarse = 1 + 1 / x0
    previous = Q(factor["upper_factor"])
    upper = previous * period / coarse
    grid = 2**23
    old = Q(factor["debit"])
    assert old == Q(1039776, grid)
    low, high = 1, int(grid * old)
    while low < high:
        middle = (low + high) // 2
        if upper < power(2, Q(middle, grid))[0]:
            high = middle
        else:
            low = middle + 1
    selected = Q(high, grid)
    accepted = power(2, selected)
    adjacent = power(2, selected - Q(1, grid))
    assert previous > accepted[1] and adjacent[1] < upper < accepted[0]
    assert selected < old

    terminal = peer["terminal"]
    g = terminal["numerical_H"]
    cg = Q(peer["gaussian"]["trial"])
    stop = Q(1, 10**18)
    gaussian = cg - selected / g
    ordinary = Q(frozen["new_ordinary_ceiling"])
    ceiling = min(ordinary, gaussian - 5 * stop)
    target = Q(ceil(ceiling * 10**15) - 1, 10**15)
    prior = Q(frozen["projected_kappa"])
    assert g == 208653 and prior < target < ceiling
    assert target + Q(1, 10**15) >= ceiling
    paid = target + 5 * stop
    signed = qualify(target, stop, paid, gaussian)
    assert (signed["strict"], signed["functional"]) == (54, 4)
    premium = ceil((target - Q(peer["entry"]["kappa"])) * terminal["stock"]["public_exponent_A"])
    complete = 1 + max(terminal["log2_C"], peer["entry"]["log2_C"] + premium)
    assert complete == frozen["full_recurring_log2_C"]
    return dict(
        scope="Directed rescale of the pinned finite loss; installed science unrun",
        lower_x=x0, old_period=coarse, changed_period=period,
        debit=selected, old_debit=old, adjacent_shortfall=upper-adjacent[1],
        reserve=accepted[0]-upper, positive_ceiling=gaussian-5*stop,
        ordinary_ceiling=ordinary, binding="ordinary" if ordinary == ceiling else "positive",
        projected_kappa=target, gain_over_frozen_tariff=target-prior,
        gain_over_pending_8094=target-Q(terminal["kappa"]), recurring_log2_C=complete,
        entry_conversion=premium, terminal_scalar=signed,
    )


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    signal.alarm(45)
    try:
        print(json.dumps(check(parser.parse_args().root), indent=2, default=str))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
