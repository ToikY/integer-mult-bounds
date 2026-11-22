"""Price complementary quarter packets on the existing width-two band grid."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import runpy
import subprocess
import sys
import time

PINS = {
    "quarter": "dbde66c13af0f44c4ba55690ee7a4324111c29961211f740eea2c3b1f513a037",
    "split": "d26a1f9ea8fd78900f45bf83c29ee2b700d015c231a82eab1cad54283b4aec66",
    "transfer": "7164831a5dd9f5c6231bf4c3f4b2061d91cbfab559071a0a5d68966e3f7ac55c",
    "outer_budget": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
}
UNIT = 2**112


def ceil(x):
    return -(-x.numerator//x.denominator)


def bounds_integer(r, t):
    n,d=t.numerator,t.denominator
    assert r>0 and n>=0 and not d&(d-1)
    whole,remainder=divmod(n,d)
    a=b=UNIT*r**whole
    low=high=UNIT*r
    while d>1:
        d//=2
        low=isqrt(low*UNIT)
        high=isqrt(high*UNIT-1)+1
        if remainder&d:
            a=a*low//UNIT
            b=-(-b*high//UNIT)
    return a,b


def bounds(r,t):
    p=Q(r)
    x,y=bounds_integer(p.numerator,t)
    if p.denominator==1:
        return Q(x,UNIT),Q(y,UNIT)
    a,b=bounds_integer(p.denominator,t)
    return Q(x*UNIT//b,UNIT),Q(-(-y*UNIT//a),UNIT)


def evaluate(a):
    for key,expected in PINS.items():
        assert sha256(getattr(a,key).read_bytes()).hexdigest()==expected,key
    q,s=[json.loads(p.read_bytes()) for p in (a.quarter,a.split)]
    c=Q(q["hypothetical_trial"])
    gauss_cap_lo,gauss_cap_hi=map(Q,q["quarter_raw_bracket_and_derivative_upper"][:2])
    old_raw_hi=Q(q["old_raw_bracket_and_derivative_upper"][1])
    old_k=Q(q["old_comparator"])
    h,D,L,ambient=20_000_000,10**18,32768,1224
    kappa=Q(int((c-Q(39,256*h)-Q(1,10**13))*10**13),10**13)
    assert c.denominator==2**40 and old_raw_hi<c<gauss_cap_lo
    assert kappa>old_raw_hi-Q(39,256*h)-Q(5,D)>old_k
    assert Q(1)-c>Q(996,1000)

    target={Q(r):n for r,n in s["source_targets"]}
    paid={Q(r):n for r,n in s["source_paid"]}
    paid[1]+=2
    del paid[Q(1,2)]
    paid.update({Q(1,4):1006,Q(3,4):1006})
    assert sum(target.values())==105216<2**17 and sum(paid.values())==564142<2**20
    assert min(paid)==Q(1,4) and max(paid)==448 and max(target)==1032
    pm={r:n*bounds(r,1-c)[1] for r,n in paid.items()}
    tm={k:n*bounds(k,1-c)[0] for k,n in target.items()}
    ratio=sum(pm.values())/sum(tm.values())
    assert 0<ratio<1 and bounds(1032,c)[1]<Q(106,100)
    p_low=sum(n*bounds(r,1-c)[0] for r,n in paid.items())
    t_high=sum(n*bounds(k,1-c)[1] for k,n in target.items())
    assert 100*p_low>99*t_high and p_low>10

    cells={(Q(r),Q(k)):Q(v) for r,k,v in q["checks"]["coupling"][1]}
    assert len(cells)==55 and max(r/k for r,k in cells)==Q(3,4)
    assert cells[448,1032]==1 and min(cells.values())/sum(target.values())>Q(1,2**64)
    row,col=defaultdict(Q),defaultdict(Q)
    least_lower=None
    for (r,k),share in cells.items():
        row[r]+=share
        col[k]+=share*pm[r]
        assert 4*k>=5*r
        errors=(Q(0),)
        if r==Q(1,4):
            errors+=(Q(-1,2),)
        elif r==Q(3,4):
            errors+=(Q(1,2),)
        for error in errors:
            lower=8*k-10*r+error
            upper=10*k-8*r+error
            assert 0<=lower and upper<10*k
            assert error<=8*r
            least_lower=lower if least_lower is None else min(least_lower,lower)
    assert dict(row)=={r:1 for r in paid}
    assert dict(col)=={k:v*ratio for k,v in tm.items()}

    # The reciprocal root range doubles with min paid rank 1/4. At H>=1024
    # one grid unit is less than the gap between 1/(4128N) and 1/(8192N).
    # There are at most 40 root iterations and 41 rounded products.
    h_min=1024
    N=2**h_min
    grid_bits=64*(h_min+1)
    assert Q(1,4128*N)-Q(1,2**grid_bits)>Q(1,8192*N)
    lipschitz_bits=(h_min+14)//2  # H even here; next assert proves decreasing slack.
    # Each root is at most 2^lipschitz_bits-Lipschitz. Permit 4 times this
    # factor per step including rounding and one extra limiting step.
    root_width_bits=41*(2+lipschitz_bits)
    mass_error_bits=root_width_bits+6+6*h_min+2-grid_bits
    assert mass_error_bits<-132
    assert 41<2*(64-6)  # Exponent strictly falls with H in each parity class.
    assert mass_error_bits+41<-132  # Allows the odd-height ceiling and all later H.
    assert (2*(N//(2048*ambient)))>L*4128

    # Analytic inequalities supply the same continuous lower bound for both
    # the terminal and external sides. The positive ln term uses
    # ln(5/4) >= 2*((5/4)-1)/((5/4)+1) = 2/9.
    assert Q(100,99)**250>4 and c<Q(1,250)
    psi_over_paid=Q(99,100)*Q(2,9)
    assert psi_over_paid>Q(19,100)
    fringe=Q(10)*Q(106,100)/(Q(996,1000)*Q(99,100)*Q(19,100))
    assert fringe<64
    delta=Q(1,2**128)
    f=Q(256,255)*Q(4097,4096)*Q(1028,1024)*bounds(1024*ambient*L,c)[1]
    f*= (1+Q(64,L)+delta)/((1-Q(10,L))*(1-delta)**3)
    assert f**256<2**39
    assert Q(4,5)*(L+2)<Q(5,6)*L and Q(6,5)**77>2**20
    assert (2**46)*(N**2)<Q(N**6,2**132)
    assert Q(N**77,N**82)*2*N**6*sum(paid.values())*N<Q(N**6,2**132)

    b=Q(4391986206293,2**50)
    first_limit=Q(249,250)*(b-Q(11,8*60_000))
    first=Q(int(first_limit*10**21)-1,10**21)
    second=(249*(b-Q(11,8*960_000))+first)/250
    ordinary=kappa+Q(5,D)
    assert first<ordinary<min(second,Q(39,10000))
    pos=c-Q(39,256*h)
    outer=runpy.run_path(str(a.outer_budget))
    signed=outer["qualify"](kappa,Q(1,D),ordinary,pos)
    _,_,old_at_new=outer["margins"](kappa,Q(1,D),ordinary,old_raw_hi-Q(39,256*h))
    assert old_at_new<0
    return {
        "model":"even band grid, floor(w/4) and w-floor(w/4)",
        "source_pins":PINS,"comparator":q["exact_head"],
        "candidate_c":str(c),"kappa":str(kappa),"delta_vs_8054":str(kappa-old_k),
        "delta_vs_old_raw_less_same_debits":str(-old_at_new),
        "quarter_crossing_upper":str(gauss_cap_hi),
        "gaussian_debit_preserved":"39/(256*H)",
        "clock_factor_outward_times_1000000":ceil(f*10**6),
        "minimum_interior_residual_lower":str(least_lower),
        "fringe_coefficient_upper":str(fringe),
        "reciprocal_mass_enclosure_error_at_min_H_bits_upper":mass_error_bits,
        "signed":signed,"paid":sum(paid.values()),"productive":sum(target.values()),
        "cells":len(cells),
        "work_remaining":"literal parity-aware scheduler, complete installed and independent signed replay",
    }


if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    for n in ("quarter","split","transfer","outer_budget","out"):
        parser.add_argument("--"+n.replace("_","-"),type=Path,required=True)
    parser.add_argument("--child",action="store_true")
    a=parser.parse_args()
    if a.child:
        result=evaluate(a)
        with a.out.open("x") as out:
            json.dump(result,out,indent=2,sort_keys=True)
            out.write("\n")
    else:
        start=time.perf_counter()
        r=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=45)
        print(f"exit={r.returncode} seconds={time.perf_counter()-start:.3f}")
        raise SystemExit(r.returncode)
