"""Bound the #8078 same-clock comparison across at most 16 price evaluations."""
import argparse
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from math import ceil, floor, isqrt
from pathlib import Path
import signal
import tarfile
from types import SimpleNamespace

PEER_HASH = "f084851c816440c98c9569ed2d9b5e0b758b35c241edaa17706d031b252f46fb"
PEER_BLOB = "af56ac7079a3021f59189dcce5dab8ec2fd64378"
PEER_HEAD = "b72d3fa097d2521939f6b8536029da674648d863"
PRIOR_HASH = "372217dd34163c7746c98d01409e986aee5e0197ccea2ee4b33b4658fe97801d"
FACTOR_HASH = "c06f87e5e690ee4c29b7273f605200f91ce1960671c794bf2a9723856db734e8"
ARCHIVE_HASH = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
RECEIVER_HASH = "f31089b6304fc5352feb9aa8a963cc5a950a828165d3426e16e8a973529d814e"
CLOCK_HASH = "4694db0b2218796e348c1128271cebb3fc779151a639b0e0fb5bbecf9f3ccb94"

ORD, GTRIAL = Q(4391986206293, 2**50), Q(17145637307, 2**42)
PEER_DEBIT, DEBIT, GDEBIT = Q(11239, 8192), Q(11120, 8192), Q(64939, 524288)
OLD_RATE, ENTRY_RATE = Q(".00389834"), Q(".00345")
TARGET_GUARD, ETA = Q(5, 10**18), Q(39, 10000)
TARIFF, MEAN = Q(7, 3) + Q(1, 2**16), Q(7, 3) + Q(1, 2**40)
WEIGHT, LOSS0, DECAY = Q(1, 62500), Q(1, 250), Q(249, 250)
ROOT = Q(6324555320336758663997787088865437067439, 10**41)
HEIGHT_MIN, HEIGHT_LIMIT = 8192, 2**20
OLD_H, OLD_G = (8192, 36220, 575705), 978582
CAP, FIXED_OLD, FIXED_NEW = 413727211, 1731, 1758
CASE_LIMIT = 16


def pin(path, digest):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == digest, path.name
    return data


def qtext(value):
    return str(Q(value))


def gaussian(g):
    return GTRIAL - GDEBIT / g


def ordinary(heights, debit):
    used = Q(0)
    before = []
    for i, h in enumerate(heights, 1):
        eligible = (249 * (ORD - debit / h) + used) / 250
        assert 0 < eligible < ETA and used < eligible
        if i == len(heights):
            return eligible, before
        used = Q(floor(eligible * 10**21) - 1, 10**21)
        before.append(qtext(used))


def max_ordinary_sum(g, fixed):
    return (CAP - fixed - 220 * g) // 320


def relaxed_rate(loss, debit):
    return ORD * (1 - Q(1, 250**3)) - DECAY * debit * loss


def lower_loss_at_sum(total):
    # Cauchy relaxes h1 and the h2/h3 split. The derivative in h1 is
    # positive at HEIGHT_MIN and increases, so this lower bound is uniform.
    s = total - HEIGHT_MIN
    assert ROOT**2 < LOSS0 < (ROOT + Q(1, 10**41))**2
    assert WEIGHT * s**2 < (1 + ROOT)**2 * HEIGHT_MIN**2
    return WEIGHT / HEIGHT_MIN + (1 + ROOT)**2 / s


def optimal_unrounded_heights(total):
    s = total - HEIGHT_MIN
    # If first height is larger than HEIGHT_MIN, move one slot from
    # first to third. Its gain exceeds the first-stage loss, uniformly.
    assert total < HEIGHT_LIMIT
    assert Q(1, s * (s + 1)) > WEIGHT / (HEIGHT_MIN * (HEIGHT_MIN + 1))
    b = 2 * s + 249
    discriminant = b*b - 996*(s - s*s)
    middle = (isqrt(discriminant) - b) // 498
    def slope_numerator(k):
        return 250*k*(k+1) - (s-k)*(s-k-1)
    if slope_numerator(middle) < 0:
        middle += 1
    assert slope_numerator(middle-1) < 0 <= slope_numerator(middle)
    high = s - middle
    assert min(middle, high) >= HEIGHT_MIN and max(middle, high) < HEIGHT_LIMIT
    heights = HEIGHT_MIN, middle, high
    loss = WEIGHT / HEIGHT_MIN + LOSS0 / middle + Q(1, high)
    return heights, loss


def load_source(archive, pins, name):
    entry = f"research/tiered-native-multiplier/source/{name}.py"
    data = archive.extractfile(entry).read()
    assert sha256(data).hexdigest() == pins[entry]
    values = {"__name__": name}
    exec(compile(data, entry, "exec"), values)
    return values


