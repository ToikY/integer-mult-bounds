"""Bound every combination of at most two named weighted Gaussian unsplits."""

from argparse import ArgumentParser
from decimal import Context, Decimal
from fractions import Fraction as Q
from functools import cache
from hashlib import sha1, sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys

PINS = {
    "round375/unsplit-frontier/screen.py": "a6b35438f271200b43efc2868e2bceb290331f24f06fae8779fd250a7d6baff4",
    "round367/independent/audit.py": "bc2a8de7028287d6c816b8caed9b2b686e2b50449b7e8f67d55cd5dd958f381c",
    "round368/primary/receipt.json": "e60a50062125f75613ac0423c98a3aa81be576d43ea09193c1a24e78ba919b49",
    "round376/audit/receipt.json": "5d892761adc42cb9bfea1187f06127b7260b8d2968105dc74ade5a61074c3bb5",
}
PEER_HEAD = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
PEER_RECEIPT = "research/frequency-weighted-native-multiplier/RESULT.json"
PEER_BLOB = "c7ed01eff900b13d3cf70fc9b7c52daad598a41c"
C_OLD = Q(17145637167, 2**42)
H = 483871
LOSS = Q(65081, 524288) / H + Q(5, 10**18)
UPPER = Q(".004")


def need(x, error):
    if not x:
        raise ValueError(error)


def interval_text(low, high):
    return [str(low), str(high)]


def screen(root, peer):
    for path, expected in PINS.items():
        need(sha256((root / path).read_bytes()).hexdigest() == expected, path)
    head = subprocess.check_output(["git", "-C", str(peer), "rev-parse", "HEAD"], text=True).strip()
    need(head == PEER_HEAD, "Expected the #8057 independently replayed head")
    peer_receipt = (peer / PEER_RECEIPT).read_bytes()
    need(sha1(f"blob {len(peer_receipt)}\0".encode() + peer_receipt).hexdigest() == PEER_BLOB,
         "Peer receipt Git blob")
    peer_result = json.loads(peer_receipt)
    need(Q(peer_result["gaussian"]["trial"]) == C_OLD and
         Q(peer_result["gaussian"]["raw_loss"]) == Q(65081, 524288) and
         peer_result["terminal"]["numerical_H"] == H, "Fixed comparison invoice")
    old = json.loads((root / "round368/primary/receipt.json").read_bytes())
    names = old["1006_literal_touched_paid_clock_and_tag"]
    need(names == [[1592, ["return", 9977, 0, 91990]], [1593, ["return", 9977, 0, 91966]]],
         "Only the two previously named independent ports")
    support = runpy.run_path(str(root / "round375/unsplit-frontier/screen.py"))
    unmix, weighted = support["unmix"], support["weighted"]
    target_base, paid_base = map(unmix, (old["source_targets"], old["source_paid"]))
    T = weighted(target_base)[2]
    old_P = weighted(paid_base, 1008)[2]
    P = weighted(paid_base, 1006)[2]
    need(sum(T.values()) == peer_result["gaussian"]["weighted_targets"] == 4787328,
         "Source-bound target count")
    need(sum(old_P.values()) == peer_result["gaussian"]["weighted_loans"] == 25623696 and
         sum(P.values()) == 25623694 and old_P[Q(1, 2)] - P[Q(1, 2)] == 4 and P[1] - old_P[1] == 2,
         "Optimistic invoice unsplits both allowed sites exactly, once per type-zero job")
    power = cache(runpy.run_path(str(root / "round367/independent/audit.py"))["power_bounds"])

    def signed(paid):
        coefficients = T.copy()
        coefficients.subtract(paid)
        return coefficients

    largest = signed(P)
    baseline = signed(old_P)

    def moment(coefficients, c):
        low = high = Q()
        for rank, n in coefficients.items():
            lo, hi = sorted(n * z for z in power(rank, 1 - c))
            low += lo
            high += hi
        return low, high

    ctx = Context(prec=82)
    slope = Q()
    for rank, n in largest.items():
        if rank == 1 or not n:
            continue
        rank = Q(rank)
        primitive = ctx.divide(Decimal(rank.numerator), Decimal(rank.denominator))
        ln = ctx.ln(primitive)
        ln_ends = Q(ctx.next_minus(ln)), Q(ctx.next_plus(ln))
        ends = (*power(rank, 1 - UPPER), *power(rank, 1 - C_OLD))
        slope += min(n * pc * la for pc in (min(ends), max(ends)) for la in ln_ends)
    need(slope > 0, "Raw margin must decrease throughout the entire admissible tail")
    need(moment(baseline, C_OLD)[0] > 0, "Original positive control")
    need(moment(largest, UPPER)[1] < 0, "Bounded high-end raw rejection")

    # For any c>0, replacing 2 halves by a unit removes 2^c-1>0.
    # The 2-site case bounds every subset, without enumerating alternatives.
    lo, hi = C_OLD, UPPER
    for _ in range(45):
        trial = (lo + hi) / 2
        l, h = moment(largest, trial)
        if l > 0:
            lo = trial
        elif h < 0:
            hi = trial
        else:
            raise ValueError("Directed root sign unresolved")
    bound = hi - LOSS
    r376 = json.loads((root / "round376/audit/receipt.json").read_bytes())
    k = Q(r376["candidate_kappa"])
    terminal = r376["funding"]["terminal"]
    installed = k + min(Q(terminal["gaussian_gap"]), Q(terminal["ordinary_gap"]))
    baseline_kappa = Q(peer_result["terminal"]["kappa"])
    return {
        "scope": "At most two named type-zero unsplits, fixed H, finite debit and signed stopping denominator",
        "peer": PEER_HEAD,
        "peer_result_path_and_blob": {PEER_RECEIPT: PEER_BLOB},
        "campaign_inputs_and_sha256": PINS,
        "scope_sites": names,
        "baseline_kappa": str(baseline_kappa),
        "old_signed_amount_at_peer_trial": interval_text(*moment(baseline, C_OLD)),
        "raw_two_unsplit_ceiling_bracket": interval_text(lo, hi),
        "strictly_negative_derivative_abs_lower": str(slope),
        "optimistic_complete_cap": str(bound),
        "optimistic_net_gain_over_8057": str(bound - baseline_kappa),
        "provisional_R376_rate": str(k),
        "R376_installed_cap": str(installed),
        "optimistic_net_gain_over_R376_rate": str(bound - k),
        "optimistic_net_gain_over_R376_installed_cap": str(bound - installed),
        "raw_at_R376_funding": interval_text(*moment(largest, k + LOSS)),
        "family_excluded": bound < k,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("root", "peer", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    a = parser.parse_args()
    if a.child:
        result = screen(a.root, a.peer)
        with a.out.open("x") as receipt:
            receipt.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]],
                       timeout=30, check=True)


if __name__ == "__main__":
    main()
