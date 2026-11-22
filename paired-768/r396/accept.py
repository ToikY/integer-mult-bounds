"""Detached exact verification of one literal lower ordinary opening floor."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha1,sha256
from pathlib import Path
from types import SimpleNamespace
import json
import runpy
import signal

HEAD="19e67d1b36210e3047bbf3d04625d1262cba672a"
PKG="research/p104-weighted-ordinary-debit"
PREV="round394/publish/"+PKG
FREQ="research/frequency-weighted-native-multiplier/"
TIER="research/tiered-native-multiplier/"
K0,K=Q(".00389821103"),Q(".00389821126")
B,C=Q(4391986206293,2**50),Q(17145637307,2**42)
D0,D,DG=Q(703,512),Q(1405,1024),Q(64944,524288)
OLD,HEIGHTS=(8192,129406,523763),(8192,129406,523443)
H0,H=484799,485263
L0,L,A=32768,18960,134
G,ETA=Q(1,10**18),Q(".0039")
T,GRID=Q(1,2**128),2**112
K7="9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"

PINS={
    "round394/exact-head":"135d839ea3e9035b0292f967dd5fb6f68dd262306e19dc596886d6f4562332e4",
    "round394/preflight.log":"60ebbfb864fef6ca908655b89f881ff79ed6f02148780ed6b16e4cd0a3eca381",
    "round394/independent/verified.json":"1eef4f1fb8c85e2ae81cf9cd4bede2a9e83f7c2e7e0a3508534100ce6e3e6ba7",
    "round394/independent/accept.py":"a1e240a31f4c61d036c56b421df91bb36c15c4133f0ebb604773130ddfca7e31",
    "round395/price/COMPLETE.json":"58aa0edbeab98b8ddf7ff61ef0c90185b518145f580e92d93ce5d7790b7779ea",
    "round395/price/check.py":"7ebb5841ed9088564f1ec5a866a1c448db32f7436a2ecf973fd951a66ade93c0",
    "round395/price/receipt.json":"6f569271cd681883949b23d5286c855f688f574e08c1a1e7224ef0f032e3299d",
    "round395/audit/check.py":"cbcedbd4cc1ece6d5659b7dc0a5af84904fd525437443f99990742289b43b51e",
    "round395/audit/receipt.json":"f6a37af5397fdc3d2c508546493d62d0242ebcf56470356722e2dcc74cf6650b",
    "round378/independent/accept.py":"001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round375/independent/coupling.py":"fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    "round391/price/check.py":"5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    f"{PREV}/RESULT.json":"44b2d59a1b7e6d7f3336567dbdd4fe27b6ee3b64edd97172698aafdc91db9383",
    f"{PREV}/prepare.py":"48fca2618df3f3483c1640c8c77ded20cc3aeb37232c69e10466c9a5b323d098",
    f"{PREV}/VERIFY.json":"f3413a19f8215ce676bb59e5689b96c2a06188ab315d6bfb1d8735b38d32f6f2",
}
PROOF={"TRANSFER.md":("c8a5afa257aeddb47825e843b1c9063f9b9a05e3","7164831a5dd9f5c6231bf4c3f4b2061d91cbfab559071a0a5d68966e3f7ac55c"),
       "RECEIVER.md":("90ed818f7273a9cd275ade1774f87ffa94f42a5c","f31089b6304fc5352feb9aa8a963cc5a950a828165d3426e16e8a973529d814e"),
       "ORDINARY-CLOCK.md":("7155d52a9006c044e8df87f9cf320f3cef61d58c","4694db0b2218796e348c1128271cebb3fc779151a639b0e0fb5bbecf9f3ccb94")}


def need(p,why):
    if not p:
        raise ValueError(why)


def sha(raw):
    return sha256(raw).hexdigest()


def pin(path,digest):
    raw=path.read_bytes()
    need(sha(raw)==digest,f"Exact authentication {path.name}")
    return raw


def unique(pairs):
    obj={}
    for key,value in pairs:
        need(key not in obj,f"Duplicate manifest key {key}")
        obj[key]=value
    return obj


def parse(raw):
    return json.loads(raw,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def factor(sources,power,primary,physical):
    original={}
    for name,(blob,digest) in PROOF.items():
        raw=pin(sources/name,digest)
        need(sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==blob,
             f"Git proof blob {name}")
        original[name]=raw.decode()
    transfer=original["TRANSFER.md"]
    need("(256/255)(4097/4096)(1028/1024)(1024 A L)^c" in transfer
         and "(1+64/L+δ) / [(1−10/L)(1−δ)^3]" in transfer
         and "8k-10r" in transfer
         and "75/32" in original["RECEIVER.md"]
         and "s=t and s=1" in original["ORDINARY-CLOCK.md"],
         "Authenticated all-size transfer and two physical child moments")

    def interval(floor):
        integer=power(Q(1024*A*floor),B)
        common=(Q(256,255)*Q(4097,4096)*Q(1028,1024)*Q(47,20)
                *(1+Q(64,floor)+T)/((1-Q(10,floor))*(1-T)**3))
        return [Q(y,GRID)*common for y in integer]

    lo,hi=interval(L)
    prior_lo,prior_hi=interval(L0)
    debit_lo,debit_hi=(Q(y,GRID) for y in power(Q(2),D))
    need(hi**1024<2**1405<prior_lo**1024 and hi<debit_lo<debit_hi<prior_lo
         and prior_hi**512<2**703, "Directed new floor, old-fence rejection and good prior price control")
    need(int(lo*10**12)==physical["charged_factor_lower_1e12"]
         and up(hi*10**12)==physical["charged_factor_upper_1e12"]
         and up(hi*10**15)==primary["new_floor_factor_upper_1e15"],
         "All independent charged factor enclosures")
    t=1-B
    n=1<<1024
    u=2*(n//(2048*A))
    floor_weight=Q(power(Q(L),t)[0],GRID)
    need(floor_weight>2**14 and L%2==0 and L>48 and (L-8)%4==0 and (L-6)%4==2
         and 24*(L+2)<25*L and u>2064*L and u*1032<n//4,
         "Both native phase residues, cut and opposite fringe bands, and unchanged downward deadlines")
    need(Q(1)/(t*floor_weight)+Q(2,n**5)<2 and 104652<2**19
         and Q(2**19,(1024*A*L)**77)+Q(1,n**77)<1 and Q(6,5)**77>2**20
         and Q(6,5)**4>2 and (1-T)*n<=1024*A*u and T*n>=2048*A,
         "Uniform birth, lifetime, historical stock and integer period estimates")
    need(Q(1)-Q(10,L)>Q(".99")
         and (1-Q(10,L))*(1-T)*Q("1.9")>1
         and (1-Q(1,n))/Q(1028,1024)>Q(1,2)
         and 2*4096*18906<n and T*n>=1
         and 2**46*n**2<Q(n**6,2**132)
         and 2**20*Q(n**6,n**4)<Q(n**6,2**132)
         and B.denominator==2**50 and 401-27*1024-64<-2,
         "All-size integer error, exterior cycles, group padding and serial stock")
    need(physical["binary_all_size"]["fringe_upper_1e9"]<64*10**9
         and physical["binary_all_size"]["whole_field_width"]=="N^92"
         and physical["binary_all_size"]["birth_bound"]=="2V"
         and physical["binary_all_size"]["copy_group_bound"]=="3N^3"
         and Q(75,32)/Q(47,20)==Q(375,376) and 1/(1-Q(375,376))==376,
         "Full retained suffix, paid group and both moment bounds")
    return {"proof_commit":"dfd25d553a843a946ca0b94130a5ff8943e98fdd","original_proof_sha256":PROOF,
            "new_factor_upper_1e15":up(hi*10**15),"new_factor_margin_floor_1e15":int((debit_lo-hi)*10**15),
            "old_fence_failure_floor_1e15":int((prior_lo-debit_hi)*10**15),
            "physical_t_min_h_checked":1024,"both_paid_moments":"375/376","all_depth_multiplier":376}


def ordinary_and_gaussian(old,new,price,physical,caller,ordinary):
    limits,select,geom,stock,signed=caller
    need(old["gaussian"]==new["gaussian"] and new["gaussian"]["finite_loss"]==physical["gaussian_loss"],
         "No changed Gaussian cost or actual Cartesian word")
    previous_rates,prior_cap=ordinary(OLD,D0,K0+5*G)
    old_cross=min(prior_cap,C-DG/H0)-5*G
    _,old_at_new=ordinary(HEIGHTS,D0)
    need(old["terminal"]["ordinary_rates"]==[str(x) for x in previous_rates]
         and Q(old["terminal"]["kappa"])==K0 and old["terminal"]["numerical_H"]==H0
         and old_cross==Q(price["old_installed_cap"])<K and K-old_cross==Q(price["clears_exact_prior_cap"])
         and K+5*G-old_at_new==Q(physical["old_debit_ideal_negative_gap"])>0,
         "Known-good prior installed cap and exact negative with ideal prior ordinary debit")
    check={}
    for name,k,h,ranks in (("entry",Q(".00345"),1024,(3000,3080)),("terminal",K,H,HEIGHTS)):
        row=new[name]
        booked=k+5*G
        pos=C-DG/h
        rates,cap=ordinary(ranks,D,booked)
        r=stock(SimpleNamespace(rank_logs=ranks,complex_log=h,eta=ETA))
        g=geom["entrance_geometry"](r["public_exponent_A"])
        a=r["public_exponent_A"]
        z=signed(k,G,booked,pos)
        expected=physical[f"complete_signed_{name}"]
        need(Q(row["kappa"])==k and row["ordinary_H"]==list(ranks) and row["numerical_H"]==h
             and row["ordinary_rates"]==expected["ordinary_rates"]==[str(x) for x in rates]
             and list(limits(ranks))==r["binary_cuts"]
             and row["stock"]==r==expected["stock"] and row["geometry"]==g==expected["geometry"]
             and row["signed"]==z==expected["signed"] and (z["strict"],z["functional"])==(54,4)
             and Q(row["gaussian_rate"])==pos and pos-booked==Q(expected["gaussian_gap"])
             and cap>booked and cap-booked==Q(expected["ordinary_gap"])
             and geom["connected_exponent"](r["binary_cuts"][-1],h)==a,
             "Exact active tiers, true public geometry and complete signed quotas")
        header=(1<<a)+r["first_public_offset"]
        need(header%6==0 and (header-6).bit_length()==a and header.bit_length()==a+1,
             "True cofinal header and finite earlier tier")
        for s,c in enumerate(r["binary_cuts"],1):
            need([select(c+j,len(ranks),ranks) for j in (-1,0,1)]==[s-1,s,s]
                 and select(c+1,s-1,ranks)==s-1,
                 "Full before, at and after cuts plus retained nested cutoff")
        check[name]={"ordinary_slack":str(cap-booked),"gaussian_slack":str(pos-booked),"tests":[54,4]}
    before,late=new["entry"],new["terminal"]
    b=128+320*sum(HEIGHTS)
    clock=1602+220*H+b
    premium=up((K-Q(".00345"))*late["stock"]["public_exponent_A"])
    recurring=1+max(clock,before["log2_C"]+premium)
    need(b==late["log2_B"]==211533248 and clock==late["log2_C"]
         and recurring==new["complete_log2_C"]==318292711==old["complete_log2_C"]-320
         and premium==new["entry_price_surcharge"]==514
         and late["stock"]["public_exponent_A"]==1146778
         and late["stock"]["binary_cuts"]==[8290,137760,661267]
         and late["stock"]["absolute_log2_private_control_envelope"]==536005635
         and late["stock"]["storage_upper"]=="6.2 p T < 297.6 n bits",
         "Finite prefix, all-size tape and fully charged lower recurring clock")
    w=2**38
    z=2*w+2
    setup=(2**68+1)*(8*4*w*2**68*512*128+2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2+2**120)*2**32
    need(max(H,*HEIGHTS).bit_length()==19 and new["max_native_H"]==523443
         and setup==new["native_setup_transition_upper"]==old["native_setup_transition_upper"]<2**228
         and new["native_setup_grade_actions"]==269057152<2**32,
         "Separate native precomputation, immutable index widths and setup costs")
    floors=[up(D/(B-K-5*G)),up(DG/(C-K-5*G))]
    need(floors==new["fixed_funding_height_floors"]==[516572,485174],
         "Same exact resource proof for both fundable height floors")
    return {"signed_tiers":check,"delta_kappa":str(K-K0),"gain_percent":str(100*(K-K0)/K0),
            "previous_installed_ceiling":str(old_cross),"strict_old_cap_separation":str(K-old_cross),
            "old_debit_ideal_failure":str(K+5*G-old_at_new),"complete_log2_C":recurring,
            "native_height_bits":19,"fixed_setup_log2_ceiling":228}


def fixture(record,power):
    """Recompute every finite fixture birth and paid subtotal via exact quadrature."""
    from functools import cache

    r,k=49,64
    hi=2*up(Q((L+4)*k,2*r))+4
    n=1<<(4*k*hi-1).bit_length()
    volume=8*hi**2
    ticks=5
    t=1-B

    @cache
    def inv(x):
        lo,hi=power(Q(x),t)
        return Q(GRID,hi),Q(GRID,lo)

    def mass(a,b,decide):
        lo,hi=inv(a)
        l2,h2=inv(b)
        low=decide(volume*(lo-h2)/t)
        high=decide(volume*(hi-l2)/t)
        need(low==high,"Both outward directions decide one exact paid count")
        return low

    births={e:mass(e,e+2,up) for e in range(L,hi,2)}
    raw_axes=ticks*sum(2*r*(e-8)*q for e,q in births.items())
    actual_grants={}
    per_width={}
    reduction=0
    loans=0
    for d in range(L,hi,2):
        e1=Q(d*k,r)
        e2=Q((d+2)*k,r)
        funded=[]
        for e in range(2*(e1//2),min(hi,2*up(e2/2)),2):
            lo,upper=max(e,e1),min(e+2,e2)
            if lo>=upper:
                continue
            share=mass(lo,upper,lambda x:(x/2).__floor__())
            if share:
                need(0<=r*(e-8)-k*(d-8)<10*k,"Exact paid suffix and full parent operand")
                # All actual parent widths on this fixture fit the first raised clock level.
                need(Q(6,5)*L<=e<Q(6,5)**2*L and d<Q(6,5)*L and 2<4,
                     "Both literal source return deadlines")
                funded.append((e,share))
        if funded:
            grant=2*(ticks+max(0,ticks-4))*sum(v for _,v in funded)
            per_width[d-8]=grant
            loans+=grant
            reduction+=grant*k*(d-8)
            actual_grants[d]=funded
    first=[]
    for d in (L,L+2):
        grants=[[i,j,e,c] for i in range(2) for e,c in actual_grants[d] for j in range(2)]
        first.append([d,births[d],grants])
    opens=ticks*sum(births.values())
    need(record["tested_occupied_K7_grade"]==[r,k] and record["carrier"]==n
         and record["lower"]==L and record["upper"]==hi and record["first_band_contacts"]==first
         and record["native_opens"]==record["native_closes"]==opens==323165
         and record["returned_paid_prefixes"]==loans==432
         and record["paid_singletons"]==raw_axes-reduction==683705746532
         and record["lower_return_counts"]=={str(e-8):per_width[e-8] for e in (L,L+2)},
         "Independent aggregate of the complete literal fixture births, grants, returns and exact billed axes")
    return {"independently_counted_bin_total":len(births),"paid_raw_singleton_axes":raw_axes,
            "paid_prefix_axis_offsets":reduction}


def overlay(prev,candidate,arch,pricer,old_plan):
    p,q=(runpy.run_path(str(place/"prepare.py")) for place in (prev,candidate))
    a,b=(sub["EDITS"] for sub in (p,q))
    need(a.keys()==b.keys() and {k for k in a if a[k]!=b[k]}=={
         "runtime.patch","receipt.py","independent_price.py","verify.py"},
         "Scoped literal source replacement only")
    sources=pricer["original_binary"](arch)
    need(q["RAW_FLOOR_IMAGES"]=={
         "before":sources["retimed-source.tar.gz::raw_binary_stage.py"],
         "after":"e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0"},
         "Immutable raw K7 recipe before and after edit")
    patch=q["RAW_FLOOR_PATCH"].splitlines()
    before="    return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C)"
    after=before[:-1]+", level_floor=18960)"
    need(patch[:3]==["--- a/raw_binary_stage.py","+++ b/raw_binary_stage.py","@@ -45,7 +45,7 @@"]
         and [x for x in patch[3:] if x.startswith(("-","+"))]==["-"+before,"+"+after],
         "Only actual K7 constructor adds 18960, generic reserve and transport preserved")
    from io import BytesIO
    import tarfile
    with tarfile.open(fileobj=BytesIO(arch[TIER+"source/installer.tar.gz"])) as installer:
        retimed=installer.extractfile("retimed-source.tar.gz").read()
    with tarfile.open(fileobj=BytesIO(retimed)) as original:
        raw=original.extractfile("raw_binary_stage.py").read()
    need(raw.count(before.encode())==1 and sha(raw)==q["RAW_FLOOR_IMAGES"]["before"]
         and sha(raw.replace(before.encode(),after.encode()))==q["RAW_FLOOR_IMAGES"]["after"],
         "Independently materialize and hash the exact native binary recipe")
    need(q["NEW_INSTALLATION"]=="83685b2077f32bf6eb4d014534489cafd051d03d8989282780e2dc2b6bbf1ac4",
         "New literal terminal installation digest")

    def emit(changes):
        out={}
        for name,modify in changes.items():
            text=arch[FREQ+name].decode()
            for old,new in modify:
                need(text.count(old)==1,f"Unique installed replacement at {name}")
                text=text.replace(old,new)
            out[name]=text
        return out

    left,right=(emit(x) for x in (a,b))
    want=left["runtime.patch"].replace('8192, 129406, 523763), 484799, Q(".00389821103")',
                                      '8192, 129406, 523443), 485263, Q(".00389821126")')
    need(right["runtime.patch"]==want or right["runtime.patch"]==want+q["RAW_FLOOR_PATCH"],
         "Only scalar terminal profile and bind exact paid floor at native entry")
    need("ORDINARY_DEBIT = Q(1405, 1024)" in right["receipt.py"]
         and "ordinary_floor=18960" in right["receipt.py"] and "516572, 485174" in right["receipt.py"],
         "Actual charged profile and same machine record expose the new debit")
    unchanged=("grades.py","positive_debit.py","typed_raw.py","typed_transport.py","check_placement.py",
               "check_calendar.py","check_raw.py","check_exterior.py","check_nested.py","check_ownership.py")
    pins={}
    for name in unchanged:
        original=arch[FREQ+name].decode()
        old_text=left.get(name,original)
        new_text=right.get(name,original)
        need(old_text==new_text,f"Identical phase, raw and positive source bytes at {name}")
        pins[FREQ+name]=sha(new_text.encode())
    need(sha(arch[TIER+"source/strong-bit-k7.json.gz"])==K7,
         "Exact same K7 word and paid/restored directions")
    pins[TIER+"source/strong-bit-k7.json.gz"]=K7
    before_plan=[(c["argv"],c["timeout_seconds"]) for c in old_plan["commands"]]
    plan=parse((candidate/"VERIFY.json").read_bytes())
    cmds=[(c["argv"],c["timeout_seconds"]) for c in plan["commands"]]
    need([cmd for cmd,_ in cmds]==[cmd for cmd,_ in before_plan] and len(cmds)==7
         and sum(sec for _,sec in cmds)<=1200,"Full registered mode coverage under repository cap")
    need('"check_ordinary_floor.py"' in right["verify.py"] and '"check_ordinary_floor.py"' in (candidate/"verify.py").read_text()
         and (candidate/"check_cutoff.py").read_text()==(prev/"check_cutoff.py").read_text().replace("484799","485263"),
         "New physical floor fixtures run in the registered calendar without deleting prior tests")
    return pins


def evidence_rows(log,audit):
    def marker(name):
        tag=name+" "
        matched=[line[len(tag):] for line in log.splitlines() if line.startswith(tag)]
        need(len(matched)==1,f"One literal receipt {name}")
        return parse(matched[0])

    floor=marker("PASS_LITERAL_ORDINARY_FLOOR")
    need(all(floor[name]==audit[name] for name in ("binary_all_size","binary_integer_fixture","new_binary_openings")),
         "Literal ordinary floor native constructors and all occupied fixture evidence agree")
    need(floor["new_binary_openings"]==[
         {"height":h,"lower":L,"ambient":A,"first_columns":L-8,"plan_arguments_checked":True}
         for h in (3000,3080,*HEIGHTS)],"Actual five native constructors all bind the one new floor")
    ordinary=marker("PASS_LITERAL_ORDINARY_DEBIT")
    need(ordinary["stage_seams"][1]=={"ranks":list(HEIGHTS),"cuts":[8290,137760,661267],
         "direct":audit["ordinary_direct_seams"],"compiled":audit["ordinary_compiled_seams"]}
         and ordinary["signed_tape"]==audit["literal_signed_tape"]
         and Q(ordinary["old_debit_negative_gap"])==Q(audit["old_debit_ideal_negative_gap"])
         and [x["records"] for x in ordinary["signed_tape"]]==[81,6561]
         and all(x["wrong_signed_return_rejected"] for x in ordinary["signed_tape"]),
         "Actual changed ordinary seams, both signed bank tapes and old debit control")
    anchor="PASS_INDEPENDENT_WEIGHTED_AND_QUARTER_PRICES\n"
    need(log.count(anchor)==1,"One literal unchanged positive price and new placement test")
    actual,_=json.JSONDecoder(object_pairs_hook=unique).raw_decode(log.split(anchor)[1])
    scale=1724*306
    y=Q(3*258,2*scale)
    need(1360*y<1 and (1364*y-1)*(1<<1024)>1364*Q(23*258,2),
         "All-height exact Gaussian period 1364 still holds")
    verify=[]
    for h in (1024,H):
        m=1<<h
        u=2*(m//scale)
        e=2*(3*u//8)
        width=258*(e-8)
        period=4*up(Q(m,4*width))
        need(period==1364 and 2*period<5*((period*width-m)//4),"Same first Gaussian ticket branches")
        verify.append([h,period,[j*period//5 for j in range(3)],[1,272,1]])
    need([[p["H"],p["period"],p["tickets"],p["first_swap"]] for p in actual]==verify
         and [[p["height"],p["period"],p["tickets"],p["first_swap"]] for p in audit["gaussian_placement"]]==verify,
         "Exact physical exterior first move at new H485263")
    return floor,ordinary,actual


def check(root,capsule,sources,log,pinned):
    data={n:pin(root/n,d) for n,d in PINS.items()}
    prior=parse(data["round395/price/COMPLETE.json"])
    need(prior.keys()=={f"round394/{key}.{ext}" for key in ("scientific","onboarding","historical")
                          for ext in ("log","exit")},"Exact prior repository and science receipts")
    logs={n:pin(root/n,d) for n,d in prior.items()}
    need(data["round394/exact-head"].strip()==HEAD.encode()
         and f'"commit": "{HEAD}"'.encode() in data["round394/preflight.log"]
         and all(logs[f"round394/{k}.exit"].strip()==b"0" for k in ("scientific","onboarding","historical"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in logs["round394/scientific.log"]
         and b"OK (skipped=31)" in logs["round394/onboarding.log"] and b"Ran 760 tests" in logs["round394/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in logs["round394/historical.log"],
         "All complete exact comparison gates including corrected repository run")
    refs,first,audit=(parse(data[n]) for n in ("round394/independent/verified.json","round395/price/receipt.json",
                                               "round395/audit/receipt.json"))
    need(refs["frozen_candidate"]["capsule/RESULT.json"]==PINS[f"{PREV}/RESULT.json"]
         and Q(refs["kappa"])==K0 and first["comparator"]==audit["baseline_head"]==HEAD
         and Q(first["candidate_kappa"])==Q(audit["candidate"])==K
         and audit["binary_lower_floor"]==L and Q(audit["debit"])==D,
         "All matched directed and physical prerequisites")
    names={"prepare.py","RESULT.json","verify.py","VERIFY.json","TASK.json","SOURCES.json","PEER-SOURCE.json",
           "peer8057.tar.gz","check_cutoff.py","check_ordinary_floor.py","check_stage_seam.py"}
    need(pinned.keys()=={f"capsule/{n}" for n in names}|{"build.log"},
         "Frozen candidate map covers every unique replay input")
    c={n:pin(capsule/n,pinned[f"capsule/{n}"]) for n in names}
    literal=pin(log,pinned["build.log"]).decode()
    need(all(s in literal for s in ("regenerate exit 0","PASS_WEIGHTED_COMPLETE_PRICE 318292711",
                                   "PASS_DIRECTED_ORDINARY_FLOOR 18960 1405/1024 375/376",
                                   "PASS_LITERAL_UPPER_FENCE 1724 1874 (1024, 485263)",
                                   "PASS_ORDINARY_FLOOR calendar","PASS_ORDINARY_FLOOR price")),
         "Actual new ordinary and positive constructor ages and passing exact price receipts")
    old,new=parse(data[f"{PREV}/RESULT.json"]),parse(c["RESULT.json"])
    need(Q(new["previous_rate"])==K0 and Q(new["rate_delta"])==K-K0
         and new["ordinary_floor"]==L and Q(new["ordinary_finite_debit"])==D
         and Q(new["ordinary_child_contraction"])==Q("375/376"),
         "Literal result states exact priced improvement and its actual floor")
    archive=runpy.run_path(str(root/"round378/independent/accept.py"))["restore_reference"](capsule)
    need(len(archive)==88,"Every exact original archive path")
    pricer=runpy.run_path(str(root/"round395/price/check.py"))
    unchanged=overlay(root/PREV,capsule,archive,pricer,parse(data[f"{PREV}/VERIFY.json"]))
    caller=runpy.run_path(str(root/"round391/price/check.py"))["archived_caller"](archive)
    power=runpy.run_path(str(root/"round375/independent/coupling.py"))["power_interval"]
    early=runpy.run_path(str(root/"round394/independent/accept.py"))
    directed=factor(sources,power,first,audit)
    rates=ordinary_and_gaussian(old,new,first,audit,caller,early["ordinary"])
    floor,ordinary,positive=evidence_rows(literal,audit)
    ledger=fixture(floor["binary_integer_fixture"],power)
    return {"status":"INDEPENDENT_LITERAL_FLOOR_ACCEPTANCE_PASS; FULL_REGISTERED_SUITE_SEPARATE",
            "comparator":HEAD,"kappa":str(K),"sealed_prior":PINS|prior,"literal_pins":pinned,
            "unchanged_sources_sha256":unchanged,"archived_paths":len(archive),"literal_floor":floor,
            "literal_ordinary":ordinary,"positive_placement":positive,"detached_fixture_ledger":ledger,
            **directed,**rates}


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for field in ("inputs","capsule","sources","log","frozen","out"):
        p.add_argument("--"+field,type=Path,required=True)
    a=p.parse_args()
    signal.alarm(60)
    result=check(a.inputs,a.capsule,a.sources,a.log,parse(a.frozen.read_bytes()))
    signal.alarm(0)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
