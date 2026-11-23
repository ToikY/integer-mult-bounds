"""Exact Round 404 cap crossing and whole signed invoice."""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
from subprocess import check_output
import tarfile
from types import SimpleNamespace


HEAD = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
RECEIPT = "1cb65536235c27fd2e5673de49a3d8a0c320358cf90dea3e7c491795d46a6025"
ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
PACKAGE = "research/p104-weighted-capped-allocation-490950"
ORDINARY_TRIAL = Fraction(4391986206293, 2**50)
GAUSSIAN_TRIAL = Fraction(17145637307, 2**42)
OLD_DEBIT, ORDINARY_DEBIT = Fraction(11239, 8192), Fraction(11204, 8192)
GAUSSIAN_DEBIT = Fraction(64939, 524288)
ETA, GUARD = Fraction(39, 10000), Fraction(5, 10**18)
CAP, OLD_G, MIN_ORDINARY, MAX_HEIGHT = 318292011, 490950, 8192, 524288
CROSSING = (501830, 501831, 501832)
CLOCK_BASE, ORDINARY_CLOCK, GAUSSIAN_CLOCK = 1731, 320, 220


def load_inputs(repository, receipt_path):
    def git(*args):
        return check_output(["git", "-C", repository, *args])

    assert git("rev-parse", "HEAD").decode().strip() == HEAD
    assert not git("status", "--porcelain")
    retained = repository / PACKAGE
    for name in ("PEER-SOURCE.json", "peer8057.tar.gz", "RESULT.json"):
        assert (retained / name).read_bytes() == git("show", f"HEAD:{PACKAGE}/{name}")
    manifest = json.loads((retained / "PEER-SOURCE.json").read_bytes())
    assert sha256((retained / "peer8057.tar.gz").read_bytes()).hexdigest() == ARCHIVE
    assert manifest["archive_sha256"] == ARCHIVE
    receipt_data = receipt_path.read_bytes()
    assert sha256(receipt_data).hexdigest() == RECEIPT
    receipt = json.loads(receipt_data)
    assert receipt["head"] == HEAD and receipt["exit_code"] == 0
    assert receipt["clean_detached_checkout"] and len(receipt["modes"]) == 7
    assert all(mode["result"] == "pass" for mode in receipt["modes"])
    source = {}
    hashes = {}
    with tarfile.open(retained / "peer8057.tar.gz") as archive:
        for name in ("outer_budget", "activation", "outer_clock"):
            member = f"research/tiered-native-multiplier/source/{name}.py"
            data = archive.extractfile(member).read()
            assert sha256(data).hexdigest() == manifest["files_sha256"][member]
            hashes[member] = manifest["files_sha256"][member]
            namespace = {"__name__": name}
            exec(compile(data, member, "exec"), namespace)
            source[name] = namespace
    return json.loads((retained / "RESULT.json").read_bytes()), receipt, source, hashes


def ordinary_rate(heights, debit):
    current = Fraction(0)
    preceding = []
    for i, height in enumerate(heights, start=1):
        current = (249 * (ORDINARY_TRIAL - debit / height) + current) / 250
        assert current < ETA
        if i < len(heights):
            current = Fraction(floor(current * 10**21) - 1, 10**21)
            preceding.append(current)
    return current, preceding


def gaussian_rate(height):
    return GAUSSIAN_TRIAL - GAUSSIAN_DEBIT / height


def price(g):
    middle = ((CAP - CLOCK_BASE - GAUSSIAN_CLOCK * g) // ORDINARY_CLOCK
              - MIN_ORDINARY - MAX_HEIGHT)
    assert MIN_ORDINARY < middle < MAX_HEIGHT
    heights = MIN_ORDINARY, middle, MAX_HEIGHT
    ordinary, earlier = ordinary_rate(heights, ORDINARY_DEBIT)
    recurring = CLOCK_BASE + ORDINARY_CLOCK * sum(heights) + GAUSSIAN_CLOCK * g
    assert recurring <= CAP < recurring + ORDINARY_CLOCK
    return dict(g=g, heights=heights, ordinary=ordinary, gaussian=gaussian_rate(g),
                preceding=earlier, recurring=recurring)


def screen():
    left, right, higher = map(price, CROSSING)
    assert right["g"] - left["g"] == 1
    assert left["gaussian"] < right["ordinary"] < right["gaussian"]
    assert higher["ordinary"] < right["ordinary"]
    return left, right, higher