def timed_out(_signum, _frame):
    raise TimeoutError("Round 406 allocation screen reached its 30-second cap")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("peer-price", "prior-price", "factor-receipt", "archive", "receiver-proof", "clock-proof"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    assert __debug__
    signal.signal(signal.SIGALRM, timed_out)
    signal.alarm(30)
    try:
        price(args)
    except TimeoutError as exc:
        parser.exit(124, str(exc) + "\n")
    finally:
        signal.alarm(0)


def price(args):
    peer_bytes = pin(args.peer_price, PEER_HASH)
    assert sha1(b"blob " + str(len(peer_bytes)).encode() + b"\0" + peer_bytes).hexdigest() == PEER_BLOB
    peer = json.loads(peer_bytes)
    prior = json.loads(pin(args.prior_price, PRIOR_HASH))
    factor = json.loads(pin(args.factor_receipt, FACTOR_HASH))
    pin(args.receiver_proof, RECEIVER_HASH)
    pin(args.clock_proof, CLOCK_HASH)
    pin(args.archive, ARCHIVE_HASH)
    assert (tuple(peer["terminal"]["ordinary_H"]), peer["terminal"]["numerical_H"]) == (OLD_H, OLD_G)
    assert (Q(peer["terminal"]["kappa"]), Q(peer["ordinary_finite_debit"]), peer["complete_log2_C"]) == (OLD_RATE, PEER_DEBIT, CAP)
    assert peer["ordinary_child_contraction"] == "375/376" and peer["ordinary_floor"] == 18960
    assert peer["log2_fixed_setup_upper"] == prior["whole_invoice"]["fixed_setup_exponent"] == 228
    assert peer["native_setup_transition_upper"] == prior["whole_invoice"]["fixed_setup_transition_upper"] < 2**228
    assert peer["native_setup_grade_actions"] < 2**32
    assert prior["inventory"]["series"] == "2401" and Q(prior["gaussian_debit"]) == GDEBIT
    assert factor["booking"] == "11204/8192"
    x = 3**26
    assert Q(7, 3) < Q(21*x + 3, 9*x - 1) < MEAN < TARIFF
    assert Q(21*x + 3, 9*x - 1) == Q(7, 3) + Q(16, 3*(9*x-1))
    contraction = MEAN / TARIFF
    series = 1 / (1 - contraction)
    assert series == Q(1539326345216, 10066329)
    assert 32*2401 < series < 64*2401
    assert 2**33 < (Q(7, 10) * series)**2 < 2**34
    lower, upper = (Q(endpoint)*TARIFF/Q(47, 20) for endpoint in factor["new_factor"])
    assert 2**11119 < lower**8192 <= upper**8192 < 2**11120

    old_price, old_steps = ordinary(OLD_H, PEER_DEBIT)
    old_short = relaxed_rate(lower_loss_at_sum(sum(OLD_H)-1), PEER_DEBIT)
    threshold = OLD_RATE + TARGET_GUARD
    assert old_short < threshold < old_price
    assert gaussian(OLD_G-1) < threshold < gaussian(OLD_G)
    assert FIXED_OLD+320*sum(OLD_H)+220*OLD_G == CAP
    old_ceiling = gaussian(OLD_G) - TARGET_GUARD

    # Any improved candidate requires strictly more ordinary weight than
    # a Cauchy lower bound for the peer rate. Use it to bound the search.
    allowance = (ORD*(1-Q(1, 250**3))-threshold)/(DECAY*DEBIT) - WEIGHT/HEIGHT_MIN
    assert allowance > 0
    minimum_sum = HEIGHT_MIN + floor((1+ROOT)**2 / allowance) + 1
    high = (CAP-FIXED_NEW-320*minimum_sum)//220 + 1
    assert OLD_G < high < HEIGHT_LIMIT
    lows = OLD_G
    visits = {}

    def inspect(g):
        if g in visits:
            return visits[g]
        assert len(visits) < CASE_LIMIT
        heights, loss = optimal_unrounded_heights(max_ordinary_sum(g, FIXED_NEW))
        ideal = relaxed_rate(loss, DEBIT)
        actual, intermediate = ordinary(heights, DEBIT)
        assert 0 < ideal-actual < Q(1, 10**21)
        quote = (heights, actual, ideal, gaussian(g), intermediate)
        visits[g] = quote
        return quote

    first, last = inspect(lows), inspect(high)
    assert first[3] < first[1] and last[2] < last[3]
    assert last[2] < threshold
    while high-lows > 1 and len(visits) < CASE_LIMIT:
        middle = (high+lows)//2
        trial = inspect(middle)
        if trial[2] < trial[3]:
            high = middle
        else:
            lows = middle
    assert high-lows == 1
    left, right = inspect(lows), inspect(high)
    upper_rate = max(left[3], right[2]) - TARGET_GUARD
    g, winner = max(((lows, left), (high, right)), key=lambda pair: min(pair[1][1], pair[1][3]))
    heights, upper_ordinary, relaxed_ordinary, upper_gaussian, intermediate = winner
    admissible = min(upper_ordinary, upper_gaussian) - TARGET_GUARD
    tick = floor(admissible*10**15)
    if Q(tick, 10**15) == admissible:
        tick -= 1
    rate = Q(tick, 10**15)
    assert old_ceiling < rate < admissible <= upper_rate
    assert g > OLD_G
    assert all(h < HEIGHT_LIMIT for h in heights)
    assert len(heights) == 3
    assert gaussian(g-1) < rate + TARGET_GUARD
    assert min(*heights, 1024) > 28

    pins = prior["verified_archive_source_paths"]
    with tarfile.open(args.archive) as archive:
        margins = load_source(archive, pins, "outer_budget")["margins"]
        stock = load_source(archive, pins, "activation")["resource_receipt"]
        finance = load_source(archive, pins, "outer_clock")["financial_checks"]
    for trial, rates, gaussian_height in (
        (ENTRY_RATE, ordinary((3000,3080), DEBIT)[0], 1024),
        (OLD_RATE, old_price, OLD_G),
        (rate, upper_ordinary, g),
    ):
        assert trial + TARGET_GUARD < rates
        strict, functional, paid = margins(trial, TARGET_GUARD/5, trial+TARGET_GUARD, gaussian(gaussian_height))
        assert len(strict) == 54 and len(functional) == 4 and min(*strict, *functional, paid) > 0
    instantiated = stock(SimpleNamespace(rank_logs=heights, complex_log=g, eta=ETA))
    old_stock = stock(SimpleNamespace(rank_logs=OLD_H, complex_log=OLD_G, eta=ETA))
    assert old_stock == peer["terminal"]["stock"]
    assert tuple(instantiated["binary_cuts"])[0] == 8290
    exponent, offset = instantiated["public_exponent_A"], instantiated["first_public_offset"]
    entry_cost = 125660258
    conversion = ceil((rate-ENTRY_RATE)*exponent)
    terminal_b = 155 + 320*sum(heights)
    terminal_cost = 1602+220*g+terminal_b
    finite = 1 + finance()["early_log2_C_bound"]
    complete = 1 + max(entry_cost+conversion, terminal_cost, finite)
    assert complete == FIXED_NEW+320*sum(heights)+220*g <= CAP
    assert CAP - complete < 320
    assert max(*heights, g) == g
    print(json.dumps({
        "status": "EXACT_CHARGED_FEASIBILITY_NOT_A_SIGNED_REPLAY",
        "peer_head": PEER_HEAD,
        "peer_kappa": "0.00389834",
        "peer_max_height": OLD_G,
        "peer_unchanged_invoice_stopped_ceiling_upper": qtext(old_ceiling),
        "peer_ordinary_first_two_rates": old_steps,
        "peer_ordinary_shorter_sum_margin": qtext(threshold-old_short),
        "trial_kappa": f"0.{tick:015d}",
        "exact_trial_delta": qtext(rate-OLD_RATE),
        "exact_percent_delta": qtext(100*(rate-OLD_RATE)/OLD_RATE),
        "trial_excess_above_peer_stopped_ceiling": qtext(rate-old_ceiling),
        "scenario_stopped_upper": qtext(upper_rate),
        "trial_strict_ordinary_margin": qtext(upper_ordinary-rate-TARGET_GUARD),
        "trial_strict_gaussian_margin": qtext(upper_gaussian-rate-TARGET_GUARD),
        "scenario_exact_at_trial_height": admissible == upper_rate,
        "ordinary_heights": heights, "ordinary_first_two_rates": intermediate,
        "gaussian_height": g, "max_height_increase": g-OLD_G,
        "ordinary_debit": qtext(DEBIT), "gaussian_debit": qtext(GDEBIT),
        "geometric_ratio": qtext(contraction), "geometric_series": qtext(series),
        "entry_log2_c": entry_cost, "entry_conversion": conversion,
        "terminal_log2_b": terminal_b, "recurring_log2_C": complete,
        "whole_recurring_cap": CAP, "price_evaluations": len(visits), "price_gs": list(visits),
        "activation": [exponent, offset], "binary_cuts": instantiated["binary_cuts"],
        "private_log2": instantiated["absolute_log2_private_control_envelope"],
        "fixed_setup_log2": 228,
        "lower_crossing_G": lows, "upper_crossing_G": high,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
