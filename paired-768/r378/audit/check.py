"""Audit native setup and retuned invoices on exact #8057 source, without Wasm."""
from argparse import ArgumentParser
from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HEAD="cbe847a953b971f9c6c5a0a6661e2008acd29086"
C=Q(17145637167,2**42)
D=Q(65000,524288)
K=Q(".00389821030")
OLD_K=Q(".00389821005")
G=Q(1,10**18)
PINS={
    "frequency-weighted-native-multiplier/bootstrap.py":"a824c0ba9bb5efe5ad5b6c9b891b363b6d2ac31b0a57b9e27b68a6c2bca6f7ee",
    "frequency-weighted-native-multiplier/SOURCES.json":"01d9e6b6b28cd174800cadfb59f4f064b3844575da297d82e16eb19a0d11c868",
    "frequency-weighted-native-multiplier/RESULT.json":"2f4faa6648592f589df22a8a0a07ba6856d20786294a44a7776c7d6e0efa14a5",
    "frequency-weighted-native-multiplier/FINITE-LOSS.md":"12c6069437a0cbb61c80804f89f027ef9709c186e67d26fb0584ad6e71048052",
    "frequency-weighted-native-multiplier/PROOF.md":"4dbb38cdbe5b691edf4845fe8cf2a99be5d43455cc73199ab7e305abaa91acca",
    "tiered-native-multiplier/SETUP.md":"6951a98f2f8a0bf73c8d60b16ebbbd66bf87584251df8afbefe4e3a0330bfbf3",
    "tiered-native-multiplier/check_serial_setup.py":"11d1c3209cb523a360ab9abaefb3122507fdf5cb469169890fe2dac636812c47",
    "tiered-native-multiplier/source/activation.py":"6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b",
    "tiered-native-multiplier/source/ordinary_clock.py":"91dcf0ef72dddbde998b80f3d8b30c8036de9ce97e06e2bbd9c4159bf292020d",
    "tiered-native-multiplier/source/outer_budget.py":"ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
}


