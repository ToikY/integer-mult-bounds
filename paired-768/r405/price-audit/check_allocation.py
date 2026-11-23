"""Exact Round 405 cap crossing and whole signed invoice."""

import argparse
from fractions import Fraction
from functools import cache
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
from subprocess import check_output
import tarfile
from types import SimpleNamespace


HEAD = "cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e"
RECEIPT = "0654a74dd2c424ff2e8b26cb9828f451b76bde6f8b35762cb2cb69ba83fdd1ce"
ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
PACKAGE = "research/p104-weighted-k7-suffix"
ORDINARY_TRIAL = Fraction(4391986206293, 2**50)
GAUSSIAN_TRIAL = Fraction(17145637307, 2**42)
OLD_DEBIT, ORDINARY_DEBIT = Fraction(11204, 8192), Fraction(11178, 8192)
GAUSSIAN_DEBIT = Fraction(64939, 524288)
ETA, GUARD = Fraction(39, 10000), Fraction(5, 10**18)
CAP, OLD_G, MIN_ORDINARY, MAX_HEIGHT = 318291911, 501831, 8192, 524288
PRICE_SHA = "5a1798f012442618ec20af2071183848abef842dc665af1db6f5ddf709ba57fd"
FACTOR_SHA = "c06f87e5e690ee4c29b7273f605200f91ce1960671c794bf2a9723856db734e8"
LOW_ENTRY_LOG, HIGH_ENTRY_LOG = 57, 62
OLD_TERMINAL_LOG, TERMINAL_LOG = 128, 137
CLOCK_BASE, ORDINARY_CLOCK, GAUSSIAN_CLOCK = 1 + 1602 + TERMINAL_LOG, 320, 220
PROFILE_LIMIT = 24
CASES = []


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


