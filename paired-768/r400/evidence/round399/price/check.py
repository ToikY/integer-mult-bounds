"""Exact whole-family fixed-clock height bound for the reproduced R398 supplier."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal
import subprocess

PACKAGE = "research/p104-weighted-capped-allocation"
ARCHIVE = "research/tiered-native-multiplier/source/strong-bit-k7.json.gz"
K7 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
K0 = Q(".00389821380")
B, C = Q(4391986206293, 2**50), Q(17145637307, 2**42)
D, DG, G = Q(1405, 1024), Q(64944, 524288), Q(1, 10**18)
MIN, MAX, CLOCK = 8192, 524288, 318292711
GAUSSIAN_MIN, ETA = 1024, Q(".0039")
MAX_EVALUATIONS = 20
M, WEIGHTS = Q(249, 250), (Q(1, 62500), Q(1, 250), Q(1))
MODE_NAMES = ("price", "calendar", "raw", "exterior", "nested", "product", "setup")
LOG_NAMES = ("scientific", "onboarding", "historical")
COMPARATOR_FILES = ("RESULT.json", "prepare.py", "verify.py", "VERIFY.json", "PEER-SOURCE.json", "peer8057.tar.gz")
WORKSPACE_FILES = ("round378/independent/accept.py", "round391/price/check.py")
WORKSPACE_PINS = (
    "001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
)
EVIDENCE_FILES = ("independent/INPUTS.json", "independent/verified.json", "preflight.log", "exact-head")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, f"Duplicate manifest key {key}")
        out[key] = value
    return out


def parse(data):
    return json.loads(data, object_pairs_hook=unique)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], timeout=10)


def file_paths(comparator, evidence, workspace):
    paths = {f"comparator/{PACKAGE}/{name}": comparator / PACKAGE / name for name in COMPARATOR_FILES}
    evidence_names = (*EVIDENCE_FILES, *(f"{mode}.{ext}" for mode in LOG_NAMES for ext in ("log", "exit")))
    paths.update({f"evidence/{name}": evidence / name for name in evidence_names})
    paths.update({f"workspace/{name}": workspace / name for name in WORKSPACE_FILES})
    return paths


def authenticated(comparator, evidence, workspace, manifest):
    head = git(comparator, "rev-parse", "HEAD").decode().strip()
    need(manifest["head"] == head == (evidence / "exact-head").read_text().strip(),
         "Comparator checkout and separate completion manifest identify one exact commit")
    paths = file_paths(comparator, evidence, workspace)
    pins = manifest["sha256_by_path"]
    need(pins.keys() == paths.keys(), "Complete stable path-keyed inventory")
    data = {name: path.read_bytes() for name, path in paths.items()}
    need(all(sha256(raw).hexdigest() == pins[name] for name, raw in data.items()), "All exact input hashes")
    need(all(pins[f"workspace/{name}"] == digest for name,digest in
             zip(WORKSPACE_FILES,WORKSPACE_PINS,strict=True)), "Exact prior replay helper identities")
    for name in COMPARATOR_FILES:
        local = f"{PACKAGE}/{name}"
        need(git(comparator, "show", f"{head}:{local}") == data[f"comparator/{local}"],
             f"Committed comparator input {local}")
    logs = {name: data[f"evidence/{name}.log"] for name in LOG_NAMES}
    marker = f"PASS_REGISTERED_RESEARCH_PACKAGE {PACKAGE} outcome=completed".encode()
    need(all(data[f"evidence/{name}.exit"].strip() == b"0" for name in LOG_NAMES)
         and all(f"PASS_CAPPED_ALLOCATION {name}\n".encode() in logs["scientific"] for name in MODE_NAMES)
         and marker in logs["scientific"]
         and b"Ran 760 tests" in logs["onboarding"] and b"OK (skipped=31)" in logs["onboarding"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in logs["historical"]
         and f'"commit": "{head}"'.encode() in data["evidence/preflight.log"],
         "Complete exact-head science, independent repository and commit gates")
    independent = parse(data["evidence/independent/verified.json"])
    frozen = parse(data["evidence/independent/INPUTS.json"])
    need(Q(independent["kappa"]) == K0 and independent["authenticated_original_entries"] == 88
         and independent["status"].startswith("INDEPENDENT_LITERAL_CAPPED_ALLOCATION_PASS")
         and independent["frozen_candidate"] == frozen
         and all(frozen[f"capsule/{name}"] == pins[f"comparator/{PACKAGE}/{name}"]
                 for name in COMPARATOR_FILES), "Exact independently accepted signed input pins")
    old = parse(data[f"comparator/{PACKAGE}/RESULT.json"])
    return old, head


def ordinary(heights):
    rates = []
    previous = Q()
    for i, height in enumerate(heights):
        unconstrained = M * (B - D / height) + previous / 250
        cap = min(ETA, unconstrained)
        need(cap == unconstrained < ETA, "Inactive actual arithmetic clamp on tangent optimizer")
        if i == 2:
            return rates, cap
        previous = Q((cap*10**21).__floor__()-1, 10**21)
        rates.append(previous)


def tangent(g):
    budget = (CLOCK-1731-220*g)//320
    h = (MIN, budget-MIN-MAX, MAX)
    need(all(MIN <= height <= MAX for height in h), "Tangent optimizer lies in declared height box")
    slopes = tuple(w/height**2 for w, height in zip(WEIGHTS, h, strict=True))
    need(slopes[0] <= slopes[1] <= slopes[2], "Exact tangent derivative order")
    ideal = B * (1-Q(1, 250**3)) - M*D*sum(w/height for w, height in zip(WEIGHTS,h,strict=True))
    early, actual = ordinary(h)
    # For any other integer vector the strict reciprocal tangent remainder
    # is at least min(w)/MAX**3, before multiplication by M*D.
    gap = M*D*min(WEIGHTS)/MAX**3
    ticks = Q(2, 10**21)*(Q(1, 250)+Q(1, 250**2))
    need(0 <= ideal-actual < ticks < gap, "True earlier ticks cannot change the optimizer")
    positive = C-DG/g
    return {"g":g, "h":h, "ideal":ideal, "ordinary":actual, "positive":positive,
            "actual_cap":min(actual,positive)-5*G, "earlier_ticks":early,
            "derivatives":slopes, "tangent_gap":gap, "tick_loss_upper":ticks}


def certify_family(g0):
    seen = {}

    def evaluate(g):
        if g not in seen:
            need(len(seen) < MAX_EVALUATIONS, "Exact scalar evaluation cap reached")
            seen[g] = tangent(g)
        return seen[g]

    low0, high0 = g0-2048, g0+2048
    need(GAUSSIAN_MIN <= low0 < g0 < high0 <= MAX, "Initial bracket in full Gaussian domain")
    lo, hi = evaluate(low0), evaluate(high0)
    need(lo["positive"] <= lo["ordinary"] and hi["positive"] >= hi["ordinary"],
         "Declared bracket did not cross; no whole-family verdict")
    # h2 is monotonically decreasing, so feasibility, both derivative order
    # inequalities and the inactive clamp extend across the bracket.
    low, high = low0, high0
    while high-low > 1:
        mid = (low+high)//2
        row = evaluate(mid)
        if row["positive"] <= row["ordinary"]:
            low = mid
        else:
            high = mid
    left, right = evaluate(low), evaluate(high)
    winner = max((left,right),key=lambda row:row["actual_cap"])
    # The Gaussian cap increases below the bracket. The higher Gaussian
    # heights give smaller nested ordinary feasible sets, even where this
    # tangent recipe no longer has active h1=min and h3=max.
    outer = (lo["positive"]-5*G,hi["ordinary"]-5*G)
    need(max(outer) <= winner["actual_cap"], "Outside-bracket global cap")
    return winner, (left,right), (lo,hi), outer, list(seen.values())


def check(old, comparator, workspace):
    term = old["terminal"]
    old_h, old_g = tuple(term["ordinary_H"]),term["numerical_H"]
    need(old_h == (8192,124986,524288) and old_g == 490463 and Q(term["kappa"]) == K0,
         "Active fixed-clock comparison profile")
    need(old["complete_log2_C"] == CLOCK and old["ordinary_floor"] == 18960
         and Q(old["ordinary_finite_debit"]) == D and Q(old["ordinary_child_contraction"]) == Q(375,376)
         and Q(old["gaussian"]["raw_loss"]) == DG and Q(old["gaussian"]["trial"]) == C
         and old["gaussian"]["weights"] == [5,451], "Retained ordinary and positive payable construction")
    ticks, old_ordinary = ordinary(old_h)
    old_positive = C-DG/old_g
    old_cap = min(old_ordinary, old_positive)-5*G
    need(tuple(Q(rate) for rate in term["ordinary_rates"]) == (*ticks,K0+5*G)
         and Q(term["gaussian_rate"]) == old_positive and K0 < old_cap,
         "Exact scientific comparator using its true prior ticks")
    optimal, edges, outer_bracket, outside, evaluations = certify_family(old_g)
    ceiling = optimal["actual_cap"]
    need(ceiling >= old_cap, "Feasible incumbent control")
    result = {"old_kappa":K0, "old_installed_cap":old_cap, "family_ceiling":ceiling,
              "ceiling_delta":ceiling-old_cap,"search_bracket":outer_bracket,
              "outside_upper_bounds":outside,"crossing":edges,"evaluations":evaluations,"optimum":optimal}
    if ceiling == old_cap:
        return dict(result,status="EXACT_SCOPED_EXCLUSION")

    archive = runpy.run_path(str(workspace/WORKSPACE_FILES[0]))["restore_reference"](comparator/PACKAGE)
    need(len(archive)==88 and sha256(archive[ARCHIVE]).hexdigest()==K7, "Exact signed K7 source identity")
    cuts, selector, geometry, stock, qualify = runpy.run_path(str(workspace/WORKSPACE_FILES[1]))["archived_caller"](archive)
    hs,h = optimal["h"],optimal["g"]
    # A finite decimal strictly between the old cap and the new crossing.
    k = Q((ceiling*10**16).__ceil__()-1,10**16)
    if k <= old_cap:
        k = (ceiling+old_cap)/2
    need(old_cap < k < ceiling,"Strictly improves the exact old installed ceiling")
    profile = stock(SimpleNamespace(rank_logs=hs,complex_log=h,eta=ETA))
    a = profile["public_exponent_A"]
    header = (1 << a) + profile["first_public_offset"]
    prefix = ((k-Q(old["entry"]["kappa"]))*a).__ceil__()
    log_b = 128+320*sum(hs)
    clock = 1+max(84500001,1602+220*h+log_b,old["entry"]["log2_C"]+prefix)
    positions = []
    for i,cut in enumerate(cuts(hs),1):
        expected = tuple(selector(cut+j,3,hs) for j in (-1,0,1))+(selector(cut+1,i-1,hs),)
        need(expected == (i-1,i,i,i-1),"Exact admitted and predecessor-clipped ordinary seam")
        positions.append([cut,*expected])
    entry = old["entry"]
    early = qualify(Q(entry["kappa"]),G,Q(entry["ordinary_rates"][-1]),Q(entry["gaussian_rate"]))
    late = qualify(k,G,k+5*G,optimal["positive"])
    need(early==entry["signed"] and (late["strict"],late["functional"])==(54,4)
         and header%6==0 and header.bit_length()==a+1 and (header-6).bit_length()==a
         and a==geometry["connected_exponent"](cuts(hs)[-1],h)
         and profile["binary_cuts"]==list(cuts(hs)) and profile["storage_upper"]=="6.2 p T < 297.6 n bits"
         and clock<=CLOCK and max(h,*hs).bit_length()<=20
         and old["native_setup_transition_upper"]<2**228, "Complete exact same-resource signed stage price")
    return dict(result,status="VIABLE_PRICE_ONLY",candidate_kappa=k,delta_kappa=k-K0,
                gain_over_exact_old_cap=k-old_cap,clock=clock,ordinary_log2_B=log_b,
                entry_conversion=prefix,stock=profile,stage_controls=positions,
                terminal_signed=late,ordinary_ticks=(*optimal["earlier_ticks"],k+5*G))


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("comparator","evidence","workspace","complete","out"):
        parser.add_argument("--"+name,required=True,type=Path)
    args = parser.parse_args()
    signal.alarm(60)
    manifest = parse(args.complete.read_bytes())
    old, head = authenticated(args.comparator,args.evidence,args.workspace,manifest)
    result = check(old,args.comparator,args.workspace)
    result.update(comparator_head=head,pinned_inputs_by_path=manifest["sha256_by_path"],
                  scope={"max_scalar_evaluations":MAX_EVALUATIONS,"actual_evaluations":len(result["evaluations"]),
                         "ordinary_height_min":MIN,"height_max":MAX,"gaussian_height_min":GAUSSIAN_MIN,
                         "recurring_log2_max":CLOCK})
    signal.alarm(0)
    args.out.write_text(json.dumps(result,default=str,sort_keys=True,indent=2)+"\n")


if __name__=="__main__":
    main()
