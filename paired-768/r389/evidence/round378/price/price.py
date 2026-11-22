"""Reprice the unchanged #8057 physical packet census using its exact edge loss."""

from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from math import isqrt
import json
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

HEAD = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
WEIGHTED = "research/frequency-weighted-native-multiplier"
SOURCE = "research/tiered-native-multiplier/source"
PEER = {
    f"{WEIGHTED}/RESULT.json": "2f4faa6648592f589df22a8a0a07ba6856d20786294a44a7776c7d6e0efa14a5",
    f"{WEIGHTED}/SOURCES.json": "01d9e6b6b28cd174800cadfb59f4f064b3844575da297d82e16eb19a0d11c868",
    f"{WEIGHTED}/receipt.py": "82d921fdc33006e2d356d8bf78f3c85777722322d716be44b42bc763a04c8095",
    f"{WEIGHTED}/positive_debit.py": "7320b6a4ef1320d765e9b41a9b1e286db83a1d36d96f46bee0bef37974e8b8d9",
    f"{WEIGHTED}/independent_price.py": "448811cdb4a2bdefd4f736c2bad81c2a833bde634bcf65498e05267b5ee7ead0",
    f"{SOURCE}/activation.py": "6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b",
    f"{SOURCE}/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    f"{SOURCE}/ordinary_clock.py": "91dcf0ef72dddbde998b80f3d8b30c8036de9ce97e06e2bbd9c4159bf292020d",
    f"{SOURCE}/installer.tar.gz": "6696459e2e3552f802e7caaaf93dc86c9bb6b62ee38631702bff2e3a8a9a481a",
}
CAMPAIGN = {
    "round367/independent/audit.py": "bc2a8de7028287d6c816b8caed9b2b686e2b50449b7e8f67d55cd5dd958f381c",
    "round368/primary/receipt.json": "e60a50062125f75613ac0423c98a3aa81be576d43ea09193c1a24e78ba919b49",
    "round368/independent/support.py": "e510f6fd1e561213cf68243856d8aec12b862088114d55f0ae30da43dfb8e599",
    "round375/unsplit-frontier/screen.py": "a6b35438f271200b43efc2868e2bceb290331f24f06fae8779fd250a7d6baff4",
    "round376/audit/receipt.json": "5d892761adc42cb9bfea1187f06127b7260b8d2968105dc74ade5a61074c3bb5",
}
C = Q(17145637167, 2**42)
D = Q(65000, 524288)
OLD_D = Q(65081, 524288)
BIT = Q(4391986206293, 2**50)
ETA = Q(39, 10000)
K = Q(".00389821030")
G = Q(1, 10**18)
UNIT = 2**112


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pin(root, pins):
    for path, expected in pins.items():
        need(sha256((root / path).read_bytes()).hexdigest() == expected, path)


