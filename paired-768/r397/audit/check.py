"""Audit one clock-matched signed ordinary/Gaussian height balance and physical seams."""
from argparse import ArgumentParser
from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from itertools import islice, product
import json
from math import isqrt
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time

HEAD = "04228ea5a1292cf8526a20037060f6fc6e15a858"
PINS = {
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "prepare.py": "e4dea11a94e13b7ae5a70544e6dff8fdcc0de98533767cd04c1aadff95766682",
    "RESULT.json": "8754f0ffe158404b2f3df2a9e94ce20b77b2e7e62882794d614b7eea2c6bdb60",
    "verify.py": "0d5f7941aee774405de60b61443e517eb3cb680f094801af84ad802c5c4fd206",
}
BASE_RECEIPT = "79042dce46983afdcf6891d410cfb72bcbc897229c7d05d22c67cfe7b61459fb"
BASE_LOG = "1ae8005f720708eaf2daced150b635647ec2a685b1e6ea725364a457172886b0"
K7 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
K = Q(".00389821380")
G = Q(1, 10**18)
POS_DEBIT = Q(64944, 524288)
DEBIT = Q(1405, 1024)
LOWER = 18960
OLD_LOWER = 32768
RANKS = (8192, 124986, 524288)
HG = 490463


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


class DyadicWidth(int):
    """Speed up exact exponentiation of a mathematically dyadic test width."""
    def __pow__(self, exponent):
        assert self.bit_count() == 1 and exponent >= 0
        return 1 << ((self.bit_length() - 1) * exponent)


