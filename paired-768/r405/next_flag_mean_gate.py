"""One scoped Round 406 flag-mean price gate. Do not search neighboring profiles."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import signal
import tarfile
from types import SimpleNamespace

PRIOR_PRICE_SHA = "372217dd34163c7746c98d01409e986aee5e0197ccea2ee4b33b4658fe97801d"
FACTOR_SHA = "c06f87e5e690ee4c29b7273f605200f91ce1960671c794bf2a9723856db734e8"
ARCHIVE_SHA = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
RECEIVER_SHA = "f31089b6304fc5352feb9aa8a963cc5a950a828165d3426e16e8a973529d814e"
CLOCK_SHA = "4694db0b2218796e348c1128271cebb3fc779151a639b0e0fb5bbecf9f3ccb94"
H, G = (8192, 101728, 524288), 524288
ENTRY_H, ENTRY_G = (3000, 3080), 1024
CAP, RATE, ENTRY_RATE = 318291900, Q(".003898230325603"), Q(".00345")
MEAN, TARIFF = Q(7, 3) + Q(1, 2**40), Q(7, 3) + Q(1, 2**16)
DEBIT, GAUSSIAN_DEBIT = Q(11120, 8192), Q(64939, 524288)
ORDINARY_TRIAL, GAUSSIAN_TRIAL = Q(4391986206293, 2**50), Q(17145637307, 2**42)
GUARD, ETA = Q(5, 10**18), Q(39, 10000)


def pinned(path, digest):
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"Source digest differs: {path.name}")
    return data


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Repeated pinned key: {key}")
        result[key] = value
    return result


def read_json(path, digest):
    return json.loads(pinned(path, digest), object_pairs_hook=unique)


def archive_source(bundle, source_hashes, module):
    member = f"research/tiered-native-multiplier/source/{module}.py"
    data = bundle.extractfile(member).read()
    assert sha256(data).hexdigest() == source_hashes[member]
    namespace = {"__name__": module}
    exec(compile(data, member, "exec"), namespace)
    return namespace


def physical_clock_charges():
    # x >= 3**26 already follows from N >= 28. Actual N >= 2**1024.
    x = 3**26
    assert 2**min(ENTRY_G, G, *H, *ENTRY_H) >= 28
    assert 16 * 2**40 < 3 * (9 * x - 1)
    sharp_mean = Q(21 * x + 3, 9 * x - 1)
    assert sharp_mean == Q(7, 3) + Q(16, 3 * (9 * x - 1))
    assert Q(7, 3) < sharp_mean < MEAN < TARIFF
    contraction = MEAN / TARIFF
    series = 1 / (1 - contraction)
    assert series == Q(1539326345216, 10066329)
    assert 32 * 2401 < series < 64 * 2401
    assert 2**33 < (Q(7, 10) * series)**2 < 2**34
    return contraction, series


def ordinary(heights, debit):
    previous = Q(0)
    for index, height in enumerate(heights, 1):
        funded = (249 * (ORDINARY_TRIAL - debit / height) + previous) / 250
        assert previous < funded < ETA
        assert 0 < ORDINARY_TRIAL - debit / height < 1
        if index == len(heights):
            return funded
        previous = Q(floor(funded * 10**21) - 1, 10**21)


def gaussian(height):
    return GAUSSIAN_TRIAL - GAUSSIAN_DEBIT / height


def price_case(args):
    prior = read_json(args.prior_price, PRIOR_PRICE_SHA)
    factor = read_json(args.factor_receipt, FACTOR_SHA)
    pinned(args.archive, ARCHIVE_SHA)
    pinned(args.receiver_proof, RECEIVER_SHA)
    pinned(args.clock_proof, CLOCK_SHA)
    assert Q(prior["booked_rate"]) == Q(".003898223617430")
    assert tuple(prior["chosen"]["heights"]) == (8192, 111681, 524288)
    assert (prior["chosen"]["g"], prior["chosen"]["recurring"]) == (509812, CAP)
    assert Q(prior["gaussian_debit"]) == GAUSSIAN_DEBIT
    assert prior["inventory"]["series"] == "2401"
    assert factor["booking"] == "11204/8192"

    contraction, series = physical_clock_charges()
    lower, upper = (Q(endpoint) * TARIFF / Q(47, 20) for endpoint in factor["new_factor"])
    assert 2**11119 < lower**8192 <= upper**8192 < 2**11120

    assert RATE > Q(prior["family_ceiling"]) > Q(prior["booked_rate"])
    assert ordinary(H, Q(prior["ordinary_debit"])) < RATE + GUARD
    assert RATE + GUARD < gaussian(G) < ordinary(H, DEBIT)
    assert gaussian(G - 1) < RATE + GUARD < gaussian(G) < RATE + GUARD + Q(1, 10**15)
    assert ENTRY_RATE + GUARD < min(ordinary(ENTRY_H, DEBIT), gaussian(ENTRY_G))

    sources = prior["verified_archive_source_paths"]
    with tarfile.open(args.archive) as bundle:
        margins = archive_source(bundle, sources, "outer_budget")["margins"]
        activation = archive_source(bundle, sources, "activation")["resource_receipt"]
        finance = archive_source(bundle, sources, "outer_clock")["financial_checks"]
    for rate, gg in ((ENTRY_RATE, ENTRY_G), (RATE, G)):
        strict, functional, paid = margins(rate, GUARD / 5, rate + GUARD, gaussian(gg))
        assert len(strict) == 54 and len(functional) == 4
        assert min(*strict, *functional, paid) > 0

    late = activation(SimpleNamespace(rank_logs=H, complex_log=G, eta=ETA))
    early = activation(SimpleNamespace(rank_logs=ENTRY_H, complex_log=ENTRY_G, eta=ETA))
    assert tuple(late["binary_cuts"]) == (8290, 110082, 634434)
    exponent, offset = late["public_exponent_A"], late["first_public_offset"]
    assert (exponent, offset) == (1158970, 2)
    assert early["public_exponent_A"] == 7437
    assert late["absolute_log2_private_control_envelope"] == 536870915
    assert max(G, *H) == max(prior["chosen"]["g"], *prior["chosen"]["heights"]) == 524288
    assert len(H) + len(ENTRY_H) + 2 == 7
    assert prior["whole_invoice"]["fixed_setup_exponent"] == 228
    assert prior["whole_invoice"]["fixed_setup_transition_upper"] < 2**228

    finite = 1 + finance()["early_log2_C_bound"]
    entry_B = 40 + 34 + 16384 * sum(ENTRY_H) + 25818582
    terminal_B = 128 + (3 + 6) * len(H) + 320 * sum(H)
    entry_C = max(finite, 1602 + 220 * ENTRY_G + entry_B)
    conversion = ceil((RATE - ENTRY_RATE) * exponent)
    terminal_C = max(finite, 1602 + 220 * G + terminal_B)
    complete = 1 + max(entry_C + conversion, terminal_C)
    assert (entry_B, terminal_B, entry_C, conversion) == (125433376, 202946715, 125660258, 520)
    assert complete == 318291678 <= CAP < complete + 320
    gain = RATE - Q(prior["booked_rate"])
    assert gain == Q(6708173, 10**15)
    print(json.dumps({
        "status": "ONE_PRICE_CASE_PASSED",
        "ordinary_heights": H, "gaussian_height": G,
        "tariff": str(TARIFF), "mean_upper": str(MEAN),
        "both_moment_contraction": str(contraction), "both_moment_series": str(series),
        "entry_log2_B": entry_B, "terminal_log2_B": terminal_B,
        "entry_log2_C": entry_C, "entry_conversion": conversion,
        "recurring_log2_C": complete, "cap": CAP,
        "target": str(RATE), "gain_if_replayed": str(gain),
        "activation": [exponent, offset], "strict_gaussian_margin": str(gaussian(G) - RATE - GUARD),
        "controls": ["sharp arbitrary frame exceeds 7/3", "next lower ordinary tick misses factor",
                     "old ordinary booking and G-1 each miss target"],
    }, sort_keys=True))


def timeout(signum, frame):
    raise TimeoutError("one flagged-mean price case reached its 30-second cap")


def main():
    if not __debug__:
        raise RuntimeError("Enable assertions for the price gate")
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("prior-price", "factor-receipt", "archive", "receiver-proof", "clock-proof"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    try:
        price_case(args)
    except TimeoutError as exc:
        parser.exit(124, f"{exc}\n")
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
