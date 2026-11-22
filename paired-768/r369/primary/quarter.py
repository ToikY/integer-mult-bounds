"""Test the quarter split against the pinned #8054 inventory and band interface."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib
import json
import runpy
import subprocess
import sys
import tempfile
import time

HEAD = "f6f4ecd5dd717ce2b155dd564469e9693ac90f6d"
OLD = Q(".0038981730255")
C0 = Q(133940467, 2**35)
PINS = {
    "bootstrap.py": "e7609488216e31baf99d3a9b6acaba0e45b1a4c97288d563c43bb414fd0eb183",
    "transport.py": "98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9",
    "unpowered_price.py": "04cac4d63621c55111d870597f3a84d53786177aea5c2f831b16cbe6a6de188b",
    "retimed_supplier.py": "bdc5bf5e5228fe1179951a074508f59a90f6d2634f5af8e2d5a097329e484755",
    "installations.py": "983fdc1fd09ec8727d8c573ba171d52a0fc0200437f9233f249a2aa5e7be9503",
    "outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "RESULT.json": "1315e92c43f0c23a8584beb64217411572a1a2aa1178969ca220ce53073ea8c5",
}
WRAPPER_SHA = "775c7ff81f05b7df6d9ad3aa244bbcc539c383be96e1d07855881c53417f9844"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def log_bounds(q):
    z = (q-1)/(q+1)
    lo = 2*sum(z**(2*i+1)/(2*i+1) for i in range(20))
    return lo, lo+2*z**41/(41*(1-z*z))


def log_rank(q):
    power = 0
    while q >= 2:
        q = Q(q,2)
        power += 1
    while q < 1:
        q *= 2
        power -= 1
    lo, hi = log_bounds(Q(2))
    if power < 0:
        lo,hi = hi,lo
    x,y = log_bounds(Q(q))
    return x+power*lo,y+power*hi


def evaluate(pkg, temp):
    for name,sha in PINS.items():
        assert digest(pkg/name)==sha, name
    sys.path.insert(0,str(pkg))
    ins=temp/"installed"
    importlib.import_module("bootstrap").install(ins)
    sys.path.insert(0,str(ins))
    import unpowered_price as core
    from installations import EXTENDED, GAUSSIAN_C
    from retimed_supplier import SMALL_SPLITS, source_ranks, word
    from transport import Plan
    assert EXTENDED.kappa == OLD and GAUSSIAN_C == C0
    assert (EXTENDED.complex_log,EXTENDED.positive_stop_denominator) == (20_000_000,10**18)
    t,p=core.ranks()
    literal_t,literal_p=source_ranks(word(*core.load_changed(ins/"inputs")))
    assert (Counter(literal_t),Counter(literal_p))==(t,p)
    assert (sum(t.values()),sum(p.values()),SMALL_SPLITS,p[Q(1,2)])==(105216,564142,1006,2012)
    fixed_coupling=core.certify(C0,(t,p))
    assert fixed_coupling[0]>0 and len(fixed_coupling[1])==54
    new=p.copy()
    del new[Q(1,2)]
    new.update({Q(1,4):1006,Q(3,4):1006})
    unit=core.UNIT

    def bounds(r, e):
        if isinstance(r,Q) and r.denominator>1:
            x,y=core.power_interval(r.numerator,e)
            a,b=core.power_interval(r.denominator,e)
            return unit*x//b, -(-unit*y//a)
        return core.power_interval(int(r), e)

    def moment(s,c):
        low=high=0
        for r,n in s.items():
            a,b=bounds(r,1-c)
            low+=n*(a if n>=0 else b)
            high+=n*(b if n>=0 else a)
        return Q(low,unit),Q(high,unit)

    def difference(other):
        s=t.copy()
        s.subtract(other)
        return s

    cutoff=2**50
    debit=Q(39,256*EXTENDED.complex_log)+Q(5,EXTENDED.positive_stop_denominator)
    bottom=int((OLD+debit)*cutoff)
    top=(cutoff+249)//250

    def crossing(s):
        lo,hi=bottom,top
        slope=Q(0)
        for r,n in s.items():
            e0,e1=1-Q(hi,cutoff),1-Q(lo,cutoff)
            if r<1:
                e0,e1=e1,e0
            a=bounds(r,e0)[0]
            b=bounds(r,e1)[1]
            slope+=max(-n*x*y for x in log_rank(r) for y in (a,b))/unit
        assert slope<0 and moment(s,Q(lo,cutoff))[0]>0 and moment(s,Q(hi,cutoff))[1]<0
        for _ in range(42):
            if hi-lo==1:
                break
            mid=(hi+lo)//2
            a,b=moment(s,Q(mid,cutoff))
            if a>0:
                lo=mid
            elif b<0:
                hi=mid
            else:
                raise ArithmeticError("Unresolved directed crossing")
        assert hi-lo==1
        return Q(lo,cutoff),Q(hi,cutoff),Q(-((-slope*100)//1),100)

    old_low,old_high,old_slope=crossing(difference(p))
    raw_low,raw_high,slope=crossing(difference(new))
    assert old_high<raw_low
    c=Q(int((old_high+raw_low)*2**39),2**40)
    assert old_high<c<raw_low
    savings=moment(Counter({Q(1,2):2012,Q(1,4):-1006,Q(3,4):-1006}),c)
    assert 0<savings[0]<=savings[1]

    def hall():
        pm={r:n*bounds(r,1-c)[1] for r,n in new.items()}
        tm={r:n*bounds(r,1-c)[0] for r,n in t.items()}
        rho=Q(sum(pm.values()),sum(tm.values()))
        assert 0<rho<1
        deficit={}
        for r in sorted(pm,reverse=True):
            demand=sum(v for rk,v in pm.items() if rk>=r)
            cap=rho*sum(v for rk,v in tm.items() if 4*rk>=5*r)
            assert cap>=demand
            deficit[str(r)]=str((cap-demand)/unit)
        return deficit

    def coupling():
        previous=core.intervals
        core.intervals=bounds
        try:
            margin,cells=core.certify(c,(t,new))
        finally:
            core.intervals=previous
        assert margin>0 and cells and cells[448,1032]==1
        assert min(cells.values())/sum(t.values())>Q(1,2**64)
        assert max(max(v.numerator.bit_length(),v.denominator.bit_length()) for v in cells.values())<512
        assert all(4*k>=5*r for (r,k) in cells)
        return str(margin),[[str(r),k,str(v)] for (r,k),v in sorted(cells.items())]

    def native_guard():
        lower=32768
        even_band=32770
        args=(2**20,[1]*4,[],{},1-c,lower,32772,2**70,4,256)
        def sample(ranks):
            terms=list(args)
            terms[2]=ranks
            terms[3]={(r,1):Q(1) for r in ranks}
            return Plan(*terms,delay_base=2)
        good=sample([Q(1,2),Q(1,2)])
        invalid=sample([Q(1,4),Q(3,4)])
        assert even_band in good.bands and even_band in invalid.bands and invalid.count[even_band]
        iterator=good.events()
        assert next(iterator)[2]==even_band-8
        value=next(iterator)
        assert value[0]==1 and value[3]==(even_band-8)//2
        iterator=invalid.events()
        assert next(iterator)[2]==even_band-8
        try:
            next(iterator)
        except ArithmeticError as error:
            assert str(error)=="The parent cannot cover the selected interval."
        else:
            raise AssertionError("Quarter rank must fail on the second band")
        return {"band":even_band, "columns":even_band-8,
                "paid_sizes":[str(r*(even_band-8)) for r in (Q(1,4),Q(3,4))],
                "old_sizes":[int(Q(1,2)*(even_band-8))]*2,
                "directed_asset_note":"minimum paid rank 1/2 is independently required by check_complete.tariff",
                "result":"fractional axis in unchanged native scheduler"}

    timings, first_results={},None
    actions={"support":hall,"coupling":coupling,"guard":native_guard}
    for order in (("support","guard","coupling"),("coupling","guard","support")):
        begin=time.perf_counter()
        results={step:actions[step]() for step in order}
        timings[",".join(order)]=time.perf_counter()-begin
        if first_results is None:
            first_results=results
        else:
            assert first_results==results
    return {
        "exact_head":HEAD,"pins":PINS,
        "old_comparator":str(OLD),"price_reference_trial":str(C0),
        "old_raw_bracket_and_derivative_upper":[str(v) for v in (old_low,old_high,old_slope)],
        "quarter_raw_bracket_and_derivative_upper":[str(v) for v in (raw_low,raw_high,slope)],
        "hypothetical_trial":str(c),
        "optimistic_whole_kappa_upper_no_new_cost":str(raw_high-debit),
        "optimistic_whole_delta_upper_no_new_cost":str(raw_high-debit-OLD),
        "gross_raw_saving_at_trial":[str(v) for v in savings],
        "paid_count":sum(new.values()),"productive_count":sum(t.values()),
        "decision":"UNCHANGED_NATIVE_SCHEDULER_EXCLUSION; ALL_SIZE REPAIR UNRESOLVED",
        "same_decision_both_orders":True,"checks":first_results,
    },timings


if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--variant",type=Path)
    source.add_argument("--unsplit-package",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--child",action="store_true")
    a=parser.parse_args()
    if a.child:
        with tempfile.TemporaryDirectory(prefix="gaussian-quarter-") as root:
            work=Path(root)
            if a.unsplit_package:
                wrapper=a.unsplit_package.resolve()
                assert digest(wrapper/"prepare.py")==WRAPPER_SHA
                assert digest(wrapper/"RESULT.json")==PINS["RESULT.json"]
                pkg=work/"source"
                runpy.run_path(str(wrapper/"prepare.py"))["materialize"](wrapper/"peer8053",pkg)
                (pkg/"RESULT.json").write_bytes((wrapper/"RESULT.json").read_bytes())
            else:
                pkg=a.variant.resolve()
            evidence,timings=evaluate(pkg,work)
        with a.out.open("x") as out:
            json.dump(evidence,out,sort_keys=True,indent=2)
            out.write("\n")
        print(json.dumps(timings,sort_keys=True))
    else:
        start=time.monotonic()
        r=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=45)
        print(f"exit={r.returncode} seconds={time.monotonic()-start:.3f}")
        raise SystemExit(r.returncode)
