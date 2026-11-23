"""Check the matched-suffix invoice, 25-bit signed seams and predecessor bound."""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

RUNTIME = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RUNTIME))
from upstream import install
install()
sys.path.append(str(HERE.parent / "tiered-native-multiplier" / "source"))

from activation import resource_receipt
from band_product import prepare_native
from check_stage_seam import verify_stage, verify_tape
from installations import ENTRY, TERMINAL, BINARY_C, GAUSSIAN_C, activation
from outer_budget import qualify
from outer_clock import financial_checks
from raw_binary_stage import binary_word
from retune import PROFILES
from staged_carriers import entrance_logs

ORDINARY = Q(11239, 8192)
GAUSSIAN = Q(130699669, 2**30)
PREVIOUS_GAUSSIAN = Q(64934, 524288)
PREVIOUS_RATE = Q(".003898460000505")
PREVIOUS_HEIGHTS = (8192, 38102, 604363)
PREVIOUS_GAUSSIAN_HEIGHT = 18845934
PREVIOUS_RECURRING_CAP = 4354317451
PREVIOUS_RESULT_SHA256 = "8c8b7cebbdea179329d225d828f31e37e2fddfcfd177750803ae81e39726def8"
PROFILE_IMAGE_SHA256 = "961808a1447a9e4f7ec7101d9dc7dbfb44b7d6b62af8a2c900a849cbd83ec17f"
TICK = 10**21
STOP = Q(1, 10**18)


def ordinary_upper(heights):
    r = Q(0)
    for index, h in enumerate(heights):
        u = min(TERMINAL.eta, (249 * (BINARY_C - ORDINARY / h) + r) / 250)
        r = u if index == len(heights) - 1 else Q((u * TICK).__floor__() - 1, TICK)
    return r


def gaussian_upper(h, debit=GAUSSIAN):
    return GAUSSIAN_C - debit / h


def rejected(function, label):
    try:
        function()
    except (AssertionError, ArithmeticError, ValueError):
        return label
    raise AssertionError(f"Negative control {label} was not rejected")


def relaxed_ordinary_upper(total):
    """Upper bound the ordinary rate under a maximum height sum.

    Intermediate floor ticks and the eta clamp are relaxed.  Cauchy gives
    w2/h2 + w3/h3 >= (sqrt(w2)+sqrt(w3))^2/(h2+h3).  We use a strict
    rational lower enclosure on 1/sqrt(250) and prove the resulting function
    increases from h1=8192, so even the relaxed shorter sum cannot pass.
    """
    m = total
    hmin = 8192
    w1 = Q(1, 62500)
    r = Q(6324555320336758663997787088865437067439, 10**41)
    assert r*r < Q(1, 250) < (r + Q(1, 10**41))**2
    assert w1 / hmin**2 < (1 + r)**2 / (m - hmin)**2
    loss_lower = w1 / hmin + (1 + r)**2 / (m - hmin)
    return BINARY_C * (1 - Q(1, 250**3)) - Q(249, 250) * ORDINARY * loss_lower


def predecessor_upper():
    data = (HERE / "PREDECESSOR-RESULT.json").read_bytes()
    assert sha256(data).hexdigest() == PREVIOUS_RESULT_SHA256
    previous = json.loads(data)
    term = previous["terminal"]
    assert (tuple(term["ordinary_H"]), term["numerical_H"], Q(term["kappa"])) == (
        PREVIOUS_HEIGHTS, PREVIOUS_GAUSSIAN_HEIGHT, PREVIOUS_RATE)
    assert Q(previous["ordinary_finite_debit"]) == ORDINARY
    assert Q(previous["gaussian"]["raw_loss"]) == PREVIOUS_GAUSSIAN
    height = PREVIOUS_GAUSSIAN_HEIGHT
    paid = PREVIOUS_RATE + 5 * STOP
    gaussian = gaussian_upper(height, PREVIOUS_GAUSSIAN)
    assert Q(term["gaussian_rate"]) == gaussian
    assert gaussian_upper(height - 2, PREVIOUS_GAUSSIAN) <= paid
    assert paid < gaussian_upper(height - 1, PREVIOUS_GAUSSIAN) < gaussian
    assert ordinary_upper(term["ordinary_H"]) > gaussian
    assert previous["complete_log2_C"] == PREVIOUS_RECURRING_CAP
    assert PREVIOUS_RECURRING_CAP == 1731 + 320 * sum(PREVIOUS_HEIGHTS) + 220 * height
    # Beating the previous booking first requires enough ordinary height.
    # Charge that minimum before bounding the available Gaussian height.
    minimum_sum = 650656
    assert relaxed_ordinary_upper(minimum_sum - 1) < paid
    maximum_gaussian = (PREVIOUS_RECURRING_CAP - 1731 - 320 * minimum_sum) // 220
    assert maximum_gaussian == 18845935
    ceiling = gaussian_upper(maximum_gaussian, PREVIOUS_GAUSSIAN) - 5 * STOP
    assert ceiling == Q(49304965441196404811631259733, 12647292888678400000000000000000)
    assert PREVIOUS_RATE < ceiling
    return ceiling


