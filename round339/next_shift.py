"""Prospective R340: one global bound for fixed p20/q=.749 and scalar shifts."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import signal
import sys
from time import monotonic
from types import ModuleType

CUT = 2700
P, V, Q = 20,451,F(749,1000)
BIT = "538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749"
R339 = "41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e"
HELP = "2df053c036c3bf8c3f4f6deccdcdfa3d4821b3c801c6410fe0e377dba6149d23"

def experiment(args, out):
    code=args.previous_screen.read_bytes()
    if sha256(code).hexdigest()!=HELP:
        raise ValueError("wrong previous screen")
    helper=ModuleType("frozen_newton")
    exec(compile(code,str(args.previous_screen),"exec"),helper.__dict__)
    data=helper.read(args.bit_source,BIT,True)
    old=helper.read(args.round339_receipt,R339)
    if (old["p"],old["h"],old["uniform_J"],F(old["mean"]),old["pins"]["BIT-451.json"])!=(20,1804,786,Q,BIT):
        raise ValueError("wrong complete comparator")
    mu=list(map(F,old["moments"]))
    lo,hi=map(F,data["uniform"]["eta"])
    if len(mu)!=P+1 or mu[:2]!=[1,Q] or any(m<Q**k for k,m in enumerate(mu)):
        raise ValueError("formal numerator Jensen lower bound is unavailable")
    if not (2**(10*CUT)>=11**(17*V) and 134**20<=11**41 and 134>11):
        raise ValueError("exact logarithmic cut guards failed")
    large_lower=((F(17,10)+Q)/(F(17,10)+F(41,20)))**P
    out["large_shift"]={"from":CUT,"formal_height_zero_lower":str(large_lower),"eta_upper":str(hi),
                        "ruled_out":large_lower>=hi}
    if large_lower<hi:
        return "unresolved upper shift half-line; no numerical site sweep"
    H=data["uniform"]["H"]
    h=CUT-1
    J=(((H+h)**P)//h**P).bit_length()
    if not ((h**P << (J-1)) <= (H+h)**P < (h**P << J)):
        raise ValueError("carrier debit inequality failed")
    tick=F(1,10**14)
    cover=F(data["separation"]["trial"])-F(J,H)-F(1,H*2**44)
    rate=F(data["cover_and_stock"]["seed"])
    rho=F(data["cover_and_stock"]["rho"])
    if not 0<rho<1:
        raise ValueError("stage monotonicity unavailable")
    for _ in range(7):
        rate=(1-rho)*cover+rho*rate
    continuous=rate-7*tick
    # If a candidate is an integral tick and candidate+7*tick < rate, then
    # candidate <= (ceil(continuous/tick)-1)*tick, even at exact grid equality.
    largest_tick=(-((-continuous)//tick)-1)*tick
    ceiling=F(data["raw_crossing"][1])-F(old["uniform_J"],H)-7*tick
    out["small_shift"]={"inclusive":[1,h],"optimistic_min_carrier_loss_units":J,
                        "covered_upper":str(cover),"unrounded_stage_upper":str(rate),
                        "continuous_upper_after_seven_ticks":str(continuous),
                        "strict_grid_upper_after_seven_ticks":str(largest_tick),
                        "old_relaxed_ceiling":str(ceiling),"old_claim":old["candidate_grid_claim"]}
    if continuous<=ceiling:
        return "entire positive-integer shift family excluded at fixed continuous seven-test price"
    if largest_tick<=ceiling:
        return "entire positive-integer shift family excluded on the fixed comparison grid; continuous relaxation open"
    # Allow one exact candidate only. Charging the old extraction/stages at the
    # optimistic endpoint also upper-bounds the literal exporter at every smaller h.
    helper.P,helper.H_SHIFT=P,h
    try:
        priced=helper.price(data,old)
    except ValueError as error:
        out["endpoint_price_guard"]=str(error)
        return "endpoint price guard fails; remaining smaller shifts unresolved"
    out["endpoint_price"]=priced
    if not priced["passes"]:
        if F(priced["claim"])<=ceiling:
            return "fixed literal exporter ceiling excludes the whole family; looser grid price unresolved"
        return "endpoint cannot pass terminal/stage guards; remaining smaller shifts unresolved"
    if F(h+(134**V).bit_length()-1,h)**P<=F(data["uniform"]["ambient_power"][1]):
        return "endpoint sufficient base guard fails; smaller shifts unresolved"
    with localcontext() as ctx:
        ctx.prec=80
        ln2,ln11,ln134=(Decimal(n).ln() for n in (2,11,134))
        a_hi=F(h,V)*F(ln2.next_plus())/F(ln11.next_minus())
        a_lo=F(h,V)*F(ln2.next_minus())/F(ln11.next_plus())
        c_lo=F(ln134.next_minus())/F(ln11.next_plus())
    scale=10**6
    helper.A=F(-((-a_hi*scale)//1),scale)
    helper.B=F((a_lo+c_lo)*scale//1,scale)
    ns,ds=helper.newton(mu)
    if len(ns)!=21 or min(ds)<=0:
        raise ValueError("coefficient domain mismatch")
    out["endpoint"]={"h":h,"A_upper":str(helper.A),"B_lower":str(helper.B),
                     "beta":str(helper.BETA),"ratios":{}}
    for j in [0,P]+list(range(1,P)):
        out["endpoint"]["ratios"][str(j)]=str(ns[j]/ds[j])
        if ns[j]>=lo*ds[j]:
            return "endpoint sufficient coefficient screen fails; smaller admissible shifts unresolved"
    return "endpoint passes fully priced component; independent proof and signed consumer required"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-source",type=Path,required=True)
    parser.add_argument("--round339-receipt",type=Path,required=True)
    parser.add_argument("--previous-screen",type=Path,default=Path(__file__).resolve().parents[1]/"round337"/"next_minimum.py")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if sys.version_info[:2]!=(3,12) or sys.implementation.name!="cpython" or args.out.exists():
        parser.error("requires CPython 3.12 and a new output path")
    out={"p":P,"q":str(Q),"cut":CUT,"discovery_seconds":45,"reserved_seconds":15,
         "maximum_cost_cases":2,"maximum_endpoint_candidates":1,"maximum_coefficients":21,
         "inputs":{"BIT-451.json":BIT,"round339/independent/receipt.json":R339,"round337/next_minimum.py":HELP}}
    def stop(*_):
        raise TimeoutError
    signal.signal(signal.SIGALRM,stop)
    start=monotonic()
    signal.alarm(45)
    try:
        out["decision"]=experiment(args,out)
    except TimeoutError:
        out["decision"]="CAPPED; uncertified portions of the domain remain unresolved"
    finally:
        signal.alarm(0)
    out["discovery_elapsed"]=monotonic()-start
    with args.out.open("x") as stream:
        json.dump(out,stream,indent=2)
        stream.write("\n")
    print(out["decision"])
    return 2 if out["decision"].startswith("CAPPED") else 0

if __name__=="__main__":
    raise SystemExit(main())
