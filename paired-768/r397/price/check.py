"""One fixed-invoice redistribution of the existing ordinary and positive ranks."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal

HEAD="04228ea5a1292cf8526a20037060f6fc6e15a858"
PKG="research/p104-weighted-ordinary-floor"
OLD="round396/publish/"+PKG
TIER="research/tiered-native-multiplier/"
K0,K=Q(".00389821126"),Q(".00389821380")
B,C=Q(4391986206293,2**50),Q(17145637307,2**42)
D,DG=Q(1405,1024),Q(64944,2**19)
G,ETA=Q(1,10**18),Q(".0039")
OLD_H,HS=(8192,129406,523443),(8192,124986,524288)
OLD_G,H=485263,490463
L=18960
K7="9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"

PINS={
    "round396/exact-head":"f9ee2bc08c8f771bcaea4ba08412acd2e71b813ca7526ac362a3b017b56c2bd7",
    "round396/preflight.log":"09b680274cad34f50e1d55916989555e2d0463987dfce537f69c67fd6fb4e8f2",
    "round396/independent/verified.json":"79042dce46983afdcf6891d410cfb72bcbc897229c7d05d22c67cfe7b61459fb",
    "round396/independent/INPUTS.json":"46720209acf17c9924a0c715bda130d8df7ed5d8484405bd615d0ed3bf0e3b66",
    "round396/independent/accept.py":"575e8eb3f85b71eb485c874c3d1006c9c02fef84c4dfa6ae59fae773ffc7e5b5",
    "round394/independent/accept.py":"a1e240a31f4c61d036c56b421df91bb36c15c4133f0ebb604773130ddfca7e31",
    "round391/price/check.py":"5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    "round378/independent/accept.py":"001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round395/price/check.py":"7ebb5841ed9088564f1ec5a866a1c448db32f7436a2ecf973fd951a66ade93c0",
    "round375/independent/coupling.py":"fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    f"{OLD}/RESULT.json":"8754f0ffe158404b2f3df2a9e94ce20b77b2e7e62882794d614b7eea2c6bdb60",
    f"{OLD}/prepare.py":"e4dea11a94e13b7ae5a70544e6dff8fdcc0de98533767cd04c1aadff95766682",
    f"{OLD}/peer8057.tar.gz":"0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    f"{OLD}/PEER-SOURCE.json":"798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
}
REPLAYS={f"round396/{m}.{ext}" for m in ("scientific","onboarding","historical") for ext in ("log","exit")}


def need(p,why):
    if not p:
        raise ValueError(why)


def digest(raw):
    return sha256(raw).hexdigest()


def pin(path,sha):
    raw=path.read_bytes()
    need(digest(raw)==sha,f"Exact input {path.name}")
    return raw


def unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,f"Duplicate pin {k}")
        out[k]=v
    return out


def parse(b):
    return json.loads(b,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def check(root,complete):
    need(complete.keys()==REPLAYS,"All exact current registered and repository logs")
    pins=PINS|complete
    data={n:pin(root/n,sha) for n,sha in pins.items()}
    science=data["round396/scientific.log"]
    need(data["round396/exact-head"].strip()==HEAD.encode()
         and f'"commit": "{HEAD}"'.encode() in data["round396/preflight.log"]
         and all(data[f"round396/{state}.exit"].strip()==b"0" for state in ("scientific","onboarding","historical"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in science
         and all(f"PASS_ORDINARY_FLOOR {mode}\n".encode() in science
                 for mode in ("price","calendar","raw","exterior","nested","product","setup"))
         and b"Ran 760 tests" in data["round396/onboarding.log"] and b"OK (skipped=31)" in data["round396/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in data["round396/historical.log"],
         "Exact completed same-head scientific, repository and historical controls")
    old=parse(data[f"{OLD}/RESULT.json"])
    independent=parse(data["round396/independent/verified.json"])
    freeze=parse(data["round396/independent/INPUTS.json"])
    need(independent["literal_pins"]==freeze
         and freeze["capsule/RESULT.json"]==PINS[f"{OLD}/RESULT.json"]
         and freeze["capsule/prepare.py"]==PINS[f"{OLD}/prepare.py"]
         and Q(independent["kappa"])==K0 and independent["both_paid_moments"]=="375/376"
         and old["ordinary_floor"]==L and Q(old["ordinary_finite_debit"])==D
         and Q(old["gaussian"]["raw_loss"])==DG and Q(old["gaussian"]["trial"])==C,
         "Retain both proved tariffs, native binary floor and budgets")
    archive=runpy.run_path(str(root/"round378/independent/accept.py"))["restore_reference"](root/OLD)
    need(len(archive)==88 and digest(archive[TIER+"source/strong-bit-k7.json.gz"])==K7,
         "All exact archived productive and paid sources")
    need(Q(75,32)/Q(47,20)==Q(375,376) and 1/(1-Q(375,376))==376
         and old["gaussian"]["weights"]==[5,451],"Retained child and signed weighted Gaussian supplier")
    # R396 paid proofs hold uniformly for every installed rank; screen the same
    # all-size envelope and only the new scalar caller allocation here.
    charged=runpy.run_path(str(root/"round395/price/check.py"))
    power=runpy.run_path(str(root/"round375/independent/coupling.py"))["power_interval"]
    _,F=charged["factor"](power,L)
    need(F**1024<2**1405 and up(F*10**15)==independent["new_factor_upper_1e15"]
         and independent["physical_t_min_h_checked"]<=min(HS),
         "All actual native ranks satisfy the same proved finite transport envelope")
    ordinary=runpy.run_path(str(root/"round394/independent/accept.py"))["ordinary"]
    rates_old,upper_old=ordinary(OLD_H,D,K0+5*G)
    pos_old=C-DG/OLD_G
    old_cap=min(upper_old,pos_old)-5*G
    need(old["terminal"]["ordinary_rates"]==[str(x) for x in rates_old]
         and old["terminal"]["ordinary_H"]==list(OLD_H) and old["terminal"]["numerical_H"]==OLD_G
         and Q(old["terminal"]["gaussian_rate"])==pos_old
         and Q(old["terminal"]["kappa"])==K0<old_cap, "Known-good exact predecessor cap")
    _ideal,cap=ordinary(HS,D)
    pos=C-DG/H
    trial=K+5*G
    available=min(cap,pos)-5*G
    result={"status":"PRICE_FAIL","comparator_head":HEAD,"comparator_rate":str(K0),"target":str(K),
            "ordinary_heights":HS,"positive_height":H,"ordinary_floor":L,
            "ordinary_debit":str(D),"gaussian_debit":str(DG),"prior_installed_complete_cap":str(old_cap),
            "candidate_ideal_complete_cap":str(available),"exact_path_pins":pins}
    if K<=old_cap or K>=available:
        return result

    cuts,select,geom,resources,qualify=runpy.run_path(str(root/"round391/price/check.py"))["archived_caller"](archive)
    profile={}
    for name,hs,h,k in (("entry",(3000,3080),1024,Q(".00345")),("terminal",HS,H,K)):
        booked=k+5*G
        rates,max_ordinary=ordinary(hs,D,booked)
        state=resources(SimpleNamespace(rank_logs=hs,complex_log=h,eta=ETA))
        a=state["public_exponent_A"]
        q=state["first_public_offset"]
        header=(1<<a)+q
        signed=qualify(k,G,booked,C-DG/h)
        need((signed["strict"],signed["functional"])==(54,4)
             and geom["connected_exponent"](cuts(hs)[-1],h)==a
             and list(cuts(hs))==state["binary_cuts"]
             and header%6==0 and header.bit_length()==a+1 and (header-6).bit_length()==a,
             "Each complete signed tier and both public dispatch boundaries")
        checked=[]
        for i,c in enumerate(state["binary_cuts"],1):
            result_at=[select(c+j,len(hs),hs) for j in (-1,0,1)]
            need(result_at==[i-1,i,i] and select(c+1,i-1,hs)==i-1,
                 "Native adjacent and clipped old stage controls")
            checked.append([c,*result_at,i-1])
        profile[name]={"ordinary_rates":[str(t) for t in rates],"signed":signed,
                       "ordinary_margin":str(max_ordinary-booked),"positive_margin":str(C-DG/h-booked),
                       "stock":state,"geometry":geom["entrance_geometry"](a),"controls":checked}
    need(profile["entry"]["ordinary_rates"]==old["entry"]["ordinary_rates"]
         and profile["entry"]["stock"]==old["entry"]["stock"]
         and profile["entry"]["geometry"]==old["entry"]["geometry"]
         and profile["entry"]["signed"]==old["entry"]["signed"],
         "Actual early supplier and its accounting are identical")
    s=profile["terminal"]["stock"]
    a=s["public_exponent_A"]
    a_old=old["terminal"]["stock"]["public_exponent_A"]
    b=128+320*sum(HS)
    clock=max(84500001,1602+220*H+b)
    premium=up((K-Q(".00345"))*a)
    complete_clock=1+max(clock,old["entry"]["log2_C"]+premium)
    need(min(HS)>=8192 and max(*HS,H)==524288
         and s["storage_upper"]=="6.2 p T < 297.6 n bits"
         and 320*(sum(HS)-sum(OLD_H))+220*(H-OLD_G)==0
         and complete_clock==old["complete_log2_C"]==318292711,
         "The same existing all-size clock and native rank ceiling")
    w=2**38
    z=2*w+2
    setup=(2**68+1)*(8*4*w*2**68*512*128+2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2+2**120)*2**32
    need(max(*HS,H).bit_length()==20 and setup==old["native_setup_transition_upper"]<2**228
         and old["native_setup_grade_actions"]==269057152<2**32,
         "Entire fixed setup still fits the admitted 20-bit ceiling")
    floors=[up(D/(B-trial)),up(DG/(C-trial))]
    result.update(status="VIABLE_PRICE_ONLY",delta_kappa=str(K-K0),gain_percent=str(100*(K-K0)/K0),
                  exact_separation_from_old_cap=str(K-old_cap),profiles=profile,
                  candidate_booked_complete_cap=str(min(max_ordinary,pos)-5*G),
                  full_agreed_clock=complete_clock,ordinary_log2_b=b,cofinal_log2_c=clock,entry_surcharge=premium,
                  public_exponent_shift=a-a_old,maximum_native_h=max(*HS,H),native_h_bits=20,fixed_setup_bound=setup,
                  single_profile_height_floors=floors,
                  remaining_gate="Literal native dispatch, changed ordinary rank seams, true positive placement and complete independent signed replay.")
    return result


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for f in ("inputs","complete","out"):
        p.add_argument("--"+f,type=Path,required=True)
    a=p.parse_args()
    signal.alarm(60)
    r=check(a.inputs.resolve(),parse(a.complete.read_bytes()))
    signal.alarm(0)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
