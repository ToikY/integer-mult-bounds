"""Check one new physical ordinary floor and its directed whole signed price."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import runpy
import signal
import tarfile
from types import SimpleNamespace

HEAD="19e67d1b36210e3047bbf3d04625d1262cba672a"
PKG="research/p104-weighted-ordinary-debit"
OLD_PATH="round394/publish/"+PKG
TIER="research/tiered-native-multiplier/"
K0,K=Q(".00389821103"),Q(".00389821126")
B,C=Q(4391986206293,2**50),Q(17145637307,2**42)
OLD_D,D,DG=Q(703,512),Q(1405,1024),Q(64944,524288)
OLD_L,L,A=32768,18960,134
BEFORE,HS=(8192,129406,523763),(8192,129406,523443)
OLD_H,H=484799,485263
G,ETA=Q(1,10**18),Q(".0039")
DELTA,GRID=Q(1,2**128),2**112
K7="9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"

PINS={
    "round394/exact-head":"135d839ea3e9035b0292f967dd5fb6f68dd262306e19dc596886d6f4562332e4",
    "round394/preflight.log":"60ebbfb864fef6ca908655b89f881ff79ed6f02148780ed6b16e4cd0a3eca381",
    "round394/independent/verified.json":"1eef4f1fb8c85e2ae81cf9cd4bede2a9e83f7c2e7e0a3508534100ce6e3e6ba7",
    "round394/independent/sources/TRANSFER.md":"7164831a5dd9f5c6231bf4c3f4b2061d91cbfab559071a0a5d68966e3f7ac55c",
    "round394/independent/sources/RECEIVER.md":"f31089b6304fc5352feb9aa8a963cc5a950a828165d3426e16e8a973529d814e",
    "round394/independent/sources/ORDINARY-CLOCK.md":"4694db0b2218796e348c1128271cebb3fc779151a639b0e0fb5bbecf9f3ccb94",
    "round394/independent/accept.py":"a1e240a31f4c61d036c56b421df91bb36c15c4133f0ebb604773130ddfca7e31",
    "round391/price/check.py":"5a5e8b7c8f96703986b02760386b0790e4019a781e3ee47e1200a0cc356db687",
    "round378/independent/accept.py":"001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round375/independent/coupling.py":"fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    f"{OLD_PATH}/RESULT.json":"44b2d59a1b7e6d7f3336567dbdd4fe27b6ee3b64edd97172698aafdc91db9383",
    f"{OLD_PATH}/prepare.py":"48fca2618df3f3483c1640c8c77ded20cc3aeb37232c69e10466c9a5b323d098",
    f"{OLD_PATH}/PEER-SOURCE.json":"798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    f"{OLD_PATH}/peer8057.tar.gz":"0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}
INSTALLER=TIER+"source/installer.tar.gz"
RETIMED="retimed-source.tar.gz"
BINARY_SOURCE={
    INSTALLER:"6696459e2e3552f802e7caaaf93dc86c9bb6b62ee38631702bff2e3a8a9a481a",
    RETIMED:"3d30e35c5a77f43372e94ccca7aaa38ce706631fc5b4601293bbd8619dfb2775",
    f"{RETIMED}::raw_binary_stage.py":"0c805a525322acf4eb03f083c2c763f3046c3d488e1f993beb484a3e2c2ff4a9",
    f"{RETIMED}::transport.py":"98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9",
}
LOGS={f"round394/{stage}.{suffix}" for stage in ("scientific","onboarding","historical") for suffix in ("log","exit")}


def need(ok,reason):
    if not ok:
        raise ValueError(reason)


def authenticate(raw,digest):
    need(sha256(raw).hexdigest()==digest,"Archived bytes differ")
    return raw


def unique(pairs):
    data={}
    for key,value in pairs:
        need(key not in data,f"Duplicate pin {key}")
        data[key]=value
    return data


def parse(raw):
    return json.loads(raw,object_pairs_hook=unique)


def up(q):
    return -(-q.numerator//q.denominator)


def original_binary(archive):
    def get(arch,path,key):
        with tarfile.open(fileobj=BytesIO(arch)) as tar:
            files=[member for member in tar if member.name==path]
            need(len(files)==1 and files[0].isfile(),f"Exact archived file {path}")
            return authenticate(tar.extractfile(files[0]).read(),BINARY_SOURCE[key])

    i=authenticate(archive[INSTALLER],BINARY_SOURCE[INSTALLER])
    retimed=get(i,RETIMED,RETIMED)
    binary=get(retimed,"raw_binary_stage.py",f"{RETIMED}::raw_binary_stage.py").decode()
    plan=get(retimed,"transport.py",f"{RETIMED}::transport.py").decode()
    need("return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C)" in binary
         and "level_floor=2**15" in plan and "self.level_floor," in plan
         and "max(256, 64 * n.bit_length())" in plan and "width_log = 92 * rank_log" in plan,
         "Real ordinary Recipe.open takes the current physical floor")
    return BINARY_SOURCE


def factor(power,floor):
    common=Q(47,20)*Q(256,255)*Q(4097,4096)*Q(1028,1024)
    common*= (1+Q(64,floor)+DELTA)/((1-Q(10,floor))*(1-DELTA)**3)
    return tuple(Q(x,GRID)*common for x in power(Q(1024*A*floor),B))


def transport_support(power):
    # Every H currently installed on the ordinary side is at least 3000.
    h0=3000
    n=1<<h0
    u=2*(n//(2048*A))
    t=1-B
    lo=Q(power(Q(L),t)[0],GRID)
    paid_count=104652
    productive_count=18906
    # Use conservative ancestor bounds on grade ratios. K7 only reduced ranks.
    kmax,rmin=1032,Q(1,2)
    ratio=kmax/rmin
    need(L%2==0 and L>48 and 0<L<u and n%4==0 and u%2==0
         and [((L+j)-8)%4 for j in (0,2)]==[0,2]
         and 5*rmin<=4*kmax and 4*(L+2)*6<5*L*5,
         "Even legal new owners, complete original child deadline ordering and phase residues")
    need(4*kmax*(u-8)<n and u>ratio*L and u*kmax<n
         and (1-DELTA)*n<=1024*A*u and DELTA*n>2048*A,
         "Both real boundaries untruncated, full width and source period fit")
    need(Q(6,5)**4>2 and Q(6,5)**77>2**20
         and paid_count<2**19 and
         Q(paid_count,(1024*A*L)**77)+Q(1,n**77)<1
         and Q(1,t*lo)+Q(2,n**5)<2,
         "Whole binary lifetime, stage descent, opening and owner-return budget")
    need(t>Q(".996") and B.denominator==2**50
         and lo>2**14 and Q(power(Q(kmax),B)[1],GRID)<Q("1.06"),
         "Matching fringe, exponent grid and finite ordinary lower denominator")
    # The original at most 61-root error bound applies to the actual 50-root exponent.
    enclosure_bits=401-27*h0-64
    need(enclosure_bits < -2 and 2**46 < Q(n**4,2**132)
         and 2*paid_count < Q(n**4,2**132), "Exact quadrature and missing terminal-tick loss")
    eta=1-Q(10,L)
    # Exterior sum >V from Psi>.19 P, P>10 and U^c>1.
    # Incomplete periods have q/R<=1/N, each paid period s'q/N<=1028/1024.
    need(eta>Q(".99") and eta*(1-DELTA)*Q("1.9")>1
         and Q((1-Q(1,n)),Q(1028,1024))>Q(1,2)
         and n>4096*2*productive_count and 1<n*DELTA,
         "Full real cycle cap, incomplete-zero covers, final group padding and live exterior stock")
    return {"min_checked_ordinary_H":h0,"lower_fence":L,"first_two_native_widths":[L-8,L-6],
            "new_width_phase_residues":[0,2],"historical_upper_divisor":2048*A,
            "unchanged_max_grade_ratio":str(ratio),"conservative_delay_max":"N^77",
            "raw_opening_cap":"2V","live_exterior_rows":"h<N^91; B>=4096h",
            "interval_mass_error_bits_at_min_H":enclosure_bits,"proof_scope":"signed physical source unchanged; numeric structural bounds only"}


def check(root,complete):
    need(complete.keys()==LOGS,"Authenticate all completed R394 repository and scientific logs")
    pins=PINS|complete
    data={path:authenticate((root/path).read_bytes(),digest) for path,digest in pins.items()}
    history=data["round394/scientific.log"]
    need(data["round394/exact-head"].strip()==HEAD.encode()
         and f'"commit": "{HEAD}"'.encode() in data["round394/preflight.log"]
         and all(data[f"round394/{mode}.exit"].strip()==b"0" for mode in ("scientific","onboarding","historical"))
         and all(f"PASS_ORDINARY_DEBIT {phase}\n".encode() in history
                 for phase in ("price","calendar","raw","exterior","nested","product","setup"))
         and f"PASS_REGISTERED_RESEARCH_PACKAGE {PKG} outcome=completed".encode() in history
         and b"Ran 760 tests" in data["round394/onboarding.log"] and b"OK (skipped=31)" in data["round394/onboarding.log"]
         and b"PASS_HISTORICAL_SELECTED_REPLAY_GAP" in data["round394/historical.log"],
         "Exact previously reproduced signed and repository comparability")
    old=parse(data[OLD_PATH+"/RESULT.json"])
    bill=parse(data["round394/independent/verified.json"])
    need(bill["frozen_candidate"]["capsule/RESULT.json"]==PINS[OLD_PATH+"/RESULT.json"]
         and Q(bill["kappa"])==Q(old["terminal"]["kappa"])==K0
         and bill["same_stage_two_moment_ratio"]=="375/376" and bill["all_depth_multiplier"]==376,
         "Exact independent incumbent and unchanged all-depth proof")
    priced=runpy.run_path(str(root/"round394/independent/accept.py"))
    ordinary=priced["ordinary"]
    restore=runpy.run_path(str(root/"round378/independent/accept.py"))["restore_reference"]
    archive=restore(root/OLD_PATH)
    need(len(archive)==88 and sha256(archive[TIER+"source/strong-bit-k7.json.gz"]).hexdigest()==K7,
         "Every original source path authenticated and same 24-cell K7 provider")
    binary=original_binary(archive)
    power=runpy.run_path(str(root/"round375/independent/coupling.py"))["power_interval"]
    old_flo,old_fhi=factor(power,OLD_L)
    new_flo,new_fhi=factor(power,L)
    threshold_lo,threshold_hi=(Q(n,GRID) for n in power(Q(2),D))
    check_good=old_fhi**512<2**703
    enough=new_fhi**1024<2**1405
    negative_old=old_flo**1024>2**1405
    need(check_good and (not enough or new_fhi<threshold_lo)
         and (not negative_old or threshold_hi<old_flo),"Strict directed old/new fully charged envelope comparison")
    structural=transport_support(power)
    need(Q(75,32)/Q(47,20)==Q(375,376) and 1/(1-Q(375,376))==376
         and 0<B-D/min(HS)<1, "Unchanged normalized receiver and both moments")
    r0,cap0=ordinary(BEFORE,OLD_D,K0+5*G)
    old_ceiling=min(cap0,C-DG/OLD_H)-5*G
    need(tuple(old["terminal"]["ordinary_H"])==BEFORE
         and old["terminal"]["numerical_H"]==OLD_H
         and old["terminal"]["ordinary_rates"]==[str(x) for x in r0]
         and old["gaussian"]["finite_loss"]["upper_divisor"]==1724
         and old["gaussian"]["weights"]==[5,451],"Actual prior terminal prices and Gaussian source")
    _,cap_old_d=ordinary(HS,OLD_D)
    _ideal,cap=ordinary(HS,D)
    positive=C-DG/H
    booking=K+5*G
    output={"status":"PRICE_FAIL","comparator":HEAD,"old_kappa":str(K0),"candidate_kappa":str(K),
            "candidate_ordinary_H":HS,"candidate_positive_H":H,"candidate_ordinary_debit":str(D),
            "old_installed_cap":str(old_ceiling),"old_debit_ideal_cap_at_candidate":str(cap_old_d-5*G),
            "old_floor_factor_lower_1e15":(old_flo*10**15).__floor__(),
            "new_floor_factor_lower_1e15":(new_flo*10**15).__floor__(),
            "new_floor_factor_upper_1e15":up(new_fhi*10**15),
            "new_debit_exponential_interval_1e15":[(threshold_lo*10**15).__floor__(),up(threshold_hi*10**15)],
            "same_old_fence_fails_new_debit":negative_old,"candidate_unrounded_ordinary_upper":str(cap),
            "unchanged_child_factor":"47/20","two_moment_contraction":"375/376","all_depth_multiplier":376,
            "pinned_inputs":pins,"signed_binary_paths":binary,"transport_support":structural}
    if not (enough and negative_old and booking<min(positive,cap)):
        return output
    need(K>old_ceiling and cap_old_d<booking,"Actual comparator crossing and old debit ideal negative")

    cuts,dispatch,geometry,stock,qualify=runpy.run_path(str(root/"round391/price/check.py"))["archived_caller"](archive)
    profiles={}
    for name,heights,h,k in (("entry",(3000,3080),1024,Q(".00345")),("terminal",HS,H,K)):
        booked=k+5*G
        rates,actual=ordinary(heights,D,booked)
        row=stock(SimpleNamespace(rank_logs=heights,complex_log=h,eta=ETA))
        A0=row["public_exponent_A"]
        signed=qualify(k,G,booked,C-DG/h)
        need((signed["strict"],signed["functional"])==(54,4)
             and geom_compare(A0,row,h,cuts(heights),geometry),"Every signed inequality and real activation")
        seams=[]
        for j,cut in enumerate(row["binary_cuts"],1):
            steps=[dispatch(cut+x,len(heights),heights) for x in (-1,0,1)]
            need(steps==[j-1,j,j] and dispatch(cut+1,j-1,heights)==j-1,
                 "Actual adjacent before/after and clipped previous-stage condition")
            seams.append([cut,*steps,j-1])
        profiles[name]={"ordinary_rates":[str(x) for x in rates],"ordinary_margin":str(actual-booked),
                        "positive_margin":str(C-DG/h-booked),"signed":signed,"stock":row,
                        "geometry":geometry["entrance_geometry"](A0),"stage_seams":seams}
    terminal=profiles["terminal"]["stock"]
    a=terminal["public_exponent_A"]
    b=128+320*sum(HS)
    c=max(84500001,1602+220*H+b)
    premium=up((K-Q(".00345"))*a)
    clock=1+max(c,old["entry"]["log2_C"]+premium)
    need(min(HS)>=8192 and clock==318292711==old["complete_log2_C"]-320 and premium==514
         and terminal["storage_upper"]=="6.2 p T < 297.6 n bits",
         "Whole recurring, precision, old setup guard, tape and finite-prefix price")
    w=2**38
    z=2*w+2
    S=2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2
    setup=(2**68+1)*(8*4*w*2**68*512*128+S+2**120)*2**32
    need(max(*HS,H).bit_length()==19 and setup==old["native_setup_transition_upper"]<2**228
         and old["native_setup_grade_actions"]==269057152<2**32,"Full separately billed native setup")
    output.update(status="VIABLE_PRICE_ONLY",delta_kappa=str(K-K0),gain_percent=str(100*(K-K0)/K0),
                  clears_exact_prior_cap=str(K-old_ceiling),ideal_old_debit_negative_gap=str(booking-cap_old_d),
                  exact_complete_signed_profiles=profiles,log2_B=b,complete_log2_C=clock,entry_surcharge=premium,
                  native_setup=setup,native_max_height_field_bits=19,
                  fixed_funding_height_floors=[up(D/(B-booking)),up(DG/(C-booking))],
                  remaining="Install lower as explicit binary Recipe(..., level_floor=18960), verify true new bin/child and native tape, complete registered replay.")
    return output


def geom_compare(a,row,numerical,cuts,geometry):
    public=(1<<a)+row["first_public_offset"]
    return (list(cuts)==row["binary_cuts"] and a==geometry["connected_exponent"](cuts[-1],numerical)
            and public%6==0 and public.bit_length()==a+1 and (public-6).bit_length()==a)


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for name in ("inputs","complete","out"):
        p.add_argument("--"+name,type=Path,required=True)
    arg=p.parse_args()
    signal.alarm(60)
    result=check(arg.inputs.resolve(),parse(arg.complete.read_bytes()))
    signal.alarm(0)
    arg.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