def verify_stage(profile, cuts, number, log_width):
    import ordinary_carrier as carrier

    calls = []
    base = DyadicWidth(1 << log_width)
    prev = 1 << cuts[number-2]
    power = 1 << (log_width//250)
    assert log_width % 10000 == 0
    width = max(prev+1, power)
    component = 1 << (39*log_width//10000)
    count = -(-width//component)
    short, longer = divmod(width,count)
    expected_layout = (longer, short+1, count-longer, short)
    rank = 1 << profile.rank_logs[number-1]
    expect_direct = -(-base//width) <= 1 << (8*profile.rank_logs[number-1])

    def root(value, degree):
        assert value.bit_count() == 1
        quotient, remainder = divmod(value.bit_length()-1,degree)
        assert not remainder
        return 1 << quotient

    def receiver(dimension, layout, previous, *, direct, profile):
        assert dimension == rank and layout == expected_layout and direct == expect_direct
        assert previous.func is carrier.ternary
        assert previous.keywords == {"maximum": number-1, "profile": profile}
        return number

    def body(source,target,digits,prefix,gap,suffix,backend):
        assert digits==base and (prefix,gap,suffix)==(1,3,5) and backend==number
        calls.append((digits.bit_length()-1,backend))

    actual = carrier.ceil_root, carrier.Receiver, carrier.root_body
    try:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = root, receiver, body
        carrier.ternary(None,None,base,1,3,5,maximum=number,profile=profile)
    finally:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = actual
    assert calls == [(log_width,number)]
    return {"stage":number,"scanned_log":log_width,"rank_log":rank.bit_length()-1,
            "predecessor_cut":cuts[number-2],"direct":expect_direct,
            "component_log":component.bit_length()-1}


def verify_tape(width, u, v):
    from five_exchange import same_order_line
    from growing_binary import Weighted
    from same_order_body import SameOrderBody
    from streaming_routes import cold_swap_tape
    from ternary_leaf import select_pivot

    class Core(SameOrderBody, Weighted):
        def __init__(self):
            super().__init__(2,(1,width,0,0),cold_swap_tape)
            self.stock=self.owners
            self.calls=0

        def weighted(self,*args,**kwargs):
            assert kwargs["atoms"]==1<self.n
            self.calls+=1
            return super().weighted(*args,**kwargs)

    core = Core()
    modulus=core.modulus
    assert modulus==3**width and core.atom==modulus
    assert sum(a*b for a,b in zip(u,v,strict=True))%modulus==1
    weight=lambda row,j: (2,4)[j]
    inverse = tuple(pow(weight(0,j),-1,modulus) for j in range(2))
    dims = (modulus,)*4

    def dense(sign):
        out=bytearray(len(raw))
        size=modulus**4
        for x0,x1,y0,y1 in product(range(modulus),repeat=4):
            delta=sum(v[j]*(y-inverse[j]*x)
                      for j,(x,y) in enumerate(zip((x0,x1),(y0,y1),strict=True)))%modulus
            target=((x0+sign*2*u[0]*delta)%modulus,(x1+sign*4*u[1]*delta)%modulus,
                    (y0-sign*u[0]*delta)%modulus,(y1-sign*u[1]*delta)%modulus)
            i=((x0*modulus+x1)*modulus+y0)*modulus+y1
            k=0
            for value in target:
                k=k*modulus+value
            assert 0<=k<size
            out[4*k:4*k+4]=raw[4*i:4*i+4]
        return bytes(out)

    raw=b"".join(i.to_bytes(4,"little") for i in range(modulus**4))
    source,destination=BytesIO(raw),BytesIO()
    same_order_line(core,source,destination,pivot=select_pivot(u,v),factors=lambda _: (u,v),
                    f=1,unused=1,heights=1,older=1,gap=1,suffix=4,weight=weight)
    assert source.getvalue()==raw and source.tell()==len(raw)
    assert destination.getvalue()==dense(1)
    assert destination.getvalue()!=dense(-1), "wrong signed return was accepted"
    assert 1<=core.calls<=5
    return {"component_width":width,"modulus":modulus,"records":modulus**4,
            "paid_exchanges":core.calls,"wrong_signed_return_rejected":True}


def ceil(x):
    return -(-x.numerator//x.denominator)


def dyadic_power(base, exponent):
    """Independent outward 192-bit root and product arithmetic."""
    grid=1<<192
    assert 0<exponent<1 and exponent.denominator.bit_count()==1
    lo=hi=base*grid
    lop=hip=grid
    for bit in range(exponent.denominator.bit_length()-2,-1,-1):
        lo=isqrt(lo*grid)
        hi=isqrt(hi*grid-1)+1
        if exponent.numerator>>bit&1:
            lop=lop*lo//grid
            hip=(hip*hi+grid-1)//grid
    return Q(lop,grid),Q(hip,grid)


def factor(bound, lower):
    delta=Q(1,2**128)
    return (Q(47,20)*Q(256,255)*Q(4097,4096)*Q(1028,1024)*bound
            *(1+Q(64,lower)+delta)/((1-Q(10,lower))*(1-delta)**3))


def all_size_stock(word, c, intervals, unit):
    """Discharge the parameterized TRANSFER.md hypotheses at the new floor."""
    t = 1-c
    targets, paid = Counter(word.targets), Counter(word.paid)
    assert max(targets) <= 134 and min(paid) >= 1
    assert all(5*r <= 4*k for r,k in word.cells)
    assert all(sum(p for (u,k),p in word.cells.items() if u==r)==1 for r in paid)
    # Check actual directed per-receiving-label funding and the whole raw margin.
    t_lower = {k: intervals(k,t)[0] for k in targets}
    p_upper = {r: intervals(r,t)[1] for r in paid}
    t_hi = sum(n*intervals(k,t)[1] for k,n in targets.items())
    p_lo = sum(n*intervals(r,t)[0] for r,n in paid.items())
    assert sum(targets[k]*v for k,v in t_lower.items())>sum(paid[r]*v for r,v in p_upper.items())
    assert 100*p_lo>99*t_hi
    for k,n in targets.items():
        load=sum(paid[r]*p*p_upper[r] for (r,s),p in word.cells.items() if s==k)
        assert 0<load<=n*t_lower[k]
    psi=sum(paid[r]*p*r*(Q(intervals(k,c)[0],intervals(r,c)[1])-1)/c
            for (r,k),p in word.cells.items())
    fringe=10*sum(k*n for k,n in targets.items())/(t*psi)
    assert 0<fringe<64 and psi>1

    # Check the smallest admitted numerical scale; every margin below grows
    # with N. Actual binary native stages start no earlier than H=3000.
    H=1024
    N=1<<H
    V=N**6
    ambient=134
    U=2*(N//(2048*ambient))
    delta=Q(1,2**128)
    assert LOWER%2==0 and 8<LOWER and 24*(LOWER+2)<25*LOWER
    assert (LOWER-8,LOWER-6)==(18952,18954)
    assert max(Q(k,r) for r,k in word.cells)*LOWER<U
    assert max(Q(k,r) for r,k in word.cells)*(U+2)<N
    assert 4*max(targets)*(U-8)<N and U*ambient<=Q(N,1024)
    assert U*1024*ambient>=(1-delta)*N
    assert Q(6,5)**4>2 and Q(6,5)**73>2**19
    assert len(word.paid)<2**19
    assert 2**19*Q(1,1024*ambient*LOWER)**77+Q(1,N**77)<1
    lower_power=Q(intervals(LOWER,t)[0],unit)
    assert lower_power>1024 and Q(1,t*lower_power)+Q(2,N**5)<2
    # Endpoint inverse bases are >1/(512N) through all roots. The
    # original 61-stage envelope costs 397+30.5H bits per endpoint.
    assert c.denominator.bit_length()-1<=60 and Q(1,N)-Q(1,2**(64*(H+1)))>Q(1,512*N)
    grid_error_bits=397+31*H+6*H+3-64*(H+1)
    assert grid_error_bits<-132
    assert 2**46*N**2 < Q(V,2**132)
    assert Q(2**20*V,N**4) < Q(V,2**132)
    assert 4096*2*len(word.targets)<N**2
    assert (1-Q(10,LOWER))*psi-Q(1,2**130)>1
    assert (1-Q(1,N))/Q(257,256)>Q(1,2)
    return {"fringe_upper_1e9":ceil(fringe*10**9),"psi_lower_floor":int(psi),
            "grid_absolute_error_exponent_at_H1024":grid_error_bits,
            "birth_bound":"2V","copy_group_bound":"3N^3","whole_field_width":"N^92",
            "first_two_columns":[LOWER-8,LOWER-6],"minimum_positive_scale_h_guard":1024}


def bound_recipe(old, lower):
    """Pass the proposed literal cutoff through the installed Recipe.open seam."""
    import transport

    assert old.level_floor==lower
    N=1<<old.rank_log
    expected=2*(N//(2048*old.ambient))

    def capture(n,targets,paid,cells,t,l,u,volume,ticks,rounds,**flags):
        assert n==N and (l,u)==(lower,expected) and t==1-old.trial
        assert targets is old.targets and paid is old.paid and cells is old.cells
        assert (volume,ticks,rounds)==(N**6,N**82,N**2)
        assert flags=={"width":1<<(92*old.rank_log),"delay_base":1<<19}
        return True

    real_plan=transport.Plan
    try:
        transport.Plan=capture
        assert old.open()
    finally:
        transport.Plan=real_plan
    return {"height":old.rank_log,"lower":lower,"ambient":old.ambient,
            "first_columns":lower-8,"plan_arguments_checked":True}


def check_placement(recipe):
    import grades
    from periodic import Job
    from raw48 import ComplexRaw
    from transport import axes

    atlas,word,*_=grades.numerical_source()
    rotated=tuple(p.tag for p in word.targets if p.rank==129 and p.tag[:2]==("root","rotated"))
    assert len(rotated)==384 and rotated[0]==("root","rotated",0,4080,1)
    native=recipe.types()
    count=native[1].targets.count(258)
    pi=recipe.typed_cells()[1,112,1,258]/count
    assert count==624 and pi==Q(1,624) and recipe.cells[112,258]==1
    carrier=1<<recipe.rank_log
    divisor=grades.UPPER_DIVISOR*recipe.ambient
    upper=2*(carrier//divisor)
    band=2*(3*upper//8)
    lo,hi=Q(band*258,112),Q((band+2)*258,112)
    assert 1874<band<upper<lo<hi<carrier
    assert grades.WEIGHTS[1]*(hi-lo)*carrier*pi>4
    size=258*(band-8)
    period=4*ceil(Q(carrier,4*size))
    tickets=tuple(islice(axes(carrier,size,period,0),3))

    class Column:
        window=1
        swap=None
    class Field:
        def __init__(self):
            self.swaps=[]
        def swap(self,a,b,n,service):
            self.swaps.append((a,b,n))

    field=Field()
    raw=ComplexRaw(atlas,{},Column(),low=0,bundle=1,slots=carrier)
    raw.align(field,Job(0,tickets),tuple(range(3)))
    assert period==1364 and tickets==(0,272,545) and field.swaps[0]==(1,272,1)

    def capture(length,types,cells,t,lower,actual_upper,volume,ticks,rounds,**options):
        assert (length,lower,actual_upper)==(carrier,1874,upper)
        assert (volume,ticks,rounds)==(carrier**6,carrier**82,carrier**2)
        assert t==1-recipe.trial and tuple(r.multiplicity for r in types)==(5,451)
        assert len(cells)==88 and options=={"width":1<<(92*recipe.rank_log),"delay_base":1<<19}
        return True

    installed_plan=grades.TypedPlan
    try:
        grades.TypedPlan=capture
        assert recipe.open()
    finally:
        grades.TypedPlan=installed_plan

    return {"height":recipe.rank_log,"period":period,"tickets":tickets,
            "first_swap":field.swaps[0],"share":str(pi),"minimum_directed_grant":3,
            "source_rotated_roots":len(rotated),"literal_plan_arguments":True}


def clock(profile,cut_stock,prior_entry):
    h=profile.rank_logs
    recurrent=128+320*sum(h)
    premium=ceil((profile.kappa-Q(".00345"))*cut_stock["public_exponent_A"])
    return {"entry_premium":premium,"terminal_log2_B":recurrent,
            "complete_log2_C":1+max(prior_entry+premium,1602+220*profile.complex_log+recurrent)}


def check(capsule,baseline_receipt,baseline_log,tmp):
    for name,d in PINS.items():
        assert digest(capsule/name)==d,name
    assert digest(baseline_receipt)==BASE_RECEIPT
    assert BASE_LOG is not None and digest(baseline_log)==BASE_LOG
    assert b"PASS_REGISTERED_RESEARCH_PACKAGE research/p104-weighted-ordinary-floor" in baseline_log.read_bytes()
    previous=json.loads((capsule/"RESULT.json").read_bytes())
    signature=json.loads(baseline_receipt.read_bytes())
    assert signature["literal_pins"]["capsule/RESULT.json"]==PINS["RESULT.json"]
    assert signature["complete_log2_C"]==previous["complete_log2_C"]==318292711
    package=runpy.run_path(str(capsule/"verify.py"))["restore"](tmp)
    runpy.run_path(str(capsule/"prepare.py"))["materialize"](package)
    runtime=tmp/"image"
    subprocess.run([sys.executable,"-IB",str(package/"bootstrap.py"),str(runtime)],check=True,timeout=20)
    sys.path.insert(0,str(runtime))
    from upstream import install
    install()
    sys.path.append(str(package.parent/"tiered-native-multiplier"/"source"))
    sys.path.insert(0,str(package))
    import grades
    import installations as ins
    from activation import resource_receipt
    from band_product import prepare_native
    from linear_geometry import entrance_geometry
    from outer_budget import qualify
    from ordinary_carrier import stage_for_width_log
    from positive_debit import certify_loss
    from raw_binary_stage import binary_word
    from staged_carriers import entrance_logs
    from strict_moment import UNIT,power_interval
    from unpowered_price import intervals

    baseline=ins.TERMINAL
    candidate=replace(baseline,rank_logs=RANKS,complex_log=HG,kappa=K)
    assert baseline.rank_logs==(8192,129406,523443) and baseline.kappa==Q(".00389821126")
    assert baseline.complex_log==485263 and grades.UPPER_DIVISOR==1724
    w=binary_word()
    assert digest(runtime/"strong-bit.json.gz")==K7
    assert digest(runtime/"raw_binary_stage.py")=="e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0"
    assert (len(w.targets),len(w.paid),len(w.cells))==(18906,104652,24)
    assert 0<ins.BINARY_C< Q(1,8)
    base=1024*134*LOWER
    lows,highs=dyadic_power(base,ins.BINARY_C)
    lower,upper=factor(lows,LOWER),factor(highs,LOWER)
    direct_upper=factor(Q(power_interval(base,ins.BINARY_C)[1],UNIT),LOWER)
    assert 0<lower<=upper and lower<=direct_upper
    assert max(upper,direct_upper)**1024<2**1405
    old_low,old_high=dyadic_power(1024*134*OLD_LOWER,ins.BINARY_C)
    assert factor(old_high,OLD_LOWER)**512<2**703
    assert factor(old_low,OLD_LOWER)**1024>2**1405
    assert lower**1024>2**1404
    contraction=Q(75,32)/Q(47,20)
    assert contraction==Q(375,376) and 1/(1-contraction)==376

    def price(profile,debit):
        rate=Q(0)
        rates=[]
        for i,h in enumerate(profile.rank_logs):
            local=ins.BINARY_C-debit/h
            assert 0<local<Q(1,8)
            limit=min(profile.eta,(249*local+rate)/250)
            rate=profile.ordinary if i==len(profile.rank_logs)-1 else Q(int(limit*10**21)-1,10**21)
            assert 0<rate<limit and profile.eta+Q(1,2)<1-rate
            rates.append(str(rate))
        gaussian=ins.GAUSSIAN_C-POS_DEBIT/profile.complex_log
        return {"ordinary_gap":str(limit-rate),"gaussian_gap":str(gaussian-rate),"ordinary_rates":rates,
                "signed":qualify(profile.kappa,G,profile.ordinary,gaussian),
                "stock":resource_receipt(profile),"geometry":entrance_geometry(ins.activation(profile))}

    known=price(baseline,DEBIT)
    assert all(known[k]==previous["terminal"][k] for k in ("ordinary_rates","signed","stock","geometry"))
    prior_entry=price(ins.ENTRY,DEBIT)
    assert all(prior_entry[k]==previous["entry"][k] for k in ("ordinary_rates","signed","stock","geometry"))
    tier_old=Q(0)
    for h in baseline.rank_logs:
        tier_old=min(baseline.eta,(249*(ins.BINARY_C-DEBIT/h)+tier_old)/250)
    old_positive=ins.GAUSSIAN_C-POS_DEBIT/baseline.complex_log
    assert max(tier_old,old_positive)<candidate.ordinary

    terminal=price(candidate,DEBIT)
    entry=price(ins.ENTRY,DEBIT)
    assert entry==prior_entry
    old_native=prepare_native(baseline)
    try:
        ins.TERMINAL=candidate
        ins.PROFILES["terminal"]=candidate
        exact_profiles=prepare_native()
        assert len(exact_profiles)==2
        a,b=exact_profiles
        assert [r.rank_log for r in b]==[*RANKS,HG]
        assert [r.rank_log for r in a]==[3000,3080,1024]
        assert all(r.targets is w.targets and r.paid is w.paid and r.cells is w.cells
                   for r in (*b[:-1],*old_native[:-1]))
        assert b[0] is old_native[0] and all(r.level_floor==LOWER for r in (*a[:-1],*b[:-1]))
        opening=[bound_recipe(r, LOWER) for r in (*a[:-1],*b[:-1])]
        assert b[-1].targets is old_native[-1].targets and b[-1].cells is old_native[-1].cells
        A=terminal["stock"]["public_exponent_A"]
        edge=1<<A
        public=edge+(-edge)%6
        assert ins.at_public(public-6) is ins.ENTRY and ins.at_public(public) is candidate
        placement=[check_placement(p[-1]) for p in (a,b)]
        loss=certify_loss(b[-1],grades.LOWER)
        assert Q(loss["debit"])==POS_DEBIT and loss==previous["gaussian"]["finite_loss"]
    finally:
        ins.TERMINAL=baseline
        ins.PROFILES["terminal"]=baseline

    data=clock(candidate,terminal["stock"],previous["entry"]["log2_C"])
    assert data["complete_log2_C"]==previous["complete_log2_C"]==318292711
    assert data["terminal_log2_B"]==210389248 and A==1148403
    cuts=tuple(entrance_logs(candidate.rank_logs))
    assert cuts==tuple(terminal["stock"]["binary_cuts"])==(8290,133340,657692)
    for i,c in enumerate(cuts,1):
        assert [stage_for_width_log(c+d,3,candidate.rank_logs) for d in (-1,0,1)]==[i-1,i,i]
        assert stage_for_width_log(c+1,i-1,candidate.rank_logs)==i-1
    direct=[verify_stage(candidate,cuts,2,140000),verify_stage(candidate,cuts,3,670000)]
    compiled=[verify_stage(candidate,cuts,2,1100000),verify_stage(candidate,cuts,3,4400000)]
    assert all(x["direct"] for x in direct) and not any(x["direct"] for x in compiled)
    stock=all_size_stock(w,ins.BINARY_C,intervals,UNIT)
    assert stock==signature["literal_floor"]["binary_all_size"]
    finite=signature["literal_floor"]["binary_integer_fixture"]
    assert finite["native_closes"]==323165 and finite["paid_singletons"]==683705746532
    tape=[verify_tape(1,[0,1],[2,1]),verify_tape(2,[1,7],[3,1])]
    assert max(candidate.rank_logs)==524288 and max(candidate.rank_logs).bit_length()==20
    assert max(baseline.rank_logs).bit_length()==19
    assert signature["fixed_setup_log2_ceiling"]==228
    assert previous["native_setup_transition_upper"]<2**228
    return {"baseline_head":HEAD,"baseline_exact_receipt":BASE_RECEIPT,"pins":PINS,
            "baseline_science_log":BASE_LOG,"max_fixed_height_descriptor_bits":20,
            "heights":RANKS,"gaussian_height":HG,"candidate":str(K),"delta":str(K-baseline.kappa),
            "binary_lower_floor":LOWER,"predecessor_lower_floor":OLD_LOWER,
            "binary_all_size":stock,"new_binary_openings":opening,"reused_binary_integer_fixture":finite,
            "debit":str(DEBIT),"charged_factor_lower_1e12":int(lower*10**12),
            "charged_factor_upper_1e12":ceil(max(upper,direct_upper)*10**12),
            "same_two_moment_contraction":str(contraction),
            "old_binary_ideal_negative_gap":str(candidate.ordinary-tier_old),
            "old_gaussian_negative_gap":str(candidate.ordinary-old_positive),
            "complete_signed_entry":entry,"complete_signed_terminal":terminal,"first_public_offset":public-edge,
            "clock":data,"maximum_fixed_setup":previous["native_setup_transition_upper"],
            "gaussian_placement":placement,"gaussian_loss":loss,"ordinary_direct_seams":direct,
            "ordinary_compiled_seams":compiled,"literal_signed_tape":tape,
            "scope":"detached actual profile and signed finite tapes, full pinned literal replay still required"}


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--capsule",type=Path,required=True)
    p.add_argument("--baseline-receipt",type=Path,required=True)
    p.add_argument("--baseline-log",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--child",action="store_true")
    args=p.parse_args()
    if not args.child:
        start=time.monotonic()
        result=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=90)
        print(f"exit={result.returncode} seconds={time.monotonic()-start:.3f}")
        raise SystemExit(result.returncode)
    with tempfile.TemporaryDirectory(prefix="matched-profile-") as tmp:
        r=check(args.capsule.resolve(),args.baseline_receipt.resolve(),args.baseline_log.resolve(),Path(tmp))
    with args.out.open("x") as f:
        json.dump(r,f,indent=2,sort_keys=True)
        f.write("\n")


if __name__=="__main__":
    main()
