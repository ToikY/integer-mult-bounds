"""Directed arithmetic for one weighted physical schedule at birth counts (8, 721)."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

PEER = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
BENCHMARK = "c34c958114297cdbd1f493666342b8859531d40d"
PINS = {
    "round378/price/price.py": "6ddddfd71283bfe375cc8c094a2153c7be20537be5b54823347f79d8d07b6be0",
    "round378/price/receipt.json": "1a3600d7f62b82986ea752a0f285be28a551b44b8e05e91a40e09642238ccbc7",
}
C = Q(17145637167 + 64, 2**42)
K = Q(".00389821033")
K0 = Q(".00389821030")
DEBIT = Q(65000, 524288)
BINARY = Q(4391986206293, 2**50)
ETA = Q(39, 10000)
G = Q(1, 10**18)
WEIGHTS = (8, 721)
H = 483871
L = 2048
WIDTH = 306
UNIT = 2**112


def need(ok, message):
    if not ok:
        raise ValueError(message)


def ceil(q):
    return -(-q.numerator // q.denominator)


def mix(variants, weights):
    total = Counter()
    for x, weight in zip(variants, weights, strict=True):
        total.update({r: weight * n for r, n in x.items()})
    return total


def compare(root, peer):
    for file, known in PINS.items():
        need(sha256((root / file).read_bytes()).hexdigest() == known, file)
    previous = runpy.run_path(str(root / "round378/price/price.py"))
    previous["pin"](root, previous["CAMPAIGN"])
    previous["pin"](peer, previous["PEER"])
    need(subprocess.check_output(["git", "-C", str(peer), "rev-parse", "HEAD"],
                                 text=True).strip() == PEER, "Pinned mathematical ancestry")
    prior = json.loads((root / "round378/price/receipt.json").read_bytes())
    terminal = prior["profiles"]["terminal"]
    old_upper = K0 + min(Q(terminal["ordinary_rates_and_slack"][-1][1]),
                        Q(terminal["signed"]["positive_margin"]))
    need(Q(terminal["kappa"]) == K0 and Q(prior["gaussian"]["debit"]) == DEBIT
         and K > old_upper, "Beats exact benchmark ceiling")
    r368 = json.loads((root / "round368/primary/receipt.json").read_bytes())
    functions = runpy.run_path(str(root / "round375/unsplit-frontier/screen.py"))
    unmix, weighted = functions["unmix"], functions["weighted"]
    Tv = weighted(unmix(r368["source_targets"]))[:2]
    Pv = weighted(unmix(r368["source_paid"]), 1008)[:2]
    need([sum(v.values()) for v in Tv] == [52608, 52608] and
         [sum(v.values()) for v in Pv] == [282576, 281568], "Exact physical role counts")
    T, P = mix(Tv, WEIGHTS), mix(Pv, WEIGHTS)
    t = 1 - C
    bounds_112 = previous["dyadic_112"]
    ranges = {r: bounds_112(r, t) for r in T.keys() | P.keys()}
    targets = {r: n * ranges[r][0] for r, n in T.items()}
    paid = {r: n * ranges[r][1] for r, n in P.items()}
    target_total, paid_total = sum(targets.values()), sum(paid.values())
    directed_margin = Q(target_total - paid_total, UNIT)
    need(directed_margin > 0, "The actual weighted raw invoice fails")
    old_t, old_p = mix(Tv, (1, 90)), mix(Pv, (1, 90))
    old_upper_raw = Q(sum(n * ranges[r][1] for r, n in old_t.items())
                      - sum(n * ranges[r][0] for r, n in old_p.items()), UNIT)
    need(old_upper_raw < 0, "New raw trial separates from the unchanged weighted word")
    quantile = runpy.run_path(str(root / "round368/independent/support.py"))["quantile_cells"]
    cells = quantile(targets, paid)
    need(len(cells) == 51 and cells[112, 258] == 1, "Existing 51-grade support")
    typed = {}
    row_sums, owner_loads = defaultdict(Q), defaultdict(Q)
    for (r, k), share in cells.items():
        for a, payer in enumerate(Pv):
            for b, receiver in enumerate(Tv):
                if not (payer[r] and receiver[k]):
                    continue
                port_share = share * WEIGHTS[b] / T[k]
                typed[a, r, b, k] = port_share
                row_sums[a, r] += port_share * receiver[k]
                owner_loads[b, k] += port_share * WEIGHTS[a] * payer[r] * Q(paid[r], P[r])
    need(len(typed) == 88 and min(typed.values()) > Q(1, 2**26), "Thin typed shares")
    need(typed[1, 112, 1, 258] == Q(1, 624), "Same largest first placement")
    need(all(row_sums[a, r] == 1 for a, inv in enumerate(Pv) for r in inv), "Every paid role")
    need(all(0 < owner_loads[b, k] <= WEIGHTS[b] * Q(targets[k], T[k])
             for b, inv in enumerate(Tv) for k in inv), "Every target owner")
    cut2 = Q(sum(v for k, v in targets.items() if k > 2)
             - sum(v for r, v in paid.items() if 5*r > 8), UNIT)
    unit_cut = Q(paid[Q(1, 2)] - Q(targets[1] * paid_total, target_total), UNIT)
    need(cut2 > 0 and unit_cut > 0, "Both thin cuts admit physical loans")

    power = cache(runpy.run_path(str(root / "round367/independent/audit.py"))["power_bounds"])
    psi = Q()
    for (r, k), fraction in cells.items():
        ratio = Q(k, r)
        lo = power(ratio.numerator, C)[0] / power(ratio.denominator, C)[1]
        psi += P[r] * fraction * r * (lo - 1) / C
    linear = sum(k*n for k, n in T.items())
    fringe = 10*linear / (t*psi)
    delta = Q(1, 2**128)
    finite_factor = ((1+delta) * (1+Q(4*258,1024*WIDTH))
                     * power(1024*WIDTH*L, C)[1] * (1+fringe/L+delta)
                     / (1-delta)**4)
    gap = power(2, DEBIT)[0] - finite_factor
    need(gap > 0, "Common exact-edge finite debit")
    need(0 < Q(paid_total, target_total) < 1 and
         Q(paid_total, target_total) > Q(99, 100) and t > Q(996,1000), "Thin positive ratio")
    # The existing complete proof uses its coarse schedule inequalities as well
    # as the factor. Re-price the enlarged real number of weighted births here.
    M = 1 << 1024
    upper_band = 2 * (M // (2048 * WIDTH))
    need(sum(WEIGHTS)/(t*2**10) + Q(2,M**5) < 2 and upper_band > 516*L
         and 5160 <= delta*upper_band and (1-delta)*M <= 1024*WIDTH*upper_band
         and 11*t > 10, "Fixed-domain coarse birth and integration fences")
    need(2**46 < Q(M**4,2**132) and 2**20 < Q(M**4,2**132)
         and 2**19*(upper_band+L)**77 + L**77 < (M*L)**77,
         "Existing worst-band count and delay bounds")
    bank = peer / previous["SOURCE"]
    reserve = runpy.run_path(str(bank / "activation.py"))["resource_receipt"]
    qualify = runpy.run_path(str(bank / "outer_budget.py"))["qualify"]
    profile_rows = {}
    profiles = (((3000,3080),1024,Q(".00345")),
                ((8192,129414,524355),H,K))
    for label, (heights, hg, k) in zip(("entry","terminal"), profiles, strict=True):
        booked = Q()
        stage_slacks = []
        for j, h in enumerate(heights):
            cap = min(ETA,(249*(BINARY-Q(11,8*h))+booked)/250)
            selected = k+5*G if j == len(heights)-1 else Q(int(cap*10**21)-1,10**21)
            need(booked < selected < cap, f"{label} ordinary funding at requested H={h}")
            stage_slacks.append(str(cap-selected))
            booked = selected
        signed = qualify(k,G,booked,C-DEBIT/hg)
        stock = reserve(SimpleNamespace(rank_logs=heights, complex_log=hg, eta=ETA))
        profile_rows[label] = {"heights": heights, "numerical_H": hg, "kappa": str(k),
                               "signed": signed, "ordinary_stage_slacks": stage_slacks,
                               "stock": stock}
    activation = profile_rows["terminal"]["stock"]["public_exponent_A"]
    surcharge = ceil((K-Q(".00345"))*activation)
    return {
        "status": "VIABLE_PRICE_ONLY",
        "predecessor": PEER, "comparator": BENCHMARK, "old_kappa": str(K0),
        "kappa": str(K), "prior_installed_cap": str(old_upper),
        "delta_kappa": str(K-K0), "gain_over_prior_cap": str(K-old_upper),
        "gain_percent": str(100*(K-K0)/K0), "trial_c": str(C),
        "weights": WEIGHTS, "physical_widths": [1, 2], "scaled_paid_labels": sum(P.values()),
        "scaled_productive_labels": sum(T.values()), "raw_margin_lower": str(directed_margin),
        "previous_raw_bound_at_trial": str(old_upper_raw),
        "gaussian_debit": str(DEBIT), "raw_high_cut_slack": str(cut2),
        "normalized_unit_cut_slack": str(unit_cut), "nonempty_grade_cells": len(cells),
        "nonempty_typed_cells": len(typed), "min_actual_share": str(min(typed.values())),
        "grade_fraction_bits": max(max(x.numerator.bit_length(), x.denominator.bit_length())
                                   for x in cells.values()),
        "slot_112_to_258_probability": str(typed[1,112,1,258]),
        "psi_lower_rounded_down": str(Q(int(psi*10**7),10**7)),
        "fringe_upper_rounded_up": str(Q(ceil(fringe*10**10),10**10)),
        "factor_headroom_rounded_down": str(Q(int(gap*10**13),10**13)),
        "profiles": profile_rows, "finite_entry_surcharge_bits": surcharge,
        "receipt_sha256": PINS,
        "pending": "Literal calendar, independent full recurring stock/cost and setup proof, and scheduled signed replay",
    }


def main():
    p = ArgumentParser(description=__doc__)
    for arg in ("root","peer","out"):
        p.add_argument("--"+arg,type=Path,required=True)
    p.add_argument("--child",action="store_true")
    a = p.parse_args()
    if a.child:
        result = compare(a.root,a.peer)
        with a.out.open("x") as f:
            f.write(json.dumps(result, sort_keys=True, indent=2)+"\n")
    else:
        subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],
                       timeout=60,check=True)


if __name__ == "__main__":
    main()
