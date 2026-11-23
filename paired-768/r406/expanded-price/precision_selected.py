"""Reconstruct the selector geometry, precision and smaller-prefix charge for one selected profile."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil
from pathlib import Path

RECEIPT_SHA = "fb3e558e9a48a0e653c810c247d01b28ccf04555c9d0abb62ba9cd416a58dae6"


def precision(receipt):
    heights = receipt["ordinary_heights"]
    g = receipt["gaussian_height"]
    rate = Q(receipt["trial_kappa"])
    eta, c_o, c_g = Q(39, 10000), Q(4391986206293, 2**50), Q(17145637307, 2**42)
    guard = Q(5, 10**18)
    assert eta > Q(1, 258) and eta * min(heights) - 1 > 30
    assert 2660000 * (30 + 2) < 2**30 and 2 * (30 + 2) >= 30 + 3
    cuts = []
    for h in heights:
        cuts.append(max(ceil(Q(250 * (h + 64), 249)), cuts[-1]+h+64 if cuts else 0))
    assert cuts == receipt["binary_cuts"] and all(c + 2 < h for c, h in zip(cuts, heights[1:]))
    target = cuts[-1] + g + 102
    first_s = next(s for s in range(target, target + 500) if s - 7 * (s - 1).bit_length() >= target)
    exponent, offset = first_s - 1, (-pow(2, first_s - 1, 6)) % 6
    assert first_s - 1 - 7 * (first_s - 2).bit_length() < target
    assert [exponent, offset] == receipt["activation"]
    assert ceil((rate-Q(".00345")) * exponent) == receipt["entry_conversion"]
    # Reprice the entry prefixes from the original polynomial loop.
    degree = 20 * 253
    surcharges = []
    for h, padding, term in ((3000, 4, 2 * degree), (3080, 259, 258 * degree)):
        surcharges.append(max(0, 20 * 24 + degree * padding + 2 + term * (term - 1).bit_length() - 944 * h))
    assert surcharges == [0, 25818582]
    entry_cost = 1602 + 220 * 1024 + 40 + 34 + 16384 * (3000 + 3080) + sum(surcharges)
    assert entry_cost == receipt["entry_log2_c"]
    assert receipt["recurring_log2_C"] == 1 + max(
        84500001, entry_cost + receipt["entry_conversion"],
        1602 + 220 * g + 155 + 320 * sum(heights)
    )
    catalog_width = 1 << 38
    datum = 2 * catalog_width + 2
    scalar = 2**16 * (datum + 4) * (7 * datum + 9) + 8 * 2**16 * (datum + 4)**2
    lookup = 4 * catalog_width * 2**68 * 8 * 512 * 128
    setup = (2**68 + 1) * (lookup + scalar + 2**120) * 2**32
    assert 17**16 * 10**(21*16) < 2**1182
    assert max(g,*heights).bit_length() == 20 and len(heights)+2+2 == 7 and setup < 2**228
    minimum_window = 128 * (4 * (first_s + 1) + 6)
    axis_degree = (6 * minimum_window - 1).bit_length()
    assert exponent - axis_degree >= (6 * exponent).bit_length()
    axis_count = 1 << (exponent - axis_degree)
    public = (1 << exponent) + offset
    block, remainder = divmod(public, 6)
    assert not remainder and public - 6 < 1 << exponent <= public
    endpoints = []
    for extent in (block + 4 - exponent, block + 5 - exponent):
        assert (extent // minimum_window).bit_length() == exponent - axis_degree + 1
        width = ceil(Q(extent, axis_count))
        active = max(1, axis_count // (1024 * (public + 1).bit_length()))
        rounds = 20000 * (axis_count + 1) * (width + 2)**6 + 2 * axis_count
        bits = (public + 67 + 32768 * active * (width + 6)
                + 4 * (rounds * (axis_count + 1)).bit_length()
                + (axis_count + 1).bit_length())
        assert public < bits < 1 << (exponent + 1)
        endpoints.append(dict(width=width, precision_bits=bits.bit_length(),
                              precision_sha256=sha256(bits.to_bytes((bits.bit_length()+7)//8,"big")).hexdigest()))
    widest = max(item["width"] for item in endpoints)
    assert widest == ceil(Q(1 << axis_degree, 6))
    carrier = 1 << g
    upper = 2 * (carrier // (1724 * 306))
    assert upper > 2 * (carrier // (2048 * 306)) and 4 * 258 * (upper - 8) < carrier
    assert upper % 2 == 0 and 68 + 83 * g < 92 * g
    ordinary_funding = ceil(Q(receipt["ordinary_debit"]) / (c_o-rate-guard))
    gaussian_funding = ceil(Q(receipt["gaussian_debit"]) / (c_g-rate-guard))
    assert ordinary_funding <= sum(heights) and gaussian_funding == g
    return {
        "funding_heights": [ordinary_funding, gaussian_funding],
        "initial_s": first_s, "axis_degree": axis_degree, "public_axis_count_log2": exponent-axis_degree,
        "private_scalar_clock_upper": 1024 * (widest + first_s + 67) + first_s,
        "entry_prefix_surcharges": surcharges, "entry_log2_C_before_conversion": entry_cost,
        "actual_precision_endpoints": endpoints, "setup_transition_upper": setup,
        "scope": "exact arithmetic once at the selected profile; no scientific replay",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    source = args.receipt.read_bytes()
    assert sha256(source).hexdigest() == RECEIPT_SHA
    print(json.dumps(precision(json.loads(source)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