def ceil(q):
    return -(-q.numerator//q.denominator)


def evaluate(root,work):
    for p,h in PINS.items():
        assert sha256((root/p).read_bytes()).hexdigest()==h,p
    package=root/"frequency-weighted-native-multiplier"
    predecessor=root/"tiered-native-multiplier"
    subprocess.run([sys.executable,"-IB",str(package/"bootstrap.py"),str(work)],
                   check=True,timeout=15)
    sys.path.insert(0,str(work))
    from upstream import install
    install()
    sys.path.append(str(predecessor/"source"))
    import installations as ins
    from activation import resource_receipt
    from band_product import prepare_native
    from grades import LOWER,SCALES,WEIGHTS,SPLITS
    from linear_geometry import entrance_geometry
    from ordinary_carrier import stage_for_width_log
    from ordinary_clock import first_stage_bound,polynomial_to_fibre_bound
    from outer_budget import qualify
    from strict_moment import UNIT,power_interval

    old=json.loads((package/"RESULT.json").read_bytes())
    assert SCALES==(1,2) and WEIGHTS==(1,90) and SPLITS==1008 and LOWER==2048
    assert ins.GAUSSIAN_C==C and ins.TERMINAL.rank_logs==(8192,129414,524288)
    assert ins.TERMINAL.complex_log==483871
    early=ins.ENTRY
    terminal=replace(ins.TERMINAL,rank_logs=(8192,129414,524349),kappa=K)
    assert terminal.rank_logs[-1].bit_length()==ins.TERMINAL.rank_logs[-1].bit_length()==20
    ins.TERMINAL=terminal
    ins.PROFILES["terminal"]=terminal
    low,high=prepare_native()
    assert tuple(q.rank_log for q in low)==(*early.rank_logs,early.complex_log)
    assert tuple(q.rank_log for q in high)==(*terminal.rank_logs,terminal.complex_log)
    assert low[-1].cells is high[-1].cells and low[-1].targets is high[-1].targets
    assert all(q.width_log==92*q.rank_log and not hasattr(q,"count") for q in (*low,*high))
    numerical=high[-1]
    types=numerical.types()
    real = [[len(x.targets),len(x.paid)] for x in types]
    assert real==[[52608,282576],[52608,281568]]
    assert [x.multiplicity for x in types]==[1,90]
    cells=numerical.cells
    assert numerical.trial==C and numerical.ambient==306 and len(cells)==51
    typed=numerical.typed_cells()
    assert len(typed)==88
    assert typed[1,112,1,258]/types[1].targets.count(258)==Q(1,624)
    assert all(5*r<=4*k and v>0 for (r,k),v in cells.items())
    observed_paid = Counter()
    for native in types:
        for rank, count in Counter(native.paid).items():
            observed_paid[rank] += native.multiplicity * count
    assert observed_paid == numerical.paid.histogram

    def power(r,t):
        r=Q(r)
        a,b=power_interval(r.numerator,t)
        s,z=power_interval(r.denominator,t)
        return Q(a,z),Q(b,s)

    t=1-C
    psi=Q(0)
    for (r,k),share in cells.items():
        edge_power_lower=power(Q(k,r),C)[0]
        assert edge_power_lower>1
        psi+=numerical.paid.histogram[r]*share*r*(edge_power_lower-1)/C
    axes=sum(k*v for k,v in numerical.targets.histogram.items())
    fringe=Q(10*axes)/(t*psi)
    assert axes==135150528 and psi>Q("184971191.2157") and fringe<Q("7.335168")
    eps=Q(1,2**128)
    factor=(1+eps)*(1+Q(4*258,1024*306))*power(1024*306*LOWER,C)[1]
    factor*= (1+fringe/LOWER+eps)/(1-eps)**4
    factor_cap=power(2,D)[0]
    assert factor<factor_cap
    assert power(2,Q(65081,524288))[0]>factor_cap
    assert C-D/483871>K+5*G>C-Q(65081,524288)/483871

    # Native fixed setup stores grade descriptors and rank parameters. It
    # leaves all dynamic calendars to the recurring tape budget.
    grade_count=len(numerical.paid.histogram)+len(numerical.targets.histogram)
    real_rows=sum(sum(x) for x in real)
    assert real_rows<2**20 and grade_count<2**8 and max(len(low),len(high))<=4
    max_bits=max(max(v.numerator.bit_length(),v.denominator.bit_length())
                 for v in (*cells.values(),*typed.values()))
    assert max_bits<512 and (1-C).denominator==2**42
    added=2**20*256+2**8*256*8+(grade_count+4)**2*32+2**12
    assert added<2**29<2**32
    w=2**38
    z=2*w+2
    scalar=2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2
    store=4*w*2**68
    lookup=8*store*512*128
    fixed=(2**68+1)*(lookup+scalar+2**120)*2**32
    assert fixed<2**228 and store==2**108 and scalar<2**110

    def invoice(p):
        rates=[]
        prior=Q()
        final_slack=None
        for i,h in enumerate(p.rank_logs):
            cap=min(p.eta,(249*(ins.BINARY_C-Q(11,8*h))+prior)/250)
            rate=Q(int(cap*10**21)-1,10**21) if i+1<len(p.rank_logs) else p.ordinary
            assert prior<rate<cap
            prior=rate
            rates.append(str(rate))
            final_slack=cap-rate
        positive=C-D/p.complex_log
        signed=qualify(p.kappa,G,p.ordinary,positive)
        stock=resource_receipt(p)
        A=ins.activation(p)
        assert stock["public_exponent_A"]==A
        for i,cut in enumerate(stock["binary_cuts"],1):
            assert stage_for_width_log(cut-1,len(p.rank_logs),p.rank_logs)==i-1
            assert stage_for_width_log(cut,len(p.rank_logs),p.rank_logs)==i
            assert stage_for_width_log(cut,i-1,p.rank_logs)==i-1
        if min(p.rank_logs)>=8192:
            B=128+320*sum(p.rank_logs)
        else:
            bounds=(first_stage_bound(p.eta),polynomial_to_fibre_bound())
            B=40+17+16384*sum(p.rank_logs)+sum(max(0,e-944*h)
                                              for e,h in zip(bounds,p.rank_logs,strict=True))
        clock=max(84500001,1602+220*p.complex_log+B)
        return {"kappa":str(p.kappa),"ordinary_rates":rates,"signed":signed,
                "ordinary_final_gap":str(final_slack),
                "gaussian_gap":str(positive-p.ordinary),"stock":stock,
                "geometry":entrance_geometry(A),"log2_B":B,"log2_C":clock}

    first,last=invoice(early),invoice(terminal)
    assert first["log2_B"]==old["entry"]["log2_B"]
    A=last["stock"]["public_exponent_A"]
    boundary=1<<A
    public=boundary+(-boundary)%6
    assert ins.at_public(public-6) is early and ins.at_public(public) is terminal
    premium=ceil((K-early.kappa)*A)
    clock=1+max(first["log2_C"]+premium,last["log2_C"])
    return {
        "peer_exact_head":HEAD,"kappa_candidate":str(K),"delta_vs_8058":str(K-OLD_K),
        "gaussian_raw":str(C),"gaussian_debit":str(D),
        "weighted_calendar_prefix":LOWER,"literal_widths":SCALES,"weights":WEIGHTS,
        "physical_counts":real,"cell_counts":[len(cells),len(typed)],
        "fixed_datum_bits_upper":w,"max_share_bits_observed":max_bits,
        "fixed_grade_recipe_actions_upper":added,"fixed_recipe_shape":[[v.rank_log for v in seq]
                                                                    for seq in (low,high)],
        "fixed_native_setup_clock_upper":fixed,"fixed_native_setup_clock_log2_upper":228,
        "fixed_native_record_store_upper":store,
        "exact_psi_lower_floor_1e4":int(psi*10**4),
        "exact_fringe_upper_1e9":ceil(fringe*10**9),
        "finite_factor_upper_1e12":ceil(factor*10**12),
        "finite_factor_reserve_lower_1e12":int((factor_cap-factor)*10**12),
        "entry":first,"terminal":last,
        "entry_fee_bits":premium,"first_public_offset":public-boundary,
        "complete_recurring_log2_C":clock,
        "scope":"native fixed compiler and exact price audit; full new scientific replay pending",
        "pins":PINS,
    }


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--research",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--child",action="store_true")
    a=p.parse_args()
    if a.child:
        with tempfile.TemporaryDirectory(prefix="weighted-audit-") as t:
            result=evaluate(a.research.resolve(),Path(t)/"runtime")
        with a.out.open("x") as out:
            json.dump(result,out,indent=2,sort_keys=True)
            out.write("\n")
    else:
        t=time.monotonic()
        r=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=90)
        print(f"exit={r.returncode} seconds={time.monotonic()-t:.3f}")
        raise SystemExit(r.returncode)
