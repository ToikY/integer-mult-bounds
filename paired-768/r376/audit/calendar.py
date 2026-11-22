"""Audit the 48-bit retune against the installed literal Calendar/Measure."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile
import time

PINS = {
    "bootstrap.py": "ac5c3a6e1645257c65f2a5653cd55d222dd076d39cf5cdb55ea63aca4e8db6da",
    "quarter_overlay.py": "da8efaf6c5210c499af7560ab7f2ade13c8d538ab454e5200c13d19d0051245e",
    "SOURCES.json": "d40e10c78e2a1cc74797b5e8735c2f37d955f9e84ba4e6abbc549ee42434bf1f",
    "RESULT.json": "0d20d4607fd2d68dfe0aaf84e063d986cb2c8e614a89dcd3a825135d62e075c6",
    "CLOCK.md": "cf71e4a3216df23eb7e4fa8a8d9de3735e6257c65ca8a60a5085d9f3c90c4ecb",
    "NUMERICAL.md": "14b86724db522393981ed54b540a35f27bd952f3d95d6e6d14c5b23896811dc9",
    "SETUP.md": "6951a98f2f8a0bf73c8d60b16ebbbd66bf87584251df8afbefe4e3a0330bfbf3",
    "source/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
}
EXTRA = {
    "coupling.py": "fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    "coupling.json": "2828f5a208b24b3c556313601d6f05a62fef57509e58dc00d161c9f2d8023553",
}
C = Q(1097317122991,2**48)
DEBIT = Q(339,2048)
K = Q(".00389821005")
G = Q(1,10**18)
H_MIN = 1024


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def ceil(q):
    return -(-q.numerator//q.denominator)


def inverse_by_forward_power(x,t,bits):
    """Independently enclose x^t first, then invert at the end."""
    grid=2**bits
    q=x*grid
    lo,hi=q.numerator//q.denominator,ceil(q)
    result_lo=result_hi=grid
    assert 0<t<1 and t.denominator.bit_count()==1
    for bit in range(t.denominator.bit_length()-2,-1,-1):
        lo,hi=isqrt(lo*grid),1+isqrt(hi*grid-1)
        if (t.numerator>>bit)&1:
            result_lo=result_lo*lo//grid
            result_hi=-(-result_hi*hi//grid)
    return Q(grid,result_hi),Q(grid,result_lo)


def compute(stage,coupling,work):
    for name,sha in PINS.items():
        assert digest(stage/name)==sha,name
    for name,sha in EXTRA.items():
        assert digest(coupling/name)==sha,name
    receipt=json.loads((coupling/"coupling.json").read_bytes())
    assert Q(receipt["raw_trial"])==C and Q(receipt["gaussian_debit_units"])==DEBIT
    assert Q(receipt["kappa_if_complete_replay_passes"])==K
    assert receipt["recurring_clock_log2_upper"]==340530371
    cells={(Q(r),Q(k)):Q(v) for r,k,v in receipt["transport_cells"]}
    assert len(cells)==63 and cells[4424,10191]==1 and max(k/r for r,k in cells)==9
    assert all(v>0 and 4*k>=5*r for (r,k),v in cells.items())
    margins=[]
    for r,k in cells:
        err=Q(-1,2) if r==Q(1,4) else Q(1,2) if r==Q(3,4) else Q(0)
        lower=8*k-10*r+min(0,err)
        assert 0<=lower and 10*k-8*r+max(0,err)<10*k and err<=8*r
        margins.append(lower)
    assert min(margins)==Q(1,2)
    widest=max(max(p.numerator.bit_length(),p.denominator.bit_length()) for p in cells.values())
    assert widest==receipt["largest_reduced_cell_bits"]==263
    numerical_ambient=12087
    delta=Q(1,2**128)
    # Quantize the factor using the independent directed square-root routine
    # from the price artifact. This is separate from the actual calendar
    # inverse-power test below.
    cert=runpy.run_path(str(coupling/"coupling.py"))
    unit=cert["UNIT"]
    factor=(Q(256,255)*Q(4097,4096)*Q(1028,1024)
            * Q(cert["power_interval"](Q(1024*numerical_ambient*32768),C)[1],unit)
            * (1+Q(64,32768)+delta)/((1-Q(10,32768))*(1-delta)**3))
    assert factor**2048<2**339
    assert factor**256>=2**42  # Tightening retains a genuine positive finite-height debit.
    fringe=Q(10)*Q(106,100)/(Q(996,1000)*Q(99,100)*Q(19,100))
    assert fringe<64 and Q(100,99)**250>4 and Q(99,100)*Q(2,9)>Q(19,100)

    N=2**H_MIN
    grids=64*(H_MIN+1)
    assert (1-C).denominator==2**48
    assert Q(1,40764*N)-Q(1,2**grids)>Q(1,65536*N)
    root_factor_exponent=(H_MIN+16)//2+2
    mass_width_bits=49*root_factor_exponent+6+6*H_MIN+2-grids
    assert mass_width_bits+49<-132
    assert 49<2*(64-6)
    assert 40766<32*2066 and 2**80*N**93<N**96
    assert 2**46*N**2<Q(N**6,2**132)
    assert 2*N**6*564144*N*Q(N**77,N**82)<Q(N**6,2**132)
    # Each endpoint operation can use a schoolbook 512(H+1)-bit schedule
    # workspace. Less than 256 such root/product/division actions per mass
    # query leave large room in the inherited N^700 control-only bill.
    workspace_bits=512*(H_MIN+1)
    arithmetic_proxy=2**30*(2*workspace_bits+4)**2
    assert arithmetic_proxy<2**(H_MIN//8)

    destination=work/"installed"
    subprocess.run([sys.executable,"-IB",str(stage/"bootstrap.py"),str(destination)],
                   check=True,timeout=15)
    transport_path=destination/"transport.py"
    transport=runpy.run_path(str(transport_path))
    t=1-C
    measure=transport["Measure"](t,N**6,grids)
    assert measure.grid==2**grids
    U=2*(N//(2048*numerical_ambient))
    points=(Q(32768),Q(65539,2),Q(U-2),Q(40764*N))
    checked=[]
    for x in points:
        a,b=measure.inverse_power(x)
        lo,hi=inverse_by_forward_power(x,t,grids+96)
        assert Q(a,measure.grid)<=lo<=hi<=Q(b,measure.grid)
        integral=measure.mass(x,x+2) if x+2<=points[-1] else measure.mass(x-2,x)
        assert 0<integral[0]<=integral[1] and integral[1]-integral[0]<Q(1,4)
        checked.append({"argument_bits":x.numerator.bit_length(),
                        "inverse_interval_units":b-a,
                        "integral_error_less_than_quarter":True})

    # Small complete rounded-size identity with the actual constructor,
    # event and singleton methods, using a direct-paid all-exterior fixture.
    plan=transport["Plan"](2**20,[1]*4,[Q(1,4),Q(3,4)],
                           {(Q(1,4),1):Q(1),(Q(3,4),1):Q(1)},t,
                           32768,32772,2**70,4,256,delay_base=2)
    records=plan.events()
    birth,issue=next(records),next(records)
    assert birth[2]==32762 and issue[3]==8190 and issue[4]==0
    whole=sum(plan.ticks*plan.count[e]*(e-8) for e in plan.bands)
    assert plan.leaves_per_epoch==whole
    for w in (32760,32762):
        assert transport["paid_axis_count"](Q(1,4),w)==w//4
        assert transport["paid_axis_count"](Q(3,4),w)==w-w//4
    try:
        transport["paid_axis_count"](Q(1,4),32761)
    except ValueError:
        pass
    else:
        raise ValueError("Odd width accepted")

    # Recompute the tier funding, retaining the exact inherited signed gates.
    outer=runpy.run_path(str(stage/"source"/"outer_budget.py"))
    binary=Q(4391986206293,2**50)
    bench={}
    for name,h1,h2,H,k in (("entry",3000,3080,1024,Q(".00345")),
                            ("terminal",35327,561325,680000,K)):
        first=Q(int(Q(249,250)*(binary-Q(11,8*h1))*10**21)-1,10**21)
        ordinary_limit=(249*(binary-Q(11,8*h2))+first)/250
        ordinary=k+5*G
        assert first<ordinary<ordinary_limit and ordinary<Q(39,10000)
        positive=C-DEBIT/H
        signed=outer["qualify"](k,G,ordinary,positive)
        assert signed==receipt[name]["signed"]
        bench[name]={"ordinary_gap":str(ordinary_limit-ordinary),
                     "gaussian_gap":str(positive-ordinary),"inequalities":signed}

    return {
        "candidate_kappa":str(K),"gaussian_C":str(C),"gaussian_debit":str(DEBIT),
        "support_cells":len(cells),"largest_share_bits":widest,
        "smallest_integral_prefix_reserve":str(min(margins)),
        "whole_fringe_coefficient_upper":str(fringe),
        "retimed_factor_millionth_upper":ceil(factor*10**6),
        "root_iterations":48,"product_count_upper":49,
        "actual_calendar_checks":checked,
        "calendar_transport_sha256":digest(transport_path),
        "odd_width_rejected":True,"rounded_paid_leaf_total_reconciles":True,
        "analytic_mass_error_bits_upper_at_H1024":mass_width_bits,
        "control_workspace_bits_per_number_at_H1024":workspace_bits,
        "funding":bench,
        "scope":"one retuning audit on the already-installed R374 calendar, no candidate full replay",
        "stage_pins":PINS,"support_pins":EXTRA,
    }


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for n in ("stage","coupling","out"):
        p.add_argument("--"+n,type=Path,required=True)
    p.add_argument("--child",action="store_true")
    a=p.parse_args()
    if a.child:
        with tempfile.TemporaryDirectory(prefix="calendar48-audit-") as temp:
            answer=compute(a.stage.resolve(),a.coupling.resolve(),Path(temp))
        with a.out.open("x") as f:
            json.dump(answer,f,sort_keys=True,indent=2)
            f.write("\n")
    else:
        start=time.perf_counter()
        r=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=90)
        print(f"exit={r.returncode} seconds={time.perf_counter()-start:.3f}")
        raise SystemExit(r.returncode)
