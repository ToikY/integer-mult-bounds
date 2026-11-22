"""Verify the single literal fixed-clock rank allocation from finished evidence."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal

HEAD="04228ea5a1292cf8526a20037060f6fc6e15a858"
PKG="research/p104-weighted-ordinary-floor"
OLD="round396/publish/"+PKG
FREQ="research/frequency-weighted-native-multiplier/"
TIER="research/tiered-native-multiplier/"
K0,K=Q(".00389821126"),Q(".00389821380")
B,C=Q(4391986206293,2**50),Q(17145637307,2**42)
D,DG=Q(1405,1024),Q(64944,524288)
G,ETA=Q(1,10**18),Q(".0039")
OLD_H,HS=(8192,129406,523443),(8192,124986,524288)
OLD_G,H=485263,490463
L=18960
K7="9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"

PINS={
    "round396/exact-head":"f9ee2bc08c8f771bcaea4ba08412acd2e71b813ca7526ac362a3b017b56c2bd7",
    "round396/preflight.log":"09b680274cad34f50e1d55916989555e2d0463987dfce537f69c67fd6fb4e8f2",
    "round396/independent/verified.json":"79042dce46983afdcf6891d410cfb72bcbc897229c7d05d22c67cfe7b61459fb",
    "round396/independent/accept.py":"575e8eb3f85b71eb485c874c3d1006c9c02fef84c4dfa6ae59fae773ffc7e5b5",
    "round397/price/COMPLETE.json":"08c7d2499f25797f1a831cfee0028f003591c6cfe6d125b251b8e53e5c316158",
    "round397/price/check.py":"d67ec333301a6638148dfa4f9ff5a77d413066d98b264e383d99f3e77410e347",
    "round397/price/receipt.json":"285ccefc35ff461365557b41a5ceb123da1a0fc9e7991a06bf6294ff1dd31deb",
    "round397/audit/check.py":"a7915788b1704807c887c2c6fd950f56a8440eb17920634183c364ccfa084d4d",
    "round397/audit/receipt.json":"bc055b9a277304d61e6361a0ed0c6fa1a6eab121301a291dc776635d04dbb49a",
    "round394/independent/accept.py":"a1e240a31f4c61d036c56b421df91bb36c15c4133f0ebb604773130ddfca7e31",
    "round391/price/check.py":"5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    "round378/independent/accept.py":"001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round395/price/check.py":"7ebb5841ed9088564f1ec5a866a1c448db32f7436a2ecf973fd951a66ade93c0",
    "round375/independent/coupling.py":"fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    f"{OLD}/RESULT.json":"8754f0ffe158404b2f3df2a9e94ce20b77b2e7e62882794d614b7eea2c6bdb60",
    f"{OLD}/prepare.py":"e4dea11a94e13b7ae5a70544e6dff8fdcc0de98533767cd04c1aadff95766682",
    f"{OLD}/VERIFY.json":"66be970197a0cb5216dfaf5b9336b8f394bbd2b5fe9189ebbd6cb5b5eb16a436",
    f"{OLD}/check_ordinary_floor.py":"6961893d858da143c2d658bec56bb38cb99522b5fc48e3218b50682cc49a3b10",
    f"{OLD}/check_cutoff.py":"f5375158af7c07cc0df21b035a012b262d7529f1af57ec311749832df5c23e3a",
}


def need(ok,why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return sha256(raw).hexdigest()


def pin(path,digest):
    raw=path.read_bytes()
    need(sha(raw)==digest,f"Exact bytes {path.name}")
    return raw


def unique(pairs):
    keys={}
    for k,v in pairs:
        need(k not in keys,f"Repeated path key {k}")
        keys[k]=v
    return keys


def parse(raw):
    return json.loads(raw,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def budgets(ordinary,caller,old,new,price,audit):
    cuts,select,geometry,stock,signed=caller
    need(new["gaussian"]==old["gaussian"] and new["gaussian"]["finite_loss"]==audit["gaussian_loss"]
         and new["entry"]==old["entry"] and new["ordinary_floor"]==old["ordinary_floor"]==L
         and Q(new["ordinary_finite_debit"])==D and Q(new["gaussian"]["raw_loss"])==DG
         and Q(new["gaussian"]["trial"])==C and new["gaussian"]["weights"]==[5,451],
         "All genuine unchanged finite proof premises and exact early tiers")
    old_rates,old_bound=ordinary(OLD_H,D,K0+5*G)
    _,old_ideal=ordinary(OLD_H,D)
    old_pos=C-DG/OLD_G
    previous_ceiling=min(old_bound,old_pos)-5*G
    need([str(x) for x in old_rates]==old["terminal"]["ordinary_rates"] and
         Q(old["terminal"]["gaussian_rate"])==old_pos and Q(old["terminal"]["kappa"])==K0
         and K0<previous_ceiling==Q(price["prior_installed_complete_cap"])<K,
         "Exact prior installed complete known-good and strict crossing separation")
    target=K+5*G
    gaps=(target-old_ideal,target-old_pos)
    need(gaps==(Q(audit["old_binary_ideal_negative_gap"]),Q(audit["old_gaussian_negative_gap"]))
         and min(gaps)>0,"Both earlier supplier heights fail even under ideal ordinary funding")
    actual_caps=[]
    tiers={}
    for name,hs,h,k in (("entry",(3000,3080),1024,Q(".00345")),("terminal",HS,H,K)):
        row=new[name]
        paid=k+5*G
        rates,top=ordinary(hs,D,paid)
        pos=C-DG/h
        r=stock(SimpleNamespace(rank_logs=hs,complex_log=h,eta=ETA))
        a=r["public_exponent_A"]
        e=geometry["entrance_geometry"](a)
        q=signed(k,G,paid,pos)
        check=audit[f"complete_signed_{name}"]
        need(Q(row["kappa"])==k and row["ordinary_H"]==list(hs) and row["numerical_H"]==h
             and row["ordinary_rates"]==check["ordinary_rates"]==[str(x) for x in rates]
             and row["signed"]==q==check["signed"] and (q["strict"],q["functional"])==(54,4)
             and row["stock"]==r==check["stock"] and row["geometry"]==e==check["geometry"]
             and Q(row["gaussian_rate"])==pos and pos-paid==Q(check["gaussian_gap"])>0
             and top-paid==Q(check["ordinary_gap"])>0,
             "Both actual profiles, all signed margins, stock and accurate cofinal geometry")
        public=(1<<a)+r["first_public_offset"]
        need(list(cuts(hs))==r["binary_cuts"] and geometry["connected_exponent"](cuts(hs)[-1],h)==a
             and public%6==0 and public.bit_length()==a+1 and (public-6).bit_length()==a,
             "Connected exact header and previous public control")
        decisions=[]
        for j,c in enumerate(r["binary_cuts"],1):
            vals=[select(c+i,len(hs),hs) for i in (-1,0,1)]
            need(vals==[j-1,j,j] and select(c+1,j-1,hs)==j-1,
                 "All exact neighboring ordinary admissions and clipped child gates")
            decisions.append([c,*vals,j-1])
        tiers[name]={"signed_checks":[54,4],"ordinary_slack":str(top-paid),"positive_slack":str(pos-paid),
                     "cuts":r["binary_cuts"],"native_seams":decisions}
        actual_caps.append(min(top,pos)-5*G)
    terminal=new["terminal"]
    s=terminal["stock"]
    need(actual_caps[-1]==Q(price["candidate_booked_complete_cap"])>K
         and s["binary_cuts"]==[8290,133340,657692] and s["public_exponent_A"]==1148403
         and s["first_public_offset"]==4 and s["absolute_log2_private_control_envelope"]==536870915
         and s["storage_upper"]=="6.2 p T < 297.6 n bits",
         "No extra phase, custody or all-size live storage premise")
    b=128+320*sum(HS)
    c=max(84500001,1602+220*H+b)
    premium=up((K-Q(".00345"))*s["public_exponent_A"])
    total=1+max(c,new["entry"]["log2_C"]+premium)
    need(320*(sum(HS)-sum(OLD_H))+220*(H-OLD_G)==0 and min(HS)>=8192
         and b==terminal["log2_B"]==210389248 and c==terminal["log2_C"]==318292710
         and premium==new["entry_price_surcharge"]==old["entry_price_surcharge"]+1==515
         and total==new["complete_log2_C"]==old["complete_log2_C"]==318292711,
         "Actually charge the extra finite conversion bit inside the same complete fixed clock")
    w=2**38
    z=2*w+2
    setup=(2**68+1)*(8*4*w*2**68*512*128+2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2+2**120)*2**32
    need(max(*HS,H)==new["max_native_H"]==524288 and max(*HS,H).bit_length()==20
         and new["native_setup_transition_upper"]==old["native_setup_transition_upper"]==setup<2**228
         and new["native_setup_grade_actions"]==269057152<2**32
         and new["fixed_funding_height_floors"]==[up(D/(B-target)),up(DG/(C-target))],
         "Fixed native setup and exact height cap are fully charged")
    return {"strict_separation_from_prior_cap":str(K-previous_ceiling),"exact_prior_installed_cap":str(previous_ceiling),
            "old_ideal_ordinary_shortfall":str(gaps[0]),"old_gaussian_shortfall":str(gaps[1]),
            "delta_kappa":str(K-K0),"gain_percent":str(100*(K-K0)/K0),"exact_signed_tiers":tiers,
            "complete_log2_C":total,"finite_entry_surcharge":premium,"native_max_H":524288,"native_setup_log2":228,
            "private_control_bits_log2":s["absolute_log2_private_control_envelope"]}


def overlay(prev,capsule,archive,plan):
    old,new=(runpy.run_path(str(p/"prepare.py")) for p in (prev,capsule))
    a,b=(d["EDITS"] for d in (old,new))
    need(a.keys()==b.keys() and {k for k in a if a[k]!=b[k]}=={
         "runtime.patch","receipt.py","independent_price.py"},
         "Only terminal profile and exact corresponding price/threshold checker lines")
    need(new["RAW_FLOOR_IMAGES"]==old["RAW_FLOOR_IMAGES"] and new["RAW_FLOOR_PATCH"]==old["RAW_FLOOR_PATCH"]
         and new["NEW_INSTALLATION"]=="bb92320f8030e957101bdc62dbb0f5d54485a696e66f5004cb37d9321f0f5ae1",
         "Only installed terminal tuple digest changes, K7 runtime floor is identical")

    def emit(edits):
        rendered={}
        for name,changes in edits.items():
            image=archive[FREQ+name].decode()
            for find,change in changes:
                need(image.count(find)==1,f"Unambiguous edit in {name}")
                image=image.replace(find,change)
            rendered[name]=image
        return rendered

    x,y=(emit(e) for e in (a,b))
    need(y["runtime.patch"]==x["runtime.patch"].replace(
         '8192, 129406, 523443), 485263, Q(".00389821126")',
         '8192, 124986, 524288), 490463, Q(".00389821380")'),
         "Actual calendar and owner raw sources remain identical")
    need("318292711 and premium == 515" in y["receipt.py"]
         and "517067, 490050" in y["receipt.py"] and "ORDINARY_DEBIT = Q(1405, 1024)" in y["receipt.py"],
         "Actual installed invoice explicitly charges both sides and the new entry bit")
    pins={}
    for name in ("grades.py","positive_debit.py","typed_raw.py","typed_transport.py","check_placement.py",
                 "check_calendar.py","check_raw.py","check_exterior.py","check_nested.py","check_ownership.py","verify.py"):
        source=archive[FREQ+name].decode()
        earlier=x.get(name,source)
        later=y.get(name,source)
        need(earlier==later,f"Phase, ownership, source and restoration bytes unchanged at {name}")
        pins[FREQ+name]=sha(later.encode())
    need(sha(archive[TIER+"source/strong-bit-k7.json.gz"])==K7,"Exact original signed K7 word")
    pins[TIER+"source/strong-bit-k7.json.gz"]=K7
    for name in ("PEER-SOURCE.json","peer8057.tar.gz"):
        need((prev/name).read_bytes()==(capsule/name).read_bytes(),f"Same sealed {name}")
    floor=(prev/"check_ordinary_floor.py").read_text()
    expect=floor.replace("(8192,129406,523443)","(8192,124986,524288)").replace("485263","490463")
    need((capsule/"check_ordinary_floor.py").read_text()==expect
         and (capsule/"check_cutoff.py").read_text()==(prev/"check_cutoff.py").read_text().replace("485263","490463")
         and (capsule/"verify.py").read_text()==(prev/"verify.py").read_text().replace(
             "PASS_ORDINARY_FLOOR","PASS_CAPPED_ALLOCATION"),
         "Reused finite clock code unchanged; recorded actual installed calls include the new heights")
    modes=lambda mapping:[(o["argv"],o["timeout_seconds"]) for o in mapping["commands"]]
    active=modes(parse((capsule/"VERIFY.json").read_bytes()))
    need(active==modes(plan) and len(active)==7 and sum(s for _,s in active)<=1200,
         "Every registered scientific command and existing full budget preserved")
    return pins


def physical(log,audit,paid,proof,power,cost):
    def readmark(tag):
        matches=[line[len(tag):] for line in log.splitlines() if line.startswith(tag)]
        need(len(matches)==1,f"One literal passing record {tag.strip()}")
        return parse(matches[0])

    prior=paid["literal_floor"]
    new=readmark("PASS_LITERAL_ORDINARY_FLOOR ")
    need(new["binary_integer_fixture"]==prior["binary_integer_fixture"]==audit["reused_binary_integer_fixture"]
         and new["binary_all_size"]==prior["binary_all_size"]==audit["binary_all_size"],
         "Reusing exact finite fixture only at the identical physical floor and input pins")
    need(new["new_binary_openings"]==audit["new_binary_openings"]==[
         {"ambient":134,"first_columns":18952,"height":h,"lower":L,"plan_arguments_checked":True}
         for h in (3000,3080,*HS)], "Actual K7 constructor at all five intended binary ranks")
    ledger=proof["fixture"](new["binary_integer_fixture"],power)
    need(ledger==paid["detached_fixture_ledger"],"Independent repeated aggregate exact same finite paid axes")
    # The exact directed factor is independently recomputed at the unchanged actual floor.
    delta=Q(1,2**128)
    scale=2**112
    bound=Q(power(Q(1024*134*L),B)[1],scale)
    bound*=Q(47,20)*Q(256,255)*Q(4097,4096)*Q(1028,1024)*(1+Q(64,L)+delta)
    bound/= (1-Q(10,L))*(1-delta)**3
    need(bound**1024<2**1405 and up(bound*10**15)==paid["new_factor_upper_1e15"]
         and up(bound*10**12)==audit["charged_factor_upper_1e12"] and paid["physical_t_min_h_checked"]==1024
         and Q(75,32)/Q(47,20)==Q(375,376) and 1/(1-Q(375,376))==376,
         "Identical rechecked fully charged all-size factor and both signed moments")

    seam=readmark("PASS_LITERAL_CAPPED_ALLOCATION ")
    need(seam["stage_seams"][1]=={
          "ranks":list(HS),"cuts":[8290,133340,657692],
          "direct":audit["ordinary_direct_seams"],"compiled":audit["ordinary_compiled_seams"]}
         and seam["signed_tape"]==audit["literal_signed_tape"]==paid["literal_ordinary"]["signed_tape"]
         and [o["records"] for o in seam["signed_tape"]]==[81,6561]
         and [o["paid_exchanges"] for o in seam["signed_tape"]]==[3,1]
         and all(o["wrong_signed_return_rejected"] for o in seam["signed_tape"])
         and Q(seam["prior_binary_negative_gap"])==Q(cost["old_ideal_ordinary_shortfall"])
         and Q(seam["prior_gaussian_negative_gap"])==Q(cost["old_gaussian_shortfall"]),
         "Literal mixed-height dispatch, unchanged real signed bits and both old-cap controls")
    anchor="PASS_INDEPENDENT_WEIGHTED_AND_QUARTER_PRICES\n"
    need(log.count(anchor)==1,"One literal complete positive and historical factor test")
    observed,_=json.JSONDecoder(object_pairs_hook=unique).raw_decode(log.split(anchor,1)[1])
    frames=[]
    scale=1724*306
    slope=Q(3*258,2*scale)
    need(1360*slope<1 and (1364*slope-1)*(1<<1024)>1364*Q(23*258,2),
         "Recheck all-height true first source period")
    for h in (1024,H):
        n=1<<h
        u=2*(n//scale)
        e=2*(3*u//8)
        width=258*(e-8)
        q=4*up(Q(n,4*width))
        need(q==1364 and 2*q<5*((q*width-n)//4) and u*112<e*258<(e+2)*258<n*112,
             "Actual weighted owner and period both legal at new native height")
        frames.append([h,q,[j*q//5 for j in range(3)],[1,272,1]])
    need([[x["H"],x["period"],x["tickets"],x["first_swap"]] for x in observed]==frames
         and [[x["height"],x["period"],x["tickets"],x["first_swap"]] for x in audit["gaussian_placement"]]==frames
         and all(x["cell"]==[1,112,1,258] and x["share"]=="1/624" for x in observed),
         "Actual new Gaussian owner makes the same signed exchange on exact new rank")
    return {"literal_binary_floor":new,"literal_ordinary_stage":seam,"literal_gaussian_placement":observed,
            "unchanged_finite_paid_ledger":ledger,"directed_factor_ceiling_1e15":up(bound*10**15)}


def check(root,capsule,log,freeze):
    data={p:pin(root/p,h) for p,h in PINS.items()}
    done=parse(data["round397/price/COMPLETE.json"])
    need(done.keys()=={f"round396/{s}.{t}" for s in ("scientific","onboarding","historical") for t in ("log","exit")},
         "Exact complete historical/action and repository gates in prior closure")
    receipts={name:pin(root/name,dig) for name,dig in done.items()}
    science=receipts["round396/scientific.log"]
    need(data["round396/exact-head"].strip()==HEAD.encode()
         and f'"commit": "{HEAD}"'.encode() in data["round396/preflight.log"]
         and all(receipts[f"round396/{stage}.exit"].strip()==b"0" for stage in ("scientific","onboarding","historical"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in science
         and all(f"PASS_ORDINARY_FLOOR {mode}\n".encode() in science
                 for mode in ("price","calendar","raw","exterior","nested","product","setup"))
         and b"OK (skipped=31)" in receipts["round396/onboarding.log"]
         and b"Ran 760 tests" in receipts["round396/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in receipts["round396/historical.log"],
         "Current strongest exact predecessor complete replay and full repository scope")
    paid,price,audit=(parse(data[p]) for p in ("round396/independent/verified.json",
                                               "round397/price/receipt.json","round397/audit/receipt.json"))
    need(Q(paid["kappa"])==K0 and Q(price["target"])==Q(audit["candidate"])==K
         and paid["literal_pins"]["capsule/RESULT.json"]==PINS[f"{OLD}/RESULT.json"]
         and audit["baseline_head"]==price["comparator_head"]==HEAD
         and audit["baseline_science_log"]==done["round396/scientific.log"],
         "Both exact preflight receipts and full previous acceptance")
    paths={"prepare.py","verify.py","RESULT.json","SOURCES.json","TASK.json","VERIFY.json","PEER-SOURCE.json",
           "peer8057.tar.gz","check_cutoff.py","check_ordinary_floor.py","check_stage_seam.py"}
    need(freeze.keys()=={"build.log"}|{f"capsule/{p}" for p in paths},
         "All required path-keyed literal replay inputs, no ambiguous keys")
    literal={n:pin(capsule/n,freeze[f"capsule/{n}"]) for n in paths}
    gate=pin(log,freeze["build.log"]).decode()
    need(all(s in gate for s in ("regenerate exit 0","PASS_WEIGHTED_COMPLETE_PRICE 318292711",
                                "PASS_DIRECTED_ORDINARY_FLOOR 18960 1405/1024 375/376",
                                "PASS_LITERAL_UPPER_FENCE 1724 1874 (1024, 490463)",
                                "PASS_CAPPED_ALLOCATION price","PASS_CAPPED_ALLOCATION calendar")),
         "Literal price and actual rank-switch calendar modes and exit")
    previous,new=parse(data[f"{OLD}/RESULT.json"]),parse(literal["RESULT.json"])
    need(Q(new["previous_rate"])==K0 and Q(new["rate_delta"])==K-K0
         and Q(new["ordinary_child_contraction"])==Q(375,376),"Exact comparator and scope of current literal change")
    restore=runpy.run_path(str(root/"round378/independent/accept.py"))["restore_reference"]
    archive=restore(capsule)
    need(len(archive)==88,"Authentic original archive inventory")
    sources=overlay(root/OLD,capsule,archive,parse(data[f"{OLD}/VERIFY.json"]))
    caller=runpy.run_path(str(root/"round391/price/check.py"))["archived_caller"](archive)
    ordinary=runpy.run_path(str(root/"round394/independent/accept.py"))["ordinary"]
    rate=budgets(ordinary,caller,previous,new,price,audit)
    proof=runpy.run_path(str(root/"round396/independent/accept.py"))
    power=runpy.run_path(str(root/"round375/independent/coupling.py"))["power_interval"]
    bounded=physical(gate,audit,paid,proof,power,rate)
    return {"status":"INDEPENDENT_LITERAL_CAPPED_ALLOCATION_PASS; COMPLETE_REGISTERED_SCIENCE_SEPARATE",
            "kappa":str(K),"comparator_head":HEAD,"pinned_prior_evidence":PINS|done,"frozen_candidate":freeze,
            "authenticated_original_entries":len(archive),"unchanged_native_hashes":sources,**rate,**bounded}


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for name in ("inputs","capsule","log","frozen","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    signal.alarm(60)
    result=check(a.inputs,a.capsule,a.log,parse(a.frozen.read_bytes()))
    signal.alarm(0)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
