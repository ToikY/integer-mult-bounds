"""Check the new paid extent, true periods and both signed all-size budgets."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import runpy
import subprocess

OLD_HEAD = "682fd9512ccbf3035089d7e5f9cb4dedf9f746b4"
OLD_PATH = "round388/publish/research/p104-weighted-lower-band"
FREQ = "research/frequency-weighted-native-multiplier/"
PINS = {
    "round389/price/receipt.json": "106db88b62b4f1c1a88c2a516292e2be8f72f44df101e03828cfbf46afd16abc",
    "round389/audit/receipt.json": "8b1c01f0ee18d0b6110f95e8c81c4e40ddf182989c2426e81e0d5c27f84efa08",
    "round388/independent/accept.py": "a8ad7768fb373545632d087c7edb81645585fed98b757daa335713f1e21e3c2e",
    "round388/independent/verified.json": "a795a3fd9e4812d5bba4f46ab1a6c403bf83180fc1247b2196beae756c58693c",
    "round388/scientific.log": "d4416c0c60fbdf735c6b1583e11f907870041cb8d5b5254bd9519f651fb5febc",
    "round388/scientific.exit": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "round388/onboarding.log": "128f901401ccbdeb1428d7cae5ffe055f044479e745d57767cce11daa9d6e654",
    "round378/independent/accept.py": "001284bf901f84def95ff270e4012bab16a3875e1ee6de3d3ae490c5980e341e",
    "round375/independent/coupling.py": "fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    "round366/gaussian/receipt.json": "9e1206f26d124f9f788a96ff43453195c4ae8c9b679acbf8a0ca132c80a5b7a1",
    f"{OLD_PATH}/RESULT.json": "42f26ff677d6b302592e916b0cb57780a82cab1e620cc41bb8602a831abebe4c",
    f"{OLD_PATH}/prepare.py": "9b09ac31b2a1adf78b76c685bdee2bd4b8b8dff53ab68b66d2a15e021644e05e",
}
C = Q(17145637307, 2**42)
K, K0 = Q(".00389821053"), Q(".00389821040")
B, B0 = Q(64944, 2**19), Q(64982, 2**19)
G, DELTA = Q(1, 10**18), Q(1, 2**128)
A, A0, L, ULP = 263772, 313344, 1874, 2**112


def need(assertion, reason):
    if not assertion:
        raise ValueError(reason)


def digest(content):
    return sha256(content).hexdigest()


def pin(file, expected):
    data = file.read_bytes()
    need(digest(data) == expected, f"Authentication failed at {file.name}")
    return data


def unique_object(pairs):
    keys = {}
    for name, value in pairs:
        need(name not in keys, f"Repeated key {name}")
        keys[name] = value
    return keys


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def up(q):
    return -(-q.numerator // q.denominator)


def price_factors(census, coupled, baseline, fresh, screen, audit):
    src = census["ranks"]
    target, paid = [Counter({Q(r): n for r,n in src[family].items()}) for family in ("target","paid")]
    paid[1] += paid.pop(Q(1,2)) // 2
    targets, payers = [coupled["base_copy"](x) for x in (target, paid)]
    pays = payers.copy()
    pays[1] -= 1008
    pays[Q(1,2)] = 2016
    hist = []
    for lo, hi in ((targets, targets), (pays, payers)):
        combined = Counter({r:5*n for r,n in lo.items()})
        combined.update({2*r:451*n for r,n in hi.items()})
        hist.append(combined)
    target, paid = hist
    need([target.total(),paid.total()] == [23989248,128400048], "All actual paid and productive positions")
    raw_ratio, cells = coupled["allocate"](C,target,paid)
    need(len(cells)==51 and cells[112,258]==1, "Exact weighted edge support")
    need(Q(baseline["directed_margin"]) == raw_ratio == Q(fresh["directed_margin"]), "Same signed raw margin")
    need(baseline["typed_cells"] == fresh["typed_cells"] == 88 and fresh["grade_cells"] == 51,
         "All verified types and legal pairings preserved")
    power = coupled["power_interval"]
    psi_lo = psi_hi = Q()
    for (r,k), f in cells.items():
        x, y = power(k,C)
        u, v = power(r,C)
        lo, hi = Q(x*ULP//v,ULP), Q(up(Q(y*ULP,u)),ULP)
        need(1 < lo <= hi, "True directed edge and price interval")
        psi_lo += paid[r]*f*r*(lo-1)/C
        psi_hi += paid[r]*f*r*(hi-1)/C
    axes = sum(k*n for k,n in target.items())
    need(axes == 677246016, "Charged boundary axes")
    fringe_hi, fringe_lo = (10*axes/((1-C)*psi) for psi in (psi_lo,psi_hi))

    def envelope(scale, fringe, side):
        return ((1+DELTA)*(1+Q(1032,scale))*Q(power(Q(scale*L),C)[side],ULP)
                *(1+fringe/L+DELTA)/(1-DELTA)**4)

    new_factor = envelope(A,fringe_hi,1)
    old_lower = envelope(A0,fringe_lo,0)
    old_upper = envelope(A0,fringe_hi,1)
    debit = (Q(v,ULP) for v in power(Q(2),B))
    debit_lo,debit_hi = debit
    need(new_factor < debit_lo < debit_hi < old_lower <= old_upper < Q(power(Q(2),B0)[0],ULP),
         "New factor reaches the tighter debit and both predecessor controls agree")
    loss = fresh["finite_loss"]
    need(Q(loss["upper_factor"]) == new_factor and Q(loss["psi_lower"]) == psi_lo
         and Q(loss["fringe"]) == fringe_hi and Q(fresh["raw_loss"]) == B
         and loss["weighted_target_axes"] == axes and loss["lower_band"] == L,
         "Literal result uses the complete exact active factor")
    need(Q(screen["new_factor_upper"]) >= new_factor
         and up(new_factor*10**12) == audit["finite_factor_upper_1e12"],
         "Independent price controls agree under directed rounding")
    return {"raw_margin": str(raw_ratio), "weighted_targets_and_paid": [target.total(),paid.total()],
            "typed_count": 88, "min_per_target_top_share":"1/624",
            "new_factor_ceiling_1e14": up(new_factor*10**14),
            "finite_factor_headroom_floor_1e13": int((debit_lo-new_factor)*10**13),
            "old_divisor_fail_floor_1e13": int((old_lower-debit_hi)*10**13)}


def first_geometry():
    minimum = 1 << 1024
    t = 1-C
    u = 2*(minimum//(2*A))
    need(u > 516*L and 5160 < DELTA*u and (1-DELTA)*minimum <= A*u, "Rounded width and fringe")
    need(4*258*(u-8) < minimum and 516*(u+2) < minimum and 2*52608 < minimum,
         "All rank, direct support and physical owner copies charged")
    need(L % 2 == 0 and (L-8) % 4 == 2 and 24*(L+2) < 25*L and L*L > 2*1024**2,
         "Legal lower band with both existing phase cases")
    need(Q(456)/(t*1024)+Q(2,minimum**5) < 2 and 2**46*minimum**2 < Q(minimum**6,2**132)
         and Q(2**20*minimum**6,minimum**4) < Q(minimum**6,2**132),
         "All weighted openings and stock rounding")
    need(2**19*(Q(1,A*L)+Q(1,minimum))**77+Q(1,minimum**77) < 1,
         "Charged historical delay and final partial group")
    x = Q(3*258,4*A)
    lost = Q(23*258,2)
    need((1364*x-1)*minimum > 1364*lost and 1360*x < 1,
         "Two period brackets at all admissible heights")
    geometry = []
    for h in (1024,483871):
        m = 1 << h
        upper = 2*(m//(2*A))
        e = 2*(3*upper//8)
        width = 258*(e-8)
        count = 4*up(Q(m,4*width))
        fifths = (count*width-m)//4
        tickets = [divmod(j*count,5)[0] for j in range(3)]
        need(L < e < upper and upper*112 < 258*e < 258*(e+2) < m*112
             and 451*2*258*m > 4*624*112,
             "Positive first exterior root and physical type-one funding")
        need(count == 1364 and 2*count < 5*fifths and tickets == [0,272,545],
             "True fivefold first three slots")
        geometry.append([h,count,tickets,[1,272,1]])
    return geometry


def signed_tiers(literal, old, archived, audit):
    from types import SimpleNamespace
    native = "research/tiered-native-multiplier/source/"

    def source(name):
        env = {"__name__": "pinned_science"}
        exec(compile(archived[native+name], native+name, "exec"), env)
        return env

    signed = source("outer_budget.py")["margins"]
    stock = source("activation.py")["resource_receipt"]
    binary = Q(4391986206293,2**50)
    rows = {}
    for name, heights, h, k in (("entry",[3000,3080],1024,Q(".00345")),
                                  ("terminal",[8192,129414,524395],483871,K)):
        actual, preflight = literal[name], audit["complete_signed_tiers"][name]
        need(actual["ordinary_H"]==heights and actual["numerical_H"]==h and Q(actual["kappa"])==k,
             "Both literal profiles")
        booked = Q()
        for i, (height, rate) in enumerate(zip(heights,actual["ordinary_rates"],strict=True)):
            ordinary = min(Q(".0039"), (249*(binary-Q(11,8*height))+booked)/250)
            r = Q(rate)
            expected = Q(int(ordinary*10**21)-1,10**21) if i+1<len(heights) else k+5*G
            need(booked<r==expected<ordinary, "Strict signed ordinary recurrence")
            if i+2==len(heights) and name=="terminal":
                preceding=r
            booked=r
        positive=C-B/h
        need(Q(actual["gaussian_rate"])==positive, "Full finite numerical charge")
        strict,functional,gap=signed(k,G,booked,positive)
        need(len(strict)==54 and len(functional)==4 and min(*strict,*functional,gap)>0,
             "Every signed strict and functional bound")
        need(gap==Q(preflight["gaussian_gap"]) and ordinary-booked==Q(preflight["ordinary_gap"])
             and actual["signed"]==preflight["signed"]
             and actual["stock"]==preflight["stock"]==stock(SimpleNamespace(rank_logs=heights,complex_log=h,eta=Q(".0039")))
             and actual["geometry"]==preflight["geometry"],
             "Literal and independent exact caller, paid margin, stock and placement agree")
        rows[name]={"ordinary_gap":str(ordinary-booked),"positive_gap":str(gap),"checks":[54,4]}

    def installed(ordinary_prev,height,gaussian):
        return min(Q(".0039"),(249*(binary-Q(11,8*height))+ordinary_prev)/250,gaussian)-5*G

    old_row=old["terminal"]
    old_cap=installed(Q(old_row["ordinary_rates"][-2]),524369,Q(old_row["gaussian_rate"]))
    one_smaller=installed(preceding,524394,C-B/483871)
    need(Q(old_row["kappa"])==K0 and Q(old_row["gaussian_rate"])==C-B0/483871
         and K>old_cap and K>one_smaller and K-K0==Q(13,10**11),
         "Crosses actual old installed cap and insufficient adjacent height")
    terminal=literal["terminal"]
    entrance=terminal["stock"]["public_exponent_A"]
    first_offset=(-pow(2,entrance,6))%6
    premium=up((K-Q(".00345"))*entrance)
    need((entrance,first_offset)==(1146346,2) and terminal["stock"]["binary_cuts"]==[8290,137768,662227]
         and terminal["geometry"]["public_offset_above_2_to_A"]==2
         and terminal["stock"]["storage_upper"]=="6.2 p T < 297.6 n bits",
         "First exact terminal header and inherited complete linear storage")
    b_clock=128+320*sum(terminal["ordinary_H"])
    c_clock=1602+220*483871+b_clock
    need(b_clock==terminal["log2_B"] and c_clock==terminal["log2_C"]
         and premium==literal["entry_price_surcharge"]==514
         and literal["entry"]["log2_C"]==old["entry"]["log2_C"]
         and literal["complete_log2_C"]==1+max(c_clock,literal["entry"]["log2_C"]+premium)==318293671,
         "Fully charged recurring tape clock through both public regimes")
    w=2**38
    z=2*w+2
    scalar=2**16*(z+4)*(7*z+9)+8*2**16*(z+4)**2
    native_setup=(2**68+1)*(8*4*w*2**68*512*128+scalar+2**120)*2**32
    need(literal["native_setup_transition_upper"]==old["native_setup_transition_upper"]==native_setup
         and native_setup<2**228 and literal["log2_fixed_setup_upper"]==228
         and literal["native_setup_grade_actions"]==269057152<audit["fixed_grade_recipe_actions_upper"],
         "Full precomputed native setup and indexed tape")
    return {"signed_tiers":rows,"exact_previous_installed_cap":str(old_cap),
            "separation_from_installed_cap":str(K-old_cap),"one_smaller_H3_cap":str(one_smaller),
            "complete_log2_C":literal["complete_log2_C"],"fixed_setup_log2":228}


def check_edits(archived, old, fresh):
    before = runpy.run_path(str(old/"prepare.py"))
    after = runpy.run_path(str(fresh/"prepare.py"))
    names = {"grades.py", "positive_debit.py", "independent_price.py", "check_placement.py",
             "runtime.patch", "receipt.py"}
    need(before["EDITS"].keys()==after["EDITS"].keys(), "No added file changes")
    need({f for f in before["EDITS"] if before["EDITS"][f]!=after["EDITS"][f]}==names,
         "Only intended cutoff, pricing and verification change points")

    def realize(edits):
        result={}
        for name, changes in edits.items():
            content=archived[FREQ+name].decode()
            for a,b in changes:
                need(content.count(a)==1, f"Single literal source change in {name}")
                content=content.replace(a,b)
            result[name]=content
        return result

    base, candidate = (realize(x["EDITS"]) for x in (before,after))
    need({name for name in base if base[name]!=candidate[name]}==names,
         "Actual changed source set")
    need(candidate["grades.py"]==base["grades.py"].replace("LOWER = 1874","LOWER = 1874\nUPPER_DIVISOR = 1724")
         .replace("2048 * self.ambient","UPPER_DIVISOR * self.ambient"),
         "Production upper fence, no other recipe or calendar edit")
    need(candidate["runtime.patch"]==base["runtime.patch"].replace("524369","524395")
         .replace(".00389821040",".00389821053"), "Only new terminal height and certified rate")
    need(after["NEW_INSTALLATION"]=="64f415e0d6c13776c1b73c71c687ea989d8fea9807340fd0ca39517f99dd04b0",
         "Exact installed profile pin")
    price=candidate["positive_debit.py"]
    need(all(x in price for x in ("2 * (M // (2 * scale))","scale * upper",
         "Q(4 * max(targets), scale)","power_interval(scale * lower, c)",
         '"upper_divisor": UPPER_DIVISOR','"upper_scale": scale')),
         "Archived invoice reuses all changed actual-coordinate factor terms")
    placement=candidate["check_placement.py"]
    need(all(x in placement for x in ("UPPER_DIVISOR == 1724","LOWER < e < U < lo < hi < M",
         "period == 1364","tickets == (0, 272, 545)","f.swaps[0] == (1, 272, 1)",
         "raw.align(f, Job(0, tickets), tuple(range(3)))")),
         "Literal alignment still called on the revised coordinates")
    cutoff=(fresh/"check_cutoff.py").read_text()
    need(all(x in cutoff for x in (
         "recipe.open()", "upper == 2 * (carrier // (1724 * 306))",
         "grades.TypedPlan = original", "len(cells) == 88", "PASS_LITERAL_LOWER_CUTOFF")),
         "Check both true constructor paths and keep the prior lower fixture")
    unchanged=("typed_raw.py","typed_transport.py","check_raw.py","check_calendar.py",
               "check_nested.py","check_exterior.py","check_ownership.py","verify.py")
    return {name:digest(candidate[name].encode() if name in candidate else archived[FREQ+name])
            for name in unchanged}


def check(inputs, capsule, build_log, frozen):
    data={path:pin(inputs/path,sha) for path,sha in PINS.items()}
    old_root=(inputs/OLD_PATH).resolve()
    def git(*args):
        return subprocess.check_output(["git","-C",str(old_root),*args])
    git_pins=(("RESULT.json",f"{OLD_PATH}/RESULT.json"),("prepare.py",f"{OLD_PATH}/prepare.py"))
    need(all(git("show",f"{OLD_HEAD}:research/p104-weighted-lower-band/{name}")==data[path]
             for name,path in git_pins), "Both predecessor bytes are in the exact #8063 commit")
    need(data["round388/scientific.exit"].strip()==b"0"
         and b"PASS_REGISTERED_RESEARCH_PACKAGE research/p104-weighted-lower-band outcome=completed"
         in data["round388/scientific.log"],"Exact complete predecessor control passed")
    screen,audit,old=(parse(data[path]) for path in ("round389/price/receipt.json","round389/audit/receipt.json",
                                                   f"{OLD_PATH}/RESULT.json"))
    need(screen["comparator"]==audit["prior_exact_head"]==OLD_HEAD,"Both presolve receipts pin #8063")
    cap_files={"prepare.py","check_cutoff.py","RESULT.json","PEER-SOURCE.json","peer8057.tar.gz",
               "verify.py","VERIFY.json","TASK.json","SOURCES.json"}
    need(frozen.keys()=={f"capsule/{name}" for name in cap_files}|{"build.log"}, "Complete path-keyed frozen inputs")
    contents={name:pin(capsule/name,frozen[f"capsule/{name}"]) for name in sorted(cap_files)}
    need(contents["verify.py"]==(old_root/"verify.py").read_bytes().replace(b"PASS_WEIGHTED_LOWER_BAND",b"PASS_WEIGHTED_UPPER_BAND"), "No wrapper-coverage change")
    prior_plan=parse((old_root/"VERIFY.json").read_bytes())
    active_plan=parse(contents["VERIFY.json"])
    old_commands=[(x["argv"],x["timeout_seconds"]) for x in prior_plan["commands"]]
    active_commands=[(x["argv"],x["timeout_seconds"]) for x in active_plan["commands"]]
    need(active_commands==old_commands and [x[0][-1] for x in active_commands]==[
         "price","calendar","raw","exterior","nested","product","setup"],
         "All seven scientific commands and full prior limits retained")
    new=parse(contents["RESULT.json"])
    evidence=pin(build_log,frozen["build.log"]).decode()
    original=runpy.run_path(str(inputs/"round378/independent/accept.py"))
    archived=original["restore_reference"](capsule)
    need(len(archived)==88,"All 88 archive sources")
    unchanged=check_edits(archived,old_root,capsule)
    geometry=first_geometry()
    need(geometry==audit["placement"],"Independent all-height placement predictions agree")
    anchor="PASS_INDEPENDENT_WEIGHTED_AND_QUARTER_PRICES\n"
    need(evidence.count(anchor)==1, "One passing exact price replay")
    recorded,_=json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(evidence.split(anchor)[1])
    need([[r["H"],r["period"],r["tickets"],r["first_swap"]] for r in recorded]==geometry
         and all(r["cell"]==[1,112,1,258] and r["share"]=="1/624"
                  and r["rotated_roots"]==384 and r["first_root"]==["root","rotated",0,4080,1]
                  for r in recorded), "Genuine signed exterior alignment at both installed heights")
    need(all(marker in evidence for marker in (
          "PASS_WEIGHTED_COMPLETE_PRICE 318293671","PASS_LITERAL_UPPER_FENCE 1724 1874 (1024, 483871)",
          "PASS_LITERAL_LOWER_CUTOFF 1874","PASS_WEIGHTED_UPPER_BAND price\nprice exit 0",
          "PASS_WEIGHTED_UPPER_BAND calendar\ncalendar exit 0")),
         "Direct price, both actual constructors and preserved lower cutoff ran")
    need(all(new["gaussian"][field]==old["gaussian"][field] for field in (
         "trial","weights","real_targets","real_loans","weighted_targets","weighted_loans","grade_cells",
         "typed_cells","min_individual_share","capacity_cut")),"Unchanged complete ordered source inventory")
    need((new["gaussian"]["finite_loss"]["upper_divisor"],new["gaussian"]["finite_loss"]["upper_scale"])==(1724,A)
         and Q(new["terminal"]["kappa"])==K and Q(new["previous_rate"])==K0 and Q(new["rate_delta"])==K-K0,
         "Complete literal rate, comparison and new fence fields")
    coupled=runpy.run_path(str(inputs/"round375/independent/coupling.py"))
    factors=price_factors(parse(data["round366/gaussian/receipt.json"]),coupled,
                          old["gaussian"],new["gaussian"],screen,audit)
    tiers=signed_tiers(new,old,archived,audit)
    need(Q(screen["prior_installed_cap"])==Q(tiers["exact_previous_installed_cap"])
         and Q(screen["ordinary_ceiling_if_H3_524394"])==Q(tiers["one_smaller_H3_cap"]),
         "Independent old and insufficient height controls agree on exact cap")
    return {"status":"INDEPENDENT_LITERAL_PRICE_AND_BOUNDARY_REPLAY_PASS; FULL_REGISTERED_SUITE_SEPARATE",
            "comparator_head":OLD_HEAD,"kappa":str(K),"delta_kappa":str(K-K0),
            "gain_percent":str(100*(K-K0)/K0),"pinned_inputs":PINS,"candidate_and_gate_pins":frozen,
            "unchanged_signed_native_sha256":unchanged,"physical_placements":geometry,
            **factors,**tiers}


if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--inputs",type=Path,required=True)
    parser.add_argument("--capsule",type=Path,required=True)
    parser.add_argument("--build-log",type=Path,required=True)
    parser.add_argument("--frozen",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=check(args.inputs,args.capsule,args.build_log,parse(args.frozen.read_bytes()))
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
