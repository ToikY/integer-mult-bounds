"""Price one eight-level ordinary transfer against the exact replayed supplier."""
from argparse import ArgumentParser
import ast
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import runpy
import signal
import subprocess
import tarfile
from types import SimpleNamespace

HEAD = "e4fccb224ce5d9bc530a8027d4f617a6a37d4562"
PKG = "research/p104-weighted-upper-band"
FREQ = "research/frequency-weighted-native-multiplier/"
TIER = "research/tiered-native-multiplier/"
K0, K = Q(".00389821053"), Q(".00389821057")
BINARY, ETA = Q(4391986206293, 2**50), Q(".0039")
G, D, CG = Q(1,10**18), Q(64944,2**19), Q(17145637307,2**42)
OLD, NEW, LESS = (8192,129414,524395), (8192,129406,524403), (8192,129407,524402)

PINS = {
    "round390/preflight.log": "d593fed8dbf1808ad9d256fcce80f8506432d01c0be634d20f32e5abf9282358",
    "round390/exact-head": "f332bcd5c97e13104f8549c119244d902f311f5301a2e173c845c3d09f49516e",
    "round390/scientific.log": "9a3e5db1106844d26ea14a5622aff4032de94fa176544ba3a219157d64729a6e",
    "round390/scientific.exit": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "round390/onboarding.log": "7bd03a787cda5976a257852c61a74266840d5f171650385e7e5a7e5fe48131b3",
    "round390/onboarding.exit": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "round390/independent/verified.json": "d3725f1e0133c3111322ad9ef4f6381aa3d1c7d7173eecc6129874ce30e43980",
    "round378/independent/accept.py": "001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
}
BASE_PINS = {
    "prepare.py": "3008490ace39180d90c27cec497976072ed46103641593278cc64194ac6b3fac",
    "RESULT.json": "755ff19972c4a1709d837174f8f13a572b20ef8069112dae53566d9bea87c584",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}
