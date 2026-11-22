"""One detached 8-level ordinary transfer, with exact stage and signed tape controls."""
from argparse import ArgumentParser
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time

HEAD = "e4fccb224ce5d9bc530a8027d4f617a6a37d4562"
PINS = {
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "prepare.py": "3008490ace39180d90c27cec497976072ed46103641593278cc64194ac6b3fac",
    "RESULT.json": "755ff19972c4a1709d837174f8f13a572b20ef8069112dae53566d9bea87c584",
    "verify.py": "d623b66ac478fcb2ef1429f7b6ac4fcc80e73d2330abe4bdde99852e09c3e659",
}
K7 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
K = Q(".00389821057")
G = Q(1, 10**18)
DEBIT = Q(64944, 524288)
RANKS = (8192, 129406, 524403)


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


def check(capsule, tmp):
    for name,d in PINS.items():
        assert digest(capsule/name)==d,name
    old_result=json.loads((capsule/"RESULT.json").read_bytes())
    old=runpy.run_path(str(capsule/"verify.py"))["restore"](tmp)
    runpy.run_path(str(capsule/"prepare.py"))["materialize"](old)
    runtime=tmp/"image"
    subprocess.run([sys.executable,"-IB",str(old/"bootstrap.py"),str(runtime)],check=True,timeout=20)
    sys.path.insert(0,str(runtime))
    from upstream import install
    install()
    tier=old.parent/"tiered-native-multiplier"
    sys.path.append(str(tier/"source"))
    import installations as ins
    from activation import resource_receipt
    from band_product import prepare_native
    from linear_geometry import entrance_geometry
    from outer_budget import qualify
    from ordinary_carrier import stage_for_width_log
    from raw_binary_stage import binary_word
    from staged_carriers import entrance_logs

    inherited=("strong-bit.json.gz","binary_receiver.py","ordinary_carrier.py","five_exchange.py",
               "raw_binary_stage.py","transport.py","band_product.py")
    payload={name:digest(runtime/name) for name in inherited}
    assert payload["strong-bit.json.gz"]==digest(tier/"source/strong-bit-k7.json.gz")==K7
    before=ins.TERMINAL
    after=replace(before,rank_logs=RANKS,kappa=K)
    assert before.rank_logs==(8192,129414,524395) and before.kappa==Q(".00389821053")
    assert (before.complex_log,after.complex_log)==(483871,483871)
    a=prepare_native(before)
    b=prepare_native(after)
    w=binary_word()
    assert [r.rank_log for r in b]==[*RANKS,483871] and a[-1] is b[-1] and a[0] is b[0]
    assert all(r.targets is w.targets and r.paid is w.paid and r.cells is w.cells
               for r in (*a[:-1],*b[:-1]))
    assert (len(w.targets),len(w.paid),len(w.cells))==(18906,104652,24)

    result={}
    for label, p in (("R390",before),("R391",after)):
        cuts=tuple(entrance_logs(p.rank_logs))
        expected=(8290,137768,662227) if label=="R390" else (8290,137760,662227)
        assert cuts==expected
        for i,c in enumerate(cuts,1):
            assert [stage_for_width_log(c+d,3,p.rank_logs) for d in (-1,0,1)]==[i-1,i,i]
            assert stage_for_width_log(c+1,i-1,p.rank_logs)==i-1
        stage=[verify_stage(p,cuts,2,140000),verify_stage(p,cuts,3,670000)]
        compile_stage=[verify_stage(p,cuts,2,1100000),verify_stage(p,cuts,3,4400000)]
        assert all(x["direct"] for x in stage) and not any(x["direct"] for x in compile_stage)
        rate=Q(0)
        rates=[]
        for i,h in enumerate(p.rank_logs):
            limit=min(p.eta,(249*(ins.BINARY_C-Q(11,8*h))+rate)/250)
            rate=p.ordinary if i==2 else Q(int(limit*10**21)-1,10**21)
            assert rate<limit
            rates.append(str(rate))
        gaussian=ins.GAUSSIAN_C-DEBIT/p.complex_log
        signed=qualify(p.kappa,G,p.ordinary,gaussian)
        stock=resource_receipt(p)
        assert stock["binary_cuts"]==list(cuts)
        result[label]={"ordinary_gap":str(limit-rate),"gaussian_gap":str(gaussian-rate),
                       "rates":rates,"signed":signed,"stock":stock,"direct":stage,
                       "compiled":compile_stage,"geometry":entrance_geometry(ins.activation(p))}

    assert result["R390"]["rates"]==old_result["terminal"]["ordinary_rates"]
    for key in ("stock","signed","geometry"):
        assert result["R390"][key]==old_result["terminal"][key],key
    assert result["R390"]["geometry"]==result["R391"]["geometry"]
    stock=tuple(result[name]["stock"] for name in ("R390","R391"))
    assert stock[0]["absolute_log2_private_control_envelope"]+8192==stock[1]["absolute_log2_private_control_envelope"]
    assert stock[0]["public_exponent_A"]==stock[1]["public_exponent_A"]==1146346
    assert sum(before.rank_logs)==sum(after.rank_logs)==662001
    assert 128+320*sum(after.rank_logs)==211840448
    assert 1+1602+220*after.complex_log+211840448==old_result["complete_log2_C"]==318293671

    tape=[verify_tape(1,[0,1],[2,1]),verify_tape(2,[1,7],[3,1])]
    assert payload=={name:digest(runtime/name) for name in inherited}
    return {"baseline_head":HEAD,"capsule_pins":PINS,"literal_inherited_runtime_hashes":payload,
            "target":str(K),"delta":str(K-before.kappa),"heights":RANKS,
            "proof_scope":"literal pinned emitter and reduced tape; exact stage parameters on detached profile",
            "signed_tape_transposition":tape,"verified_profiles":result,
            "pending":"literal candidate binding and full registered signed replay"}


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--capsule",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--child",action="store_true")
    args=p.parse_args()
    if not args.child:
        start=time.monotonic()
        result=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=90)
        print(f"exit={result.returncode} seconds={time.monotonic()-start:.3f}")
        raise SystemExit(result.returncode)
    with tempfile.TemporaryDirectory(prefix="ordinary-transfer-") as tmp:
        r=check(args.capsule.resolve(),Path(tmp))
    with args.out.open("x") as f:
        json.dump(r,f,indent=2,sort_keys=True)
        f.write("\n")


if __name__=="__main__":
    main()