def ceiling(n):
    return -(-n.numerator // n.denominator)


@cache
def dyadic_112(rank, exponent):
    """Reconstruct canonical 112-bit masses independently of the peer emitter."""
    if rank == Q(1, 2):
        a, b = dyadic_112(2, exponent)
        return UNIT * UNIT // b, ceiling(Q(UNIT * UNIT, a))
    need(rank.denominator == 1 and 0 < exponent < 1
         and exponent.denominator.bit_count() == 1, "Exact declared grade")
    low = high = UNIT
    root_lo = root_hi = int(rank) * UNIT
    for bit in range(exponent.denominator.bit_length() - 2, -1, -1):
        root_lo = isqrt(root_lo * UNIT)
        root_hi = 1 + isqrt(root_hi * UNIT - 1)
        if exponent.numerator >> bit & 1:
            low = low * root_lo // UNIT
            high = ceiling(Q(high * root_hi, UNIT))
    return low, high


def verify(root, peer):
    need(subprocess.check_output(["git", "-C", str(peer), "rev-parse", "HEAD"],
                                 text=True).strip() == HEAD, "Pinned scientific peer")
    pin(peer, PEER)
    pin(root, CAMPAIGN)
    source = json.loads((root / "round368/primary/receipt.json").read_bytes())
    history = json.loads((peer / WEIGHTED / "RESULT.json").read_bytes())
    roots = runpy.run_path(str(root / "round375/unsplit-frontier/screen.py"))
    unmix, weighted = roots["unmix"], roots["weighted"]
    t0, t1, targets = weighted(unmix(source["source_targets"]))
    p0, p1, paid = weighted(unmix(source["source_paid"]), 1008)
    need([sum(t0.values()), sum(t1.values())] == history["gaussian"]["real_targets"] and
         [sum(p0.values()), sum(p1.values())] == history["gaussian"]["real_loans"], "Real labels")
    need(sum(targets.values()) == 4787328 and sum(paid.values()) == 25623696, "Weighted labels")
    t = 1 - C
    target_mass = {r: n * dyadic_112(r, t)[0] for r, n in targets.items()}
    paid_mass = {r: n * dyadic_112(r, t)[1] for r, n in paid.items()}
    target_total, paid_total = sum(target_mass.values()), sum(paid_mass.values())
    need(1 - Q(paid_total, target_total) == Q(history["gaussian"]["directed_margin"]),
         "Whole archived signed raw margin exactly reproduced")
    intersections = runpy.run_path(str(root / "round368/independent/support.py"))["quantile_cells"]
    cells = intersections(target_mass, paid_mass)
    need(len(cells) == 51 and cells[112, 258] == 1, "51 grade couplings and actual first placement")
    weights = 1, 90
    typed = {}
    rows, loads = defaultdict(Q), defaultdict(Q)
    for (r, k), share in cells.items():
        for a, payer in enumerate((p0, p1)):
            for b, recipient in enumerate((t0, t1)):
                if not (payer[r] and recipient[k]):
                    continue
                single = share * weights[b] / targets[k]
                typed[a, r, b, k] = single
                rows[a, r] += single * recipient[k]
                loads[b, k] += weights[a] * payer[r] * single * Q(paid_mass[r], paid[r])
    need(len(typed) == 88 and min(typed.values()) == Q(history["gaussian"]["min_individual_share"]),
         "Archive matches every typed support index and minimum share")
    need(all(v == 1 for v in rows.values()) and
         all(0 < v <= weights[b] * Q(target_mass[k], targets[k])
             for (b, k), v in loads.items()) and typed[1, 112, 1, 258] == Q(1, 624),
         "Every actual owner is funded")
    power = cache(runpy.run_path(str(root / "round367/independent/audit.py"))["power_bounds"])
    coarse = Q()
    psi = Q()
    for (r, k), share in cells.items():
        coefficient = paid[r] * share * r
        u = Q(k-r, k+r)
        coarse += coefficient * 2 * (u + u**3 / 3 + u**5 / 5)
        ratio = Q(k, r)
        root_ratio_lo = power(ratio.numerator, C)[0] / power(ratio.denominator, C)[1]
        psi += coefficient * (root_ratio_lo - 1) / C
    need(coarse == Q(history["gaussian"]["finite_loss"]["psi_lower"]), "Identical peer grade fractions")
    axes = sum(k * n for k, n in targets.items())
    fringe = 10 * axes / (t * psi)
    need(axes == 135150528 and psi > Q("184971191.2157") and fringe < Q("7.335168"),
         "Stronger exact-edge loss")
    delta = Q(1, 2**128)
    factor = ((1 + delta) * (1 + Q(4 * 258, 1024 * 306))
              * power(1024 * 306 * 2048, C)[1] * (1 + fringe / 2048 + delta)
              / (1 - delta)**4)
    gap = power(2, D)[0] - factor
    need(gap > 0 and D < OLD_D, "Strict directed debit payment")

    path = peer / SOURCE
    banks = runpy.run_path(str(path / "activation.py"))
    qualify = runpy.run_path(str(path / "outer_budget.py"))["qualify"]
    bill = runpy.run_path(str(path / "ordinary_clock.py"))
    profiles = (((3000, 3080), 1024, Q(".00345")),
                ((8192, 129414, 524349), 483871, K))
    out = {}
    for name, (heights, h, k) in zip(("entry", "terminal"), profiles, strict=True):
        profile = SimpleNamespace(rank_logs=heights, complex_log=h, eta=ETA)
        stock = banks["resource_receipt"](profile)
        activation = stock["public_exponent_A"]
        booked, boxes = Q(), []
        for i, H in enumerate(heights):
            cap = min(ETA, (249 * (BIT - Q(11, 8 * H)) + booked) / 250)
            next_rate = k + 5*G if i == len(heights) - 1 else Q(int(cap * 10**21) - 1, 10**21)
            need(booked < next_rate < cap, "Every ordinary stage is strictly funded")
            boxes.append((str(next_rate), str(cap - next_rate)))
            booked = next_rate
        signed = qualify(k, G, booked, C-D/h)
        if min(heights) >= 8192:
            bound = 128 + 320*sum(heights)
            additions = []
        else:
            local = bill["first_stage_bound"](ETA), bill["polynomial_to_fibre_bound"]()
            additions = [max(0, e-944*H) for e, H in zip(local, heights, strict=True)]
            bound = 57 + 16384*sum(heights) + sum(additions)
        # Reproduce the signed selector's extent and side picker in integer arithmetic.
        minimum = 128 * (4 * (activation + 2) + 6)
        q = (6 * minimum - 1).bit_length()
        need(activation - q >= (6 * activation).bit_length(), "Controller dyadic gap")
        largest = ((1 << q) + 5) // 6
        geometry = {"first_public_offset": (-pow(2, activation, 6)) % 6,
                    "first_extent_bits_minus_b": 4 - activation,
                    "last_extent_bits_minus_b": 5 - activation,
                    "minimum_width": minimum, "log2_axis_count": activation - q,
                    "largest_axis_width": largest,
                    "private_clock_log2_upper": 1024*(largest + activation + 68) + activation + 1,
                    "dense_root_entry_log2": 2*largest}
        out[name] = {"kappa": str(k), "ordinary_H": heights, "gaussian_H": h,
                     "ordinary_rates_and_slack": boxes, "stock": stock,
                     "geometry": geometry, "signed": signed,
                     "ordinary_local_additions": additions, "log2_B": bound,
                     "log2_C": max(84500001, 1602 + 220*h + bound)}
    for label in ("entry", "terminal"):
        need(out[label]["log2_C"] - (0 if label == "entry" else 61 * 320)
             == history[label]["log2_C"], "Recurring clock matches inherited accounting")
    premium = ceiling((K - Q(out["entry"]["kappa"])) * out["terminal"]["stock"]["public_exponent_A"])
    complete = 1 + max(out["entry"]["log2_C"] + premium, out["terminal"]["log2_C"])
    r376 = json.loads((root / "round376/audit/receipt.json").read_bytes())
    peer8058 = Q(r376["candidate_kappa"])
    allowance = r376["funding"]["terminal"]
    ceiling8058 = peer8058 + min(Q(allowance["ordinary_gap"]), Q(allowance["gaussian_gap"]))
    need(K > ceiling8058, "Strict separation from #8058's installed ceiling")
    return {
        "status": "VIABLE_PRICE_ONLY",
        "input_sha256": {"peer": PEER, "campaign": CAMPAIGN},
        "predecessor_head": HEAD,
        "comparison_8058_head": "4ff66ca09aa7727768aeaf24ac444e69675804de",
        "comparison_8058": str(peer8058), "installed_ceiling_8058": str(ceiling8058),
        "delta_over_8058": str(K - peer8058), "delta_over_8058_ceiling": str(K - ceiling8058),
        "exact_percent_over_8058": str(100*(K-peer8058)/peer8058),
        "paid_shape": {"weights": weights, "widths": [1, 2], "splits": 1008, "lower": 2048,
                       "grade_cells": len(cells), "typed_cells": len(typed),
                       "first_rotated_root_share": str(typed[1, 112, 1, 258]),
                       "same_literal_grade_coupling": True},
        "gaussian": {"trial": str(C), "debit": str(D),
                     "directed_psi_floor": "184971191.2157", "fringe_upper": "7.335168",
                     "directed_factor_headroom": str(Q(int(gap*10**12), 10**12))},
        "profiles": out, "entry_surcharge_bits": premium, "complete_log2_C": complete,
        "setup_bound": "pending new literal installed tape receipt",
    }


def main():
    cli = ArgumentParser(description=__doc__)
    for n in ("root", "peer", "out"):
        cli.add_argument("--" + n, type=Path, required=True)
    cli.add_argument("--child", action="store_true")
    a = cli.parse_args()
    if a.child:
        data = verify(a.root, a.peer)
        with a.out.open("x") as f:
            f.write(json.dumps(data, sort_keys=True, indent=2) + "\n")
    else:
        subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]],
                       timeout=60, check=True)


if __name__ == "__main__":
    main()
