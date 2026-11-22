"""One directed ordinary-debit profile with actual signed physical seam controls."""
from argparse import ArgumentParser
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

HEAD = "ffa64503646a62a7ac3cd2c47787d670da911f89"
PINS = {
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "prepare.py": "3862a6fb149d5d35be194ace5dd9c135013e46abdaa3d6396641a85af794e788",
    "RESULT.json": "65b29858741c054434863612a357b9c6b833d8865530812659943293ff1155f5",
    "verify.py": "306480bf045e5a0590bbc9a5fb4c34d0e53da4faab049ef32d7fc7ca97ab6269",
}
BASE_RECEIPT = "dcf57d8bab8cfc76769b0f9d8b570d233e670032b8ab2aed481172ff21c3c2a9"
BASE_LOG = "1e2ac85c87da9e425180b85ccff811f508ebb4b28035cc7ab898a918fe3aaff5"
K7 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
K = Q(".00389821103")
G = Q(1, 10**18)
POS_DEBIT = Q(64944, 524288)
OLD_DEBIT = Q(11, 8)
NEW_DEBIT = Q(703, 512)
RANKS = (8192, 129406, 523763)
HG = 484799


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


def factor(bound):
    delta=Q(1,2**128)
    lower=32768
    return (Q(47,20)*Q(256,255)*Q(4097,4096)*Q(1028,1024)*bound
            *(1+Q(64,lower)+delta)/((1-Q(10,lower))*(1-delta)**3))


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
    assert digest(baseline_log)==BASE_LOG
    assert b"PASS_REGISTERED_RESEARCH_PACKAGE research/p104-weighted-ordinary-transfer" in baseline_log.read_bytes()
    previous=json.loads((capsule/"RESULT.json").read_bytes())
    signature=json.loads(baseline_receipt.read_bytes())
    assert signature["frozen_candidate"]["capsule/RESULT.json"]==PINS["RESULT.json"]
    assert signature["complete_log2_C"]==previous["complete_log2_C"]==318293671
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

    baseline=ins.TERMINAL
    candidate=replace(baseline,rank_logs=RANKS,complex_log=HG,kappa=K)
    assert baseline.rank_logs==(8192,129406,524403) and baseline.kappa==Q(".00389821057")
    assert baseline.complex_log==483871 and grades.UPPER_DIVISOR==1724
    w=binary_word()
    assert digest(runtime/"strong-bit.json.gz")==K7
    assert (len(w.targets),len(w.paid),len(w.cells))==(18906,104652,24)
    assert 0<ins.BINARY_C< Q(1,8)
    base=1024*134*32768
    lows,highs=dyadic_power(base,ins.BINARY_C)
    lower=factor(lows)
    upper=factor(highs)
    predecessor_factor=factor(Q(power_interval(base,ins.BINARY_C)[1],UNIT))
    assert 0<lower<=upper and lower<=predecessor_factor
    assert max(upper,predecessor_factor)**512<2**703
    assert lower**512>2**702, "new debit control exceeds one lower 1/512 grid value"
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

    known=price(baseline,OLD_DEBIT)
    assert all(known[k]==previous["terminal"][k] for k in ("ordinary_rates","signed","stock","geometry"))
    prior_entry=price(ins.ENTRY,OLD_DEBIT)
    assert all(prior_entry[k]==previous["entry"][k] for k in ("ordinary_rates","signed","stock","geometry"))
    tier_old=Q(0)
    for h in RANKS:
        tier_old=min(candidate.eta,(249*(ins.BINARY_C-OLD_DEBIT/h)+tier_old)/250)
    assert tier_old<candidate.ordinary

    terminal=price(candidate,NEW_DEBIT)
    entry=price(ins.ENTRY,NEW_DEBIT)
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
        assert all(x is y for x,y in zip(b[:2],old_native[:2],strict=True))
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
    assert data["complete_log2_C"]==318293031<previous["complete_log2_C"]
    assert data["terminal_log2_B"]==211635648 and A==1146634
    cuts=tuple(entrance_logs(candidate.rank_logs))
    assert cuts==tuple(terminal["stock"]["binary_cuts"])==(8290,137760,661587)
    for i,c in enumerate(cuts,1):
        assert [stage_for_width_log(c+d,3,candidate.rank_logs) for d in (-1,0,1)]==[i-1,i,i]
        assert stage_for_width_log(c+1,i-1,candidate.rank_logs)==i-1
    direct=[verify_stage(candidate,cuts,2,140000),verify_stage(candidate,cuts,3,670000)]
    compiled=[verify_stage(candidate,cuts,2,1100000),verify_stage(candidate,cuts,3,4400000)]
    assert all(x["direct"] for x in direct) and not any(x["direct"] for x in compiled)
    tape=[verify_tape(1,[0,1],[2,1]),verify_tape(2,[1,7],[3,1])]
    assert max(candidate.rank_logs).bit_length()==19<max(baseline.rank_logs).bit_length()==20
    assert signature["fixed_setup_bound"]<2**228
    return {"baseline_head":HEAD,"baseline_exact_receipt":BASE_RECEIPT,"pins":PINS,
            "baseline_science_log":BASE_LOG,"max_fixed_height_descriptor_bits":19,
            "heights":RANKS,"gaussian_height":HG,"candidate":str(K),"delta":str(K-baseline.kappa),
            "debit":str(NEW_DEBIT),"charged_factor_lower_1e12":int(lower*10**12),
            "charged_factor_upper_1e12":ceil(max(upper,predecessor_factor)*10**12),
            "same_two_moment_contraction":str(contraction),
            "old_debit_ideal_negative_gap":str(candidate.ordinary-tier_old),
            "complete_signed_entry":entry,"complete_signed_terminal":terminal,"first_public_offset":public-edge,
            "clock":data,"maximum_fixed_setup":signature["fixed_setup_bound"],
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
    with tempfile.TemporaryDirectory(prefix="ordinary-debit-") as tmp:
        r=check(args.capsule.resolve(),args.baseline_receipt.resolve(),args.baseline_log.resolve(),Path(tmp))
    with args.out.open("x") as f:
        json.dump(r,f,indent=2,sort_keys=True)
        f.write("\n")


if __name__=="__main__":
    main()
