"""Authenticate and reject one adjacent type-one Gaussian paid fusion."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from itertools import islice
import json
from math import isqrt
from pathlib import Path
import runpy
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

HEAD = "2d0d7d378929269b00dcabfac1099b2bb23b3b3b"
PEER = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
PACKAGE = "research/p104-weighted-optimal-allocation"
PINS = {
    "RESULT.json": "03eb56a8c62976a10cd37718fbb77a849db0620196514a5fb2ae2318de0e450b",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "prepare.py": "f45daf92a2459de76a0a091c0fb53fa3c893edd157dd9f7d2d29df1e75f47b57",
    "verify.py": "a30cf62aa1a9ca1dd25972135a97751c73af12e2de2c3ba64775acb000c51544",
}
RUNTIME = {
    "clock_ports.py": "7d67eb9db9c50fec056440ef17acc6566cdcac740f44d74790213a5179d34b1e",
    "grades.py": "6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d",
    "raw48.py": "86c30fd4a906830bb6f4b54cdc0be083bd2649bebf68da7383efd7beee223700",
    "typed_raw.py": "0c268432c9d48798c17d927f2d900b5e69dfc6585166cd71f253913e389c3b47",
    "typed_transport.py": "b76b9ad3dc0dd91473026c079585f830387eaa3c34c25a7820ee5057d5cbf941",
}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def pin(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, f"Source differs at {path.name}")
    return raw

def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], timeout=10)

def quote_power(n, q):
    grid = 2**112
    lo = hi = n*grid
    low = high = grid
    for bit in range(q.denominator.bit_length()-2,-1,-1):
        lo, hi = isqrt(lo*grid), isqrt(hi*grid-1)+1
        if q.numerator>>bit&1:
            low,high=low*lo//grid,-(-high*hi//grid)
    return Q(low,grid),Q(high,grid)

def cap(result, ranks):
    trial = Q(result["gaussian"]["trial"])
    d_g = Q(result["gaussian"]["raw_loss"])
    binary, d = Q(4391986206293, 2**50), Q(result["ordinary_finite_debit"])
    margin = Q(5, 10**18)
    t = 1-trial
    a,b = map(lambda r: quote_power(r,t), (ranks[0],sum(ranks)))
    gain = (451*(2*a[0]-b[1]),451*(2*a[1]-b[0]))
    need(gain[0]>0, "Fusion must show positive optimistic raw saving at the booked tariff")
    old = result["terminal"]
    h,g = tuple(old["ordinary_H"]),old["numerical_H"]
    clock = result["complete_log2_C"]
    need((h,g,clock)==((8192,124847,524288),490664,318292451), "Installed resource controls differ")
    weights = (Q(1,62500),Q(1,250),Q(1))
    beta = Q(249,250)
    upper = 524288
    ordinary = Q()
    for i,height in enumerate(h):
        ordinary = beta*(binary-d/height) + ordinary/250
        need(ordinary<Q(".0039"), "Unexpected capped ordinary stage")
        if i < 2:
            ordinary = Q((ordinary*10**21).__floor__()-1,10**21)
    # All larger Gaussian heights leave an ordinary budget nested below this
    # active-box tangency. Floors cannot alter its strict integer optimizer.
    slopes = [w/v**2 for w,v in zip(weights,h,strict=True)]
    ideal = binary*(1-Q(1,250**3))-beta*d*sum(w/v for w,v in zip(weights,h,strict=True))
    tangent_margin = beta*d*min(slopes[1]-slopes[0],slopes[2]-slopes[1],slopes[1])
    need(0<=ideal-ordinary<tangent_margin and sum(h)==(clock-1731-220*g)//320,
         "Whole-family integer tangent comparison fails")
    prior_gaussian = trial-d_g/(g-1)
    current_gaussian = trial-d_g/g
    need(prior_gaussian<ordinary<current_gaussian, "Expected exact two-supplier crossing")
    current = ordinary-margin
    need(current==Q(104641888400286240891629336349,26843545600000000000000000000000)
         and 0<current-Q(old["kappa"])<Q(1,10**16), "Old installed ceiling differs")
    return {"raw_paid_moment_saving_if_admitted_at_old_tariff": list(gain),
            "optimistic_ceiling_granting_free_gaussian_and_independent_maximum_ordinary_heights":
                (binary-d/upper)*(1-Q(1,250**3))-margin,
            "ordinary_ideal_ceiling_at_repair_height":ideal-margin,
            "old_installed_family_ceiling":current,
            "optimistic_complete_ceiling_after_unchanged_interface_repair":current,
            "certified_old_kappa":Q(old["kappa"]),
            "gaussian_upper_below_old_crossing":prior_gaussian-margin,
            "gaussian_ceiling_at_old_crossing":current_gaussian-margin,
            "tangent_height_and_clock":[list(h),g,clock],
            "integer_tangent_gap_before_snap":tangent_margin}

class DeferredRead(Exception):
    pass

def trace(runtime):
    sys.path.insert(0,str(runtime))
    from upstream import HERE, install
    _,_,_,source=install()
    from strong_complex import artifacts
    from clock_ports import clock_word
    from periodic import Job
    import raw48, typed_raw, typed_transport, grades
    import clock_ports
    modules=[raw48,typed_raw,typed_transport,grades,clock_ports]
    for mod in modules:
        path=Path(mod.__file__)
        pin(path,RUNTIME[path.name])
    atlas=artifacts(source/"research/grade14-native-realization",HERE/"inputs")
    word=clock_word(atlas)
    rows=list(islice(atlas.instructions(),708))
    labels=tuple((p.tag,p.rank) for p in word.paid[:2])
    need(labels==((("IDLE_ONE",684,4080),56),(("IDLE_ONE",707,4095),56)), "Pinned cohort changed")
    maximum=max(word.targets.ranks())*2
    need(maximum==258 and tuple(grades.WEIGHTS)==(5,451), "Pinned target/weights differ")
    want=[None]
    touched=[]
    class Field:
        def __init__(self,label=None,returned=False):
            self.label=label
            self.returned=returned
        def copy(self):
            self.read("copy")
            return Field(self.label,self.returned)
        def scale(self,*_):
            self.read("scale")
        def scale_add(self,other,*_):
            self.read("scale_add_destination")
            other.read("scale_add_source")
            self.returned |= other.returned
        def read(self,method):
            if self.returned:
                touched.append((want[0],method))
        def swap(self,*_):
            pass
        def retire(self):
            pass
        def replace(self,other):
            if isinstance(other,Deferred):
                raise DeferredRead(want[0])
            self.returned=other.returned
    class Deferred:
        pass

    inputs=[Job(i,range(p.rank*4)) for i,p in enumerate(word.targets)]
    def open_raw():
        fields={i:Field(p.tag) for i,p in enumerate(word.targets)}
        def instructions():
            for i,row in enumerate(rows):
                want[0]=i
                yield row
        run_atlas=SimpleNamespace(**vars(atlas))
        run_atlas.instructions=instructions
        columns=SimpleNamespace(window=1,offset=0,swap=None,row=lambda *_:None)
        return typed_raw.TypedRaw(word,raw48.ComplexRaw(run_atlas,fields,columns,low=0,bundle=1,slots=612)).native(inputs,3),fields

    known_good,fields=open_raw()
    first=next(known_good)
    need(want[0]==684 and len(first.axes)==4*56,"Old first paid request")
    label_a=fields[first.owner].label
    fields[first.owner]=Field(label_a,True)
    second=next(known_good)
    need(want[0]==707 and len(second.axes)==4*56,"Old second paid request")
    label_b=fields[second.owner].label
    known_good.close()
    next_read=min((clock for clock,_ in touched if clock>684),default=None)
    need(next_read is not None and next_read<707 and label_a!=label_b,"First returned owner must have intervening dependence")
    delayed,fields=open_raw()
    first_delayed=next(delayed)
    fields[first_delayed.owner]=Deferred()
    try:
        next(delayed)
    except DeferredRead as error:
        need(error.args==(684,), "Deferred result consumed at wrong clock")
    else:
        raise ValueError("Deferred first return unexpectedly survived to second yield")

    def plan(r):
        types=tuple(typed_transport.NativeType((maximum,), (r,), 1) for _ in range(2))
        shares={(i,r,i,maximum):Q(1) for i in range(2)}
        return typed_transport.TypedPlan(2**14,types,shares,Q(511,512),10,16,2**30,3,2**16,delay_base=2**19)
    need(plan(112).source_width>0,"Original grade-112 funded periodic control")
    try:
        plan(224)
    except ValueError as error:
        need(str(error)=="A physical funding edge fails strict descent","Wrong reason for the fused failure")
        rejection=str(error)
    else:
        raise ValueError("The pinned calendar accepted a grade-224 funding edge")
    second_writes = [[clock, row] for clock,row in enumerate(rows[685:707],685)
                     if row[0] not in ("PORT_VIEWS", "NATIVE")
                     and (row[1]==4095 or row[0]=="SWAP" and row[2]==4095)]
    return {"paid_ordinals":[0,1],"native_tags":[tag for tag,_ in labels],"physical_ranks":[112,112],
            "root_owner_labels":[label_a,label_b],"different_owner_tokens":True,
            "first_return_installed_at_clock":684,"first_intervening_read":next_read,
            "first_intervening_instruction":rows[next_read],
            "first_read_actual_field_callbacks":[[clock,op] for clock,op in touched if clock==next_read],
            "second_operand_issued_at_clock":707,"deferred_first_return_rejected_at_clock":684,
            "intervening_second_root_writes":second_writes,
            "fixture":{"type":1,"base_even_columns":2,"physical_columns":4},
            "max_target_grade":maximum,"target_grade_required_for_fused":280,
            "bound_check":[5*224,4*maximum],"actual_calendar_negative":rejection,
            "old_two_request_control":True,"owner_scope":"Trace tracks literal native field binding and read order; no floating phase or arbitrary-state output claim"}

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--baseline",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    signal.alarm(60)
    baseline=a.baseline.resolve()
    need(git(baseline,"rev-parse","HEAD").decode().strip()==HEAD,"Wrong baseline Git head")
    for name,expected in PINS.items():
        path=baseline/PACKAGE/name
        need(pin(path,expected)==git(baseline,"show",f"{HEAD}:{PACKAGE}/{name}"),"Checkout bytes differ from commit")
    pkg=baseline/PACKAGE
    result=json.loads((pkg/"RESULT.json").read_bytes())
    with TemporaryDirectory(prefix="gaussian-paid-fusion-") as tmp:
        work=Path(tmp)
        peer=runpy.run_path(str(pkg/"verify.py"))["restore"](work)
        runpy.run_path(str(pkg/"prepare.py"))["materialize"](peer)
        runtime=work/"runtime"
        subprocess.run([sys.executable,"-IB",str(peer/"bootstrap.py"),str(runtime)],timeout=20,check=True)
        occurrence=trace(runtime)
    receipt={"status":"EXCLUDED_LITERAL_TWO_REQUEST_FUSION",
             "scope":"First two existing type-one paid requests, one fused request, unchanged ownership ABI, typed strict-descent calendar and booked stock; exact rollback retains both original timed payments",
             "baseline":HEAD,"inherited_peer_science":PEER,
             "baseline_package_pins":PINS,"installed_source_pins":RUNTIME,
             "occurrence":occurrence,"bound":cap(result,occurrence["physical_ranks"])}
    signal.alarm(0)
    a.out.write_text(json.dumps(receipt,indent=2,default=str,sort_keys=True)+"\n")
if __name__=="__main__":
    main()
