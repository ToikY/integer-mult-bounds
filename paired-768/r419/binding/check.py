"""Exact fixed-height test of the previously verified exterior period bound."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from math import ceil, floor, isqrt
from pathlib import Path
import json
import runpy
import signal

PEER = "c20a08dc0a79a989e3515068560d5da371c0a2a8"
PROFILE = "r411/audit/inputs/8094-RESULT.json"
CALLER = "r411/audit/inputs/outer_budget.py"
FROZEN = "r414/independent-price/RECEIPT.json"
PINS = {
    PROFILE: "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
    CALLER: "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    FROZEN: "778279dcc9aa74c03df29263f05ad4230f49c8ebd8c4e6384c890bad7e30d090",
}
SOURCE_PINS = {
    "typed_transport.py": "b76b9ad3dc0dd91473026c079585f830387eaa3c34c25a7820ee5057d5cbf941",
    "grades.py": "6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d",
    "positive_debit.py": "32ee6a20e8f7fe6e2d1a3852b232179b0c6736c816f5bfd7bd9ec62cbffa9eb8",
}
GRID = 1 << 192
TICK = 10**15
STOP = Q(1, 10**18)
ORDINARY_RAW = Q(4391986206293, 2**50)


def pinned(root, path, expected):
    data = (root / path).read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"Digest mismatch for {path}")
    return data


def powers(base, exponent):
    """Enclose a dyadic power on an integer grid by directed square roots."""
    assert 0 < exponent < 1 and exponent.denominator.bit_count() == 1
    roots = [floor(base * GRID), ceil(base * GRID)]
    product_lower = product_upper = GRID
    for shift in reversed(range(exponent.denominator.bit_length() - 1)):
        roots = [isqrt(roots[0] * GRID), 1 + isqrt(roots[1] * GRID - 1)]
        if (exponent.numerator >> shift) & 1:
            product_lower = product_lower * roots[0] // GRID
            product_upper = -(-product_upper * roots[1] // GRID)
    return Q(product_lower, GRID), Q(product_upper, GRID)


def ordinary(heights, debit, eta):
    previous = Q(0)
    for i, height in enumerate(heights):
        crossing = min(eta, (249 * (ORDINARY_RAW - debit / height) + previous) / 250)
        if i + 1 != len(heights):
            previous = Q(floor(crossing * 10**21) - 1, 10**21)
    return crossing - 5 * STOP


def check(root, prepared):
    records = {p: pinned(root, p, d) for p, d in PINS.items()}
    source = {p: pinned(prepared, p, d).decode() for p, d in SOURCE_PINS.items()}
    assert "size = (e - 8) * k" in source["typed_transport.py"]
    assert "period = 4 * ceil(Q(n, 4 * size))" in source["typed_transport.py"]
    assert "self.source_width += number * ticks * (rounds // period)" in source["typed_transport.py"]
    assert "2 * (M // (UPPER_DIVISOR * self.ambient))" in source["grades.py"]
    assert "(1 + Q(4 * max(targets), scale))" in source["positive_debit.py"]
    profile = json.loads(records[PROFILE])
    frozen = json.loads(records[FROZEN])
    positive = profile["gaussian"]
    loss = positive["finite_loss"]
    axes, lower, scale = (loss[k] for k in ("weighted_target_axes", "lower_band", "upper_scale"))
    assert (axes, lower, scale) == (677246016, 1874, 263772)
    assert loss["upper_divisor"] == 1724 and scale == 1724 * 306 // 2
    x0 = Q(scale, 4 * 258)
    period = Q(257, 256)
    coarse = 1 + Q(4 * 258, scale)
    assert 255 < x0 < 256 and Q(256) / x0 < period < coarse
    raw_rate = Q(positive["trial"])
    fringe = 10 * axes / ((1 - raw_rate) * Q(loss["psi_lower"]))
    assert fringe == Q(loss["fringe"])
    delta = Q(1, 2**128)
    # The installed receipt's directed share floor is retained. Independent
    # power bounds avoid accepting any unpublished native results.
    _, powered = powers(scale * lower, raw_rate)
    finite_base = (1 + delta) * powered * (1 + fringe / lower + delta) / (1 - delta)**4
    old_factor = coarse * finite_base
    new_factor = period * finite_base
    previous = Q(positive["raw_loss"])
    debit = Q(1039701, 2**23)
    assert Q(loss["upper_factor"]) < powers(2, previous)[0]
    assert old_factor < powers(2, previous)[0]
    assert new_factor < powers(2, debit)[0] < powers(2, debit)[1] < old_factor
    assert powers(2, debit - Q(1, 2**23))[1] < new_factor
    assert previous - debit == Q(75, 2**23)

    terminal = profile["terminal"]
    heights = terminal["ordinary_H"]
    height = terminal["numerical_H"]
    inv = Q(frozen["binary_debit"])
    old_o = ordinary(heights, Q(profile["ordinary_finite_debit"]), Q(1, 256))
    new_o = ordinary(heights, inv, Q(1, 256))
    old_p = raw_rate - previous / height - 5 * STOP
    new_p = raw_rate - debit / height - 5 * STOP
    assert old_o == Q(frozen["old_guarded_ordinary_crossing"])
    assert new_o == Q(frozen["new_guarded_ordinary_crossing"])
    assert old_p == Q(frozen["new_guarded_gaussian_crossing"])
    projected = Q(ceil(min(new_o, new_p) * TICK) - 1, TICK)
    old_k = Q(terminal["kappa"])
    frozen_k = Q(frozen["maximum_display_tick"])
    assert old_k <= old_o < frozen_k < old_p < projected < new_p < new_o
    assert projected - frozen_k == Q(42850, 10**15)
    qualify = runpy.run_path(str(root / CALLER))["qualify"]
    costs, signed = [], {}
    for name, kappa, eta in (
        ("entry", Q(profile["entry"]["kappa"]), Q(39, 10000)),
        ("terminal", projected, Q(1, 256)),
    ):
        row = profile[name]
        assert kappa < ordinary(row["ordinary_H"], inv, eta)
        assert row["numerical_H"] == (1024 if name == "entry" else 208653)
        signed[name] = qualify(kappa, STOP, kappa + 5 * STOP, raw_rate - debit / row["numerical_H"])
        assert (signed[name]["strict"], signed[name]["functional"]) == (54, 4)
        if name == "entry":
            log_b = 40 + 22 + 2**14 * sum(row["ordinary_H"]) + sum(row["binary_surcharges"])
        else:
            log_b = 128 + 3 * len(heights) + 320 * sum(heights)
        assert log_b == row["log2_B"]
        costs.append(max(84_500_001, log_b + 220 * row["numerical_H"] + 1602))
        assert costs[-1] == row["log2_C"]
    surcharge = ceil((projected - Q(profile["entry"]["kappa"])) * terminal["stock"]["public_exponent_A"])
    complete = 1 + max(costs[0] + surcharge, costs[1])
    assert surcharge == 121121 and complete == 85945126846
    assert new_p < projected + Q(1, TICK)
    for next_kappa, positive_rate in (
        (projected, old_p + 5 * STOP),
        (projected + Q(1, TICK), new_p + 5 * STOP),
    ):
        try:
            qualify(next_kappa, STOP, next_kappa + 5 * STOP, positive_rate)
        except ArithmeticError:
            pass
        else:
            raise ValueError("A guarded Gaussian negative control passed")
    return {
        "scope": "One conditional fixed-height price and literal period-source preflight. Installed signed replay unrun.",
        "peer": PEER,
        "ordinary_heights_entry": profile["entry"]["ordinary_H"],
        "ordinary_heights_terminal": heights,
        "gaussian_heights_entry_terminal": [profile["entry"]["numerical_H"], height],
        "old_ordinary_ceiling": old_o, "frozen_ordinary_ceiling": new_o,
        "frozen_gaussian_ceiling": old_p, "sharpened_gaussian_ceiling": new_p,
        "old_peer_kappa": old_k, "frozen_kappa": frozen_k, "projected_grid_kappa": projected,
        "delta_over_frozen": projected - frozen_k, "delta_over_peer_report": projected - old_k,
        "delta_over_old_peer_crossing": projected - old_o,
        "old_period_factor": coarse, "sharpened_period_factor": period,
        "old_positive_debit": previous, "sharpened_positive_debit": debit,
        "directed_paid_reserve_gt": Q(floor((powers(2, debit)[0] - new_factor) * 10**18), 10**18),
        "next_lower_debit_shortfall_gt": Q(floor((new_factor - powers(2, debit - Q(1, 2**23))[1]) * 10**18), 10**18),
        "remaining_ordinary_headroom": new_o - projected,
        "entry_surcharge_bits": surcharge, "complete_recurring_log2_C": complete, "signed": signed,
        "negative_controls": ["old positive debit at new projection", "adjacent higher grid rate"],
        "source_pins": {**PINS, **SOURCE_PINS},
    }


def timeout(_signal, _frame):
    raise TimeoutError("30-second scalar cap")


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--prepared", type=Path, required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    try:
        print(json.dumps(check(args.root, args.prepared), indent=2, default=str))
    finally:
        signal.alarm(0)
