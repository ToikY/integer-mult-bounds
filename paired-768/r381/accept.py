"""Authenticate R381's literal weighted schedule and rederive the claimed price."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import runpy

PINS = {
    "round378/independent/accept.py": "001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round375/independent/coupling.py": "fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    "round366/gaussian/receipt.json": "9e1206f26d124f9f788a96ff43453195c4ae8c9b679acbf8a0ca132c80a5b7a1",
    "round380/price/receipt.json": "19299504743a95e14786310f96de73d850f698e2fd3f084b26758c3f9c9e3f9f",
    "round380/calendar/receipt.json": "09b1203a05ab1e679fd16f652ec93b7bfed8183fb450397f94234d4a0d65f3c4",
    "round381/build.log": "3cd53012b8db76a74f415c5e5e0afd7d6bd8989064251ab56bd4621b2c8d9970",
}
CAPSULE = {
    "prepare.py": "610541709f30ee19578da1825bfa47268a21760b7a121efd389f23e92bdb0f32",
    "RESULT.json": "1e5bbb53b1d373bd0499cfd3c2a4a9c4ff232058988cc0d23af6e053f48eb5fd",
}
PACKAGE = "research/frequency-weighted-native-multiplier/"
K0 = Q(".00389821030")
K = Q(".00389821033")
C = Q(17145637231, 2**42)
D = Q(65000, 2**19)
G = Q(1, 10**18)
U = 2**112
WEIGHTS = (8, 721)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def pin(path, digest):
    content = path.read_bytes()
    need(sha256(content).hexdigest() == digest, f"Wrong bytes at {path.name}")
    return content


def mix(histograms, weights):
    combined = Counter()
    for histogram, weight in zip(histograms, weights, strict=True):
        for grade, n in histogram.items():
            combined[grade] += weight * n
    return combined


def ceiling(q):
    return -(-q.numerator // q.denominator)


def power_area(left, right):
    """Directed lower mass for the actual nested fixture at n=8192."""
    grid = 2**(64 * (8192).bit_length())
    exponent = 1 - C

    def inverse(x):
        lo, hi = grid // x, -(-grid // x)
        a = b = grid
        bits = exponent.denominator.bit_length() - 1
        for bit in range(bits, -1, -1):
            if (exponent.numerator >> bit) & 1:
                a, b = a * lo // grid, -(-b * hi // grid)
            if bit:
                lo, hi = isqrt(lo * grid), 1 + isqrt(hi * grid - 1)
        return a, b

    a, _ = inverse(left)
    _, d = inverse(right)
    return Q((a-d) * 2**48, grid) / exponent


def verify_edits(capsule, baseline):
    pin(capsule / "prepare.py", CAPSULE["prepare.py"])
    edits = runpy.run_path(str(capsule / "prepare.py"))["EDITS"]
    expected = {"runtime.patch", "positive_debit.py", "receipt.py", "independent_price.py", "grades.py",
                "check_placement.py", "check_exterior.py", "check_nested.py", "check_ownership.py"}
    need(edits.keys() == expected, "exact literal edit family")
    need(edits["grades.py"] == (("WEIGHTS = (1, 90)", "WEIGHTS = (8, 721)"),), "frequency-only grade implementation")
    need(len(edits["runtime.patch"]) == 2 and any("17145637231" in b for _, b in edits["runtime.patch"]),
         "price and single height are the only runtime patch edits")
    for path, replacement in edits.items():
        text = baseline[PACKAGE + path].decode()
        for old, new in replacement:
            need(text.count(old) == 1, f"edits at unambiguous source locus {path}")
            text = text.replace(old, new)
    # These files own phase, ordered paid yields and transfer restoration.
    untouched = ("typed_raw.py", "typed_transport.py", "check_calendar.py", "check_raw.py")
    return {name: sha256(baseline[PACKAGE + name]).hexdigest() for name in untouched}


def capacities(census, routines, result, price, calendar, log):
    source = census["ranks"]
    source_t, source_p = [Counter({Q(k): v for k, v in source[key].items()}) for key in ("target", "paid")]
    source_p[1] += source_p.pop(Q(1, 2)) // 2
    t0, p0 = [routines["base_copy"](hist) for hist in (source_t, source_p)]
    tv = (t0, Counter({2*k: n for k, n in t0.items()}))
    pv = (p0.copy(), Counter({2*r: n for r, n in p0.items()}))
    pv[0][1] -= 1008
    pv[0][Q(1, 2)] = 2016
    need([(b.total(), a.total()) for a, b in zip(pv, tv)] ==
         [(52608, 282576), (52608, 281568)], "unchanged real type ports")
    t, p = mix(tv, WEIGHTS), mix(pv, WEIGHTS)
    need([t.total(), p.total()] == [38351232, 205271136] == calendar["weighted_targets_and_paid"],
         "all weighted tape positions")
    c0, p_old = mix(tv, (1, 90)), mix(pv, (1, 90))
    power = routines["power_interval"]
    lower_target = {k: n * power(k, 1-C)[0] for k, n in t.items()}
    upper_paid = {r: n * power(r, 1-C)[1] for r, n in p.items()}
    old_upper = Q(sum(n*power(k, 1-C)[1] for k, n in c0.items())
                  - sum(n*power(r, 1-C)[0] for r,n in p_old.items()), U)
    need(old_upper == Q(price["previous_raw_bound_at_trial"]) < 0, "old frequencies fail new raw trial")
    raw = Q(sum(lower_target.values()) - sum(upper_paid.values()), U)
    need(raw == Q(price["raw_margin_lower"]) > 0, "new raw payment")
    high_slack = Q(sum(x for k, x in lower_target.items() if k > 2)
                   - sum(x for r, x in upper_paid.items() if 5*r > 8), U)
    scaled_unit = Q(lower_target[1] * sum(upper_paid.values()), sum(lower_target.values()))
    unit_slack = Q(upper_paid[Q(1,2)] - scaled_unit, U)
    need(high_slack == Q(price["raw_high_cut_slack"]) > 0 and
         unit_slack == Q(price["normalized_unit_cut_slack"]) > 0, "both thin cuts")
    relative, cells = routines["allocate"](C, t, p)
    need(relative == Q(result["directed_margin"]) and len(cells) == 51, "same canonical allocation")
    per_owner = {}
    rows, load = defaultdict(Q), defaultdict(Q)
    for (r, k), share in cells.items():
        for a, payer in enumerate(pv):
            for b, receiver in enumerate(tv):
                if payer[r] and receiver[k]:
                    q = share * WEIGHTS[b] / t[k]
                    per_owner[a, r, b, k] = q
                    rows[a, r] += q * receiver[k]
                    load[b,k] += q * WEIGHTS[a] * payer[r] * Q(upper_paid[r], p[r])
    need(len(per_owner) == 88 and min(per_owner.values()) == Q(result["min_individual_share"]),
         "all typed allocations, owners and minimum shares")
    need(min(per_owner.values()) == Q(price["min_actual_share"]) > Q(1, 2**26), "independent minimum share")
    need(per_owner[1,112,1,258] == Q("1/624") == Q(price["slot_112_to_258_probability"]),
         "forced highest real exterior edge")
    need(all(rows[a,r] == 1 for a, inv in enumerate(pv) for r in inv), "all paid shares")
    need(all(0 < load[b,k] <= WEIGHTS[b]*Q(lower_target[k],t[k])
             for b, inv in enumerate(tv) for k in inv), "all productive owners")
    psi = Q()
    for (r, k), share in cells.items():
        edge = power(k, C)[0] * U // power(r, C)[1]
        need(edge > U, "strictly descending edge")
        psi += p[r] * share * r * (Q(edge, U)-1) / C
    loss = result["finite_loss"]
    need(psi == Q(loss["psi_lower"]) > Q("1481813402.4676"), "literal paid integral")
    axes = sum(k * n for k, n in t.items())
    need(axes == 1082697600 == loss["weighted_target_axes"] == calendar["exact_boundary_axis_sum"],
         "actual weighted boundary axes")
    fringe = 10 * axes / ((1-C) * psi)
    need(fringe == Q(loss["fringe"]) < Q("7.335168"), "complete opposite-side fringe")
    d = Q(1, 2**128)
    factor = ((1+d) * (1+Q(4*258,1024*306)) * Q(power(Q(1024*306*2048),C)[1], U)
              * (1+fringe/2048+d) / (1-d)**4)
    headroom = Q(power(Q(2),D)[0], U) - factor
    need(factor == Q(loss["upper_factor"]) and headroom > 0, "all finite losses")
    need((int(psi * 10**4), ceiling(fringe * 10**9), ceiling(factor * 10**12),
          int(headroom * 10**12)) ==
         tuple(calendar[key] for key in ("psi_lower_floor_1e4", "fringe_upper_1e9",
                                         "finite_factor_upper_1e12", "finite_factor_reserve_floor_1e12")),
         "all independently replayed finite calendar values")
    grant = (power_area(24, 26)*cells[1,2]*WEIGHTS[0]*WEIGHTS[1] / t[2]) // 1
    need(grant == 7206456401 and str(grant).encode() in log and b"PASS_NONZERO_INTERIOR" in log,
         "exact granted integer nested loan")
    return {"old_frequency_upper_at_new_trial": str(old_upper), "new_raw_margin_lower": str(raw),
            "real_nested_grant": grant, "typed_cells": len(per_owner), "same_individual_top_share": "1/624"}


def check(root, capsule):
    data = {name: pin(root/name, digest) for name,digest in PINS.items()}
    original = runpy.run_path(str(root / next(iter(PINS))))
    baseline = original["restore_reference"](capsule)
    pinned_result = pin(capsule / "RESULT.json", CAPSULE["RESULT.json"])
    result = json.loads(pinned_result)
    price, calendar = [json.loads(data[f"round380/{m}/receipt.json"]) for m in ("price", "calendar")]
    prices = capacities(json.loads(data["round366/gaussian/receipt.json"]),
                        runpy.run_path(str(root / "round375/independent/coupling.py")),
                        result["gaussian"], price, calendar, data["round381/build.log"])
    phases = verify_edits(capsule, baseline)
    need(result["gaussian"]["weights"] == [8,721] == calendar["integer_weights"], "actual frequencies")
    need(result["gaussian"]["finite_loss"]["lower_band"] == 2048, "calendar floor")
    need(sum(WEIGHTS) == 729 and Q(729)/((1-C)*1024) + Q(2, 2**(5*1024)) < 2,
         "729 openings fit conservative calendar bound")
    for name, heights, hg, k in (("entry", [3000,3080], 1024, Q(".00345")),
                                 ("terminal", [8192,129414,524355], 483871, K)):
        profile, prior_price = result[name], price["profiles"][name]
        gap = original["ordinary"](profile, heights, k)
        need(gap == Q(prior_price["ordinary_stage_slacks"][-1]), "whole ordinary price")
        need(profile["stock"] == prior_price["stock"] and profile["signed"] == prior_price["signed"],
             "both exact independent tier receipts")
        need(Q(profile["gaussian_rate"]) == C-D/hg, "fixed debit charged at actual height")
    need(K-Q(price["prior_installed_cap"]) > 0 and K-K0 == Q(price["delta_kappa"]), "complete comparison")
    clock = result["complete_log2_C"]
    need(clock == 318280871 == 1+max(result["terminal"]["log2_C"], result["entry"]["log2_C"]+514),
         "complete charged recurring clock")
    need(result["native_setup_transition_upper"] < 2**228 and result["native_setup_grade_actions"] == 269057152,
         "native fixed setup")
    return {"pinned_evidence": PINS, "literal_pins": CAPSULE, "verified_original_archive_files": len(baseline),
            "identical_phase_and_calendar_implementation_hashes": phases, "directed_and_nested": prices,
            "opening_total": 729, "complete_log2_C": clock, "delta_vs_8059": str(K-K0),
            "status": "LITERAL PRICE AND EXISTING NESTED RECEIPT PASS; REGISTERED SUITE SEPARATE"}


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--capsule", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = check(args.inputs, args.capsule)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
