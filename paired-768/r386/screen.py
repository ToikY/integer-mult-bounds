"""Exclude an entire finite ratio family without enumerating or building schedules."""

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

SOURCE = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
BASELINE = "56bd64bed76cadb98e459ed001ccbdf47963ccf6"
BASE_PATH = "research/p104-weighted-integer-frequencies-5-451"
PINS = {
    "round367/independent/audit.py": "bc2a8de7028287d6c816b8caed9b2b686e2b50449b7e8f67d55cd5dd958f381c",
    "round368/primary/receipt.json": "e60a50062125f75613ac0423c98a3aa81be576d43ea09193c1a24e78ba919b49",
    "round375/unsplit-frontier/screen.py": "a6b35438f271200b43efc2868e2bceb290331f24f06fae8779fd250a7d6baff4",
    "round384/price/receipt.json": "de15bc86515fe2faa4fc0d901fdc2260112a0fa733a93d4a016a05e23eb461cb",
    f"round385/publish/{BASE_PATH}/RESULT.json": "9cc1d762ff68e97166322c92c16bfa4dc5480893e77b3dafab216f7626d96c24",
    "round385/independent/verified.json": "e4a195f6f8c9a85bfef165de0aa502657ceac8fca8407d9a5a3e52a9e705ddfb",
}
PEER_PATH = "research/frequency-weighted-native-multiplier/RESULT.json"
PEER_SHA = "2f4faa6648592f589df22a8a0a07ba6856d20786294a44a7776c7d6e0efa14a5"
K = Q(".00389821035")
C0 = Q(17145637167, 2**42)
TRIAL = Q(17145637307, 2**42)
H = 483871
DEBIT = Q(65000, 524288)
STOP = Q(5, 10**18)
CHARGE = DEBIT/H + STOP
LOWER = C0-Q(1, 10**7)
UPPER = C0+Q(23, 10**9)
TAIL = Q(".004")
BUDGET = 729


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def read(path, digest):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == digest, str(path))
    return data


