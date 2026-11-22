"""Screen one type-zero last-rank-one unsplit with all other source shapes fixed."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha1, sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys

HEAD = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
PEER_DIR = "research/frequency-weighted-native-multiplier"
PEER_PINS = {
    f"{PEER_DIR}/RESULT.json": "c7ed01eff900b13d3cf70fc9b7c52daad598a41c",
    f"{PEER_DIR}/SOURCES.json": "2edf3073fc3daddcce4ac8e9aff6fd38dcc5aaf0",
    f"{PEER_DIR}/grades.py": "82b8edb65553440e2a7d2083f8397f2b86d8994b",
    f"{PEER_DIR}/positive_debit.py": "66daca9a8e7df3c54ece2bd27b8d1a20c800b2c5",
    f"{PEER_DIR}/typed_raw.py": "1797e260bbd769e895d7ceea3e0bbd03850189f7",
    f"{PEER_DIR}/typed_transport.py": "c58740b3b08b022f44de6b4a4b7d75032818fb7e",
}
ROOT_PINS = {
    "round368/primary/receipt.json": "e60a50062125f75613ac0423c98a3aa81be576d43ea09193c1a24e78ba919b49",
    "round368/independent/support.py": "e510f6fd1e561213cf68243856d8aec12b862088114d55f0ae30da43dfb8e599",
    "round367/independent/audit.py": "bc2a8de7028287d6c816b8caed9b2b686e2b50449b7e8f67d55cd5dd958f381c",
}
OLD_C = Q(17145637167, 2**42)
C = Q(17145637167 + 128, 2**42)
K = Q(".0038982100040")
NEW_H = 524289
OLD_H = 524288
G = Q(1, 10**18)
BINARY_C = Q(4391986206293, 2**50)
GAUSSIAN_H = 483871
DEBIT = Q(65081, 2**19)
HALF = Q(1, 2)
UNIT = 2**112


def need(predicate, why):
    if not predicate:
        raise ValueError(why)


def unmix(rows):
    """Invert count(r)=base(r)+base(r/8), with the split adjustment removed."""
    mixed = Counter({Q(rank): count for rank, count in rows})
    if HALF in mixed:
        need(mixed.pop(HALF) == 2016, "Pinned type-zero baseline split census")
        mixed[1] += 1008
    base = Counter()
    for rank in sorted(mixed):
        value = mixed[rank] - base[rank / 8]
        need(value >= 0, "Extract exact base count from two scales")
        if value:
            base[rank] = value
    remixed = base.copy()
    remixed.update({8 * rank: count for rank, count in base.items()})
    need(remixed == mixed, "Invert every baseline rank")
    return base


def weighted(base, splits=0):
    first = base.copy()
    if splits:
        first[1] -= splits
        first[HALF] = 2 * splits
    second = Counter({2 * rank: count for rank, count in base.items()})
    return first, second, first + Counter({rank: 90 * count for rank, count in second.items()})


def screen(root, peer):
    need(subprocess.check_output(["git", "-C", str(peer), "rev-parse", "HEAD"],
                                 text=True).strip() == HEAD, "Exact peer checkout")
    for path, expected in PEER_PINS.items():
        data = (peer / path).read_bytes()
        header = f"blob {len(data)}\0".encode()
        need(sha1(header + data).hexdigest() == expected, f"Peer object {path}")
    for path, expected in ROOT_PINS.items():
        need(sha256((root / path).read_bytes()).hexdigest() == expected, f"Receipt {path}")
    old = json.loads((peer / PEER_DIR / "RESULT.json").read_bytes())
    lit = json.loads((root / "round368/primary/receipt.json").read_bytes())
    need(lit["1006_literal_touched_paid_clock_and_tag"][-1]
         == [1593, ["return", 9977, 0, 91966]], "Last validated split tag")
    target = unmix(lit["source_targets"])
    paid = unmix(lit["source_paid"])
    t0, t1, T = weighted(target)
    p0, p1, P = weighted(paid, 1008)
    v0, v1, V = weighted(paid, 1007)
    need(sum(t0.values()) == sum(t1.values()) == 52608 and sum(T.values()) == 4787328
         and sum(p0.values()) == 282576 and sum(p1.values()) == 281568
         and sum(P.values()) == 25623696 and sum(V.values()) == 25623695, "Signed invoice")
    need(P[HALF] - V[HALF] == 2 and V[1] - P[1] == 1 and v1 == p1,
         "Only the specified type-zero paid request changes")
    bounds = cache(runpy.run_path(str(root / "round367/independent/audit.py"))["power_bounds"])
    intersect = runpy.run_path(str(root / "round368/independent/support.py"))["quantile_cells"]

    def masses(hr, c, paid_side):
        result = {}
        for rank, n in hr.items():
            lo, hi = bounds(rank, 1 - c)
            result[rank] = n * ((1 + int(hi * UNIT)) if paid_side else int(lo * UNIT))
        return result

    def evaluate(c, active, variants):
        t = masses(T, c, False)
        p = masses(active, c, True)
        difference = Q(sum(t.values()) - sum(p.values()), UNIT)
        scaled = Q(sum(p.values()), sum(t.values()))
        if difference <= 0:
            return {"raw_margin": str(difference), "positive": False}
        cells = intersect(t, p)
        types = {}
        rows, loads = defaultdict(Q), defaultdict(Q)
        for (r, k), share in cells.items():
            for a, payer in enumerate(variants):
                if r not in payer:
                    continue
                for b, recipient in enumerate((t0, t1)):
                    if k not in recipient:
                        continue
                    single = share * (1, 90)[b] / T[k]
                    types[a, r, b, k] = single
                    rows[a, r] += single * recipient[k]
                    loads[b, k] += single * (1, 90)[a] * payer[r] * Q(p[r], active[r])
        need(all(x == 1 for x in rows.values()), "Every typed row restores its mass")
        need(all(0 < total <= (1, 90)[b] * Q(t[k], T[k])
                 for (b, k), total in loads.items()), "Every retained owner has funded capacity")
        need(types[1, 112, 1, 258] == Q(1, 624), "Same mandatory first placement cell")
        first = Q(p[HALF] - t[1] * scaled, UNIT)
        psi = Q()
        for (r, k), share in cells.items():
            z = Q(k - r, k + r)
            psi += active[r] * share * r * 2 * (z + z**3 / 3 + z**5 / 5)
        target_axes = sum(k * n for k, n in T.items())
        need(target_axes == 135150528, "Same physical productive size")
        fringe = 10 * target_axes / ((1 - c) * psi)
        ambient, lower, delta = 306, 2048, Q(1, 2**128)
        finite = ((1 + delta) * (1 + Q(4 * 258, 1024 * ambient))
                  * bounds(1024 * ambient * lower, c)[1] * (1 + fringe / lower + delta)
                  / (1 - delta)**4)
        need(finite < bounds(2, DEBIT)[0], "Complete fixed Gaussian debit")
        need(fringe < Q(7579, 1000), "Existing fringe guard")
        need(scaled > Q(99, 100) and 1 - c > Q(996, 1000), "Existing recursive margins")
        need(min(types.values()) > Q(1, 2**26), "Existing minimum typed transport share")
        maxbits = max(max(x.denominator.bit_length(), x.numerator.bit_length())
                      for x in cells.values())
        need(maxbits < 512, "Existing fraction-width envelope")
        return {"positive": True, "raw_margin": str(difference),
                "unit_eligible_surplus": str(first), "grade_cells": len(cells),
                "typed_cells": len(types), "max_fraction_bits": maxbits,
                "finite_debit": str(DEBIT), "min_individual_share": str(min(types.values())),
                "fringe_upper": str(fringe), "directed_psi_lower": str(psi),
                "keeps_historical_psi_guard": psi > Q(1790217668064, 10000)}

    baseline = evaluate(OLD_C, P, (p0, p1))
    need(baseline["positive"] and baseline["grade_cells"] == 51
         and baseline["typed_cells"] == 88 and Q(baseline["raw_margin"]) > 0,
         "Reconstruct the peer's 51/88 cells from independent linked grade census")
    # To retire the old tape, enclose its signed moment from above.
    old_upper = sum(n * bounds(rank, 1 - C)[1] for rank, n in T.items())
    old_upper -= sum(n * bounds(rank, 1 - C)[0] for rank, n in P.items())
    from decimal import Context, Decimal

    ctx = Context(prec=82)
    slope = Q()
    for rank in T.keys() | P.keys():
        if rank == 1:
            continue
        r = ctx.divide(Decimal(rank.numerator), Decimal(rank.denominator))
        log = ctx.ln(r)
        logs = Q(ctx.next_minus(log)), Q(ctx.next_plus(log))
        powers = (*bounds(rank, 1 - C), *bounds(rank, 1 - Q(".004")))
        slope += min((T[rank] - P[rank]) * power * log
                     for power in (min(powers), max(powers)) for log in logs)
    try:
        case = evaluate(C, V, (v0, v1))
    except ValueError as exc:
        case = {"positive": False, "first_blocker": str(exc)}
    prior = Q(old["terminal"]["ordinary_rates"][-2])

    def ordinary_ceiling(h):
        return (249 * (BINARY_C - Q(11, 8 * h)) + prior) / 250 - 5 * G

    old_gauss = OLD_C - DEBIT / GAUSSIAN_H - 5 * G
    new_gauss = C - DEBIT / GAUSSIAN_H - 5 * G
    funded = (K > max(ordinary_ceiling(OLD_H), old_gauss)
              and K < min(ordinary_ceiling(NEW_H), new_gauss))
    return {"peer": HEAD, "roots": ROOT_PINS, "peer_blobs": PEER_PINS,
            "scope": "R375 fallback, one type-zero paid return only",
            "last_original_paid_site": lit["1006_literal_touched_paid_clock_and_tag"][-1],
            "dyadic": str(C), "target": str(K), "terminal_H3": NEW_H,
            "old_installed_ordinary_ceiling": str(ordinary_ceiling(OLD_H)),
            "old_installed_gaussian_ceiling": str(old_gauss),
            "new_ordinary_ceiling": str(ordinary_ceiling(NEW_H)),
            "new_gaussian_ceiling": str(new_gauss), "baseline": baseline,
            "old_raw_upper_at_new_trial": str(old_upper),
            "old_negative_derivative_lower_through_point004": str(slope),
            "one_unsplit_at_trial": case, "complete_directed_budgets_pass": funded,
            "passes_one_case": funded and case["positive"] and old_upper < 0 and slope > 0,
            "pending": "Type-zero literal emitter and signed independent complete replay"}


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("root", "peer", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        args.out.write_text(json.dumps(screen(args.root, args.peer), indent=2,
                                       sort_keys=True) + "\n")
    else:
        result = subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]],
                                timeout=60)
        result.check_returncode()


if __name__ == "__main__":
    main()