ANCESTORS = {
    TIER + "source/installer.tar.gz": "6696459e2e3552f802e7caaaf93dc86c9bb6b62ee38631702bff2e3a8a9a481a",
    "retimed-source.tar.gz": "3d30e35c5a77f43372e94ccca7aaa38ce706631fc5b4601293bbd8619dfb2775",
    "retimed-source.tar.gz::machine.patch": "c1f53687f856898641d2c81f0deeaecfbf8daa7a7b66d2a9fda2bb7e85447431",
    "retimed-source.tar.gz::predecessor/predecessor-8030.tar.gz": "769d5a05cc1373fa22ed5956af636992fcd19d7e5c1753a32033a73c358cd31c",
    "predecessor-8030.tar.gz::inputs/triangular/staged_carriers.py": "6c925ae4b39dc9999ac5891d1a27dcbb38e129a36e1473b2b418f27a806b6fc4",
    "predecessor-8030.tar.gz::linear_geometry.py": "6628fcddf1eed2ffa39c2d3256d79577b950e04c4a688161a66ba92baa3fb7c2",
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def auth(raw, sha, name):
    need(sha256(raw).hexdigest()==sha, f"Hash mismatch at {name}")
    return raw


def unique(pairs):
    obj={}
    for name,value in pairs:
        need(name not in obj,f"Duplicate JSON key {name}")
        obj[name]=value
    return obj


def parse(raw):
    return json.loads(raw,object_pairs_hook=unique)


def archived_member(raw, name, key):
    with tarfile.open(fileobj=BytesIO(raw)) as tar:
        paths=[row for row in tar if row.name==name]
        need(len(paths)==1 and paths[0].isfile() and ".." not in PurePosixPath(name).parts,
             f"One archived member {name}")
        return auth(tar.extractfile(paths[0]).read(),ANCESTORS[key],key)


def api(raw, name, only=None, **globals_):
    code=ast.parse(raw,filename=name)
    if only is not None:
        code.body=[x for x in code.body if isinstance(x,ast.FunctionDef) and x.name in only]
        need({x.name for x in code.body}==set(only), f"Exact callable inventory for {name}")
    exec(compile(code,name,"exec"),globals_)
    return globals_


def archived_caller(outer):
    install=TIER+"source/installer.tar.gz"
    retimed="retimed-source.tar.gz"
    previous="predecessor/predecessor-8030.tar.gz"
    original="predecessor-8030.tar.gz"
    staged="inputs/triangular/staged_carriers.py"
    geometry="linear_geometry.py"
    i=auth(outer[install],ANCESTORS[install],install)
    r=archived_member(i,retimed,retimed)
    p=archived_member(r,previous,f"{retimed}::{previous}")
    v=archived_member(p,staged,f"{original}::{staged}")
    l=archived_member(p,geometry,f"{original}::{geometry}")
    patch=archived_member(r,"machine.patch",f"{retimed}::machine.patch").decode()
    marker="+def stage_for_width_log("
    need(patch.count(marker)==1,"One installed runtime selector implementation")
    selector=marker+patch.split(marker,1)[1].split("\n+\n",1)[0]
    lines=selector.splitlines()
    need(all(line.startswith("+") for line in lines),"Only added source in patched selector")
    source=api(v,staged)
    runtime=api("\n".join(line[1:] for line in lines),"machine.patch",entrance_logs=source["entrance_logs"])
    geom=api(l,geometry,("entrance_geometry","minimum_window","connected_exponent"),
             ceil_log2=lambda n:(n-1).bit_length())
    bank=TIER+"source/"
    stock=api(outer[bank+"activation.py"],"activation.py")["resource_receipt"]
    qualify=api(outer[bank+"outer_budget.py"],"outer_budget.py")["qualify"]
    return source["entrance_logs"],runtime["stage_for_width_log"],geom,stock,qualify


def up(x):
    return -(-x.numerator//x.denominator)


def funding(heights):
    stage_rates=[]
    for h in heights:
        previous=stage_rates[-1] if stage_rates else Q()
        cap=min(ETA,(249*(BINARY-Q(11,8*h))+previous)/250)
        stage_rates.append(Q(int(cap*10**21)-1,10**21))
        need(previous<stage_rates[-1]<cap,"Strictly increasing earlier native bookings")
    return stage_rates[:-1],cap


def candidate(inputs,repo):
    inputs=inputs.resolve()
    repo=repo.resolve()
    read={name:auth((inputs/name).read_bytes(),sha,name) for name,sha in PINS.items()}
    log=read["round390/scientific.log"]
    need(read["round390/exact-head"].decode().strip()==HEAD
         and f'"commit": "{HEAD}"'.encode() in read["round390/preflight.log"], "Completed exact predecessor head")
    need(read["round390/scientific.exit"].strip()==b"0"
         and all(f"PASS_WEIGHTED_UPPER_BAND {mode}\n".encode() in log
                 for mode in ("price","calendar","raw","exterior","nested","product","setup"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in log,
         "Prior registered replay completed all seven modes")
    need(read["round390/onboarding.exit"].strip()==b"0"
         and b"Ran 760 tests" in read["round390/onboarding.log"]
         and b"OK (skipped=31)" in read["round390/onboarding.log"], "Prior repository gates passed")
    for name,sha in BASE_PINS.items():
        path=f"{PKG}/{name}"
        raw=subprocess.check_output(["git","-C",str(repo),"show",f"{HEAD}:{path}"],timeout=10)
        need(raw==auth((repo/path).read_bytes(),sha,path),f"Frozen Git bytes {name}")
    old=parse((repo/PKG/"RESULT.json").read_bytes())
    independent=parse(read["round390/independent/verified.json"])
    need(Q(independent["kappa"])==K0 and Q(old["terminal"]["kappa"])==K0
         and independent["status"].startswith("INDEPENDENT_LITERAL_PRICE_AND_BOUNDARY_REPLAY_PASS")
         and independent["candidate_and_gate_pins"]["capsule/RESULT.json"]==BASE_PINS["RESULT.json"],
         "Authenticated predecessor independent replay")
    base=runpy.run_path(str(inputs/"round378/independent/accept.py"))["restore_reference"](repo/PKG)
    need(len(base)==88,"Every inherited source input")
    cuts,selector,geom,stock,qualify=archived_caller(base)

    g=old["gaussian"]
    numerical=old["terminal"]["numerical_H"]
    positive=CG-D/numerical
    need(g["weights"]==[5,451] and Q(g["raw_loss"])==D and Q(g["trial"])==CG
         and g["finite_loss"]["upper_divisor"]==1724 and Q(old["terminal"]["gaussian_rate"])==positive
         and numerical==483871, "Same signed positive supplier and exact debit")
    early=old["entry"]
    need(qualify(Q(early["kappa"]),G,Q(early["ordinary_rates"][-1]),CG-D/early["numerical_H"])==early["signed"],
         "Exact unchanged signed entry tier 54+4")
    booked_before, before=funding(OLD)
    oldcap=min(before,positive)-5*G
    need(list(OLD)==old["terminal"]["ordinary_H"]
         and [Q(v) for v in old["terminal"]["ordinary_rates"]]==booked_before+[K0+5*G]
         and oldcap>K0, "Reconstruct the prior installed ceiling")
    booked, cap=funding(NEW)
    _, cap_less=funding(LESS)
    maximum_rate=min(cap,positive)-5*G
    control_rate=min(cap_less,positive)-5*G
    fixed_rate=K+5*G
    passes=booked[-1]<fixed_rate<cap and fixed_rate<positive
    result={"status":"PRICE_FAIL","comparator_head":HEAD,"old_kappa":str(K0),"target_kappa":str(K),
            "tested_heights":NEW,"negative_control_heights":LESS,"actual_prior_installed_cap":str(oldcap),
            "candidate_installed_cap":str(maximum_rate),"seven_level_installed_cap":str(control_rate),
            "inputs_sha256":PINS,"comparator_files_sha256":BASE_PINS,"ancestor_leaf_sha256":ANCESTORS}
    if not passes:
        return result
    need(control_rate<K and oldcap<K and sum(OLD)==sum(NEW)==sum(LESS),
         "Eight-level price beats both the old crossing and the one-fewer-transfer control")

    profile=SimpleNamespace(rank_logs=NEW,complex_log=numerical,eta=ETA)
    s=stock(profile)
    old_stock=old["terminal"]["stock"]
    expected=list(cuts(NEW))
    need(s["binary_cuts"]==expected and expected==[8290,137760,662227]
         and expected[1]==old_stock["binary_cuts"][1]-8
         and [i for i in (0,2) if expected[i]==old_stock["binary_cuts"][i]]==[0,2],
         "True earlier middle and identical final deadlines")
    boundaries=[]
    for i,cut in enumerate(expected,1):
        outcomes=(selector(cut-1,3,NEW),selector(cut,3,NEW),selector(cut,i-1,NEW))
        need(outcomes==(i-1,i,i-1),"Both top and nested stage selection on exact adjacent widths")
        boundaries.append([cut,*outcomes])
    need(selector(expected[1],3,OLD)==1 and selector(expected[1],3,NEW)==2
         and selector(expected[1]-1,3,NEW)==1 and expected[1]+2<NEW[2],
         "Literal stage-two admission actually moves and remains legal as a recursive child")
    exponent=s["public_exponent_A"]
    offset=s["first_public_offset"]
    entry_width=(1<<exponent)+offset
    geometry=geom["entrance_geometry"](exponent)
    need(geom["connected_exponent"](expected[-1],numerical)==exponent==1146346
         and geometry==old["terminal"]["geometry"]
         and entry_width%6==0 and entry_width.bit_length()==exponent+1
         and (entry_width-6).bit_length()==exponent,
         "Identical dense root and both sides of first actual terminal public header")
    need(s["absolute_log2_private_control_envelope"]==old_stock["absolute_log2_private_control_envelope"]+8*1024
         and all(s[k]==old_stock[k] for k in s if k not in ("absolute_log2_private_control_envelope","binary_cuts")),
         "Recompute changed private envelope and preserved whole linear storage")
    signed=qualify(K,G,fixed_rate,positive)
    need((signed["strict"],signed["functional"])==(54,4),"Complete terminal signed tier")
    log_b=128+320*sum(NEW)
    log_c=1602+220*numerical+log_b
    premium=up((K-Q(early["kappa"]))*exponent)
    need(log_b==old["terminal"]["log2_B"] and log_c==old["terminal"]["log2_C"]
         and premium==old["entry_price_surcharge"]==514
         and 1+max(log_c,early["log2_C"]+premium)==old["complete_log2_C"]==318293671,
         "Complete recurring ordinary/positive clocks and finite early conversion")
    width=2**38
    z=2*width+2
    scalar=2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2
    setup=(2**68+1)*(8*(4*width*2**68)*512*128+scalar+2**120)*2**32
    need(max(NEW).bit_length()==max(OLD).bit_length()==20
         and setup==old["native_setup_transition_upper"]<2**228
         and old["native_setup_grade_actions"]==269057152<2**32,
         "Same fixed setup envelope, precision representation and grade actions")
    floors=[up(Q(11,8)/(BINARY-fixed_rate)),up(D/(CG-fixed_rate))]
    result.update(status="VIABLE_PRICE_ONLY",delta_kappa=str(K-K0),gain_percent=str(100*(K-K0)/K0),
                  separation_from_old_installed_cap=str(K-oldcap),ordinary_margin=str(cap-fixed_rate),
                  gaussian_margin=str(positive-fixed_rate),ordinary_rates=[str(v) for v in booked+[fixed_rate]],
                  exact_stage_controls=boundaries,installed_report_applies_to_both_signed_tiers=True,
                  terminal_stock=s,terminal_geometry=geometry,terminal_signed=signed,entry_signed=early["signed"],
                  complete_log2_C=318293671,entry_surcharge_bits=premium,fixed_funding_height_floors=floors,
                  native_fixed_setup_upper=setup)
    return result


if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--inputs",type=Path,required=True)
    parser.add_argument("--repo",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    signal.alarm(60)
    result=candidate(args.inputs,args.repo)
    signal.alarm(0)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
