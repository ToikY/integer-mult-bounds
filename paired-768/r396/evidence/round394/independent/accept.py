"""Reconstruct the revised ordinary debit and bind it to the actual two-tier build."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha1,sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal

HEAD="ffa64503646a62a7ac3cd2c47787d670da911f89"
PKG="research/p104-weighted-ordinary-transfer"
OLD="round392/publish/"+PKG
FREQ="research/frequency-weighted-native-multiplier/"
TIER="research/tiered-native-multiplier/"
PROOF_COMMIT="dfd25d553a843a946ca0b94130a5ff8943e98fdd"
PROOF_PINS={
    "TRANSFER.md":("c8a5afa257aeddb47825e843b1c9063f9b9a05e3","7164831a5dd9f5c6231bf4c3f4b2061d91cbfab559071a0a5d68966e3f7ac55c"),
    "RECEIVER.md":("90ed818f7273a9cd275ade1774f87ffa94f42a5c","f31089b6304fc5352feb9aa8a963cc5a950a828165d3426e16e8a973529d814e"),
    "ORDINARY-CLOCK.md":("7155d52a9006c044e8df87f9cf320f3cef61d58c","4694db0b2218796e348c1128271cebb3fc779151a639b0e0fb5bbecf9f3ccb94"),
}
PINS={
    "round392/exact-head":"6e3af7c5273d0d0bbd0767b4b67e19696b5b16ea6b5c07fb87a91bfebe0d8cab",
    "round392/preflight.log":"910725b496aced72618a0d222532fa129e3251ee37dad247306065fdea168291",
    "round392/independent/verified.json":"dcf57d8bab8cfc76769b0f9d8b570d233e670032b8ab2aed481172ff21c3c2a9",
    "round393/price/COMPLETE.json":"6989eb5749cde5e3343f81aaa4a98792af2fe852b37b9981e60ce36aa866ed48",
    "round393/price/receipt.json":"07645666c11fa427e8b039fec0eebf2e6b9858d1d43919ff117cad48292a891d",
    "round393/audit/check.py":"d1b52c5b3bec3395fc193d099186c14441a464faea337bcee2ff35663f054bcf",
    "round393/audit/receipt.json":"a37b7cd070bc2d78d163dd7bba8bb97d37a3a829df4f5420a58ed8ab7abf1a21",
    "round378/independent/accept.py":"001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round375/independent/coupling.py":"fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    "round391/price/check.py":"5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    f"{OLD}/RESULT.json":"65b29858741c054434863612a357b9c6b833d8865530812659943293ff1155f5",
    f"{OLD}/prepare.py":"3862a6fb149d5d35be194ace5dd9c135013e46abdaa3d6396641a85af794e788",
    f"{OLD}/VERIFY.json":"fa5bb791bbc6c8a7fb9069c41c2ef3a1a2903fc6c1af0ebd53a3d01559bc5252",
}
K7="9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
K0,K=Q(".00389821057"),Q(".00389821103")
B,C=Q(4391986206293,2**50),Q(17145637307,2**42)
D0,D,DG=Q(11,8),Q(703,512),Q(64944,524288)
G,ETA=Q(1,10**18),Q(".0039")
H0,H=483871,484799
OLD_H,HS=(8192,129406,524403),(8192,129406,523763)
UNIT=2**112


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return sha256(raw).hexdigest()


def pin(path,digest):
    raw=path.read_bytes()
    need(sha(raw)==digest,f"Authentic bytes at {path.name}")
    return raw


def unique(pairs):
    keys={}
    for k,v in pairs:
        need(k not in keys,f"Duplicate key {k}")
        keys[k]=v
    return keys


def parse(b):
    return json.loads(b,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def proof_sources(path,routines,price,audit):
    proofs={}
    for name,(blob,digest) in PROOF_PINS.items():
        data=pin(path/name,digest)
        need(sha1(f"blob {len(data)}\0".encode()+data).hexdigest()==blob,f"Exact Git blob {name}")
        proofs[name]=data.decode()
    need(all(x in proofs["TRANSFER.md"] for x in (
         "L=32768","A=134","(256/255)(4097/4096)(1028/1024)(1024 A L)^c",
         "(1+64/L+δ) / [(1−10/L)(1−δ)^3]")),
         "Exact original all-size raw finite invoice")
    need(all(x in proofs["RECEIVER.md"] for x in ("75/32","47/20","375/376","3^N-1")) and
         all(x in proofs["ORDINARY-CLOCK.md"] for x in ("(75/32)(P(N)/B)N^(−s)","s=t and s=1","at most 376")),
         "Physical restored receiver and both moment cost normalizations")
    power=routines["power_interval"]
    delta=Q(1,2**128)
    L,A=32768,134
    shared=Q(256,255)*Q(4097,4096)*Q(1028,1024)*(1+Q(64,L)+delta)
    shared/= (1-Q(10,L))*(1-delta)**3
    floor,ceil=(Q(n,UNIT)*shared*Q(47,20) for n in power(Q(1024*A*L),B))
    debit_floor=Q(power(Q(2),D)[0],UNIT)
    need(ceil.numerator**512 < (ceil.denominator**512)<<703
         and floor.numerator**512 > (floor.denominator**512)<<702
         and ceil.numerator**8 < (ceil.denominator**8)<<11
         and debit_floor>ceil and up(ceil*10**15)==price["full_factor"]["finite_factor_ceiling_1e15"]
         and (floor*10**12).__floor__()==audit["charged_factor_lower_1e12"]
         and up(ceil*10**12)==audit["charged_factor_upper_1e12"],
         "Exact paid factor is below the new dyadic debit and prior control")
    child=Q(47,20)
    worst_small_rank=Q(7,3)+Q(16,3*(3**8-1))
    rho=Q(75,32)/child
    need(worst_small_rank<Q(75,32)<child and rho==Q("375/376")
         and 1/(1-rho)==376 and 0<B-D/min(HS)<1,
         "Fixed mean upper, normalized contraction and unchanged all-depth sum")
    return {"proof_commit":PROOF_COMMIT,
            "proof_sources":{name:{"git_blob":blob,"sha256":digest} for name,(blob,digest) in PROOF_PINS.items()},
            "all_size_child_factor":str(child),"same_stage_two_moment_ratio":str(rho),
            "all_depth_multiplier":376,"factor_upper_1e15":up(ceil*10**15),
            "same_envelope_fails_at_702_over_512":True,
            "directed_debit_headroom_floor_1e15":((debit_floor-ceil)*10**15).__floor__()}


def ordinary(heights, debit, stop=None):
    previous=Q()
    bounded=[]
    for i,h in enumerate(heights):
        cap=min(ETA,(249*(B-debit/h)+previous)/250)
        if stop is None:
            rates=cap
        elif i+1==len(heights):
            rates=stop
        else:
            rates=Q((cap*10**21).__floor__()-1,10**21)
        need(previous<rates<=cap and (stop is None or rates<cap),"All strict ordinary charges")
        bounded.append(rates)
        previous=rates
    return bounded,cap


def check_rates(baseline,new,price,audit,archive,caller):
    cuts,dispatch,geom,stock,qualify=caller
    early,terminal=new["entry"],new["terminal"]
    need(new["gaussian"]==baseline["gaussian"] and new["gaussian"]["finite_loss"]==audit["gaussian_loss"]
         and Q(new["gaussian"]["raw_loss"])==DG and Q(new["gaussian"]["trial"])==C,
         "Complete raw, Gaussian cost and owner shares retained")
    need(Q(baseline["terminal"]["kappa"])==K0 and tuple(baseline["terminal"]["ordinary_H"])==OLD_H
         and baseline["terminal"]["numerical_H"]==H0
         and Q(terminal["kappa"])==K and tuple(terminal["ordinary_H"])==HS and terminal["numerical_H"]==H,
         "Actual old and new installed profiles")
    rates_old,cap_old=ordinary(OLD_H,D0,K0+5*G)
    old_cross=min(cap_old,C-DG/H0)-5*G
    _,old_at_new=ordinary(HS,D0)
    bad_gap=K+5*G-old_at_new
    need([str(r) for r in rates_old]==baseline["terminal"]["ordinary_rates"]
         and old_cross==Q(price["prior_actual_installed_cap"])<K
         and bad_gap==Q(audit["old_debit_ideal_negative_gap"])>0
         and old_at_new-5*G==Q(price["same_heights_ideal_cap_old_debit"]),
         "Exact old installed price and old debit rejected even under ideal earlier funding")
    book=K+5*G
    terminal_rates,cap=ordinary(HS,D,book)
    positive=C-DG/H
    need(K<min(cap,positive)-5*G and
         [str(x) for x in terminal_rates]==terminal["ordinary_rates"]==price["terminal_rates"],
         "Literal new terminal directed ordinary and positive margins")
    exact_caps=[]
    for name,row,booked,h,heights in (("entry",early,Q(".00345")+5*G,1024,(3000,3080)),
                                    ("terminal",terminal,book,H,HS)):
        k=booked-5*G
        rt,cover=ordinary(heights,D,booked)
        plant=SimpleNamespace(rank_logs=heights,complex_log=h,eta=ETA)
        resources=stock(plant)
        A=resources["public_exponent_A"]
        spectrum=geom["entrance_geometry"](A)
        signed=qualify(k,G,booked,C-DG/h)
        witness=audit[f"complete_signed_{name}"]
        need(Q(row["kappa"])==k and row["ordinary_H"]==list(heights) and row["numerical_H"]==h
             and row["ordinary_rates"]==witness["ordinary_rates"]==[str(x) for x in rt]
             and row["signed"]==witness["signed"]==signed
             and signed["strict"]==54 and signed["functional"]==4
             and row["stock"]==witness["stock"]==resources and row["geometry"]==witness["geometry"]==spectrum
             and cover-booked==Q(witness["ordinary_gap"])>0
             and Q(row["gaussian_rate"])-booked==Q(witness["gaussian_gap"])>0,
             "Both exact tiers, every signed inequality and complete retimed resource envelope")
        exact_caps.append(str(cover-booked))
    s=terminal["stock"]
    a=s["public_exponent_A"]
    c=cuts(HS)
    need(list(c)==s["binary_cuts"]==[8290,137760,661587]
         and geom["connected_exponent"](c[-1],H)==a==1146634
         and s["absolute_log2_private_control_envelope"]==536333315
         and s["storage_upper"]=="6.2 p T < 297.6 n bits",
         "Exact active cuts, signed caller and total private stack")
    header=(1<<a)+(-pow(2,a,6))%6
    need(header%6==0 and header-(1<<a)==2 and (header-6).bit_length()==a
         and header.bit_length()==a+1,"First true public terminal header and preceding entry")
    seams=[]
    for i,cut in enumerate(c,1):
        decisions=[dispatch(cut+j,3,HS) for j in (-1,0,1)]
        need(decisions==[i-1,i,i] and dispatch(cut+1,i-1,HS)==i-1,
             "Actual archived stage selector around each new cutoff")
        seams.append([cut,*decisions,i-1])
    b=128+320*sum(HS)
    time=max(84500001,1602+220*H+b)
    premium=up((K-Q(".00345"))*a)
    complete=1+max(time,early["log2_C"]+premium)
    need(b==terminal["log2_B"]==211635648 and time==terminal["log2_C"]
         and premium==new["entry_price_surcharge"]==514 and early["log2_C"]==baseline["entry"]["log2_C"]
         and complete==new["complete_log2_C"]==318293031==baseline["complete_log2_C"]-640,
         "Every recurring tape or finite-prefix cost remains charged")
    w=2**38; z=2*w+2
    serial=2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2
    setup=(2**68+1)*(8*4*w*2**68*512*128+serial+2**120)*2**32
    floors=[up(D/(B-book)),up(DG/(C-book))]
    need(max(*HS,H).bit_length()==19 and 2**19>max(*HS,H)>=2**18
         and new["native_setup_transition_upper"]==audit["maximum_fixed_setup"]==setup<2**228
         and new["native_setup_grade_actions"]==269057152 <2**32
         and new["max_native_H"]==max(*HS,H)
         and floors==new["fixed_funding_height_floors"]==[516895,484738],
         "Real 19-bit descriptor and full inherited fixed setup, not a smaller asserted envelope")
    return {"delta_kappa":str(K-K0),"gain_percent":str(100*(K-K0)/K0),"strict_old_cap_separation":str(K-old_cross),
            "old_installed_cap":str(old_cross),"old_debit_ideal_shortfall":str(bad_gap),
            "ordinary_headroom_both_tiers":exact_caps,"terminal_gaussian_headroom":str(positive-book),
            "full_recurring_log2":complete,"all_size_live_bits_per_input_upper":"297.6",
            "setup_width_bits":19,"native_setup_ceiling_log2":228,"literal_stages":seams}


def placements(audit,log):
    # Both rounded cutoffs and the first three physical tickets are exact.
    Uscale=1724*306
    m0=1<<1024
    slope=Q(3*258,2*Uscale)
    loss=Q(23*258,2)
    need(1360*slope<1 and (1364*slope-1)*m0>1364*loss,
         "All-height exterior-period bracketing, including 484799")
    actual=[]
    for h in (1024,H):
        m=1<<h
        upper=2*(m//Uscale)
        e=2*(3*upper//8)
        span=258*(e-8)
        period=4*up(Q(m,4*span))
        need(period==1364 and 2*period<5*((period*span-m)//4)
             and 1874<e<upper and upper*112<e*258<(e+2)*258<m*112
             and 451*2*258*m>4*624*112,
             "True first exterior birth, directed nonzero owner and fivefold prefix")
        tickets=[(j*period)//5 for j in range(3)]
        actual.append({"H":h,"cell":[1,112,1,258],"share":"1/624","period":period,"tickets":tickets,
                       "rotated_roots":384,"first_root":["root","rotated",0,4080,1],"first_swap":[1,272,1]})
    anchor="PASS_INDEPENDENT_WEIGHTED_AND_QUARTER_PRICES\n"
    need(log.count(anchor)==1,"Unambiguous literal cost and placement run")
    rows,_=json.JSONDecoder(object_pairs_hook=unique).raw_decode(log.split(anchor,1)[1])
    need(rows==actual and [[r["H"],r["period"],r["tickets"],r["first_swap"]] for r in rows]
         ==[[x["height"],x["period"],x["tickets"],x["first_swap"]] for x in audit["gaussian_placement"]],
         "Actual 1364 placement and both native first swaps agree with independent replay")
    return rows


def verify_overlays(old,capsule,archive,old_plan):
    old_source,new_source=(runpy.run_path(str(root/"prepare.py")) for root in (old,capsule))
    a,b=(s["EDITS"] for s in (old_source,new_source))
    need(a.keys()==b.keys(),"Identical authorized overlay slots")
    need({k for k in a if a[k]!=b[k]}=={"runtime.patch","receipt.py","independent_price.py"},
         "No edits to emitted native word, Gaussian invoice or phase and owner routines")

    def realize(edits):
        out={}
        for name,updates in edits.items():
            code=archive[FREQ+name].decode()
            for before,after in updates:
                need(code.count(before)==1,f"One literal installation locus in {name}")
                code=code.replace(before,after)
            out[name]=code
        return out

    old_overlay,new_overlay=(realize(d) for d in (a,b))
    need(new_overlay["runtime.patch"]==old_overlay["runtime.patch"].replace(
         '8192, 129406, 524403), 483871, Q(".00389821057")',
         '8192, 129406, 523763), 484799, Q(".00389821103")'),
         "Actual runtime patch only changes terminal scalar profile")
    need(new_source["NEW_INSTALLATION"]=="226055f3934b21efd40fbd4d4f7077edf6b24d60197131acd173195f06d8bb89",
         "Correct new installed image digest")
    receipt=new_overlay["receipt.py"]
    need(all(x in receipt for x in ("703", "512", "47, 20", "bit_length()", "<= 20",
                                    "516895, 484738", "318293031")),
         "Active source adopts new ordinary bank, exact bound, fixed-setup bit cap and complete clock")
    for name in ("PEER-SOURCE.json","peer8057.tar.gz","check_cutoff.py"):
        if name=="check_cutoff.py":
            earlier=(old/name).read_text()
            latest=(capsule/name).read_text()
            need(latest==earlier.replace("483871","484799"),"Actual Gaussian constructor height only")
        else:
            need((old/name).read_bytes()==(capsule/name).read_bytes(),f"Identical {name}")
    need((capsule/"verify.py").read_text()==(old/"verify.py").read_text().replace(
         "PASS_ORDINARY_TRANSFER","PASS_ORDINARY_DEBIT"),
         "Same registered wrapper coverage")
    plan=parse((capsule/"VERIFY.json").read_bytes())
    get=lambda p:[(o["argv"],o["timeout_seconds"]) for o in p["commands"]]
    modes=get(plan)
    need(modes==get(old_plan) and [arg[-1] for arg,_ in modes]==[
         "price","calendar","raw","exterior","nested","product","setup"],
         "All seven inherited modes and their timeouts remain")
    kept=("typed_raw.py","typed_transport.py","grades.py","positive_debit.py","check_calendar.py",
          "check_raw.py","check_exterior.py","check_nested.py","check_ownership.py","check_placement.py","verify.py")
    stable={}
    for name in kept:
        from_archive=archive[FREQ+name].decode()
        before=old_overlay.get(name,from_archive)
        after=new_overlay.get(name,from_archive)
        need(before==after,f"Identical signed supplier file {name}")
        stable[FREQ+name]=sha(after.encode())
    need(sha(archive[TIER+"source/strong-bit-k7.json.gz"])==K7,
         "Exact unchanged K7 physical ordinary action")
    stable[TIER+"source/strong-bit-k7.json.gz"]=K7
    return stable


def check(inputs,capsule,sources,build_log,manifest):
    data={p:pin(inputs/p,dig) for p,dig in PINS.items()}
    finished=parse(data["round393/price/COMPLETE.json"])
    need(finished.keys()=={f"round392/{mode}.{ext}" for mode in ("scientific","onboarding","historical")
                          for ext in ("log","exit")},"Every exact R392 log and exit code")
    done={p:pin(inputs/p,dig) for p,dig in finished.items()}
    need(data["round392/exact-head"].strip()==HEAD.encode()
         and f'"commit": "{HEAD}"'.encode() in data["round392/preflight.log"]
         and all(done[f"round392/{m}.exit"].strip()==b"0" for m in ("scientific","onboarding","historical"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in done["round392/scientific.log"]
         and b"Ran 760 tests" in done["round392/onboarding.log"]
         and b"OK (skipped=31)" in done["round392/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in done["round392/historical.log"],
         "Pinned exact comparator full scientific and applicable repository gates")
    previous=parse(data["round392/independent/verified.json"])
    need(previous["frozen_candidate"]["capsule/RESULT.json"]==PINS[f"{OLD}/RESULT.json"] and Q(previous["kappa"])==K0,
         "R392 complete previous physical audit agrees")
    price,audit=(parse(data[f"round393/{key}/receipt.json"]) for key in ("price","audit"))
    need(price["comparator"]==audit["baseline_head"]==HEAD and Q(price["kappa"])==Q(audit["candidate"])==K
         and Q(audit["debit"])==D and audit["heights"]==list(HS) and audit["gaussian_height"]==H,
         "Both exact R393 bounded prerequisites")
    frozen_names={"prepare.py","RESULT.json","check_cutoff.py","check_stage_seam.py","verify.py",
                  "VERIFY.json","TASK.json","SOURCES.json","PEER-SOURCE.json","peer8057.tar.gz"}
    need(manifest.keys()=={f"capsule/{name}" for name in frozen_names}|{"build.log"},
         "Every executable and source dependency is uniquely pinned")
    candidate={p:pin(capsule/p,manifest[f"capsule/{p}"]) for p in frozen_names}
    log=pin(build_log,manifest["build.log"]).decode()
    need(all(m in log for m in ("regenerate exit 0","PASS_WEIGHTED_COMPLETE_PRICE 318293031",
                                "PASS_ORDINARY_DEBIT price","PASS_ORDINARY_DEBIT calendar",
                                "PASS_DIRECTED_ORDINARY_DEBIT 703/512 375/376",
                                "PASS_LITERAL_UPPER_FENCE 1724 1874 (1024, 484799)","PASS_LITERAL_LOWER_CUTOFF 1874")),
         "Actual bounded literal budget and cutoff run")
    historic,active=(parse(raw) for raw in (data[f"{OLD}/RESULT.json"],candidate["RESULT.json"]))
    need(Q(active["previous_rate"])==K0 and Q(active["rate_delta"])==K-K0,
         "Exact literal relative and absolute comparison")
    restore=runpy.run_path(str(inputs/"round378/independent/accept.py"))["restore_reference"]
    archive=restore(capsule)
    need(len(archive)==88,"All original archived paths")
    stable=verify_overlays(inputs/OLD,capsule,archive,parse(data[f"{OLD}/VERIFY.json"]))
    coupling=runpy.run_path(str(inputs/"round375/independent/coupling.py"))
    consumption=proof_sources(sources,coupling,price,audit)
    caller=runpy.run_path(str(inputs/"round391/price/check.py"))["archived_caller"](archive)
    rates=check_rates(historic,active,price,audit,archive,caller)
    routes=placements(audit,log)
    anchor="PASS_LITERAL_ORDINARY_DEBIT "
    found=[line[len(anchor):] for line in log.splitlines() if line.startswith(anchor)]
    need(len(found)==1,"One actual signed native seam receipt")
    seam=parse(found[0])
    need(seam["stage_seams"][1]=={
         "ranks":list(HS),"cuts":[8290,137760,661587],"direct":audit["ordinary_direct_seams"],
         "compiled":audit["ordinary_compiled_seams"]} and seam["signed_tape"]==audit["literal_signed_tape"]
         and Q(seam["old_debit_negative_gap"])==Q(rates["old_debit_ideal_shortfall"])
         and Q(seam["seven_level_negative_gap"])==Q(previous["ideal_seven_transfer_shortfall"])
         and all(row["wrong_signed_return_rejected"] for row in seam["signed_tape"]),
         "Actual changed native return, direct and compiled seams pass known-good and signed negative controls")
    return {"status":"INDEPENDENT_LITERAL_DEBIT_ACCEPTANCE_PASS; FULL_REGISTERED_SUITE_SEPARATE",
            "comparator":HEAD,"kappa":str(K),"sealed_prior_evidence":PINS|finished,
            "frozen_candidate":manifest,"unchanged_native_sources":stable,"literal_exterior":routes,
            "literal_ordinary":seam,"archive_files":len(archive),**consumption,**rates}


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for name in ("inputs","capsule","sources","log","frozen","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    signal.alarm(60)
    receipt=check(a.inputs,a.capsule,a.sources,a.log,parse(a.frozen.read_bytes()))
    signal.alarm(0)
    a.out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
