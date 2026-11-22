"""Independently bind the literal R392 transfer to its signed arithmetic and seams."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal

PUB = "round390/publish/research/p104-weighted-upper-band"
OLD_HEAD = "e4fccb224ce5d9bc530a8027d4f617a6a37d4562"
PINS = {
    "round390/exact-head": "f332bcd5c97e13104f8549c119244d902f311f5301a2e173c845c3d09f49516e",
    "round390/preflight.log": "d593fed8dbf1808ad9d256fcce80f8506432d01c0be634d20f32e5abf9282358",
    "round390/scientific.log": "9a3e5db1106844d26ea14a5622aff4032de94fa176544ba3a219157d64729a6e",
    "round390/scientific.exit": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "round390/onboarding.log": "7bd03a787cda5976a257852c61a74266840d5f171650385e7e5a7e5fe48131b3",
    "round390/onboarding.exit": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "round390/historical.log": "082fffa25c8dd69397b6d5f4c9c852105930e00e5e952cd4f78b45047773c34b",
    "round390/historical.exit": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "round390/independent/verified.json": "d3725f1e0133c3111322ad9ef4f6381aa3d1c7d7173eecc6129874ce30e43980",
    "round378/independent/accept.py": "001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round391/price/check.py": "5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    "round391/price/receipt.json": "19a4795048fb16016801f17c8be6ad9d38715af8a3bd941ae2b44d8c5de43b06",
    "round391/audit/receipt.json": "55a7693e59aa46d80e19adf91bfaaf300a29ce949af5b1cab9732e5ed21f5904",
    "round391/audit/check_stage_transfer.py": "357cef4b84fba359b055527baf383297e7a9d5a0d90ce80c80fddb5fcace4768",
    f"{PUB}/RESULT.json": "755ff19972c4a1709d837174f8f13a572b20ef8069112dae53566d9bea87c584",
    f"{PUB}/prepare.py": "3008490ace39180d90c27cec497976072ed46103641593278cc64194ac6b3fac",
    f"{PUB}/VERIFY.json": "7117e597401db68b4ce91cc5a58836b4604d985cc31626dbd70c5daa2ef73f99",
}
FREQ = "research/frequency-weighted-native-multiplier/"
TIER = "research/tiered-native-multiplier/"
K0,K = Q(".00389821053"), Q(".00389821057")
G,BINARY,C,D = Q(1,10**18), Q(4391986206293,2**50), Q(17145637307,2**42), Q(64944,2**19)
HEIGHTS = (8192,129406,524403)
OLD, SEVEN = (8192,129414,524395), (8192,129407,524402)
H = 483871
K7 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return sha256(raw).hexdigest()


def read(path,digest):
    data=path.read_bytes()
    need(sha(data)==digest,f"Authentication {path.name}")
    return data


def unique(pairs):
    result={}
    for k,v in pairs:
        need(k not in result,f"Duplicate source key {k}")
        result[k]=v
    return result


def parse(raw):
    return json.loads(raw,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def budgets(heights,booking, *, ideal=False):
    """Solve the entire ordinary recurrence in whole units of 1/(10**21)."""
    rates=[]
    previous=Q()
    for i,h in enumerate(heights):
        bound=min(Q(39,10**4), (249*(BINARY-Q(11,8*h))+previous)/250)
        exact=bound if ideal else Q((bound*10**21).__floor__()-1,10**21)
        if i==len(heights)-1 and not ideal:
            exact=booking+5*G
        need(previous<exact<=bound,"Positive monotone ordinary envelope")
        rates.append(exact)
        previous=exact
    return rates,bound


def layout_rows(heights,cuts):
    rows=[]
    for i,log_width in ((2,140000),(3,670000),(2,1100000),(3,4400000)):
        parent=cuts[i-2]
        height=heights[i-1]
        width=max((1<<parent)+1,1<<(log_width//250))
        direct=(1<<log_width)<=width<<(8*height)
        need(log_width>=cuts[i-1] and log_width%10000==0,"Legal exact stage width")
        rows.append(dict(stage=i,scanned_log=log_width,rank_log=height,
                         predecessor_cut=parent,direct=direct,component_log=39*log_width//10000))
    return rows


def reconstruct(old,new,primary,phase,caller):
    cuts, select, geometry, stock, signed=caller
    positive=C-D/H
    need(new["gaussian"]==old["gaussian"] and new["entry"]==old["entry"]
         and Q(old["terminal"]["gaussian_rate"])==Q(new["terminal"]["gaussian_rate"])==positive,
         "Literal weighted positive invoice and entry tier preserved at all inputs")
    ordinary_before, old_top=budgets(OLD,K0)
    ordinary, top=budgets(HEIGHTS,K)
    _, seven_top=budgets(SEVEN,K,ideal=True)
    old_ceiling=min(old_top,positive)-5*G
    seven_ideal=min(seven_top,positive)-5*G
    need(K-K0==Q(1,25_000_000_000) and K>max(old_ceiling,seven_ideal)
         and K<min(top,positive)-5*G and old_ceiling==Q(primary["actual_prior_installed_cap"]),
         "Crossing separation and negative seven-level control even without earlier rounding")
    rates=[str(v) for v in ordinary]
    need([str(v) for v in ordinary_before]==old["terminal"]["ordinary_rates"] and
         rates==new["terminal"]["ordinary_rates"]==primary["ordinary_rates"],
         "Exact baseline and literal new ordinary bookings")
    s0=stock(SimpleNamespace(rank_logs=OLD,complex_log=H,eta=Q(".0039")))
    s1=stock(SimpleNamespace(rank_logs=HEIGHTS,complex_log=H,eta=Q(".0039")))
    e=s1["public_exponent_A"]
    g=geometry["entrance_geometry"](e)
    a,b=old["terminal"],new["terminal"]
    need(a["stock"]==s0 and b["stock"]==s1==primary["terminal_stock"]
         and a["geometry"]==b["geometry"]==g and g==primary["terminal_geometry"]
         and e==s0["public_exponent_A"]==1146346 and s1["first_public_offset"]==2
         and s1["absolute_log2_private_control_envelope"]-s0["absolute_log2_private_control_envelope"]==8192
         and s1["storage_upper"]=="6.2 p T < 297.6 n bits", "Retimed native stock, actual first header and geometry")
    need(e==geometry["connected_exponent"](cuts(HEIGHTS)[-1],H)
         and tuple(cuts(HEIGHTS))==(8290,137760,662227)
         and tuple(cuts(OLD))==(8290,137768,662227), "True middle eight-level deadline transfer")
    header=(1<<e)+2
    need(header%6==0 and header.bit_length()==e+1 and (header-6).bit_length()==e,
         "Exact public header and prior entry")
    controls=[]
    stages={}
    for label,hs in (("R390",OLD),("R391",HEIGHTS)):
        c=cuts(hs)
        stages[label]=layout_rows(hs,c)
        prior=phase["verified_profiles"][label]
        need(stages[label]==prior["direct"]+prior["compiled"], "R391 exact previous seam evidence")
        for stage,x in enumerate(c,1):
            y=[select(x+j,3,hs) for j in (-1,0,1)]
            need(y==[stage-1,stage,stage] and select(x+1,stage-1,hs)==stage-1,
                 "All before/at/after and nested-previous activation deadlines")
            controls.append([label,x,*y,stage-1])
    need(select(137760,3,OLD)==1 and select(137760,3,HEIGHTS)==2,
         "Runtime stage two starts exactly eight widths earlier")

    signed_terminal=signed(K,G,ordinary[-1],positive)
    entry=new["entry"]
    signed_entry=signed(Q(entry["kappa"]),G,Q(entry["ordinary_rates"][-1]),C-D/entry["numerical_H"])
    need((signed_entry["strict"],signed_entry["functional"],signed_terminal["strict"],signed_terminal["functional"])
         ==(54,4,54,4) and signed_entry==entry["signed"] and signed_terminal==b["signed"],
         "Every strict and functional signed gate")
    log_b=128+320*sum(HEIGHTS)
    log_c=max(84500001,1602+220*H+log_b)
    premium=up((K-Q(entry["kappa"]))*e)
    complete=1+max(log_c,entry["log2_C"]+premium)
    need(sum(HEIGHTS)==sum(OLD)==662001 and log_b==211840448==b["log2_B"]
         and log_c==b["log2_C"] and premium==new["entry_price_surcharge"]==514
         and complete==new["complete_log2_C"]==old["complete_log2_C"]==318293671,
         "Same complete paid recurring and finite surcharge")
    w=2**38
    z=2*w+2
    scalar=2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2
    setup=(2**68+1)*(8*4*w*2**68*512*128+scalar+2**120)*2**32
    need(max(HEIGHTS).bit_length()==max(OLD).bit_length()==20 and new["max_native_H"]==524403
         and new["native_setup_transition_upper"]==old["native_setup_transition_upper"]==setup<2**228
         and new["native_setup_grade_actions"]==old["native_setup_grade_actions"]==269057152<2**32,
         "Fixed precision and separately fully charged setup")
    fixed_floors=[up(Q(11,8)/(BINARY-ordinary[-1])),up(D/(C-ordinary[-1]))]
    need(fixed_floors==new["fixed_funding_height_floors"]==[517541,483867],
         "Exact lower floors on each funded source")
    return stages,dict(kappa=str(K),delta_kappa=str(K-K0),gain_percent=str(100*(K-K0)/K0),
        exact_old_installed_cap=str(old_ceiling),strict_old_cap_separation=str(K-old_ceiling),
        even_ideally_funded_seven_transfer_ceiling=str(seven_ideal),
        ideal_seven_transfer_shortfall=str(K-seven_ideal),last_ordinary_slack=str(top-ordinary[-1]),
        unchanged_positive_rate=str(positive),gaussian_slack=str(positive-ordinary[-1]),
        complete_log2_C=complete,fixed_setup_bound=setup,stage_boundary_controls=controls,
        private_control_envelope=s1["absolute_log2_private_control_envelope"])


def verify_overlay(old, capsule, archive, before_plan):
    a,b=(runpy.run_path(str(p/"prepare.py")) for p in (old,capsule))
    base,current=(d["EDITS"] for d in (a,b))
    need(base.keys()==current.keys(),"Same set of source overlays")
    need({k for k in base if base[k]!=current[k]}=={"runtime.patch","receipt.py","independent_price.py","verify.py"},
         "Only scalar installment and checking source changes")

    def emitted(changes):
        out={}
        for f,pairs in changes.items():
            text=archive[FREQ+f].decode()
            for x,y in pairs:
                need(text.count(x)==1,f"Single literal replacement in {f}")
                text=text.replace(x,y)
            out[f]=text
        return out

    before,after=(emitted(x) for x in (base,current))
    need(after["runtime.patch"]==before["runtime.patch"].replace(
          '129414, 524395), 483871, Q(".00389821053")',
          '129406, 524403), 483871, Q(".00389821057")'),
         "Only terminal H2, H3 and rate change in installed machine patch")
    need(b["NEW_INSTALLATION"]=="47a51f380ffbe68578adcec81925e3e7bc2e5cf1b9a21450b256ce60ff0cd3c3",
         "Authenticate final installed profile bytes")
    for name in ("PEER-SOURCE.json","peer8057.tar.gz","check_cutoff.py"):
        need((capsule/name).read_bytes()==(old/name).read_bytes(),f"Unchanged inherited {name}")
    unchanged_route=("typed_raw.py","typed_transport.py","grades.py","positive_debit.py","check_calendar.py",
                     "check_raw.py","check_exterior.py","check_nested.py","check_ownership.py","check_placement.py")
    stable={}
    for name in unchanged_route:
        original=archive[FREQ+name]
        old_source=before[name].encode() if name in before else original
        new_source=after[name].encode() if name in after else original
        need(old_source==new_source,f"Same signed ownership, phase, cutoff and Gaussian cost at {name}")
        stable[FREQ+name]=sha(new_source)
    raw_k7=archive[TIER+"source/strong-bit-k7.json.gz"]
    need(sha(raw_k7)==K7,"Same exact K7 file used by every physical ordinary stage")
    stable[TIER+"source/strong-bit-k7.json.gz"]=K7
    expected_wrapper=(old/"verify.py").read_text().replace(
           '(peer / "check_cutoff.py").write_bytes((HERE / "check_cutoff.py").read_bytes())',
           'for name in ("check_cutoff.py", "check_stage_seam.py"):\n'
           '            (peer / name).write_bytes((HERE / name).read_bytes())').replace(
           "PASS_WEIGHTED_UPPER_BAND","PASS_ORDINARY_TRANSFER")
    need((capsule/"verify.py").read_text()==expected_wrapper and
         after["verify.py"]==before["verify.py"].replace(
           '("check_calendar.py", "check_ownership.py", "check_cutoff.py")',
           '("check_calendar.py", "check_ownership.py", "check_cutoff.py", "check_stage_seam.py")'),
         "Literal ordinary seam added to inherited coverage")
    active_plan=parse((capsule/"VERIFY.json").read_bytes())
    modes=lambda j:[(x["argv"],x["timeout_seconds"]) for x in j["commands"]]
    need(modes(active_plan)==modes(before_plan) and len(modes(active_plan))==7
         and sum(secs for _,secs in modes(active_plan))==1170,
         "Seven registered replay commands with same coverage and limits")
    return stable


def check(inputs,capsule,log,frozen):
    data={name:read(inputs/name,digest) for name,digest in PINS.items()}
    known=parse(data["round390/independent/verified.json"])
    need(f'"commit": "{OLD_HEAD}"'.encode() in data["round390/preflight.log"]
         and data["round390/exact-head"].strip()==OLD_HEAD.encode()
         and known["candidate_and_gate_pins"]["capsule/RESULT.json"]==PINS[f"{PUB}/RESULT.json"]
         and known["candidate_and_gate_pins"]["capsule/prepare.py"]==PINS[f"{PUB}/prepare.py"]
         and Q(known["kappa"])==K0,"Exact comparator commits, result and independently verified adapter")
    need(all(data[f"round390/{name}.exit"].strip()==b"0" for name in ("scientific","onboarding","historical"))
         and b"PASS_REGISTERED_RESEARCH_PACKAGE research/p104-weighted-upper-band outcome=completed" in
             data["round390/scientific.log"] and b"Ran 760 tests" in data["round390/onboarding.log"]
         and b"OK (skipped=31)" in data["round390/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in data["round390/historical.log"],
         "Prior complete signed, repository and historical gates are authentic")
    names={"prepare.py","verify.py","RESULT.json","VERIFY.json","TASK.json","SOURCES.json",
           "PEER-SOURCE.json","peer8057.tar.gz","check_cutoff.py","check_stage_seam.py"}
    need(frozen.keys()=={f"capsule/{x}" for x in names}|{"build.log"},"Exact path-keyed candidate evidence")
    bytes_={x:read(capsule/x,frozen[f"capsule/{x}"]) for x in names}
    gate=read(log,frozen["build.log"]).decode()
    need("regenerate exit 0" in gate and "PASS_WEIGHTED_COMPLETE_PRICE 318293671" in gate
         and "PASS_INDEPENDENT_WEIGHTED_AND_QUARTER_PRICES" in gate
         and "PASS_ORDINARY_TRANSFER price" in gate
         and "PASS_ORDINARY_TRANSFER calendar" in gate
         and "PASS_LITERAL_UPPER_FENCE 1724 1874 (1024, 483871)" in gate
         and "PASS_LITERAL_LOWER_CUTOFF 1874" in gate,
         "Preserved numerical cutoff controls and literal transfer ran")
    marker="PASS_LITERAL_ORDINARY_TRANSFER "
    evidence=[line[len(marker):] for line in gate.splitlines() if line.startswith(marker)]
    need(len(evidence)==1,"One successful literal transfer gate")
    evidence=parse(evidence[0])
    old,new=parse(data[f"{PUB}/RESULT.json"]),parse(bytes_["RESULT.json"])
    need(Q(new["previous_rate"])==K0 and Q(new["rate_delta"])==K-K0
         and Q(old["terminal"]["kappa"])==K0 and Q(new["terminal"]["kappa"])==K
         and tuple(new["terminal"]["ordinary_H"])==HEIGHTS
         and new["terminal"]["numerical_H"]==old["terminal"]["numerical_H"]==H,
         "The complete literal receipt binds the fixed ordinary transfer")
    primary,phase=(parse(data[p]) for p in ("round391/price/receipt.json","round391/audit/receipt.json"))
    need(primary["comparator_head"]==phase["baseline_head"]==OLD_HEAD
         and tuple(phase["heights"])==tuple(primary["tested_heights"])==HEIGHTS and Q(primary["target_kappa"])==K,
         "Both sealed preflight receipts cover those same exact inputs")
    restore=runpy.run_path(str(inputs/"round378/independent/accept.py"))["restore_reference"]
    archive=restore(capsule)
    need(len(archive)==88 and phase["literal_inherited_runtime_hashes"]["strong-bit.json.gz"]==K7,
         "All 88 path-pinned archive sources and the old native K7 identity")
    stable=verify_overlay(inputs/PUB,capsule,archive,parse(data[f"{PUB}/VERIFY.json"]))
    caller=runpy.run_path(str(inputs/"round391/price/check.py"))["archived_caller"](archive)
    stages,receipt=reconstruct(old,new,primary,phase,caller)
    expected=[]
    for label,heights,cuts in (("R390",OLD,[8290,137768,662227]),("R391",HEIGHTS,[8290,137760,662227])):
        expected.append({"ranks":list(heights),"cuts":cuts,"direct":stages[label][:2],"compiled":stages[label][2:]})
    need(evidence["stage_seams"]==expected
         and Q(evidence["seven_level_negative_gap"])==Q(receipt["ideal_seven_transfer_shortfall"]),
         "The literal direct and compiled seams agree exactly with the archived selector and R391 phase receipts")
    reduced=[{"component_width":j,"modulus":m,"records":m**4,"paid_exchanges":n,
              "wrong_signed_return_rejected":True} for j,m,n in ((1,3,3),(2,9,1))]
    need(evidence["signed_tape"]==phase["signed_tape_transposition"]==reduced,
         "Both literal reduced signed arbitrary-record controls reproduce")
    seam=bytes_["check_stage_seam.py"].decode()
    need("(18906,104652,24)" in seam and K7 in seam and "w=binary_word()" in seam
         and "old[0] is new[0] and old[-1] is new[-1]" in seam,
         "Literal passing benchmark asserts immutable K7 and shared provider reuse")
    return {"status":"INDEPENDENT_LITERAL_TRANSFER_PASS; FULL_REGISTERED_SCIENCE_SEPARATE","comparator":OLD_HEAD,
            "pinned_evidence":PINS,"frozen_candidate":frozen,"unchanged_native_and_calendar":stable,
            "verified_archive_paths":len(archive),"literal_paid_seams":evidence,"literal_k7_roles":[18906,104652,24],
            **receipt}


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--inputs",type=Path,required=True)
    p.add_argument("--capsule",type=Path,required=True)
    p.add_argument("--log",type=Path,required=True)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    signal.alarm(60)
    receipt=check(a.inputs,a.capsule,a.log,parse(a.frozen.read_bytes()))
    signal.alarm(0)
    a.out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