@cache
def price(g):
    assert len(CASES) < PROFILE_LIMIT
    CASES.append(g)
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
    lo, hi = OLD_G, MAX_HEIGHT
    assert price(lo)["gaussian"] < price(lo)["ordinary"]
    assert price(hi)["ordinary"] < price(hi)["gaussian"]
    while hi - lo > 1:
        center = (lo + hi) // 2
        quote = price(center)
        if quote["gaussian"] < quote["ordinary"]:
            lo = center
        else:
            hi = center
    winner, right = price(lo), price(hi)
    assert right["ordinary"] < winner["gaussian"] < winner["ordinary"]
    assert right["ordinary"] < right["gaussian"]
    left = price(lo - 1)
    return left, winner, right


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
    prior_entry = max(early, 1602 + 220 * entry["numerical_H"]
                      + LOW_ENTRY_LOG + 16384 * sum(entry_ranks) + sum(paid_surcharges))
    entry_bill = max(early, 1602 + 220 * entry["numerical_H"]
                     + HIGH_ENTRY_LOG + 16384 * sum(entry_ranks) + sum(paid_surcharges))
    assert prior_entry == entry["log2_C"] == 125660241 and paid_surcharges == [0, 25818582]
    assert entry_bill == prior_entry + 5
    ordinary_bill = TERMINAL_LOG + ORDINARY_CLOCK * sum(heights)
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
    parser.add_argument("prior_price", type=Path)
    parser.add_argument("factor", type=Path)
    args = parser.parse_args()
    old, prior, source, hashes = load_inputs(args.repository, args.receipt)
    known = old["terminal"]
    prior_price = args.prior_price.read_bytes()
    assert sha256(prior_price).hexdigest() == PRICE_SHA
    previous = json.loads(prior_price)
    factor_data = args.factor.read_bytes()
    assert sha256(factor_data).hexdigest() == FACTOR_SHA
    factor = json.loads(factor_data)
    old_cap = Fraction(previous["family_ceiling"])
    assert old_cap == Fraction(523210198560303585338978849681, 134217728000000000000000000000000)
    tau0, tau, mean = Fraction(47, 20), Fraction(2401, 1024), Fraction(75, 32)
    old_series, series = 1 / (1 - mean / tau0), 1 / (1 - mean / tau)
    assert (old_series, series) == (376, 2401)
    assert 1 < series / old_series < 8
    assert 2**16 < (Fraction(7, 10) * old_series)**2 < 2**17
    assert 2**21 < (Fraction(7, 10) * series)**2 < 2**22
    lo, hi = (Fraction(endpoint) * tau / tau0 for endpoint in factor["new_factor"])
    assert 2**11177 < lo**8192 <= hi**8192 < 2**11178
    old_heights = tuple(known["ordinary_H"])
    old_ordinary, _ = ordinary_rate(old_heights, OLD_DEBIT)
    assert 1 + 1602 + ORDINARY_CLOCK * sum(old_heights) + GAUSSIAN_CLOCK * OLD_G + OLD_TERMINAL_LOG == CAP
    assert known["numerical_H"] == OLD_G and old["complete_log2_C"] == CAP
    assert old_ordinary - GUARD == old_cap < gaussian_rate(OLD_G) - GUARD
    old_rate = Fraction(known["kappa"])
    assert old_rate < old_cap
    left, winner, higher = screen()
    ceiling = winner["gaussian"] - GUARD
    tick_count = ceil(ceiling * 10**15) - 1
    rate = Fraction(tick_count, 10**15)
    assert old_cap < rate < ceiling
    assert left["gaussian"] < rate + GUARD and higher["ordinary"] < rate + GUARD
    proof, higher_proof = tangent(winner), tangent(higher)
    best_nonmaximal_ordinary = (winner["ordinary"] + proof["rounding_loss"]
                               - proof["distinct_integer_loss"])
    assert best_nonmaximal_ordinary < rate + GUARD
    unchanged, _ = ordinary_rate(winner["heights"], OLD_DEBIT)
    assert unchanged < rate + GUARD
    assert higher["g"] == winner["g"] + 1 == left["g"] + 2
    assert winner["g"] == 509812 and winner["heights"] == (8192, 111681, 524288)
    assert tick_count == 3898223617430
    complete = invoice(source, old, winner, rate)
    boundary_strict, boundary_functional, boundary_paid = source["outer_budget"]["margins"](
        ceiling, GUARD / 5, ceiling + GUARD, winner["gaussian"]
    )
    assert len(boundary_strict) == 54 and len(boundary_functional) == 4
    assert min(*boundary_strict, *boundary_functional) > 0 and boundary_paid == 0
    assert ceil((ceiling - Fraction(old["entry"]["kappa"])) * complete["activation_exponent"]) == complete["entry_conversion_bits"]
    print(json.dumps(dict(
        comparator=HEAD, comparator_rate=old_rate, comparator_exact_ceiling=old_cap,
        ordinary_debit=ORDINARY_DEBIT, gaussian_debit=GAUSSIAN_DEBIT, cap=CAP,
        tested_scope=CASES, profile_evaluation_limit=PROFILE_LIMIT, cap_ceiling_ties=[winner["g"]], full_family_gaussian_scope=[1024, MAX_HEIGHT],
        full_family_ordinary_scope=[MIN_ORDINARY, MAX_HEIGHT],
        lower_neighbor=left, chosen=winner,
        next_distinct_upper_neighbor=higher, family_ceiling=ceiling, booked_rate=rate,
        booked_decimal=f"0.{tick_count:015d}", gain_vs_comparator=rate - old_rate,
        percent_gain_vs_comparator=100 * (rate-old_rate) / old_rate,
        peer_rate=Fraction("0.00389821"), gain_vs_peer=rate-Fraction("0.00389821"),
        percent_gain_vs_peer=100 * (rate-Fraction("0.00389821"))/Fraction("0.00389821"),
        inventory=dict(tariff=tau, volume=mean, contraction=mean/tau, series=series,
                       old_series=old_series, entry_delta=5, terminal_delta=9),
        gain_vs_comparator_ceiling=rate - old_cap, reserve_below_ceiling=ceiling - rate,
        lower_gaussian_shortfall=rate + GUARD - left["gaussian"],
        next_distinct_upper_ordinary_shortfall=rate + GUARD - higher["ordinary"],
        winner_tangent=proof, upper_negative_tangent=higher_proof,
        whole_invoice=complete,
        signed_limit=dict(strict=boundary_strict, functional=boundary_functional, paid=boundary_paid),
        winner_nonmaximal_ordinary_upper=best_nonmaximal_ordinary,
        unchanged_tariff_ordinary_shortfall=rate + GUARD - unchanged,
        proof_scope="fixed recurring cap and height domains, fixed directed debits and guard, fixed clock model",
        verified_archive_source_paths=hashes,
    ), default=str, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
