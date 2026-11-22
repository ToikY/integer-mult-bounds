"""Independently certify the adjacent fixed-clock integer allocation envelope."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal

HEAD="8c800e1b6458526e1ce7a59150bba8a0d29d0027"
PKG="research/p104-weighted-capped-allocation"
BASE="round398/publish/"+PKG
ARCHIVE_K7="research/tiered-native-multiplier/source/strong-bit-k7.json.gz"
K7="9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
RATE=Q(".00389821380")
B,C=Q(4391986206293,2**50),Q(17145637307,2**42)
D,DG=Q(1405,1024),Q(64944,524288)
G,ETA=Q(1,10**18),Q(".0039")
OMIN,GMIN,MAX,CLOCK=8192,1024,524288,318292711
OLD_HS=(8192,124986,524288)
OLD_G=490463
W=(Q(1,62500),Q(1,250),Q(1))

PINS={
    "round398/exact-head":"9422df8ce76a0206664e5b8ba282e3f642652bfe04490a06fbb9e66dc3a15b0b",
    "round398/preflight.log":"4cc2a884d5ec06cdc01b93a9150778b97eda04af94c2f1f0edfb1ff216360495",
    "round398/independent/verified.json":"18a9c9a64506bbd107305db10f2fac3df42d32b299d0627baba8958ac5d59924",
    "round398/independent/INPUTS.json":"8200aac92e3a53be68c972cbd94c5b7af94591e0c024d198ccda30aa99e04769",
    "round378/independent/accept.py":"001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round391/price/check.py":"5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    f"{BASE}/RESULT.json":"ba4782e227936b7654f70002857c8fc2b0276a1c7d2b11d22f7ca14af9502b1a",
    f"{BASE}/prepare.py":"d53ce9e21cf57e1b2b64fef2c91aae3abefeb9df2e083034223bd38b0a02e0b2",
    f"{BASE}/verify.py":"10362de3ceaa651cde5b71c6599fd4683d9f1f4d76cc252178e915b43a098fee",
    f"{BASE}/PEER-SOURCE.json":"798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    f"{BASE}/peer8057.tar.gz":"0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}


def need(ok,meaning):
    if not ok:
        raise ValueError(meaning)


def sha(raw):
    return sha256(raw).hexdigest()


def pin(path,digest):
    raw=path.read_bytes()
    need(sha(raw)==digest,f"Exact evidence {path.name}")
    return raw


def unique(pairs):
    table={}
    for name,b in pairs:
        need(name not in table,f"Repeated pin {name}")
        table[name]=b
    return table


def parse(raw):
    return json.loads(raw,object_pairs_hook=unique)


def up(x):
    return -(-x.numerator//x.denominator)


def tick(x):
    return Q((x*10**21).__floor__()-1,10**21)


def evaluate(g):
    """Price a single Gaussian height, and prove exact global ordinary optimum there."""
    # Max over the two branches can only enlarge the complete clock.
    summed=(CLOCK-(1+1602+128)-220*g)//320
    a=(OMIN,summed-OMIN-MAX,MAX)
    need(GMIN<=g<=MAX and all(OMIN<=h<=MAX for h in a),"Valid endpoint within known domain")
    q,p=Q(1,250),Q(249,250)
    own=tuple(p*(B-D/h) for h in a)
    x=tick(own[0])
    y=tick(own[1]+q*x)
    ordinary=own[2]+q*y
    ideal=own[2]+q*own[1]+q**2*own[0]
    need(0<x<own[0]<ETA and x<y<own[1]+q*x<ETA and y<ordinary<ETA,
         "Exact strict ticks and inactive clamp at the optimal integer vector")
    need(ideal==B*(1-q**3)-p*D*sum(w/h for w,h in zip(W,a,strict=True)),
         "Independent three-stage unrolling")
    alpha=tuple(w/h**2 for w,h in zip(W,a,strict=True))
    need(0<alpha[0]<alpha[1]<alpha[2],"Strict ordered reciprocal slopes at the integer vertex")
    # For integer feasible x != a, with dh=x-a, at least one of dh1,
    # -dh3, -sum(dh) is >=1. The tangent linear loss alone is at least
    # min(alpha2-alpha1, alpha3-alpha2, alpha2). Clamp/ticks only reduce it.
    integer_loss=p*D*min(alpha[1]-alpha[0],alpha[2]-alpha[1],alpha[1])
    true_loss=ideal-ordinary
    need(0<=true_loss < integer_loss,"Actual rebooking is strictly better than every other integer allocation")
    positive=C-DG/g
    return {"g":g,"h":list(a),"sum_budget":summed,"earlier_ticks":[str(x),str(y)],
            "ideal":str(ideal),"ordinary":str(ordinary),"positive":str(positive),
            "actual_cap":str(min(ordinary,positive)-5*G),
            "ordered_derivatives":[str(s) for s in alpha],
            "integer_tangent_loss":str(integer_loss),"actual_tick_loss":str(true_loss),
            "all_distinct_integer_allocations_ordinary_cap_upper":str(ideal-integer_loss)}


def verify_prior(root,data,main,manifest):
    p=manifest["sha256_by_path"]
    files={f"evidence/{kind}.{suffix}":root/f"round398/{kind}.{suffix}"
           for kind in ("scientific","onboarding","historical") for suffix in ("log","exit")}
    outputs={k:pin(path,p[k]) for k,path in files.items()}
    known=parse(data["round398/independent/verified.json"])
    need(known["frozen_candidate"]==parse(data["round398/independent/INPUTS.json"])
         and known["authenticated_original_entries"]==88 and Q(known["kappa"])==RATE
         and known["frozen_candidate"]["capsule/RESULT.json"]==PINS[f"{BASE}/RESULT.json"]
         and manifest["head"]==HEAD==main["comparator_head"]
         and main["pinned_inputs_by_path"]==p
         and data["round398/exact-head"].strip()==HEAD.encode()
         and f'"commit": "{HEAD}"'.encode() in data["round398/preflight.log"],
         "One exact complete signed comparator head and primary receipt")
    for k,d in PINS.items():
        expected=("comparator/"+k.removeprefix("round398/publish/") if k.startswith(BASE)
                  else "evidence/"+k.removeprefix("round398/") if k.startswith("round398/")
                  else "workspace/"+k)
        need(p[expected]==d,f"Primary and independent bytes match {expected}")
    science=outputs["evidence/scientific.log"]
    need(all(outputs[f"evidence/{name}.exit"].strip()==b"0" for name in ("scientific","onboarding","historical"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in science
         and all(f"PASS_CAPPED_ALLOCATION {mode}\n".encode() in science
                 for mode in ("price","calendar","raw","exterior","nested","product","setup"))
         and b"Ran 760 tests" in outputs["evidence/onboarding.log"]
         and b"OK (skipped=31)" in outputs["evidence/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in outputs["evidence/historical.log"],
         "Every prerequisite science and repository gate completed")
    return known,p


def profile_if_needed(root,archive,old,choice,k):
    cut,select,geom,stock,qualify=runpy.run_path(str(root/"round391/price/check.py"))["archived_caller"](archive)
    h=tuple(choice["h"])
    g=choice["g"]
    p=stock(SimpleNamespace(rank_logs=h,complex_log=g,eta=ETA))
    a=p["public_exponent_A"]
    first=(1<<a)+p["first_public_offset"]
    entry=old["entry"]
    prefix=up((k-Q(entry["kappa"]))*a)
    log_c=1+max(84500001,1602+220*g+128+320*sum(h),entry["log2_C"]+prefix)
    early=qualify(Q(entry["kappa"]),G,Q(entry["ordinary_rates"][-1]),Q(entry["gaussian_rate"]))
    late=qualify(k,G,k+5*G,Q(choice["positive"]))
    need(all((s["strict"],s["functional"])==(54,4) for s in (early,late))
         and early==entry["signed"] and log_c<=CLOCK and p["storage_upper"]=="6.2 p T < 297.6 n bits"
         and first%6==0 and first.bit_length()==a+1 and (first-6).bit_length()==a
         and a==geom["connected_exponent"](cut(h)[-1],g) and p["binary_cuts"]==list(cut(h)),
         "Single viable candidate's exact all-size signed budgets at the same resource caps")
    for i,c in enumerate(p["binary_cuts"],1):
        need([select(c+d,3,h) for d in (-1,0,1)]==[i-1,i,i] and select(c+1,i-1,h)==i-1,
             "Actual physical stage and nested predecessor contracts")
    return {"stock":p,"entry_conversion":prefix,"complete_log2_C":log_c,"terminal_signed":late}


def check(root,main,pinned_receipts,primary_digest,primary_script_digest,completed_digest):
    data={name:pin(root/name,di) for name,di in PINS.items()}
    _,receipt_pins=verify_prior(root,data,main,pinned_receipts)
    old=parse(data[f"{BASE}/RESULT.json"])
    term=old["terminal"]
    need(old["complete_log2_C"]==CLOCK and old["ordinary_floor"]==18960
         and Q(old["ordinary_finite_debit"])==D and Q(old["ordinary_child_contraction"])==Q(375,376)
         and Q(old["gaussian"]["raw_loss"])==DG and Q(old["gaussian"]["trial"])==C and old["gaussian"]["weights"]==[5,451]
         and (tuple(term["ordinary_H"]),term["numerical_H"],Q(term["kappa"]))==(OLD_HS,OLD_G,RATE),
         "Exact approved word, signed fixed stage invoice, resources and current rate")
    source=runpy.run_path(str(root/"round378/independent/accept.py"))["restore_reference"](root/BASE)
    need(len(source)==88 and sha(source[ARCHIVE_K7])==K7,"All exact archived signed source files")
    scope=main["scope"]
    need(scope["ordinary_height_min"]==OMIN and scope["height_max"]==MAX
         and scope["gaussian_height_min"]==GMIN and scope["recurring_log2_max"]==CLOCK
         and 0<scope["actual_evaluations"]==len(main["evaluations"])<=20,
         "Primary counted evaluations leave the independent four within aggregate 24")
    left,right=main["crossing"]
    gl,gr=left["g"],right["g"]
    need(GMIN<=gl<gr<=MAX and gr-gl==1,"Adjacent checked true crossing")
    best=main["optimum"]["g"]
    need(best in (gl,gr),"Primary winner is at the tested adjacent crossing")
    # Test the other immediate neighbor of the declared winner if it is in scope.
    side=2*best-(gr if best==gl else gl)
    heights=sorted({gl,gr,OLD_G} | ({side} if GMIN<=side<=MAX else set()))
    need(len(heights)<=4 and scope["actual_evaluations"]+len(heights)<=24,"Aggregate bounded cap tests")
    rows={g:evaluate(g) for g in heights}
    l,r=rows[gl],rows[gr]
    incumbent=rows[OLD_G]
    old_cap=Q(incumbent["actual_cap"])
    need(tuple(incumbent["h"])==OLD_HS and term["ordinary_rates"]==incumbent["earlier_ticks"]+[str(RATE+5*G)]
         and Q(term["gaussian_rate"])==Q(incumbent["positive"]) and RATE<old_cap==Q(main["old_installed_cap"]),
         "Reconstruct exact current installed ceiling using legal exact true ticks")
    for fresh,reported in ((l,left),(r,right)):
        need(list(reported["h"])==fresh["h"]
             and all(Q(reported[field])==Q(fresh[field]) for field in ("ideal","ordinary","positive","actual_cap")),
             "Independent exact reconstruction agrees at each adjacent cap")
    need(Q(l["positive"])<=Q(l["ordinary"]) and Q(r["ordinary"])<=Q(r["positive"]),
         "True crossing uses funded positive cap on left and ordinary cap on right")
    # For g<=gl the positive cap is <= left. For g>=gr the entire
    # ordinary set is nested in right's, regardless of slope change far away.
    outside_caps=Q(l["positive"])-5*G,Q(r["ordinary"])-5*G
    top=max(outside_caps)
    need(top==max(Q(l["actual_cap"]),Q(r["actual_cap"]))==Q(rows[best]["actual_cap"])==Q(main["family_ceiling"])
         and all(Q(row["actual_cap"])<=top for row in rows.values())
         and top-old_cap==Q(main["ceiling_delta"])>=0,
         "Whole-family upper bound at the actual discrete maximum under true ticks")
    budget={"clock":CLOCK,"ordinary_height_min":OMIN,"gaussian_height_min":GMIN,"maximum_native_H":MAX,
            "ordinary_floor":18960,"ordinary_debit":str(D),"gaussian_debit":str(DG),
            "primary_evaluations":scope["actual_evaluations"],"independent_evaluations":len(heights),
            "total_evaluations":scope["actual_evaluations"]+len(heights),"whole_family_crossing":[gl,gr]}
    r={"status":"EXACT_SCOPED_EXCLUSION","comparator":HEAD,"published_incumbent":str(RATE),
       "old_installed_cap":str(old_cap),"family_ceiling":str(top),"family_ceiling_delta":str(top-old_cap),
       "scope":budget,"verified_rows":list(rows.values()),"outer_branch_caps":[str(x) for x in outside_caps],
       "upper_bound_argument":"For g<=left use monotonic positive cap. For g>=right use exact optimum over the nested ordinary height set. Integer tangent gap exceeds the exact tick loss at each tested vertex.",
       "pinned_exact_source_and_log_paths":PINS|{key:value for key,value in receipt_pins.items() if key.startswith("evidence/")},
       "primary_receipt_sha256":primary_digest,"primary_script_sha256":primary_script_digest,
       "completed_manifest_sha256":completed_digest}
    if top==old_cap:
        need(main["status"]=="EXACT_SCOPED_EXCLUSION" and "candidate_kappa" not in main,
             "No redundant candidate advances when exact upper is equal")
        return r
    k=Q(main["candidate_kappa"])
    need(main["status"]=="VIABLE_PRICE_ONLY" and old_cap<k<top,
         "Actual true ticks certify a positive candidate strictly beyond the whole installed old crossing")
    actual=profile_if_needed(root,source,old,rows[best],k)
    need(actual["stock"]==main["stock"] and actual["entry_conversion"]==main["entry_conversion"]
         and actual["complete_log2_C"]==main["clock"] and actual["terminal_signed"]==main["terminal_signed"],
         "Candidate literal supplier budgets match independently")
    r.update(status="VIABLE_PRICE_ONLY",candidate_kappa=str(k),exact_certified_candidate_delta=str(k-RATE),
             separation_from_prior_installed_cap=str(k-old_cap),candidate_price=actual)
    return r


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for name in ("inputs","primary","primary-script","complete","out"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--primary-sha256",required=True)
    p.add_argument("--primary-script-sha256",required=True)
    p.add_argument("--complete-sha256",required=True)
    a=p.parse_args()
    signal.alarm(60)
    raw=pin(a.primary,a.primary_sha256)
    pin(a.primary_script,a.primary_script_sha256)
    completed=pin(a.complete,a.complete_sha256)
    result=check(a.inputs.resolve(),parse(raw),parse(completed),a.primary_sha256,
                 a.primary_script_sha256,a.complete_sha256)
    signal.alarm(0)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
