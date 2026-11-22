"""Bound frequency 91 with any subset of type-one physical rank-two splits."""

from argparse import ArgumentParser
from collections import Counter
from decimal import Context, Decimal
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys

HEAD = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
RESULT = "research/frequency-weighted-native-multiplier/RESULT.json"
PEER_SHA = "2f4faa6648592f589df22a8a0a07ba6856d20786294a44a7776c7d6e0efa14a5"
PINS = {
    "round367/independent/audit.py": "bc2a8de7028287d6c816b8caed9b2b686e2b50449b7e8f67d55cd5dd958f381c",
    "round368/primary/receipt.json": "e60a50062125f75613ac0423c98a3aa81be576d43ea09193c1a24e78ba919b49",
    "round375/unsplit-frontier/screen.py": "a6b35438f271200b43efc2868e2bceb290331f24f06fae8779fd250a7d6baff4",
    "round378/price/receipt.json": "1a3600d7f62b82986ea752a0f285be28a551b44b8e05e91a40e09642238ccbc7",
}
C0 = Q(17145637167, 2**42)
H = 483871
W = 91
K8058, K378 = Q(".00389821005"), Q(".00389821030")
STOP = Q(5, 10**18)
DEBIT = Q(65000, 524288)
LEFT, RIGHT = max(K8058, K378) + STOP, C0 + Q(1, 10**8)
TAIL = Q(".004")


def need(ok, label):
    if not ok:
        raise ValueError(label)


def pinned(path, digest):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == digest, str(path))
    return data