def tangent(quote):
    weights = tuple(map(Fraction, ("1/62500", "1/250", "1")))
    heights = quote["heights"]
    a, b, c = (weight / height**2 for weight, height in zip(weights, heights, strict=True))
    assert 0 < a < b < c
    relaxed = Fraction(249, 250) * sum(
        weight * (ORDINARY_TRIAL - ORDINARY_DEBIT / height)
        for weight, height in zip(weights, heights, strict=True)
    )
    rounding = relaxed - quote["ordinary"]
    loss = Fraction(249, 250) * ORDINARY_DEBIT * min(b - a, c - b, b)
    assert 0 < rounding < loss
    return dict(slopes=[a, b, c], rounding_loss=rounding, distinct_integer_loss=loss)


def signed_margins(source, rate, gaussian):
    strict, functional, paid = source["outer_budget"]["margins"](
        rate, GUARD / 5, rate + GUARD, gaussian
    )
    assert len(strict) == 54 and len(functional) == 4 and min(*strict, *functional, paid) > 0
    return dict(strict=strict, functional=functional, paid=paid,
                smallest_strict=min(strict), smallest_functional=min(functional))


def invoice(source, old, winner, rate):
    heights, g = winner["heights"], winner["g"]
    entry = old["entry"]
    entry_rate = Fraction(entry["kappa"])
    entry_ordinary, entry_ticks = ordinary_rate(tuple(entry["ordinary_H"]), ORDINARY_DEBIT)
    assert 0 < entry_ticks[0] < entry_rate + GUARD < entry_ordinary
    assert entry_rate + GUARD < gaussian_rate(entry["numerical_H"])
    assert 0 < winner["preceding"][0] < winner["preceding"][1] < rate + GUARD
    assert rate + GUARD < min(winner["ordinary"], winner["gaussian"])
    entry_signed = signed_margins(source, entry_rate, gaussian_rate(entry["numerical_H"]))
    terminal_signed = signed_margins(source, rate, winner["gaussian"])

    stock = source["activation"]["resource_receipt"](
        SimpleNamespace(rank_logs=heights, complex_log=g, eta=ETA)
    )
    cuts = []
    for h in heights:
        cuts.append(max(ceil(Fraction(250 * (h + 64), 249)),
                        cuts[-1] + h + 64 if cuts else 0))
    target = cuts[-1] + g + 102
    first_s = next(s for s in range(target, target + 500) if s - 7 * (s - 1).bit_length() >= target)
    exponent, offset = first_s - 1, (-pow(2, first_s - 1, 6)) % 6
    assert (cuts, exponent, offset) == (
        stock["binary_cuts"], stock["public_exponent_A"], stock["first_public_offset"]
    )
    premium = ceil((rate - entry_rate) * exponent)
    early = source["outer_clock"]["financial_checks"]()["early_log2_C_bound"] + 1
    assert early == 84500001
    degree = 20 * 253
    entry_ranks = entry["ordinary_H"]
    paid_surcharges = [
        max(0, 20 * 24 + degree * padding + 2 + term * (term - 1).bit_length() - 944 * h)
        for h, (padding, term) in zip(entry_ranks, ((4, 2 * degree), (259, 258 * degree)), strict=True)
    ]
    entry_bill = max(early, 1602 + 220 * entry["numerical_H"]
                     + 57 + 16384 * sum(entry_ranks) + sum(paid_surcharges))
    assert entry_bill == entry["log2_C"] == 125660241 and paid_surcharges == [0, 25818582]
    ordinary_bill = 128 + ORDINARY_CLOCK * sum(heights)
    terminal_bill = max(early, 1602 + GAUSSIAN_CLOCK * g + ordinary_bill)
    recurring = 1 + max(entry_bill + premium, terminal_bill)
    assert recurring == winner["recurring"] <= CAP

    max_height = max(*heights, g)
    assert max_height == MAX_HEIGHT and max_height.bit_length() == 20
    assert stock["absolute_log2_private_control_envelope"] == 536870915
    assert len(entry_ranks) + len(heights) + 2 == 7
    catalog_width = 1 << 38
    datum = 2 * catalog_width + 2
    scalar = 2**16 * (datum + 4) * (7 * datum + 9) + 8 * 2**16 * (datum + 4)**2
    lookup = 4 * catalog_width * 2**68 * 8 * 512 * 128
    setup = (2**68 + 1) * (lookup + scalar + 2**120) * 2**32
    assert scalar < 2**110 and lookup == 2**127 and setup < 2**228
    assert 400 + 1182 + 9 + 2 < 1602
    minimum_window = 128 * (4 * (first_s + 1) + 6)
    axis_degree = (6 * minimum_window - 1).bit_length()
    assert exponent - axis_degree >= (6 * exponent).bit_length()
    axis_count = 1 << (exponent - axis_degree)
    public = (1 << exponent) + offset
    block, remainder = divmod(public, 6)
    assert not remainder
    endpoints = []
    for extent in (block + 4 - exponent, block + 5 - exponent):
        assert (extent // minimum_window).bit_length() == exponent - axis_degree + 1
        block_width = ceil(Fraction(extent, axis_count))
        active = max(1, axis_count // (1024 * (public + 1).bit_length()))
        rounds = 20000 * (axis_count + 1) * (block_width + 2)**6 + 2 * axis_count
        precision = (public + 67 + 32768 * active * (block_width + 6)
                     + 4 * (rounds * (axis_count + 1)).bit_length()
                     + (axis_count + 1).bit_length())
        assert public < precision < 1 << (exponent + 1)
        endpoints.append(dict(width=block_width, precision_bits=precision.bit_length(),
                              precision_sha256=sha256(
                                  precision.to_bytes((precision.bit_length() + 7) // 8, "big")
                              ).hexdigest()))
    axis_width = max(x["width"] for x in endpoints)
    assert axis_width == ceil(Fraction(1 << axis_degree, 6))
    carrier = 1 << g
    upper = 2 * (carrier // (1724 * 306))
    assert upper > 2 * (carrier // (2048 * 306)) and 4 * 258 * (upper - 8) < carrier
    assert upper % 2 == 0 and 68 + 83 * g < 92 * g
    ordinary_funding = ceil(ORDINARY_DEBIT / (ORDINARY_TRIAL - rate - GUARD))
    gaussian_funding = ceil(GAUSSIAN_DEBIT / (GAUSSIAN_TRIAL - rate - GUARD))
    assert ordinary_funding <= sum(heights) and gaussian_funding <= g
    return dict(recurring=recurring, entry_log2_C=entry_bill, entry_conversion_bits=premium,
                ordinary_log2_B=ordinary_bill, gaussian_height_charge=GAUSSIAN_CLOCK * g,
                stage_cuts=cuts, activation_exponent=exponent, activation_offset=offset,
                log2_axis_count=exponent - axis_degree, axis_width=axis_width, precision=endpoints,
                private_scalar_clock_upper=1024 * (axis_width + first_s + 67) + first_s,
                fixed_setup_transition_upper=setup, fixed_setup_exponent=228,
                ordinary_funding_height=ordinary_funding, gaussian_funding_height=gaussian_funding,
                stock=stock, signed_entry=entry_signed, signed_terminal=terminal_signed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    old, prior, source, hashes = load_inputs(args.repository, args.receipt)
    known = old["terminal"]
    old_cap = Fraction(prior["new_family_ceiling"])
    old_ordinary, _ = ordinary_rate(tuple(known["ordinary_H"]), OLD_DEBIT)
    assert known["numerical_H"] == OLD_G and old["complete_log2_C"] == CAP
    assert old_ordinary - GUARD == old_cap < gaussian_rate(OLD_G) - GUARD
    old_rate = Fraction(known["kappa"])
    assert old_rate < old_cap
    left, winner, higher = screen()
    ceiling = winner["ordinary"] - GUARD
    tick_count = ceil(ceiling * 10**15) - 1
    rate = Fraction(tick_count, 10**15)
    assert old_cap < rate < ceiling
    assert left["gaussian"] < rate + GUARD and higher["ordinary"] < rate + GUARD
    proof, higher_proof = tangent(winner), tangent(higher)
    complete = invoice(source, old, winner, rate)
    endpoint_signed = signed_margins(source, ceiling, winner["gaussian"])
    assert ceil((ceiling - Fraction(old["entry"]["kappa"])) * complete["activation_exponent"]) == complete["entry_conversion_bits"]
    print(json.dumps(dict(
        comparator=HEAD, comparator_rate=old_rate, comparator_exact_ceiling=old_cap,
        ordinary_debit=ORDINARY_DEBIT, gaussian_debit=GAUSSIAN_DEBIT, cap=CAP,
        tested_scope=CROSSING, full_family_gaussian_scope=[1024, MAX_HEIGHT],
        full_family_ordinary_scope=[MIN_ORDINARY, MAX_HEIGHT],
        lower_neighbor=left, chosen=winner,
        next_distinct_upper_neighbor=higher, family_ceiling=ceiling, booked_rate=rate,
        booked_decimal=f"0.{tick_count:015d}", gain_vs_comparator=rate - old_rate,
        gain_vs_comparator_ceiling=rate - old_cap, reserve_below_ceiling=ceiling - rate,
        lower_gaussian_shortfall=rate + GUARD - left["gaussian"],
        next_distinct_upper_ordinary_shortfall=rate + GUARD - higher["ordinary"],
        winner_tangent=proof, upper_negative_tangent=higher_proof,
        whole_invoice=complete, signed_limit=endpoint_signed, verified_archive_source_paths=hashes,
    ), default=str, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
