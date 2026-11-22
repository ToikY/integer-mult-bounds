"""Price the exact #8055 quarter inventory before any literal edit."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import importlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time

HEAD = "7b48187d99525ad59f560de3921ec7e48382484c"
BASELINE = "c5cbef6e558542d6e809aabb6ead89b9e51f7b1c"
K = Q(".0038982016137")
SCALE = 2**50
PINS = {
    "bootstrap.py":"74ac8f1d3af21f86cda48a3d50084d6fa5faf84b44ec2e5929b587f40f5bcfd1",
    "SOURCES.json":"7a10012734132909e99b0c6160d68d0b8647e1607d25679efb1f5315cf8e23de",
    "runtime.patch":"6c93961841be2abc3629928074e2c7917d264e94187276fc88a33f922a3c62e4",
    "grades.py":"340684fdd5ca0e611836b0e7301f1c339282ba532bf9e3ec8055944d8981f3c8",
    "installations.py":"1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df",
    "RESULT.json":"661e16fcb533b69b97ad2dc91ab81bed79c44e7fdce01306ce573cb6f0ed7fa7",
    "receipt.py":"3d0219eb2262ea64ccf2dc8da4d2877e32c519c4670d99577703f8bfc236ba61",
    "source/activation.py":"6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b",
    "source/outer_budget.py":"ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "check_phase_passes.py":"6afd65da931476680d88cb54336ffedf531c3063af181f75403d511e24e83b94",
    "NUMERICAL.md":"14b86724db522393981ed54b540a35f27bd952f3d95d6e6d14c5b23896811dc9",
    "CLOCK.md":"cf71e4a3216df23eb7e4fa8a8d9de3735e6257c65ca8a60a5085d9f3c90c4ecb",
}


def log_around_1(x):
    z=(x-1)/(x+1)
    low=2*sum(z**(2*i+1)/(2*i+1) for i in range(24))
    return low,low+2*z**49/(49*(1-z*z))


def log_rank(r):
    x,p=Q(r),0
    while x>=2:
        x/=2
        p+=1
    while x<1:
        x*=2
        p-=1
    lo,hi=log_around_1(x)
    a,b=log_around_1(Q(2))
    add=(p*a,p*b) if p>=0 else (p*b,p*a)
    return lo+add[0],hi+add[1]


def ceil(q):
    return -(-q.numerator//q.denominator)


def evaluate(peer, work):
    for name,expected in PINS.items():
        data=(peer/name).read_bytes()
        assert sha256(data).hexdigest()==expected,name
    sys.path.insert(0,str(peer))
    runpy.run_path(str(peer/"bootstrap.py"))["install"](work)
    sys.path.insert(0,str(work))
    import unpowered_price as core
    from installations import ENTRY, TERMINAL, BINARY_C, GAUSSIAN_C
    from grades import SCALES,SPLITS
    assert SCALES==(1,79) and SPLITS==1008
    assert (ENTRY.rank_logs,ENTRY.complex_log)==((3000,3080),1024)
    assert (TERMINAL.rank_logs,TERMINAL.complex_log)==((35327,559005),680000)
    profile=lambda name: json.loads((peer/"RESULT.json").read_bytes())[name]
    resource=runpy.run_path(str(peer/"source"/"activation.py"))["resource_receipt"]
    outer=runpy.run_path(str(peer/"source"/"outer_budget.py"))
    g=Q(1,10**18)
    fixed_rates={}

    def ordinary_limit(p):
        h1,h2=p.rank_logs
        c1=min(p.eta,Q(249,250)*(BINARY_C-Q(11,8*h1)))
        rate=Q(int(c1*10**21)-1,10**21)
        cap=min(p.eta,(249*(BINARY_C-Q(11,8*h2))+rate)/250)
        return rate,cap

    terminal_first,terminal_ordinary=ordinary_limit(TERMINAL)
    overall_cap=terminal_ordinary-5*g
    assert overall_cap<K
    denominator=Q(249,250)*BINARY_C+terminal_first/250-(K+5*g)
    assert denominator>0
    h2_min=int(Q(249,250)*Q(11,8)/denominator)+1
    assert h2_min>TERMINAL.rank_logs[-1]

    raw=core.word(*core.load_changed(work/"inputs"))
    targets=Counter(scale*p.rank for scale in SCALES for p in raw.targets)
    old=Counter(scale*p.rank for scale in SCALES for p in raw.paid)
    old[1]-=SPLITS
    old[Q(1,2)]=2*SPLITS
    assert (targets.total(),old.total())==(105216,564144)
    old_margin,old_cells=core.certify(GAUSSIAN_C,(targets,old))
    assert old_margin==Q(profile("gaussian")["margin"]) and len(old_cells)==62
    fresh=old.copy()
    del fresh[Q(1,2)]
    fresh.update({Q(1,4):SPLITS,Q(3,4):SPLITS})
    assert min(fresh)==Q(1,4) and max(fresh)==4424 and max(targets)==10191
    unit=core.UNIT

    def power(r,t):
        r=Q(r)
        x,y=core.power_interval(r.numerator,t)
        if r.denominator==1:
            return Q(x,unit),Q(y,unit)
        a,b=core.power_interval(r.denominator,t)
        return Q(x*unit//b,unit),Q(-(-y*unit//a),unit)

    def diff(paid):
        signed=targets.copy()
        signed.subtract(paid)
        return signed

    def moment(s,c):
        low=high=Q(0)
        for r,n in s.items():
            a,b=power(r,1-c)
            low+=n*min(a,b) if n>=0 else n*max(a,b)
            high+=n*max(a,b) if n>=0 else n*min(a,b)
        return low,high

    def crossing(s):
        lo=int(GAUSSIAN_C*SCALE)
        hi=(SCALE+249)//250
        derivative=Q(0)
        for r,n in s.items():
            p=power(r,1-Q(lo,SCALE))+power(r,1-Q(hi,SCALE))
            derivative+=max(-n*x*y for x in log_rank(r) for y in (min(p),max(p)))
        assert derivative<0 and moment(s,Q(lo,SCALE))[0]>0 and moment(s,Q(hi,SCALE))[1]<0
        for _ in range(42):
            if hi-lo==1:break
            mid=(lo+hi)//2
            a,b=moment(s,Q(mid,SCALE))
            if a>0:lo=mid
            elif b<0:hi=mid
            else:raise ValueError("Insufficient precision")
        assert hi-lo==1
        return Q(lo,SCALE),Q(hi,SCALE),ceil(derivative)

    old_lo,old_hi,old_derivative=crossing(diff(old))
    low,high,derivative=crossing(diff(fresh))
    assert low>old_hi
    c=Q(int((old_hi+low)*2**39),2**40)
    assert old_hi<c<low
    saving=moment(Counter({Q(1,2):2016,Q(1,4):-1008,Q(3,4):-1008}),c)

    tm={k:n*power(k,1-c)[0] for k,n in targets.items()}
    pm={r:n*power(r,1-c)[1] for r,n in fresh.items()}
    rho=sum(pm.values())/sum(tm.values())
    assert Q(99,100)<rho<1 and power(max(targets),c)[1]<Q(106,100)
    cut_ratios={}
    for r in pm:
        demand=sum(v for d,v in pm.items() if d>=r)
        capacity=rho*sum(v for k,v in tm.items() if 4*k>=5*r)
        assert capacity>=demand
        cut_ratios[str(r)]=str((capacity-demand)/sum(pm.values()))
    old_interval=core.intervals
    def indexed_interval(r,t):
        v=power(r,t)
        return tuple(int(unit*x) for x in v)
    core.intervals=indexed_interval
    try:
        margin,cells=core.certify(c,(targets,fresh))
    finally:
        core.intervals=old_interval
    assert margin>0 and cells[4424,10191]==1 and targets[10191]==624
    assert min(cells.values())/targets.total()>Q(1,2**64)
    assert max(max(v.numerator.bit_length(),v.denominator.bit_length()) for v in cells.values())<512

    for r,k in cells:
        assert 4*k>=5*r
        eps=(0,Q(-1,2)) if r==Q(1,4) else (0,Q(1,2)) if r==Q(3,4) else (0,)
        for z in eps:
            assert 0<=8*k-10*r+z and 10*k-8*r+z<10*k and z<=8*r
    N=2**1024
    assert Q(1,4*max(targets)*N)-Q(1,2**(64*1025))>Q(1,65536*N)
    assert 41*(2+520)+6+6*1024+2-64*1025<-132
    assert Q(100,99)**250>4 and Q(99,100)*Q(2,9)>Q(19,100)
    assert power(1032,c)[1]<Q(106,100) and 1-c>Q(996,1000)
    assert Q(10)*Q(106,100)/(Q(996,1000)*Q(99,100)*Q(19,100))<64
    L,A=32768,12087
    delta=Q(1,2**128)
    factor=Q(256,255)*Q(4097,4096)*Q(1028,1024)*power(1024*A*L,c)[1]
    factor*=(1+Q(64,L)+delta)/((1-Q(10,L))*(1-delta)**3)
    assert factor**256<2**43

    for name,p in (("entry",ENTRY),("terminal",TERMINAL)):
        cap=c-Q(43,256*p.complex_log)
        h1,h2=p.rank_logs
        stage_first,stage_ordinary=ordinary_limit(p)
        assert stage_first<p.ordinary<stage_ordinary
        accepted=outer["qualify"](p.kappa,g,p.ordinary,cap)
        bank=resource(p)
        assert bank==profile(name)["stock"]
        assert 68+83*p.complex_log<92*p.complex_log<448*p.complex_log
        assert 872*(4*p.complex_log+1)<2**p.complex_log
        fixed_rates[name]={
            "binary_heights":p.rank_logs,"gaussian_height":p.complex_log,
            "positive_price_cap":str(cap),"fixed_ordinary_ceiling":str(stage_ordinary),
            "published_booked_rate_passes":accepted,"stock":bank,
            "log2_C_frozen":profile(name)["log2_C"],
        }
    _,_,p_only=outer["margins"](K,g,K+5*g,c-Q(43,256*TERMINAL.complex_log))
    assert p_only>0
    phase=48*(3042+697+200)
    assert phase==189072 and phase*6==1134432
    # Rank-debit support is separate from the unchanged tier fee and ruler.
    incumbent_gap=K-overall_cap
    return {
        "tested_inventory":"1008 quarter/complement pairs on exact 1,79 scales, fixed tier heights",
        "peer":HEAD,"comparator":BASELINE,"comparator_kappa":str(K),"pins":PINS,
        "gaussian_candidate_c":str(c),"gaussian_crossing":[str(low),str(high)],
        "gaussian_old_crossing":[str(old_lo),str(old_hi)],
        "new_and_old_directed_derivative_upper":[derivative,old_derivative],
        "gross_savings_bounds":[str(x) for x in saving],
        "normalized_hall_excess":cut_ratios,
        "canonical_cells":len(cells),"maximum_k_over_r":str(max(k/r for r,k in cells)),
        "canonical_reserve_factor_millionths":ceil(factor*10**6),
        "tier_prices":fixed_rates,
        "phase_qualifying_large_copy_passes":phase,"phase_equivalent_field_extents":6*phase,
        "positive_margin_at_comparator_if_binary_were_funded":str(p_only),
        "complete_upper_fixed_binary_heights":str(overall_cap),
        "shortfall_vs_comparator":str(incumbent_gap),
        "minimum_terminal_h2_if_only_h2_changed":h2_min,
        "unchanged_entry_premium":572,"unchanged_complete_clock_log2_upper":339787971,
        "decision":"EXCLUDED_FIXED_TIER_ORDINARY_PRICE",
    }


if __name__=="__main__":
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--peer",type=Path,required=True)
    cli.add_argument("--out",type=Path,required=True)
    cli.add_argument("--child",action="store_true")
    a=cli.parse_args()
    if a.child:
        with tempfile.TemporaryDirectory(prefix="tier-quarter-") as run:
            result=evaluate(a.peer.resolve(),Path(run)/"installed")
        with a.out.open("x") as out:
            json.dump(result,out,sort_keys=True,indent=2)
            out.write("\n")
    else:
        start=time.monotonic()
        r=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=45)
        print(f"exit={r.returncode} seconds={time.monotonic()-start:.3f}")
        raise SystemExit(r.returncode)
