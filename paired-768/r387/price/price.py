"""One directed finite-factor test of lower-band 1874 on the verified weighted invoice."""

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
BENCHMARK = "56bd64bed76cadb98e459ed001ccbdf47963ccf6"
PINS = {
    "round384/price/receipt.json": "de15bc86515fe2faa4fc0d901fdc2260112a0fa733a93d4a016a05e23eb461cb",
    "round385/publish/research/p104-weighted-integer-frequencies-5-451/RESULT.json": "9cc1d762ff68e97166322c92c16bfa4dc5480893e77b3dafab216f7626d96c24",
    "round385/independent/verified.json": "e4a195f6f8c9a85bfef165de0aa502657ceac8fca8407d9a5a3e52a9e705ddfb",
    "round385/scientific.log": "5e80b03236dafb4cd1ab511574e032f2191c3858b1ab4292ec448fb45d9cc0b0",
    "round385/onboarding.log": "1186b2519df0e112a0a76b022140a080f3555bede9f247f33d863baeed43e287",
    "round385/onboarding.exit": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "round378/price/price.py": "6ddddfd71283bfe375cc8c094a2153c7be20537be5b54823347f79d8d07b6be0",
    "round378/price/receipt.json": "1a3600d7f62b82986ea752a0f285be28a551b44b8e05e91a40e09642238ccbc7",
}
C = Q(17145637307, 2**42)
K = Q(".00389821040")
K0 = Q(".00389821035")
DEBIT = Q(64982, 524288)
OLD_DEBIT = Q(65000, 524288)
BINARY = Q(4391986206293, 2**50)
ETA = Q(39, 10000)
G = Q(1, 10**18)
WEIGHTS = (5, 451)
H = 483871
L = 1874
OLD_L = 2048
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
    benchmark_path = root / "round385/publish"
    actual = subprocess.check_output(["git", "-C", str(benchmark_path), "rev-parse", "HEAD"],
                                     text=True).strip()
    need(actual == BENCHMARK, "Pinned signed predecessor")
    run_log = (root / "round385/scientific.log").read_text()
    need("PASS_REGISTERED_RESEARCH_PACKAGE research/p104-weighted-integer-frequencies-5-451 outcome=completed"
         in run_log and (root / "round385/scientific.exit").read_text().strip() == "0",
         "Predecessor signed replay completed")
    installed = json.loads((benchmark_path / "research/p104-weighted-integer-frequencies-5-451/RESULT.json").read_bytes())
    prior = json.loads((root / "round384/price/receipt.json").read_bytes())
    terminal = installed["terminal"]
    prior_terminal = prior["profiles"]["terminal"]
    need(installed["gaussian"]["weights"] == [5, 451]
         and installed["gaussian"]["trial"] == prior["trial_c"]
         and terminal["ordinary_H"] == [8192, 129414, 524359]
         and terminal["numerical_H"] == H
         and terminal["signed"] == prior_terminal["signed"], "Direct literal price result matches price receipt")
    old_upper = K0 + min(Q(prior_terminal["ordinary_stage_slacks"][-1]),
                        Q(terminal["signed"]["positive_margin"]))
    need(Q(terminal["kappa"]) == K0 and Q(installed["gaussian"]["raw_loss"]) == OLD_DEBIT
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
    need(directed_margin == Q(prior["raw_margin_lower"])
         and installed["gaussian"]["finite_loss"]["lower_band"] == OLD_L,
         "The changed lower band retains the literal exact signed weighted invoice")
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
    psi_lo = psi_hi = Q()
    for (r, k), fraction in cells.items():
        ratio = Q(k, r)
        numerator = power(ratio.numerator, C)
        denominator = power(ratio.denominator, C)
        coefficient = P[r] * fraction * r
        psi_lo += coefficient * (numerator[0]/denominator[1] - 1) / C
        psi_hi += coefficient * (numerator[1]/denominator[0] - 1) / C
    linear = sum(k*n for k, n in T.items())
    fringe_hi = 10*linear / (t*psi_lo)
    fringe_lo = 10*linear / (t*psi_hi)
    delta = Q(1, 2**128)

    def factor_bounds(lower):
        common = (1+delta) * (1+Q(4*258,1024*WIDTH)) / (1-delta)**4
        time = power(1024*WIDTH*lower, C)
        return (common*time[0]*(1+fringe_lo/lower+delta),
                common*time[1]*(1+fringe_hi/lower+delta))

    old_factor_lo, old_factor_hi = factor_bounds(OLD_L)
    new_factor_lo, new_factor_hi = factor_bounds(L)
    new_debit_lo, new_debit_hi = power(2, DEBIT)
    old_excess = old_factor_lo - new_debit_hi
    gap = new_debit_lo - new_factor_hi
    need(old_factor_hi < power(2, OLD_DEBIT)[0], "Known-good old edge and old debit control")
    if gap <= 0 or old_excess <= 0:
        return {"status": "EXACT_PRICE_FAIL", "comparator": BENCHMARK, "new_L": L,
                "debit": str(DEBIT), "proposed_kappa": str(K),
                "new_factor_upper": str(new_factor_hi), "new_debit_lower": str(new_debit_lo),
                "old_factor_lower": str(old_factor_lo), "new_debit_upper": str(new_debit_hi),
                "new_directed_gap": str(gap), "old_factor_excess": str(old_excess)}
    need(0 < Q(paid_total, target_total) < 1 and
         Q(paid_total, target_total) > Q(99, 100) and t > Q(996,1000), "Thin positive ratio")
    # The existing complete proof uses its coarse schedule inequalities as well
    # as the factor. Re-price the enlarged real number of weighted births here.
    M = 1 << 1024
    upper_band = 2 * (M // (2048 * WIDTH))
    need(L % 2 == 0 and L >= 1024 and power(L,t)[0] > 1024
         and 4*(L+2)*6 < 5*L*5 and L*258 < upper_band,
         "Lower-band divisibility, real deadlines and first source width")
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
                ((8192,129414,524369),H,K))
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
        if label == "terminal":
            need(min(heights) >= 8192, "Current written terminal clock admission")
            logB = 128 + 320 * sum(heights)
            recurring = max(84500001, 1602 + 220 * hg + logB)
        else:
            recurring = installed["entry"]["log2_C"]
        profile_rows[label] = {"heights": heights, "numerical_H": hg, "kappa": str(k),
                               "signed": signed, "ordinary_stage_slacks": stage_slacks,
                               "stock": stock, "recurring_log2_if_old_all_size_envelope_proved": recurring}
    old_prior = Q(terminal["ordinary_rates"][-2])
    old_ordinary_fixed_height = (249*(BINARY-Q(11,8*terminal["ordinary_H"][-1]))+old_prior)/250-5*G
    proposed_minus_one = (249*(BINARY-Q(11,8*524368))+old_prior)/250-5*G
    old_gaussian_fixed_height = Q(terminal["gaussian_rate"]) - 5*G
    need(old_upper == min(old_ordinary_fixed_height, old_gaussian_fixed_height),
         "Literal signed same-height ceiling equals independent preflight")
    need(proposed_minus_one < K and old_ordinary_fixed_height < K, "Lower adjacent H3 does not fund")
    need("Ran 760 tests" in (root/"round385/onboarding.log").read_text()
         and "OK (skipped=31)" in (root/"round385/onboarding.log").read_text()
         and (root/"round385/onboarding.exit").read_text().strip() == "0",
         "Predecessor repository gates completed")
    activation = profile_rows["terminal"]["stock"]["public_exponent_A"]
    surcharge = ceil((K-Q(".00345"))*activation)
    return {
        "status": "VIABLE_PRICE_ONLY",
        "predecessor": PEER, "comparator": BENCHMARK, "old_kappa": str(K0),
        "kappa": str(K), "prior_installed_cap": str(old_upper),
        "prior_ordinary_ceiling_at_same_height": str(old_ordinary_fixed_height),
        "prior_gaussian_ceiling_at_same_height": str(old_gaussian_fixed_height),
        "ordinary_ceiling_if_H3_524368": str(proposed_minus_one),
        "delta_kappa": str(K-K0), "gain_over_prior_cap": str(K-old_upper),
        "gain_percent": str(100*(K-K0)/K0), "trial_c": str(C),
        "weights": WEIGHTS, "physical_widths": [1, 2], "scaled_paid_labels": sum(P.values()),
        "scaled_productive_labels": sum(T.values()), "raw_margin_lower": str(directed_margin),
        "same_archived_signed_raw_margin": True,
        "lower_band": L, "old_lower_band": OLD_L, "old_debit": str(OLD_DEBIT),
        "gaussian_debit": str(DEBIT), "raw_high_cut_slack": str(cut2),
        "normalized_unit_cut_slack": str(unit_cut), "nonempty_grade_cells": len(cells),
        "nonempty_typed_cells": len(typed), "min_actual_share": str(min(typed.values())),
        "grade_fraction_bits": max(max(x.numerator.bit_length(), x.denominator.bit_length())
                                   for x in cells.values()),
        "slot_112_to_258_probability": str(typed[1,112,1,258]),
        "psi_lower_rounded_down": str(Q(int(psi_lo*10**7),10**7)),
        "fringe_upper_rounded_up": str(Q(ceil(fringe_hi*10**10),10**10)),
        "old_factor_excess_above_new_debit_lower": str(Q(int(old_excess*10**13),10**13)),
        "new_factor_upper": str(Q(ceil(new_factor_hi*10**14),10**14)),
        "old_factor_lower": str(Q(int(old_factor_lo*10**14),10**14)),
        "new_debit_factor_interval": [str(Q(int(new_debit_lo*10**14),10**14)),
                                       str(Q(ceil(new_debit_hi*10**14),10**14))],
        "factor_headroom_rounded_down": str(Q(int(gap*10**13),10**13)),
        "profiles": profile_rows, "finite_entry_surcharge_bits": surcharge,
        "receipt_sha256": PINS,
        "conditional_whole_log2_C": 1 + max(profile_rows["entry"]["recurring_log2_if_old_all_size_envelope_proved"] + surcharge, profile_rows["terminal"]["recurring_log2_if_old_all_size_envelope_proved"]),
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
