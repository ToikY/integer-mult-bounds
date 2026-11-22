"""Screen a literal 8,721 typed calendar and the complete fixed-height invoice."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import islice
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

C = Q(17145637167 + 64, 2**42)
K = Q(".00389821033")
D = Q(65000, 524288)
G = Q(1, 10**18)
PINS = {
    "frequency-weighted-native-multiplier/bootstrap.py": "a824c0ba9bb5efe5ad5b6c9b891b363b6d2ac31b0a57b9e27b68a6c2bca6f7ee",
    "frequency-weighted-native-multiplier/SOURCES.json": "01d9e6b6b28cd174800cadfb59f4f064b3844575da297d82e16eb19a0d11c868",
    "frequency-weighted-native-multiplier/grades.py": "8d2e3d14ac2149f985d7f6a75bf36182d7f68aadf8df6595fc0774224d4951ac",
    "frequency-weighted-native-multiplier/typed_transport.py": "b76b9ad3dc0dd91473026c079585f830387eaa3c34c25a7820ee5057d5cbf941",
    "frequency-weighted-native-multiplier/typed_raw.py": "0c268432c9d48798c17d927f2d900b5e69dfc6585166cd71f253913e389c3b47",
    "frequency-weighted-native-multiplier/FINITE-LOSS.md": "12c6069437a0cbb61c80804f89f027ef9709c186e67d26fb0584ad6e71048052",
    "tiered-native-multiplier/source/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
}
PREVIOUS = "8a2099dd18818ab5f1df4d7d29d8cdbbf3df971ed567475309e35218ffe3eb71"


def ceil(q):
    return -(-q.numerator//q.denominator)


def check(root, previous, dst):
    for n,h in PINS.items():
        assert sha256((root/n).read_bytes()).hexdigest()==h,n
    assert sha256(previous.read_bytes()).hexdigest()==PREVIOUS
    prior=json.loads(previous.read_bytes())
    assert Q(prior["kappa_candidate"])==Q(".00389821030")
    package=root/"frequency-weighted-native-multiplier"
    subprocess.run([sys.executable,"-IB",str(package/"bootstrap.py"),str(dst)],
                   check=True,timeout=15)
    sys.path.insert(0,str(dst))
    from upstream import install
    install()
    sys.path.append(str(root/"tiered-native-multiplier"/"source"))
    import grades
    import installations as ins
    from periodic import Job
    from raw48 import ComplexRaw
    from strict_moment import UNIT,power_interval
    from transport import Measure, axes
    from typed_transport import NativeType, TypedPlan
    from unpowered_price import intervals as fixed_interval
    weights=(8,721)
    grades.WEIGHTS=weights
    ins.GAUSSIAN_C=C
    recipe=grades.numerical_recipe(483871)
    H_min=1024
    t=1-C
    types=recipe.types()
    assert tuple(w.multiplicity for w in types)==weights and grades.SCALES==(1,2)
    shape=tuple((len(w.targets),len(w.paid)) for w in types)
    assert shape==((52608,282576),(52608,281568))
    paid=recipe.paid.histogram
    targets=recipe.targets.histogram
    T_lo=sum(n*fixed_interval(k,t)[0] for k,n in targets.items())
    T_hi=sum(n*fixed_interval(k,t)[1] for k,n in targets.items())
    P_hi=sum(n*fixed_interval(r,t)[1] for r,n in paid.items())
    P_lo=sum(n*fixed_interval(r,t)[0] for r,n in paid.items())
    assert T_lo>P_hi and 100*P_lo>99*T_hi
    typed=recipe.typed_cells()
    rows,load=defaultdict(Q),defaultdict(Q)
    for (a,r,b,k),v in typed.items():
        assert 0<v and 5*r<=4*k
        rows[a,r]+=v
        load[b,k]+=weights[a]*recipe.paid.variants[a].histogram[r]*v*fixed_interval(r,t)[1]
    for a,native in enumerate(types):
        assert all(rows[a,r]==1 for r in set(native.paid))
        counts=Counter(native.targets)
        for k,n in counts.items():
            assert 0<load[a,k]<=weights[a]*n*fixed_interval(k,t)[0]
    def low_power(r,c):
        x=Q(r)
        return Q(power_interval(x.numerator,c)[0],power_interval(x.denominator,c)[1])
    psi=sum(paid[r]*v*r*(low_power(Q(k,r),C)-1)/C for (r,k),v in recipe.cells.items())
    linear_axes=sum(k*n for k,n in targets.items())
    fringe=10*linear_axes/(t*psi)
    L=2048
    M=2**H_min
    U=2*(M//(2048*recipe.ambient))
    V=M**6
    delta=Q(1,2**128)
    assert (11*t)>10 and sum(weights)/(t*1024)+Q(2,M**5)<2
    assert M*delta>1 and U>516*L and 5160<delta*U
    assert max(shape[i][1] for i in range(2))<2**19
    assert 2**19*(U+L)**77+L**77<(M*L)**77
    assert 2**46*M**2 < Q(V,2**132)
    assert Q(2**20*V,M**4) < Q(V,2**132)
    # Same integer quadrature geometry with a 10-bit source multiplier.
    assert C.denominator==2**42 and max(weights)<2**10
    inverse_error_bits=43*((H_min+2)//2+2)+6+6*H_min+12-64*(H_min+1)
    assert inverse_error_bits<-132
    assert Q(1,M)-Q(1,2**(64*(H_min+1)))>Q(1,2*M)
    value=Q(power_interval(1024*recipe.ambient*L,C)[1],UNIT)
    factor=(1+delta)*(1+Q(4*258,1024*recipe.ambient))*value*(1+fringe/L+delta)/(1-delta)**4
    cap=low_power(2,D)
    assert factor<cap

    # Same constructor with reduced two-grade words and actual integer
    # multiplicities. Cross-type funding shares follow the paid invoice.
    fixture_types=tuple(NativeType((2,),(1,),w) for w in weights)
    shares={(a,1,b,2):Q(w,sum(weights)) for a in range(2) for b,w in enumerate(weights)}
    f=TypedPlan(256,fixture_types,shares,t,10,30,2**18,3,16,
                delay_base=2,scale_step=Q(2),padding=1)
    measure=Measure(t,2**18,64*(256).bit_length())
    for e in f.bands:
        for a,w in enumerate(weights):
            assert f.count[e,a]==ceil(w*measure.mass(e,e+2)[1])
    assert {(a,link.kind) for (_,a,_),ls in f.send.items() for link in ls}=={(0,0),(0,1),(1,0),(1,1)}
    assert f.source_width>0 and f.leaves_per_epoch>0

    assert recipe.cells[112,258]==1 and types[1].targets.count(258)==624
    pi=typed[1,112,1,258]/624
    assert pi==Q(1,624)
    placed=[]
    class Field:
        def __init__(self): self.swaps=[]
        def swap(self,l,r,n,s): self.swaps.append((l,r,n))
    class Column:
        window=1
        swap=None
    for H in (1024,483871):
        carrier=1<<H
        upper=2*(carrier//(2048*recipe.ambient))
        band=2*(3*upper//8)
        lo,hi=Q(band*258,112),Q((band+2)*258,112)
        assert upper<lo<hi<carrier and weights[1]*(hi-lo)*carrier*pi>4
        size=258*(band-8)
        period=4*ceil(Q(carrier,4*size))
        slots=tuple(islice(axes(carrier,size,period,0),3))
        field=Field()
        raw=ComplexRaw(None,{},Column(),low=0,bundle=1,slots=carrier)
        raw.align(field,Job(0,slots),tuple(range(3)))
        assert period==1620 and slots==(0,324,648) and field.swaps[0]==(1,324,1)
        placed.append((H,period,slots,field.swaps[0]))

    prior_rate=Q(0)
    for h in (8192,129414):
        bound=(249*(ins.BINARY_C-Q(11,8*h))+prior_rate)/250
        prior_rate=Q(int(bound*10**21)-1,10**21)
    fixed_h3=524349
    limit=(249*(ins.BINARY_C-Q(11,8*fixed_h3))+prior_rate)/250
    positive=C-D/483871
    assert positive>K+5*G>limit
    h3_min=int(Q(249,250)*Q(11,8)/((249*ins.BINARY_C+prior_rate)/250-K-5*G))+1
    assert h3_min==524355
    return {
        "widths":[1,2],"integer_weights":weights,"exact_trial":str(C),"target_kappa":str(K),
        "physical_word_counts":shape,"installed_grade_and_type_cells":[len(recipe.cells),len(typed)],
        "integer_births_fixture_at_e20":[f.count[20,a] for a in range(2)],
        "cross_type_calendar_fixture":True,"rounded_fixture_leaf_count":f.leaves_per_epoch,
        "weighted_targets_and_paid":[targets.total(),paid.total()],"exact_boundary_axis_sum":linear_axes,
        "psi_lower_floor_1e4":int(psi*10**4),"fringe_upper_1e9":ceil(fringe*10**9),
        "finite_factor_upper_1e12":ceil(factor*10**12),"finite_factor_reserve_floor_1e12":int((cap-factor)*10**12),
        "interval_mass_error_bits_H1024":inverse_error_bits,
        "opening_bound_factor_lt":2,"placement":placed,
        "gaussian_margin_at_target":str(positive-K-5*G),
        "fixed_binary_shortfall_at_target":str(limit-K-5*G),
        "first_binary_height_that_might_reopen":h3_min,
        "decision":"VIABLE_PHYSICAL_GAUSSIAN_PRICE, EXCLUDED_COMPLETE_AT_FIXED_BINARY",
        "pins":PINS,"prior_receipt":PREVIOUS,
    }


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for n in ("research","previous","out"):
        p.add_argument("--"+n,type=Path,required=True)
    p.add_argument("--child",action="store_true")
    x=p.parse_args()
    if x.child:
        with tempfile.TemporaryDirectory(prefix="typed-frequency-") as tmp:
            answer=check(x.research.resolve(),x.previous.resolve(),Path(tmp)/"runtime")
        with x.out.open("x") as f:
            json.dump(answer,f,indent=2,sort_keys=True)
            f.write("\n")
    else:
        start=time.monotonic()
        r=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=90)
        print(f"exit={r.returncode} seconds={time.monotonic()-start:.3f}")
        raise SystemExit(r.returncode)