def ceil(q):
    return -(-q.numerator // q.denominator)


def bill(root, peer):
    head = subprocess.check_output(["git", "-C", str(peer), "rev-parse", "HEAD"], text=True).strip()
    need(head == HEAD, "Exact #8057 scientific source")
    old = json.loads(pinned(peer / RESULT, PEER_SHA))
    need(old["gaussian"]["weights"] == [1, 90] and old["gaussian"]["real_loans"] == [282576, 281568]
         and old["gaussian"]["trial"] == str(C0), "Original geometry control")
    local = {name: pinned(root / name, seen) for name, seen in PINS.items()}
    new = json.loads(local["round378/price/receipt.json"])
    need(Q(new["profiles"]["terminal"]["kappa"]) == K378 and Q(new["comparison_8058"]) == K8058
         and Q(new["gaussian"]["debit"]) == DEBIT, "Frozen frontier and improved debit")
    familiar = runpy.run_path(str(root / "round375/unsplit-frontier/screen.py"))["unmix"]
    tbase, pbase = map(familiar, (
        json.loads(local["round368/primary/receipt.json"])["source_targets"],
        json.loads(local["round368/primary/receipt.json"])["source_paid"],
    ))
    T, P = tbase.copy(), pbase.copy()
    T.update({2*r: W*n for r, n in tbase.items()})
    P.update({2*r: W*n for r, n in pbase.items()})
    P[1] -= 1008
    P[Q(1, 2)] += 2016
    need(sum(T.values()) == (1 + W)*52608 and sum(P.values()) == (1 + W)*281568 + 1008,
         "Every true paid and productive label in the 91-frequency invoice")
    signed = T.copy()
    signed.subtract(P)
    cut = Counter({r: n for r, n in P.items() if 5*r > 8})
    cut.subtract({k: n for k, n in T.items() if k > 2})
    power = cache(runpy.run_path(str(root / "round367/independent/audit.py"))["power_bounds"])

    def interval(counts, a, b):
        lo = hi = Q()
        for r, n in counts.items():
            value = (*power(r, 1-a), *power(r, 1-b))
            low, high = sorted((n*min(value), n*max(value)))
            lo += low
            hi += high
        return lo, hi

    def proof_of_decreasing(coefficients, start, finish):
        result = Q()
        ctx = Context(prec=82)
        for r, n in coefficients.items():
            if r == 1 or not n:
                continue
            x = ctx.divide(Decimal(r.numerator), Decimal(r.denominator))
            logarithm = ctx.ln(x)
            logs = Q(ctx.next_minus(logarithm)), Q(ctx.next_plus(logarithm))
            e = (*power(r, 1-start), *power(r, 1-finish))
            result += min(n*v*l for v in (min(e), max(e)) for l in logs)
        need(result > 0, "Strict raw margin decrease throughout all higher admissible trials")
        return result

    known_cut = interval(cut, C0, C0)
    known_raw = interval(signed, C0, C0)
    need(known_cut[0] > 1515 and known_raw[0] > Q(".03"), "Published 91-frequency negative control")
    slope = proof_of_decreasing(signed, LEFT, TAIL)
    need(interval(signed, RIGHT, RIGHT)[1] < 0, "Unchanged whole margin already fails past upper cut")
    edges = [LEFT + i * (RIGHT - LEFT) / 16 for i in range(17)]
    deficit = min(interval(cut, a, b)[0] for a, b in zip(edges, edges[1:]))
    per_site_capacity = W * power(2, 1-LEFT)[1]
    required = ceil(deficit / per_site_capacity)
    need(deficit > 0 and 0 < required <= pbase[1],
         "Necessary number among all actual type-one rank-two jobs")
    # Every changed job has an even physical width: split a real 2f into two f.
    # For c>0, replacing 2^(1-c) by 2 costs a positive amount that only grows.
    least_split_penalty = W * required * (2 - power(2, 1-LEFT)[1])
    gain_upper = interval(signed, LEFT, LEFT)[1]
    adjusted = signed.copy()
    adjusted[2] += W * required
    adjusted[1] -= 2 * W * required
    lo, hi = LEFT, RIGHT
    if interval(adjusted, lo, lo)[1] > 0:
        need(interval(adjusted, lo, lo)[0] > 0, "Directed low root sign in best admissible relaxation")
        for _ in range(42):
            c = (lo + hi) / 2
            lower, upper = interval(adjusted, c, c)
            if lower > 0:
                lo = c
            elif upper < 0:
                hi = c
            else:
                raise ValueError("Directed midpoint unresolved")
    else:
        hi = lo
    allowed_debit = max(Q(0), H * (hi - LEFT))
    # The 65000/524288 certificate is a cost of the current method, not a
    # lower bound on every possible physical construction.
    complete = hi - DEBIT / H - STOP
    retained_factor_floor = power(1024 * 306 * 2048, LEFT)[0]
    allowed_factor_ceiling = power(2, allowed_debit)[1]
    c_full = LEFT + DEBIT / H
    net = interval(adjusted, c_full, c_full)

    def couple(span):
        return [str(item) for item in span]

    return {
        "scope": "All subsets of type-one rank-two payments in the physical frequency-91 source, fixed height and paid widths",
        "peer": HEAD, "peer_result": {RESULT: PEER_SHA}, "campaign_pins": PINS,
        "weights": [1, W], "input_trial": str(C0), "tracked_thresholds": [str(K8058), str(K378)],
        "whole_cut_window": couple((LEFT, RIGHT)), "tail_end": str(TAIL),
        "original_cut_deficit_at_peer_trial": couple(known_cut),
        "original_raw_at_peer_trial": couple(known_raw),
        "possible_sites_optimistic": pbase[1],
        "weighted_high_cut_deficit_lower_entire_window": str(deficit),
        "weighted_capacity_removed_by_each_site_upper": str(per_site_capacity),
        "minimum_distinct_sites": required,
        "minimum_total_raw_payment_entire_window": str(least_split_penalty),
        "unchanged_raw_headroom_at_low_endpoint": str(gain_upper),
        "original_negative_derivative_magnitude_lower": str(slope),
        "relaxed_necessary_split_raw_upper": str(hi), "raw_root_bracket": couple((lo, hi)),
        "retained_debit": str(DEBIT), "optimistic_signed_cap_at_retained_debit": str(complete),
        "optimistic_delta_over_8058": str(complete - K8058),
        "optimistic_delta_over_round378": str(complete - K378),
        "adjusted_raw_at_prospective_round378_charge": couple(net),
        "largest_possible_debit_to_reach_round378": str(allowed_debit),
        "bare_inherited_finite_factor_lower": str(retained_factor_floor),
        "largest_allowed_debit_factor_upper": str(allowed_factor_ceiling),
        "even_bare_inherited_factor_excluded": retained_factor_floor > allowed_factor_ceiling,
        "fixed_debit_family_excluded": complete < K378,
        "uncertified": "Individual sites, alternative finite proofs, other physical types or changed owner capacities",
    }


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("root", "peer", "out"):
        parser.add_argument("--"+name, type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    a = parser.parse_args()
    if a.child:
        result = bill(a.root, a.peer)
        with a.out.open("x") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]],
                       timeout=60, check=True)


if __name__ == "__main__":
    main()
