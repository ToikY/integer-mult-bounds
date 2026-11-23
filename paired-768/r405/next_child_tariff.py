"""One prospective tariff price gate. This is not an allocation search."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import sys
import tarfile
from types import SimpleNamespace

FACTOR_SHA = "c06f87e5e690ee4c29b7273f605200f91ce1960671c794bf2a9723856db734e8"
R404_PRICE_SHA = "5a1798f012442618ec20af2071183848abef842dc665af1db6f5ddf709ba57fd"
ARCHIVE_SHA = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
TAU_OLD, TAU = Q(47, 20), Q(2401, 1024)
DEBIT_OLD, DEBIT = Q(11204, 8192), Q(11178, 8192)
ORDINARY_TRIAL, GAUSSIAN_TRIAL = Q(4391986206293, 2**50), Q(17145637307, 2**42)
GUARD, ETA = Q(5, 10**18), Q(39, 10000)
ENTRY = Q(".00345")
RATE = Q(".003898219754")


def pinned_json(path, digest):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == digest
    return json.loads(data)


def ordinary(heights, debit):
    prior = Q(0)
    for i, h in enumerate(heights):
        rate = min(ETA, (249 * (ORDINARY_TRIAL - debit / h) + prior) / 250)
        if i == len(heights) - 1:
            return rate
        prior = Q(floor(rate * 10**21) - 1, 10**21)


def gaussian(h):
    return GAUSSIAN_TRIAL - Q(64939, 524288 * h)


def old_source(archive, member):
    with tarfile.open(archive, "r:gz") as bundle:
        name = f"research/tiered-native-multiplier/source/{member}.py"
        data = bundle.extractfile(name).read()
    ns = {"__name__": member}
    exec(compile(data, name, "exec"), ns)
    return ns


def main(factor_path, prior_path, archive):
    factor = pinned_json(factor_path, FACTOR_SHA)
    prior = pinned_json(prior_path, R404_PRICE_SHA)
    assert sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA
    assert factor["booking"] == "11204/8192"
    assert Q(prior["ordinary_debit"]) == DEBIT_OLD

    mean = Q(75, 32)
    assert TAU > mean >= 1
    contraction = mean / TAU
    series = 1 / (1 - contraction)
    assert contraction == Q(2400, 2401) and series == 2401
    assert series / 376 < 8
    assert 2**16 < (Q(7, 10) * 376)**2 < 2**17
    assert 2**21 < (Q(7, 10) * series)**2 < 2**22

    lo, hi = (Q(endpoint) * TAU / TAU_OLD for endpoint in factor["new_factor"])
    assert 2**11177 < lo**8192 <= hi**8192 < 2**11178
    assert ordinary((3000, 3080), DEBIT) > ENTRY + GUARD
    assert gaussian(1024) > ENTRY + GUARD

    old = prior["chosen"]
    old_heights = tuple(old["heights"])
    assert old_heights == (8192, 117168, 524288) and old["g"] == 501831
    heights, g = (8192, 117167, 524288), 501832
    assert RATE > Q(prior["family_ceiling"])
    assert ordinary(heights, DEBIT_OLD) < RATE + GUARD
    assert RATE + GUARD < min(ordinary(heights, DEBIT), gaussian(g))

    margin = old_source(archive, "outer_budget")["margins"]
    for k, gg in ((ENTRY, 1024), (RATE, g)):
        strict, functional, paid = margin(k, GUARD / 5, k + GUARD, gaussian(gg))
        assert len(strict) == 54 and len(functional) == 4
        assert min(*strict, *functional, paid) > 0

    stock = old_source(archive, "activation")["resource_receipt"](
        SimpleNamespace(rank_logs=heights, complex_log=g, eta=ETA)
    )
    exponent, offset = stock["public_exponent_A"], stock["first_public_offset"]
    assert stock["binary_cuts"] == [8290, 125521, 649873]
    assert stock["absolute_log2_private_control_envelope"] == 536870915
    assert exponent == prior["whole_invoice"]["activation_exponent"] == 1151953
    assert offset == prior["whole_invoice"]["activation_offset"] == 4
    assert max(*heights, g) == max(*old_heights, old["g"]) == 524288

    entry_cost = prior["whole_invoice"]["entry_log2_C"] + 5
    term_B = 128 + 320 * sum(heights) + 9
    premium = ceil((RATE - ENTRY) * exponent)
    cost = 1 + max(entry_cost + premium, 84500001, 1602 + 220 * g + term_B)
    assert (entry_cost, premium, term_B, cost) == (125660246, 517, 207887177, 318291820)
    assert cost < prior["whole_invoice"]["recurring"]
    print("PASS one charged ordinary tariff price", RATE, "complete C", cost,
          "stopped Gaussian margin", gaussian(g) - RATE - GUARD,
          "activation", (exponent, offset), "entry conversion", premium)


if __name__ == "__main__":
    main(*(Path(arg) for arg in sys.argv[1:]))