def head(path):
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def scope(root, peer, comparator=None):
    need(head(peer) == SOURCE, "Exact physical ancestry")
    baseline = comparator or root / "round385/publish"
    need(head(baseline) == BASELINE, "Exact baseline round")
    read(baseline / BASE_PATH / "RESULT.json", PINS[f"round385/publish/{BASE_PATH}/RESULT.json"])
    need((root/"round385/scientific.exit").read_text().strip() == "0",
         "Local signed baseline verification has not completed")
    log = (root/"round385/scientific.log").read_bytes()
    marker = f"PASS_REGISTERED_RESEARCH_PACKAGE {BASE_PATH} outcome=completed".encode()
    need(marker in log and log.count(b"PASS_WEIGHTED_INTEGER_FREQUENCIES") == 7,
         "Require all exact registered baseline modes")
    old = json.loads(read(peer/PEER_PATH, PEER_SHA))
    sources = {name: read(root/name, digest) for name,digest in PINS.items()}
    installed = json.loads(sources[f"round385/publish/{BASE_PATH}/RESULT.json"])
    prior = json.loads(sources["round384/price/receipt.json"])
    terminal = installed["terminal"]
    need(Q(terminal["kappa"]) == K and terminal["numerical_H"] == H and
         installed["gaussian"]["weights"] == [5,451] and
         Q(installed["gaussian"]["trial"]) == TRIAL and Q(installed["gaussian"]["raw_loss"]) == DEBIT,
         "Same actual numerical profile and signed target")
    prior_cap = K+min(Q(terminal["signed"]["positive_margin"]),
                      Q(prior["profiles"]["terminal"]["ordinary_stage_slacks"][-1]))
    start = K+CHARGE
    previous = runpy.run_path(str(root/"round375/unsplit-frontier/screen.py"))
    r368 = json.loads(sources["round368/primary/receipt.json"])
    target, paid = map(previous["unmix"],(r368["source_targets"],r368["source_paid"]))
    need(sum(target.values())==52608 and sum(paid.values())==281568 and
         (target[1],target[2],paid[1])==(1008,432,183312), "Exact base counts")
    power = cache(runpy.run_path(str(root/"round367/independent/audit.py"))["power_bounds"])

    def evaluate(labels, a, b):
        low = high = Q()
        for r,n in labels.items():
            ends = (*power(r, 1-a), *power(r, 1-b))
            l,h = sorted((n*min(ends),n*max(ends)))
            low += l
            high += h
        return low,high

    def decline(labels, a, b):
        """Lower bound for the negative derivative of the signed moment."""
        ctx = Context(prec=82)
        result = Q()
        for r,n in labels.items():
            if r == 1 or not n:
                continue
            r = Q(r)
            x = ctx.divide(Decimal(r.numerator),Decimal(r.denominator))
            log = ctx.ln(x)
            log_ends = Q(ctx.next_minus(log)),Q(ctx.next_plus(log))
            powers = (*power(r,1-a),*power(r,1-b))
            result += min(n*p*l for p in (min(powers),max(powers)) for l in log_ends)
        need(result > 0, "Monotone signed moment required")
        return result

    def root_upper(labels, a, b):
        need(evaluate(labels,b,b)[1] < 0, "Upper endpoint rejects")
        if evaluate(labels,a,a)[1] < 0:
            return a,a
        need(evaluate(labels,a,a)[0] > 0, "Lower endpoint indeterminate")
        for _ in range(44):
            mid = (a+b)/2
            l,h = evaluate(labels,mid,mid)
            if l > 0:
                a = mid
            elif h < 0:
                b = mid
            else:
                raise ValueError("Indeterminate directed sign at midpoint")
        return a,b

    qmax = (5*BUDGET-1)//456
    candidates = [(q,451*q//5+1,BUDGET-q) for q in range(1,qmax+1) if 451*q//5+1<=BUDGET-q]
    count = sum(hi-lo+1 for _,lo,hi in candidates)
    lowest = min(Q(lo,q) for q,lo,hi in candidates)
    highest = max(Q(hi,q) for q,lo,hi in candidates)
    need(lowest==Q(361,4) and highest==728, "Farey boundary under actual integer sum")

    A = target.copy()
    A.subtract(paid)
    raw_max = A.copy()
    raw_max.update({2*r:highest*n for r,n in A.items()})
    raw_max[1] += 1008
    raw_max[Q(1,2)] -= 2016
    raw_slope = decline(raw_max,LOWER,TAIL)
    raw = root_upper(raw_max,LOWER,UPPER)
    need(raw[1] > C0 and LOWER < C0 < start < TRIAL, "R385 target interval")

    # Slack for a mandatory high receiver is raw productive capacity minus
    # all paid mass that cannot legally enter a grade-two-or-lower recipient.
    # Removing normalization and giving free ordinary funding are generous.
    typ0 = Counter({r:n for r,n in target.items() if r>2})
    typ0.subtract({r:n for r,n in paid.items() if 5*r>8})
    typ1 = Counter({2*r:n for r,n in target.items() if r>1})
    typ1.subtract({2*r:n for r,n in paid.items()})
    typed_coefficient_upper = evaluate(typ1,LOWER,raw[1])[1]
    need(typed_coefficient_upper < 0, "All larger ratios decrease compulsory slack")
    cut = typ0.copy()
    cut.update({r:lowest*n for r,n in typ1.items()})
    cut_slope = decline(cut,LOWER,raw[1])
    need(evaluate(cut,C0,C0)[1] < Q("-7.5"), "Peer 90/91 affine bound")
    cut_root = root_upper(cut,LOWER,C0)
    cap = cut_root[1]-CHARGE
    need(cap < K and K < prior_cap, "Excludes the entire ratio family")

    def strs(interval):
        return [str(x) for x in interval]
    return {
        "verdict": "NO_VERIFIED_GAIN_WHOLE_RATIO_FAMILY_EXCLUDED",
        "baseline": BASELINE, "physical_ancestry": SOURCE, "pins": PINS,
        "baseline_scientific_log_sha256": sha256(log).hexdigest(),
        "total_birth_budget": BUDGET, "only_denominator_windows": candidates,
        "integer_weight_pairs_excluded": count, "min_and_max_ratio": strs((lowest,highest)),
        "raw_c_affordable_from": str(start), "raw_c_upper_at_max_weight": str(raw[1]),
        "raw_c_root_at_max_ratio": strs(raw), "negative_raw_derivative_lower": str(raw_slope),
        "type_one_marginal_high_cut_slack_upper": str(typed_coefficient_upper),
        "smallest_ratio_high_cut_slack_at_c0": strs(evaluate(cut,C0,C0)),
        "smallest_ratio_high_cut_slack_at_target": strs(evaluate(cut,start,start)),
        "minimum_ratio_compulsory_cut_raw_crossing": strs(cut_root),
        "negative_cut_derivative_lower": str(cut_slope),
        "optimistic_complete_ceiling": str(cap), "shortfall_vs_certified_R385": str(K-cap),
        "shortfall_vs_installed_R385_cap": str(prior_cap-cap),
        "fixed_parameters": {"H": H, "L": 2048, "debit": str(DEBIT), "stopping_charge": str(STOP),
                             "widths": [1,2], "base_splits": 1008},
        "unresolved": "Other weighted source shapes, window or extra rank repairs remain outside the quantified family",
    }


def main():
    parser = ArgumentParser(description=__doc__)
    for arg in ("root","peer","out"):
        parser.add_argument("--"+arg,type=Path,required=True)
    parser.add_argument("--comparator", type=Path, help="Exact signed 5-to-451 checkout")
    parser.add_argument("--child",action="store_true")
    a = parser.parse_args()
    if a.child:
        result = scope(a.root, a.peer, a.comparator)
        with a.out.open("x") as f:
            f.write(json.dumps(result,sort_keys=True,indent=2)+"\n")
    else:
        subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],
                       timeout=60,check=True)


if __name__ == "__main__":
    main()
