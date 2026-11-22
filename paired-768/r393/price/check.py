"""Screen one exact ordinary debit and its complete signed scalar invoice."""
from argparse import ArgumentParser
import ast
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import re
import runpy
import signal
from types import SimpleNamespace

HEAD = "ffa64503646a62a7ac3cd2c47787d670da911f89"
PACKAGE = "research/p104-weighted-ordinary-transfer"
OLD_PATH = "round392/publish/" + PACKAGE
FREQ = "research/frequency-weighted-native-multiplier/"
TIER = "research/tiered-native-multiplier/"
K0,K = Q(".00389821057"),Q(".00389821103")
CB,CG = Q(4391986206293,2**50),Q(17145637307,2**42)
D0,D = Q(11,8),Q(703,512)
DG,G,ETA = Q(64944,2**19),Q(1,10**18),Q(39,10**4)
BEFORE,HEIGHTS = (8192,129406,524403),(8192,129406,523763)
HG0,HG = 483871,484799
UNIT = 2**112
K7 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"

PINS = {
    "round392/exact-head": "6e3af7c5273d0d0bbd0767b4b67e19696b5b16ea6b5c07fb87a91bfebe0d8cab",
    "round392/preflight.log": "910725b496aced72618a0d222532fa129e3251ee37dad247306065fdea168291",
    "round392/independent/verified.json": "dcf57d8bab8cfc76769b0f9d8b570d233e670032b8ab2aed481172ff21c3c2a9",
    "round378/independent/accept.py": "001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round375/independent/coupling.py": "fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    "round391/price/check.py": "5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    f"{OLD_PATH}/RESULT.json": "65b29858741c054434863612a357b9c6b833d8865530812659943293ff1155f5",
    f"{OLD_PATH}/prepare.py": "3862a6fb149d5d35be194ace5dd9c135013e46abdaa3d6396641a85af794e788",
    f"{OLD_PATH}/PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    f"{OLD_PATH}/peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}
LOGS = {f"round392/{mode}.{ext}" for mode in ("scientific","onboarding","historical") for ext in ("log","exit")}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def pin(path, digest):
    raw=path.read_bytes()
    need(sha256(raw).hexdigest()==digest,f"Authentic dependency {path.name}")
    return raw


def unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,f"Repeated manifest key {k}")
        out[k]=v
    return out


