#!/usr/bin/env python3
"""Exact r=16 invoice comparison for the power-of-two cubic repair.

The checker recomputes the displayed gap from the pinned schedule. It does
not import predecessor verifiers and it does not assign a physical backend.
"""

from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
RESULT = PKG / "RESULT.json"

SENTENCES = {
    "research/dyadic-cubic-repair/sources/pr6200-PROOF.md":
        "No numerical backend price is substituted here.",
    "research/dyadic-cubic-repair/PROOF.md":
        "No such backend is supplied.",
    "research/cubic-pow2-repair/README.md":
        "Fewer repair queries or shears alone do not prove a cheaper execution.",
    "research/cubic-pow2-repair/PROOF.md":
        "It does not prove the two-shear count optimal, compare physical tariffs",
}


def coeffs(r):
    r = Fraction(r)
    return (
        (r - 1) * (r - 2) / (6 * r),
        2 * (r * r - 1) / (3 * r),
        -(r - 1) * (5 * r + 2) / (6 * r),
    )


def cube_terms(weight, slope):
    weight = Fraction(weight)
    slope = Fraction(slope)
    return (
        weight,
        3 * weight * slope,
        3 * weight * slope * slope,
        weight * slope ** 3,
    )


def add_terms(*parts):
    total = [Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
    for part in parts:
        for index, value in enumerate(part):
            total[index] += value
    return tuple(total)


def defect_terms(r):
    r = Fraction(r)
    s1 = r * (r - 1) / 2
    s2 = r * (r - 1) * (2 * r - 1) / 6
    return (Fraction(0), 3 * s1, 3 * s2, s1 * s1)


def sigma(coefficient):
    """Binary synthesis length: one arbitrary shift, plus popcount(odd)-1 adds."""
    value = abs(Fraction(coefficient))
    if value == 0:
        raise ValueError("zero coefficient has no synthesis length")
    numerator, denominator = value.numerator, value.denominator
    valuation = 0
    while denominator % 2 == 0:
        denominator //= 2
        valuation += 1
    if denominator != 1:
        raise ValueError("coefficient is not dyadic: " + str(coefficient))
    odd = numerator
    while odd % 2 == 0:
        odd //= 2
        valuation -= 1
    shift = 1 if valuation != 0 else 0
    return shift + odd.bit_count() - 1


def identity_holds(r):
    c1, c2, c0 = coeffs(r)
    right = add_terms(
        cube_terms(c1, r),
        cube_terms(c2, Fraction(r, 2)),
        cube_terms(c0, 0),
    )
    return right == defect_terms(r)


def replay(r, incoming_y, incoming_a, incoming_b, c1=None, c2=None, c0=None, shears=2):
    y = Fraction(incoming_y)
    a = Fraction(incoming_a)
    b = Fraction(incoming_b)
    for _ in range(r):
        y += a ** 3
        a += b
    defaults = coeffs(r)
    if c1 is None:
        c1 = defaults[0]
    if c2 is None:
        c2 = defaults[1]
    if c0 is None:
        c0 = defaults[2]
    half = Fraction(r, 2)
    weights = (c1, c2, c0)
    for index in range(3):
        y -= weights[index] * a ** 3
        if index < shears:
            a -= half * b
    return y, a, b


def blind_gap(r, query, shear):
    return 3 * query + 2 * shear - r * shear


def weighted_gap(r, query, shear, unit):
    c1, c2, c0 = coeffs(r)
    repair = sum(query + sigma(weight) * unit for weight in (c1, c2, c0))
    repair += 2 * (shear + sigma(Fraction(r, 2)) * unit)
    eager = r * (shear + sigma(-1) * unit)
    return repair - eager


def receipt():
    r = 16
    c1, c2, c0 = coeffs(r)
    if not identity_holds(r):
        raise SystemExit("r=16 identity failed")
    for control in (4, 8, 32, 64):
        if not identity_holds(control):
            raise SystemExit("identity failed at r=" + str(control))
    points = (
        (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (5, -3, 2), (-7, 4, -1), (9, 8, -8), (3, 1, 1),
    )
    for y0, a0, b0 in points:
        y, a, b = replay(r, y0, a0, b0)
        if (y, a, b) != (y0 + r * Fraction(a0) ** 3, Fraction(a0), Fraction(b0)):
            raise SystemExit("schedule missed eager endpoint at " + repr((y0, a0, b0)))
        y, a, b = replay(4, y0, a0, b0)
        if (y, a, b) != (y0 + 4 * Fraction(a0) ** 3, Fraction(a0), Fraction(b0)):
            raise SystemExit("r=4 control schedule failed")
    bad_y, bad_a, bad_b = replay(r, 0, 1, 1, c1=c1 + 1)
    if (bad_y, bad_a, bad_b) == (r * 1, 1, 1):
        raise SystemExit("perturbed weight was not rejected")
    short_y, short_a, short_b = replay(r, 0, 1, 1, shears=1)
    if short_a == 1 and short_y == r:
        raise SystemExit("dropped shear was not rejected")
    if sigma(1) != 0 or sigma(-1) != 0 or sigma(8) != 1:
        raise SystemExit("unit or power-of-two synthesis length changed")
    if (sigma(c1), sigma(c2), sigma(abs(c0))) != (3, 4, 5):
        raise SystemExit("r=16 synthesis lengths changed")
    query, shear = Fraction(1), Fraction(1)
    if blind_gap(16, query, shear) != -11:
        raise SystemExit("blind unit gap is not -11")
    if blind_gap(4, query, shear) != 1:
        raise SystemExit("blind r=4 gap is not +1")
    if weighted_gap(16, query, shear, shear) != 3:
        raise SystemExit("weighted unit gap is not +3")
    if weighted_gap(16, query, shear, 0) != blind_gap(16, query, shear):
        raise SystemExit("zero synthesis charge did not recover the blind gap")
    present = {}
    for path, sentence in SENTENCES.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        folded = " ".join(text.split())
        if sentence not in folded:
            raise SystemExit("missing pinned sentence in " + path)
        present[path] = True
        for needle in ("Q_{35/16}", "Q_35/16", "L_{-8} =", "L_-8 ="):
            if needle in text:
                raise SystemExit("unexpected instantiated tariff " + needle + " in " + path)
    return {
        "r": 16,
        "coefficients": {"c1": "35/16", "c2": "85/8", "c0": "-205/16"},
        "checked_coefficients": [str(c1), str(c2), str(c0)],
        "sigma": {"35/16": 3, "85/8": 4, "205/16": 5, "8": 1, "1": 0},
        "blind_gap_over_shear": "(3*q - 14*l)/l",
        "blind_threshold_q_over_l": "14/3",
        "blind_unit_gap": "-11",
        "blind_r4_unit_gap": "1",
        "weighted_gap": "3*q + 14*u - 14*l",
        "weighted_unit_gap_when_u_equals_l_and_q_equals_l": "3",
        "endpoint_trials": len(points),
        "identity_arities": [4, 8, 16, 32, 64],
        "pinned_sentences_present": present,
        "status": "PASS_CUBIC_R16_REPAIR_INVOICE",
    }


def main():
    payload = receipt()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        RESULT.write_text(encoded, encoding="utf-8")
    elif not RESULT.is_file() or RESULT.read_text(encoding="utf-8") != encoded:
        raise SystemExit("RESULT.json does not match recomputation; rerun with --write")
    print(payload["status"])


if __name__ == "__main__":
    main()
