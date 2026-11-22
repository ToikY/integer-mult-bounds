"""Detach the final literal rank allocation from its exact whole-family price."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal

HEAD="8c800e1b6458526e1ce7a59150bba8a0d29d0027"
PKG="research/p104-weighted-capped-allocation"
BASE="round398/publish/"+PKG
FREQ="research/frequency-weighted-native-multiplier/"
K7_PATH="research/tiered-native-multiplier/source/strong-bit-k7.json.gz"
K7="9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
K0,K=Q(".00389821380"),Q(".0038982141167032")
B,C=Q(4391986206293,2**50),Q(17145637307,2**42)
D,DG=Q(1405,1024),Q(64944,524288)
G,ETA=Q(1,10**18),Q(".0039")
OLD,HS=(8192,124986,524288),(8192,124847,524288)
OLD_G,H=490463,490664
RES=318292711
CLOCK=318292451
L=18960
PINS={
    "round398/exact-head":"9422df8ce76a0206664e5b8ba282e3f642652bfe04490a06fbb9e66dc3a15b0b",
    "round398/preflight.log":"4cc2a884d5ec06cdc01b93a9150778b97eda04af94c2f1f0edfb1ff216360495",
    "round398/independent/verified.json":"18a9c9a64506bbd107305db10f2fac3df42d32b299d0627baba8958ac5d59924",
    "round398/independent/INPUTS.json":"8200aac92e3a53be68c972cbd94c5b7af94591e0c024d198ccda30aa99e04769",
    "round399/price/COMPLETE.json":"bf6595b97520131dabf71959f0a78c9fd0d471ca5167afe97d71ce8f925fa9dc",
    "round399/price/check.py":"a3b7980163367be1a3033541c2cc4882e375b92ce80906a68f9f4513eeba5448",
    "round399/price/receipt.json":"7a7492dc29fbacd3503ffe85730e7f768911e29533f7a546452fa9ecab66d42e",
    "round399/audit/check.py":"a838c81ca86dfe8b6e3a2519437aafdaa85f16c3f253732f0d98cc3ee597244f",
    "round399/audit/receipt.json":"12417796f9867fb1c1ae373ee8960b14931abebc18a16959e135dd7db3f62bfe",
    "round394/independent/accept.py":"a1e240a31f4c61d036c56b421df91bb36c15c4133f0ebb604773130ddfca7e31",
    "round391/price/check.py":"5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    "round378/independent/accept.py":"001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round396/independent/accept.py":"575e8eb3f85b71eb485c874c3d1006c9c02fef84c4dfa6ae59fae773ffc7e5b5",
    "round375/independent/coupling.py":"fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    f"{BASE}/RESULT.json":"ba4782e227936b7654f70002857c8fc2b0276a1c7d2b11d22f7ca14af9502b1a",
    f"{BASE}/prepare.py":"d53ce9e21cf57e1b2b64fef2c91aae3abefeb9df2e083034223bd38b0a02e0b2",
    f"{BASE}/verify.py":"10362de3ceaa651cde5b71c6599fd4683d9f1f4d76cc252178e915b43a098fee",
}


def need(ok,because):
    if not ok:
        raise ValueError(because)


def sha(raw):
    return sha256(raw).hexdigest()


def pin(path,dig):
    raw=path.read_bytes()
    need(sha(raw)==dig,f"Exact pinned bytes {path.name}")
    return raw


def unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,f"Duplicate pin {k}")
        out[k]=v
    return out


def parse(raw):
    return json.loads(raw,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def exact_rates(root,archive,old,new,price,audit):
    book=runpy.run_path(str(root/"round394/independent/accept.py"))["ordinary"]
    old_rows,old_sup=book(OLD,D,K0+5*G)
    old_gaussian=C-DG/OLD_G
    old_complete=old_gaussian-5*G
    need(old_sup>K+5*G and old_sup>old_gaussian and K0<old_complete<K
         and Q(old["terminal"]["gaussian_rate"])==old_gaussian
         and [str(x) for x in old_rows]==old["terminal"]["ordinary_rates"]
         and old_complete==Q(price["old_installed_cap"])==Q(audit["old_installed_cap"]),
         "Actual old Gaussian-bound installed ceiling from exact same physical baseline")
    exact=runpy.run_path(str(root/"round399/audit/check.py"))["evaluate"]
    gleft,gright=audit["scope"]["whole_family_crossing"]
    a,b=exact(gleft),exact(gright)
    need((gleft,gright)==(490663,490664) and audit["scope"]["total_evaluations"]==18
         and a["h"][0]==b["h"][0]==8192 and a["h"][-1]==b["h"][-1]==524288
         and Q(a["ordinary"])>Q(a["positive"]) and Q(b["ordinary"])<Q(b["positive"])
         and Q(b["actual_cap"])>Q(a["actual_cap"])
         and Q(b["actual_cap"])==Q(price["family_ceiling"])==Q(audit["family_ceiling"])
         and old_complete<K<Q(b["actual_cap"]),
         "Authenticated complete two-sided monotone family bound and strict exact true booking")
    spend=lambda g:(RES-1731-220*g)//320
    at_tie=next(x for x in audit["verified_rows"] if x["g"]==H+1)
    need(sum(HS)==spend(H)==spend(H+1)>spend(H+2)
         and at_tie["h"]==list(HS) and Q(at_tie["actual_cap"])==Q(b["actual_cap"]),
         "Two exact maximizing Gaussian heights; stricter next clock loses at least one integer level")
    need(tuple(b["h"])==HS and K-K0==Q(audit["exact_certified_candidate_delta"])
         and K-old_complete==Q(audit["separation_from_prior_installed_cap"]),
         "Exact strict comparison beyond existing frontier crossing")
    cut,choose,geom,stock,qualify=runpy.run_path(str(root/"round391/price/check.py"))["archived_caller"](archive)
    charged={}
    for kind,hs,h,k in (("entry",(3000,3080),1024,Q(".00345")),("terminal",HS,H,K)):
        spec=new[kind]
        rates,ord_cap=book(hs,D,k+5*G)
        positive=C-DG/h
        actual_state=stock(SimpleNamespace(rank_logs=hs,complex_log=h,eta=ETA))
        e=actual_state["public_exponent_A"]
        actual_geometry=geom["entrance_geometry"](e)
        signed=qualify(k,G,k+5*G,positive)
        need(Q(spec["kappa"])==k and spec["ordinary_H"]==list(hs) and spec["numerical_H"]==h
             and spec["ordinary_rates"]==[str(x) for x in rates] and Q(spec["gaussian_rate"])==positive
             and spec["stock"]==actual_state and spec["geometry"]==actual_geometry and spec["signed"]==signed
             and (signed["strict"],signed["functional"])==(54,4),
             "Both complete true signed profiles including all 54+4 and actual work stock")
        header=(1<<e)+actual_state["first_public_offset"]
        cuts=tuple(cut(hs))
        need(list(cuts)==actual_state["binary_cuts"] and geom["connected_exponent"](cuts[-1],h)==e
             and header%6==0 and header.bit_length()==e+1 and (header-6).bit_length()==e,
             "Both actual first public headers")
        for i,edge in enumerate(cuts,1):
            need([choose(edge+d,len(hs),hs) for d in (-1,0,1)]==[i-1,i,i]
                 and choose(edge+1,i-1,hs)==i-1,
                 "Full native and predecessor-clipped transition at true installed cuts")
        charged[kind]={"ordinary_gap":str(ord_cap-k-5*G),"positive_gap":str(positive-k-5*G),
                       "all_inequalities":[54,4],"actual_cuts":list(cuts)}
    last=new["terminal"]
    s=last["stock"]
    need(new["entry"]==old["entry"] and new["gaussian"]==old["gaussian"]
         and last["ordinary_rates"]==b["earlier_ticks"]+[str(K+5*G)]
         and last["signed"]==price["terminal_signed"]==audit["candidate_price"]["terminal_signed"]
         and s==price["stock"]==audit["candidate_price"]["stock"]
         and s["binary_cuts"]==[8290,133201,657553] and s["public_exponent_A"]==1148465
         and s["first_public_offset"]==4 and s["absolute_log2_private_control_envelope"]==536870915
         and s["storage_upper"]=="6.2 p T < 297.6 n bits",
         "Unchanged entry and weighted positive semantics, exact paid private storage and stage guards")
    premium=up((K-Q(".00345"))*s["public_exponent_A"])
    bin_b=128+320*sum(HS)
    c=max(84500001,1602+220*H+bin_b)
    entire=1+max(c,new["entry"]["log2_C"]+premium)
    need(bin_b==last["log2_B"] and c==last["log2_C"] and min(HS)>=8192
         and premium==new["entry_price_surcharge"]==515
         and entire==new["complete_log2_C"]==CLOCK==old["complete_log2_C"]-260,
         "Exact native and positive ticks, 515-bit prefix and complete recurring clock")
    w=2**38
    z=2*w+2
    setup=(2**68+1)*(8*4*w*2**68*512*128+2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2+2**120)*2**32
    need(max(*HS,H)==new["max_native_H"]==524288 and max(*HS,H).bit_length()==20
         and setup==new["native_setup_transition_upper"]==old["native_setup_transition_upper"]<2**228
         and new["native_setup_grade_actions"]==269057152 <2**32
         and new["fixed_funding_height_floors"]==[up(D/(B-K-5*G)),up(DG/(C-K-5*G))],
         "Native fixed setup tape unchanged and real maximum height in its capped domain")
    return {"actual_adjacent_crossing_receipts":[a,b],"both_complete_signed_tiers":charged,"recurring_log2_C":entire,
            "max_native_height":524288,"native_height_bits":20,"native_setup_log2_upper":228,
            "old_installed_cap":str(old_complete),"old_installed_binding_supplier":"Gaussian",
            "strict_separation":str(K-old_complete),"family_ceiling":b["actual_cap"],
            "old_ordinary_still_funded_margin":str(old_sup-(K+5*G)),
            "maximizing_gaussian_heights":[H,H+1],
            "delta_kappa":str(K-K0),"gain_percent":str(100*(K-K0)/K0)}


def literal_overlays(before,capsule,archive,registered):
    prev,post=(runpy.run_path(str(p/"prepare.py")) for p in (before,capsule))
    a,b=prev["EDITS"],post["EDITS"]
    need(a.keys()==b.keys() and {key for key in a if a[key]!=b[key]}=={
         "runtime.patch","receipt.py","independent_price.py"},
         "No change to physical words, operator, ownership, restoration or physical price formula")
    need(post["RAW_FLOOR_PATCH"]==prev["RAW_FLOOR_PATCH"] and post["RAW_FLOOR_IMAGES"]==prev["RAW_FLOOR_IMAGES"]
         and post["NEW_INSTALLATION"]=="c168b4cc722a140ea99474550406859c5abf888cbe04e080352c429eb0748e7f",
         "Bound actual native binary floor and exact new terminal runtime image")

    def source(edits):
        rendered={}
        for name,changes in edits.items():
            code=archive[FREQ+name].decode()
            for old,new in changes:
                need(code.count(old)==1,f"Single authorized edit {name}")
                code=code.replace(old,new)
            rendered[name]=code
        return rendered

    left,right=(source(x) for x in (a,b))
    need(right["runtime.patch"]==left["runtime.patch"].replace(
         '8192, 124986, 524288), 490463, Q(".00389821380")',
         '8192, 124847, 524288), 490664, Q(".0038982141167032")'),
         "Literal terminal runtime patch exactly matches the one frozen price")
    need(all(x in right["receipt.py"] for x in ("318292451 and premium == 515","517128, 490664",
                "ordinary_floor=18960","ORDINARY_DEBIT = Q(1405, 1024)")),
         "Literal complete new cost and inherited binary proof constants")
    unchanged={}
    for name in ("grades.py","positive_debit.py","typed_raw.py","typed_transport.py","check_placement.py",
                 "check_calendar.py","check_raw.py","check_exterior.py","check_nested.py","check_ownership.py","verify.py"):
        original=archive[FREQ+name].decode()
        old=left.get(name,original)
        cur=right.get(name,original)
        need(old==cur,f"Same authenticated physical source, paid ownership and restoration at {name}")
        unchanged[FREQ+name]=sha(cur.encode())
    need(sha(archive[K7_PATH])==K7,"Pin installed literal K7 bytes")
    unchanged[K7_PATH]=K7
    for name in ("PEER-SOURCE.json","peer8057.tar.gz"):
        need((before/name).read_bytes()==(capsule/name).read_bytes(),f"Identical anchor {name}")
    floor=(before/"check_ordinary_floor.py").read_text()
    expected=floor.replace("(8192,124986,524288)","(8192,124847,524288)").replace("490463","490664")
    need((capsule/"check_ordinary_floor.py").read_text()==expected
         and (capsule/"check_cutoff.py").read_text()==(before/"check_cutoff.py").read_text().replace("490463","490664")
         and (capsule/"verify.py").read_text()==(before/"verify.py").read_text().replace(
             "PASS_CAPPED_ALLOCATION","PASS_OPTIMAL_ALLOCATION"),
         "Genuine unchanged finite fixtures and their revalidated actual constructors")
    timebox=lambda plan:[(c["argv"],c["timeout_seconds"]) for c in plan["commands"]]
    m=timebox(parse((capsule/"VERIFY.json").read_bytes()))
    need(m==timebox(registered) and len(m)==7 and sum(h for _,h in m)<=1200,
         "Every required prior scientific mode and time cap")
    return unchanged


def physical(root,log,older,cost):
    def marker(key):
        name=key+" "
        data=[line[len(name):] for line in log.splitlines() if line.startswith(name)]
        need(len(data)==1,f"One literal passing {key} receipt")
        return parse(data[0])

    floor=marker("PASS_LITERAL_ORDINARY_FLOOR")
    q=older["literal_binary_floor"]
    need(floor["binary_all_size"]==q["binary_all_size"] and floor["binary_integer_fixture"]==q["binary_integer_fixture"]
         and floor["new_binary_openings"]==[
             {"ambient":134,"first_columns":18952,"height":h,"lower":L,"plan_arguments_checked":True}
             for h in (3000,3080,*HS)],"Same exact paid fixture, with all five actual native openings")
    power=runpy.run_path(str(root/"round375/independent/coupling.py"))["power_interval"]
    finite=runpy.run_path(str(root/"round396/independent/accept.py"))["fixture"](floor["binary_integer_fixture"],power)
    need(finite==older["unchanged_finite_paid_ledger"],"Independently priced unchanged 2,907-bin axes and custody fixture")
    delta=Q(1,2**128)
    factor=Q(power(Q(1024*134*L),B)[1],2**112)*Q(47,20)*Q(256,255)*Q(4097,4096)*Q(1028,1024)
    factor*=(1+Q(64,L)+delta)/((1-Q(10,L))*(1-delta)**3)
    need(factor**1024<2**1405 and up(factor*10**15)==older["directed_factor_ceiling_1e15"]
         and Q(75,32)/Q(47,20)==Q(375,376),
         "Only identical proof ingredients reused, finite directed factor and both moments repriced")

    stage=marker("PASS_LITERAL_OPTIMAL_ALLOCATION")
    p=stage["stage_seams"][-1]
    need((p["ranks"],p["cuts"])==(list(HS),[8290,133201,657553])
         and stage["signed_tape"]==older["literal_ordinary_stage"]["signed_tape"]
         and [r["records"] for r in stage["signed_tape"]]==[81,6561]
         and all(x["wrong_signed_return_rejected"] for x in stage["signed_tape"])
         and Q(stage["family_ceiling"])==Q(cost["family_ceiling"])
         and stage["tied_gaussian_heights"]==cost["maximizing_gaussian_heights"]
         and Q(stage["prior_gaussian_negative_gap"])==Q(cost["strict_separation"])
         and Q(stage["prior_ordinary_funded_margin"])==Q(cost["old_ordinary_still_funded_margin"])>0,
         "True new runtime direct/compiled checks, signed finite tape and actual old binding supplier")
    row_widths=(140000,670000,1100000,4400000)
    for i,e in enumerate(p["direct"]+p["compiled"]):
        stage_number=2+i%2
        h=HS[stage_number-1]
        predecessor=p["cuts"][stage_number-2]
        width=max((1<<predecessor)+1,1<<(row_widths[i]//250))
        direct=(1<<row_widths[i])<=width<<(8*h)
        need(e=={"component_log":39*row_widths[i]//10000,"direct":direct,"predecessor_cut":predecessor,
                 "rank_log":h,"scanned_log":row_widths[i],"stage":stage_number},
             "Literal actual direct and compiled stage argument recomputation")
    anchor="PASS_INDEPENDENT_WEIGHTED_AND_QUARTER_PRICES\n"
    need(log.count(anchor)==1,"Exact actual Gaussian source price and phase test")
    observed,_=json.JSONDecoder(object_pairs_hook=unique).raw_decode(log.split(anchor,1)[1])
    rows=[]
    for h in (1024,H):
        n=1<<h
        upper=2*(n//(1724*306))
        edge=2*(3*upper//8)
        width=258*(edge-8)
        q=4*up(Q(n,4*width))
        need(q==1364 and 2*q<5*((q*width-n)//4)
             and upper*112<edge*258<(edge+2)*258<n*112,"True selected exterior block at new paid rank")
        rows.append([h,q,[j*q//5 for j in range(3)],[1,272,1]])
    need([[x["H"],x["period"],x["tickets"],x["first_swap"]] for x in observed]==rows
         and all(x["cell"]==[1,112,1,258] and x["share"]=="1/624" for x in observed),
         "Literal new H490664 and unchanged entry owner/phase returns")
    return {"ordinary_floor_receipt":floor,"ordinary_signed_stage_receipt":stage,"gaussian_rank_placement":observed,
            "finite_paid_ledger":finite}


def check(root,capsule,log,frozen):
    data={name:pin(root/name,sha) for name,sha in PINS.items()}
    archived_prior=parse(data["round399/price/COMPLETE.json"])
    original_pin=archived_prior["sha256_by_path"]
    p={f"round398/{kind}.{ext}":original_pin[f"evidence/{kind}.{ext}"]
       for kind in ("scientific","onboarding","historical") for ext in ("log","exit")}
    done={x:pin(root/x,d) for x,d in p.items()}
    science=done["round398/scientific.log"]
    need(archived_prior["head"]==HEAD==data["round398/exact-head"].decode().strip()
         and f'"commit": "{HEAD}"'.encode() in data["round398/preflight.log"]
         and all(done[f"round398/{kind}.exit"].strip()==b"0" for kind in ("scientific","onboarding","historical"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in science
         and all(f"PASS_CAPPED_ALLOCATION {name}\n".encode() in science
                 for name in ("price","calendar","raw","exterior","nested","product","setup"))
         and b"Ran 760 tests" in done["round398/onboarding.log"] and b"OK (skipped=31)" in done["round398/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in done["round398/historical.log"],
         "Exact #8068 comparator completed all applicable checks")
    previous,preflight,audit=[parse(data[n]) for n in ("round398/independent/verified.json",
                                                      "round399/price/receipt.json","round399/audit/receipt.json")]
    need(previous["frozen_candidate"]==parse(data["round398/independent/INPUTS.json"])
         and previous["frozen_candidate"]["capsule/RESULT.json"]==PINS[f"{BASE}/RESULT.json"]
         and Q(previous["kappa"])==K0 and preflight["comparator_head"]==audit["comparator"]==HEAD
         and Q(preflight["candidate_kappa"])==Q(audit["candidate_kappa"])==K
         and audit["primary_receipt_sha256"]==PINS["round399/price/receipt.json"]
         and audit["completed_manifest_sha256"]==PINS["round399/price/COMPLETE.json"]
         and audit["primary_script_sha256"]==PINS["round399/price/check.py"],
         "Original capped envelope and both exact independent prior-body pins")
    names={"prepare.py","verify.py","RESULT.json","VERIFY.json","SOURCES.json","TASK.json","PEER-SOURCE.json",
           "peer8057.tar.gz","check_cutoff.py","check_ordinary_floor.py","check_stage_seam.py"}
    need(frozen.keys()=={"build.log"}|{f"capsule/{x}" for x in names},
         "Complete final literal candidate path-keyed inputs")
    files={n:pin(capsule/n,frozen[f"capsule/{n}"]) for n in names}
    gate=pin(log,frozen["build.log"]).decode()
    need(all(x in gate for x in ("regenerate exit 0","PASS_WEIGHTED_COMPLETE_PRICE 318292451",
                                 "PASS_DIRECTED_ORDINARY_FLOOR 18960 1405/1024 375/376",
                                 "PASS_LITERAL_UPPER_FENCE 1724 1874 (1024, 490664)","PASS_LITERAL_LOWER_CUTOFF 1874",
                                 "PASS_OPTIMAL_ALLOCATION price","PASS_OPTIMAL_ALLOCATION calendar")),
         "Actual complete paid price and calendar stage gates executed")
    old,new=parse(data[f"{BASE}/RESULT.json"]),parse(files["RESULT.json"])
    need(Q(new["previous_rate"])==K0 and Q(new["rate_delta"])==K-K0
         and old["ordinary_floor"]==new["ordinary_floor"]==L
         and Q(old["ordinary_finite_debit"])==Q(new["ordinary_finite_debit"])==D
         and Q(new["ordinary_child_contraction"])==Q(375,376) and Q(new["gaussian"]["raw_loss"])==DG,
         "Same signed invoice and true improvement comparison")
    restore=runpy.run_path(str(root/"round378/independent/accept.py"))["restore_reference"]
    archive=restore(capsule)
    need(len(archive)==88,"Every inherited archive path")
    plan_path=root/BASE/"VERIFY.json"
    plan_name=f"comparator/{PKG}/VERIFY.json"
    unchanged=literal_overlays(root/BASE,capsule,archive,parse(pin(plan_path,original_pin[plan_name])))
    costs=exact_rates(root,archive,old,new,preflight,audit)
    receipts=physical(root,gate,previous,costs)
    return {"status":"INDEPENDENT_LITERAL_OPTIMAL_ALLOCATION_PASS; FULL_REGISTERED_SCIENCE_SEPARATE",
            "comparator_head":HEAD,"kappa":str(K),"pins_of_replayed_original_sources":unchanged,
            "frozen_candidate":frozen,"pinned_predecessor_and_previous_checks":PINS|p,
            "archived_paths":len(archive),**costs,**receipts}


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for name in ("inputs","capsule","log","frozen","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    signal.alarm(60)
    output=check(a.inputs,a.capsule,a.log,parse(a.frozen.read_bytes()))
    signal.alarm(0)
    a.out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