def check():
    key = "460"
    expected = PROFILES[key]
    ranks = tuple(TERMINAL.rank_logs)
    height = TERMINAL.complex_log
    assert ranks == expected["heights"] == PREVIOUS_HEIGHTS
    assert height == expected["gaussian"] == 18531230
    assert TERMINAL.kappa == Q(expected["kappa"]) == Q(".003898460003746")
    old_ceiling = predecessor_upper()
    stopped_gap = TERMINAL.kappa - old_ceiling
    assert stopped_gap == Q(40977549613358026667, 12647292888678400000000000000000)
    assert TERMINAL.kappa - PREVIOUS_RATE == Q(3241, 10**15)
    paid = TERMINAL.kappa + 5 * STOP
    assert TERMINAL.ordinary == paid
    assert ordinary_upper(ranks) > paid
    assert gaussian_upper(height - 1) <= paid < gaussian_upper(height)
    assert gaussian_upper(height, PREVIOUS_GAUSSIAN) < paid
    assert 0 < paid < GAUSSIAN_C and GAUSSIAN > 0
    # For every positive Gaussian height, its finite cap is strictly below
    # this raw trial.  Thus this source alone cannot fund kappa = .0039.
    assert GAUSSIAN_C < Q(".0039") + 5 * STOP
    assert expected["max_height_bits"] == 25
    height_cap = 2**expected["max_height_bits"]
    assert all(8192 <= h < height_cap for h in ranks)
    assert 1024 <= height < height_cap

    # The inherited high-fibre proof only uses H >= 8192. At its endpoint,
    # u >= 2**30; the displayed dyadic induction closes all larger u.
    assert TERMINAL.eta == Q(39, 10000) and TERMINAL.eta > Q(1, 258)
    assert TERMINAL.eta * 8192 - 1 > 30
    assert 2660000 * (30 + 2) < 2**30 and 2 * (30 + 2) >= 30 + 3
    assert 17**16 * 10**(21 * 16) < 2**1182

    stock = resource_receipt(TERMINAL)
    cuts = tuple(stock["binary_cuts"])
    assert tuple(entrance_logs(ranks)) == cuts == (8290, 46456, 650883)
    assert (stock["public_exponent_A"], stock["first_public_offset"]) == (19182389, 4)
    assert stock["absolute_log2_private_control_envelope"] == 18975979523
    assert all(cuts[i - 1] + 2 < ranks[i] for i in range(1, len(ranks)))
    assert activation(TERMINAL) == stock["public_exponent_A"]
    assert stock["retimed_first_stripe_margin"] > 1024
    assert stock["retimed_all_size_margin_floor"] > 1024
    signed = qualify(TERMINAL.kappa, STOP, paid, gaussian_upper(height))
    assert (signed["strict"], signed["functional"]) == (54, 4)
    early = 1 + financial_checks()["early_log2_C_bound"]
    assert early == 84500001
    assert (ENTRY.rank_logs, ENTRY.complex_log, ENTRY.kappa) == ((3000, 3080), 1024, Q(".00345"))
    entry = max(early, 1602 + 220 * ENTRY.complex_log + 40 + 17 + 16384 * sum(ENTRY.rank_logs) + 25818582)
    assert entry == 125660241
    logB = 128 + 320 * sum(ranks)
    late = 1602 + 220 * height + logB
    conversion = ((TERMINAL.kappa - ENTRY.kappa) * activation(TERMINAL)).__ceil__()
    assert conversion == expected["premium"] == 8603
    assert conversion - 1 < (TERMINAL.kappa - ENTRY.kappa) * activation(TERMINAL) <= conversion
    whole = 1 + max(entry + conversion, late)
    assert whole == expected["total"] == 4285082571
    assert PREVIOUS_RECURRING_CAP - whole == 69234880

    old_ranks = (8192, 124649, 524288)
    assert ordinary_upper(old_ranks) <= paid and gaussian_upper(490950) <= paid
    h1, h2, h3 = ranks
    assert ordinary_upper((h1, h2 - 1, h3)) <= paid
    assert ordinary_upper((h1, h2, h3 - 1)) <= paid

    def require_funding(proposed_ranks, proposed_gaussian):
        if ordinary_upper(proposed_ranks) <= paid or gaussian_upper(proposed_gaussian) <= paid:
            raise ArithmeticError("Profile does not fund the terminal price")

    def require_budget(cap):
        if whole > cap:
            raise ArithmeticError("The full recurring invoice exceeds the declared cap")

    controls = [
        rejected(lambda: require_funding((h1 - 1, h2, h3), height), "first-ordinary-height-minus-one"),
        rejected(lambda: require_funding((h1, h2 - 1, h3), height), "second-ordinary-height-minus-one"),
        rejected(lambda: require_funding((h1, h2, h3 - 1), height), "third-ordinary-height-minus-one"),
        rejected(lambda: require_funding(old_ranks, 490950), "old-heights-at-new-rate"),
        rejected(lambda: qualify(TERMINAL.kappa, STOP, paid, gaussian_upper(height - 1)), "below-minimum-gaussian-height"),
        rejected(lambda: qualify(TERMINAL.kappa, STOP, paid, gaussian_upper(height, PREVIOUS_GAUSSIAN)), "previous-gaussian-booking"),
        rejected(lambda: qualify(TERMINAL.kappa, STOP, paid - STOP, gaussian_upper(height)), "outer-ordinary-margin-removed"),
        rejected(lambda: resource_receipt(replace(TERMINAL, rank_logs=(h1, cuts[0] + 2, h3))), "prefix-height-at-previous-cut"),
        rejected(lambda: require_budget(expected["total"] - 1), "recurring-bound-minus-one"),
    ]
    assert sha256((RUNTIME / "installations.py").read_bytes()).hexdigest() == expected["image_sha"] == PROFILE_IMAGE_SHA256
    assert expected["total"] > 318292011
    assert sha256((RUNTIME / "strong-bit.json.gz").read_bytes()).hexdigest() == (
        "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362")
    old = replace(TERMINAL, rank_logs=PREVIOUS_HEIGHTS, complex_log=PREVIOUS_GAUSSIAN_HEIGHT, kappa=PREVIOUS_RATE)
    old_native, new_native = prepare_native(old), prepare_native(TERMINAL)
    word = binary_word()
    assert (len(word.targets), len(word.paid), len(word.cells)) == (18906, 104652, 24)
    assert all(before is after for before, after in zip(old_native[:-1], new_native[:-1], strict=True))
    assert old_native[-1].targets is new_native[-1].targets and old_native[-1].cells is new_native[-1].cells
    assert all(v.level_floor == 18960 and v.targets is word.targets and v.paid is word.paid and v.cells is word.cells
               for v in (*old_native[:-1], *new_native[:-1]))

    def round_up(n):
        return ((n + 9999) // 10000) * 10000
    direct = [verify_stage(TERMINAL, cuts, i, round_up(cuts[i - 1])) for i in (2, 3)]
    compiled = [verify_stage(TERMINAL, cuts, i, round_up(9 * ranks[i - 1])) for i in (2, 3)]
    assert all(item["direct"] for item in direct) and not any(item["direct"] for item in compiled)
    tapes = [verify_tape(1, [0, 1], [2, 1]), verify_tape(2, [1, 7], [3, 1])]
    print("PASS_25BIT_MATCHED_PROFILE", json.dumps({
        "profile": key, "kappa": str(TERMINAL.kappa), "heights": ranks,
        "gaussian_height": TERMINAL.complex_log, "binary_cuts": cuts,
        "signed": signed, "conversion_bits": conversion, "log2_B": logB,
        "complete_log2_C": expected["total"], "stock": stock,
        "prior_stopped_upper": str(old_ceiling), "stopped_separation": str(stopped_gap), "controls": controls,
        "minimum_gaussian_height_for_target": height,
        "ordinary_margin": str(ordinary_upper(ranks) - paid),
        "gaussian_margin": str(gaussian_upper(TERMINAL.complex_log) - paid),
        "direct_stage_seams": direct, "compiled_stage_seams": compiled,
        "signed_tape_controls": tapes,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    check()