def parse(data):
    return json.loads(data,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def stage_prior(heights,debit,*,ideal=False):
    prior=Q()
    booked=[]
    for index,h in enumerate(heights):
        local=CB-debit/h
        cap=min(ETA,(249*local+prior)/250)
        if index+1<len(heights):
            next_prior=cap if ideal else Q((10**21*cap).__floor__()-1,10**21)
            need(0<=prior<next_prior<=cap,"Exact earlier ordinary bookings")
            booked.append(next_prior)
            prior=next_prior
    return booked,cap


def finite_price(archive, power):
    raw=archive[FREQ+"receipt.py"]
    need(sha256(raw).hexdigest()=="82d921fdc33006e2d356d8bf78f3c85777722322d716be44b42bc763a04c8095",
         "Exact signed tape-factor inventoried source")
    source=ast.parse(raw,filename=FREQ+"receipt.py")
    functions=[node for node in source.body if isinstance(node,ast.FunctionDef) and node.name=="tape_factor"]
    need(len(functions)==1,"One archived calibrated calendar tape factor")
    source.body=functions
    env={"Q":Q,"power_interval":power,"UNIT":UNIT}
    exec(compile(source,FREQ+"receipt.py","exec"),env)
    child=Q(47,20)
    factor=env["tape_factor"](134,CB)*child
    delta=Q(1,2**128)
    reduced=Q(256,255)*Q(4097,4096)*Q(257,256)
    physical=reduced*Q(power(Q(1024*134*32768),CB)[1],UNIT)
    physical*= (1+Q(64,32768)+delta)/((1-Q(10,32768))*(1-delta)**3)
    need(factor==physical*child and Q(75,32)/child==Q(375,376)
         and 1/(1-Q(375,376))==376,
         "Unchanged routed child operation and all-depth volume contraction")
    # The exact rational power comparison needs no real logarithm or floating approximation.
    enough=factor.numerator**512 < factor.denominator**512 << 703
    old=factor.numerator**8 < factor.denominator**8 << 11
    need(old,"Known-good prior finite debit")
    new_floor=Q(power(Q(2),D)[0],UNIT)
    margin=new_floor-factor
    need(not enough or margin>0,"Independent outward fixed-point check of the factor")
    return enough,dict(finite_factor_ceiling_1e15=up(factor*10**15),
                       physical_factor_ceiling_1e15=up(physical*10**15),
                       required_debit_cap_floor_1e15=(new_floor*10**15).__floor__(),
                       fully_charged_margin_floor_1e15=(margin*10**15).__floor__(),
                       old_debit_positive_control=old,child_factor=str(child),volume_ratio="375/376",
                       all_depth_multiplier=376,ambient=134,ordinary_lower_fence=32768)


def audit_old_uses(archive):
    owner_clock=TIER+"CLOCK.md"
    old_theorem=FREQ+"WeightedNumerical.lean"
    need(sha256(archive[owner_clock]).hexdigest()=="cf71e4a3216df23eb7e4fa8a8d9de3735e6257c65ca8a60a5085d9f3c90c4ecb"
         and sha256(archive[old_theorem]).hexdigest()=="2017bae8064554efb13c564503d8f88c4615e9f733a74aa5eaf4047e5bd8af94",
         "Prior proof and historical theorem pins")
    re_old=re.compile(r'(?<![0-9])11 ?/ ?\(?8|(?<![0-9])11, ?8\b|\*\*8\s*<\s*2\*\*11')
    result={}
    for name,s in sorted(archive.items()):
        if name.endswith((".py",".md",".lean",".patch")):
            lines=[str(i) for i,l in enumerate(s.decode().splitlines(),1) if re_old.search(l)]
            if lines:
                result[name]=lines
    need(owner_clock in result and old_theorem in result and FREQ+"receipt.py" in result,
         "Audit active and reference old-debit literals")
    return {"archived_old_debit_loci":result,
            "required_active_changes":[
                "frequency-weighted-native-multiplier/receipt.py: stronger exact tape_factor control, terminal ordinary bank, terminal height floor and setup height-bit bound <=20 (new actual width 19)",
                "registered stage seam verifier: stronger debit in tested terminal bookings and same-height old-debit negative control",
                "installed terminal Profile: ordinary H3, Gaussian height and booked rate",
                "proof: replace the terminal finite factor inequality and recurrence coefficient; prove same contraction and recompute all public and private seams",
             ],
            "historical_only":[
                "archived tiered-native-multiplier/receipt.py and CLOCK.md: predecessor fixed price and charged geometry",
                "archived frequency-weighted-native-multiplier/WeightedNumerical.lean concrete example: old fixed 517429 floor; generic boundedStages lemma still applies",
                "archived frequency-weighted-native-multiplier/independent_price.py comparison to #8056 uses its original 11/8",
            ],
            "no_physical_k7_or_clock_change_required":True}


def exact_check(root, finished):
    need(finished.keys()==LOGS,"Pin all and only completed R392 science, onboarding and historical receipts")
    pins=PINS|finished
    frozen={path:pin(root/path,hash_) for path,hash_ in pins.items()}
    need(frozen["round392/exact-head"].strip()==HEAD.encode()
         and f'"commit": "{HEAD}"'.encode() in frozen["round392/preflight.log"],
         "Exact validated R392 commit and source artifact")
    need(all(frozen[f"round392/{n}.exit"].strip()==b"0" for n in ("scientific","onboarding","historical"))
         and all(f"PASS_ORDINARY_TRANSFER {mode}\n".encode() in frozen["round392/scientific.log"]
                 for mode in ("price","calendar","raw","exterior","nested","product","setup"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PACKAGE} outcome=completed".encode() in frozen["round392/scientific.log"]
         and b"Ran 760 tests" in frozen["round392/onboarding.log"] and b"OK (skipped=31)" in frozen["round392/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in frozen["round392/historical.log"],
         "Completed exact signed, repository and historical replays")
    old=parse(frozen[OLD_PATH+"/RESULT.json"])
    verified=parse(frozen["round392/independent/verified.json"])
    need(verified["comparator"]=="e4fccb224ce5d9bc530a8027d4f617a6a37d4562"
         and Q(verified["kappa"])==Q(old["terminal"]["kappa"])==K0
         and verified["frozen_candidate"]["capsule/RESULT.json"]==PINS[OLD_PATH+"/RESULT.json"],
         "Independent incumbent on the matching literal bytes")
    restore=runpy.run_path(str(root/"round378/independent/accept.py"))["restore_reference"]
    archive=restore(root/OLD_PATH)
    need(len(archive)==88 and sha256(archive[TIER+"source/strong-bit-k7.json.gz"]).hexdigest()==K7,
         "Same 88 signed source entries including K7")
    power=runpy.run_path(str(root/"round375/independent/coupling.py"))["power_interval"]
    enough, factor=finite_price(archive,power)
    before=old["terminal"]
    prior, ordinary0=stage_prior(BEFORE,D0)
    bound0=min(ordinary0,CG-DG/HG0)-5*G
    need(tuple(before["ordinary_H"])==BEFORE and before["numerical_H"]==HG0
         and [Q(x) for x in before["ordinary_rates"]]==prior+[K0+5*G]
         and Q(before["gaussian_rate"])==CG-DG/HG0
         and before["signed"]["strict"]==54 and before["signed"]["functional"]==4,
         "Reconstruct the actual complete R392 ceiling")
    need(old["gaussian"]["finite_loss"]["upper_divisor"]==1724
         and Q(old["gaussian"]["raw_loss"])==DG and Q(old["gaussian"]["trial"])==CG
         and old["gaussian"]["weights"]==[5,451],
         "Same paid Gaussian factor and exact source profile")
    prior, ordinary=stage_prior(HEIGHTS,D)
    _, ordinary_old=stage_prior(HEIGHTS,D0,ideal=True)
    Gaussian=CG-DG/HG
    target=K+5*G
    result={"status":"PRICE_OR_FACTOR_FAIL","comparator":HEAD,"kappa":str(K),"previous_kappa":str(K0),
            "tested_ordinary_heights":HEIGHTS,"tested_gaussian_height":HG,"new_ordinary_debit":str(D),
            "unchanged_gaussian_debit":str(DG),"prior_actual_installed_cap":str(bound0),
            "candidate_cap":str(min(ordinary,Gaussian)-5*G),"same_heights_ideal_cap_old_debit":str(ordinary_old-5*G),
            "ordinary_cap_margin":str(ordinary-target),"gaussian_cap_margin":str(Gaussian-target),
            "full_factor":factor,"pinned_inputs_by_path":pins}
    if not (enough and prior[-1]<target<min(ordinary,Gaussian)):
        return result
    need(K>bound0 and ordinary_old<target,"Strict old-certificate and same-height old-debit separators")
    cuts,dispatch,geom,stock,qualify=runpy.run_path(str(root/"round391/price/check.py"))["archived_caller"](archive)
    p=SimpleNamespace(rank_logs=HEIGHTS,complex_log=HG,eta=ETA)
    s=stock(p)
    a=s["public_exponent_A"]
    offsets=s["first_public_offset"]
    new_header=(1<<a)+offsets
    need(a==geom["connected_exponent"](cuts(HEIGHTS)[-1],HG) and list(cuts(HEIGHTS))==s["binary_cuts"]
         and a==1146634 and offsets==2 and new_header%6==0 and new_header.bit_length()==a+1
         and (new_header-6).bit_length()==a, "Real two-family threshold and exact ordinary geometry")
    decisions=[]
    for stage,cut in enumerate(s["binary_cuts"],1):
        decisions_at=[dispatch(cut+i,3,HEIGHTS) for i in (-1,0,1)]
        hop=dispatch(cut+1,stage-1,HEIGHTS)
        need(decisions_at==[stage-1,stage,stage] and hop==stage-1,"Exact clipped ordinary transitions")
        decisions.append([cut,*decisions_at,hop])
    entry=old["entry"]
    early=qualify(Q(entry["kappa"]),G,Q(entry["ordinary_rates"][-1]),CG-DG/entry["numerical_H"])
    late=qualify(K,G,target,Gaussian)
    need(early==entry["signed"] and all((x["strict"],x["functional"])==(54,4) for x in (early,late)),
         "Every exact signed gate at both literal rates")
    b=128+320*sum(HEIGHTS)
    c=max(84500001,1602+220*HG+b)
    premium=up((K-Q(entry["kappa"]))*a)
    complete=1+max(c,entry["log2_C"]+premium)
    need(min(HEIGHTS)>=8192 and complete==318293031<old["complete_log2_C"]==318293671
         and premium==514 and s["storage_upper"]=="6.2 p T < 297.6 n bits",
         "Paid high-fibre, precision, retimed stock and full recurring clock")
    bound=2**38
    width=2*bound+2
    scalar=2**16*(width+4)*(7*width+9)+8*2**16*(width+4)**2
    setup=(2**68+1)*(8*4*bound*2**68*512*128+scalar+2**120)*2**32
    need(max(HG,*HEIGHTS).bit_length()<=max(HG0,*BEFORE).bit_length()==20
         and setup==old["native_setup_transition_upper"]<2**228
         and old["native_setup_grade_actions"]==269057152<2**32,
         "All indexed native setup costs retained")
    result.update(status="VIABLE_PRICE_ONLY",delta_kappa=str(K-K0),gain_percent=str(100*(K-K0)/K0),
                  above_prior_installed_cap=str(K-bound0),early_signed=early,terminal_signed=late,
                  terminal_rates=[str(x) for x in prior+[target]],
                  terminal_stock=s,terminal_geometry=geom["entrance_geometry"](a),stage_seams=decisions,
                  log2_B=b,complete_log2_C=complete,entry_premium=premium,native_setup=setup,native_height_bits=max(HG,*HEIGHTS).bit_length(),
                  height_floors=[up(D/(CB-target)),up(DG/(CG-target))],
                  old_debit_source_audit=audit_old_uses(archive))
    return result


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--inputs",type=Path,required=True)
    p.add_argument("--complete",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    signal.alarm(60)
    result=exact_check(a.inputs.resolve(),parse(a.complete.read_bytes()))
    signal.alarm(0)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
