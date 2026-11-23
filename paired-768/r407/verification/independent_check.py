"""Verify the exact detached inputs, materialized images, and independent invoices."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha1, sha256
from math import ceil, floor, isqrt
from pathlib import Path
import json
import subprocess
import sys
import tarfile

CANDIDATE = "aea1699415250d865f7a635f4df0b76f406c47b4"
PEER = "510113821774bb27f7ddaad4e8b94837a1c2cf52"
HISTORY = "0618e75a22cec54d1651394ef83d088551b7f026"
SOURCE = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
ARCHIVE = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
CANDIDATE_PACKAGE = "research/p104-period-debit-25bit"
PEER_PACKAGE = "research/p104-expanded-budget-25bit"
CB, CG = Q(4391986206293, 2**50), Q(17145637307, 2**42)
DB, DG, OLD_DG = Q(11239, 8192), Q(64934, 2**19), Q(64939, 2**19)
GUARD, ETA = Q(5, 10**18), Q(39, 10_000)
GRID = 2**208
NOMINAL_K, PEER_K = Q(".003898460000505"), Q(".00389846")
PEER_H, PEER_G, PEER_COST = (8192, 38102, 604362), 18845936, 4354317571
HERE = Path(__file__).resolve().parent


def digest(blob):
    return sha256(blob).hexdigest()


def metadata(path):
    def unique(items):
        assert len(dict(items)) == len(items)
        return dict(items)
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def bind(root, head, package):
    assert git(root, "rev-parse", "HEAD").decode().strip() == head
    assert subprocess.run(["git", "-C", root, "symbolic-ref", "-q", "HEAD"]).returncode == 1
    assert git(root, "status", "--porcelain") == b""
    assert subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", HISTORY, head]).returncode == 0
    assert git(root, "cat-file", "-t", HISTORY).strip() == b"commit"
    result = {}
    for row in git(root, "ls-tree", "-r", head, "--", package).decode().splitlines():
        info, name = row.split("\t")
        mode, kind, object_id = info.split()
        data = (root / name).read_bytes()
        assert name not in result and kind == "blob" and mode in ("100644", "100755")
        assert git(root, "cat-file", "blob", object_id) == data
        assert bool((root / name).stat().st_mode & 0o100) == (mode == "100755")
        result[name] = dict(mode=mode, sha256=digest(data), git_blob=object_id)
    assert result
    return result


def bind_sources(new, old, receipt, receipt_dir):
    assert len(receipt["modes"]) == 8 and all(m["result"] == "pass" for m in receipt["modes"])
    assert receipt["exit_code"] == 0 and receipt["head"] == PEER and receipt["clean_detached_checkout"]
    for name, expected in receipt["evidence_file_sha256"].items():
        assert digest((receipt_dir / name).read_bytes()) == expected, name
    assert (new / "PREDECESSOR-RESULT.json").read_bytes() == (old / "RESULT-460.json").read_bytes()
    for name in ("LICENSE", "PEER-SOURCE.json", "peer8057.tar.gz", "prepare.py",
                 "upstream_verify.py", "UPSTREAM-README.md", "UPSTREAM-PROOF.md",
                 "UPSTREAM-NOTICE.md", "check_cutoff.py", "check_stage_seam.py",
                 "check_ordinary_floor.py", "SOURCE-8072-PINS.json"):
        assert (new / name).read_bytes() == (old / name).read_bytes(), name
    pins = metadata(new / "SOURCE-8072-PINS.json")
    assert pins["head"] == SOURCE and len(pins["files"]) == 10
    names = {"verify.py": "upstream_verify.py", "NOTICE.md": "UPSTREAM-NOTICE.md",
             "README.md": "UPSTREAM-README.md", "PROOF.md": "UPSTREAM-PROOF.md"}
    for path, expected in pins["files"].items():
        name = Path(path).name
        data = (new / names.get(name, name)).read_bytes()
        assert sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == expected, path
    sources = metadata(new / "PEER-SOURCE.json")
    archive = new / "peer8057.tar.gz"
    assert sources["head"] == ARCHIVE and digest(archive.read_bytes()) == sources["archive_sha256"]
    members = {}
    with tarfile.open(archive) as handle:
        for item in handle:
            if item.isdir():
                continue
            path = Path(item.name)
            assert item.isfile() and not path.is_absolute() and ".." not in path.parts and item.name not in members
            members[item.name] = digest(handle.extractfile(item).read())
    assert len(members) == 88 and members == sources["files_sha256"]
    return dict(source_8072_git_blobs=pins["files"], source_8057_archive_sha256=sources["archive_sha256"],
                source_8057_members=members)


def image(tree):
    return {file.relative_to(tree).as_posix(): digest(file.read_bytes())
            for file in sorted(tree.rglob("*")) if file.is_file()}


def power(base, exponent):
    """Consecutive square-root enclosure on an independent 208-bit integer grid."""
    scaled = Q(base)*GRID
    assert 0 < exponent < 1 and exponent.denominator.bit_count() == 1
    left, right = floor(scaled), ceil(scaled)
    product_l = product_r = GRID
    for place in range(exponent.denominator.bit_length()-2, -1, -1):
        left = isqrt(left*GRID)
        square = right*GRID
        root = isqrt(square)
        right = root + (root*root != square)
        if (exponent.numerator >> place) & 1:
            product_l = product_l*left//GRID
            product_r = -(-product_r*right//GRID)
    return Q(product_l, GRID), Q(product_r, GRID)


def period_and_weights(runtime, recipe, result):
    transport = (runtime / "typed_transport.py").read_text()
    for line in ("size = (e - 8) * k", "period = 4 * ceil(Q(n, 4 * size))",
                 "self.source_width += number * ticks * (rounds // period)",
                 "if self.delay[d] >= self.delay[e]:",
                 'raise ArithmeticError("A target owner received two independent fields")'):
        assert line in transport
    grades = (runtime / "grades.py").read_text()
    assert "UPPER_DIVISOR = 1724" in grades
    assert recipe.ambient == 306 and max(recipe.targets.histogram) == 258
    scale, lower = 1724*306//2, 1874
    first_x = Q(scale, 4*max(recipe.targets.histogram))
    exterior = Q(257, 256)
    assert 255 < first_x < 256 and Q(256)/first_x < exterior < 1 + 1/first_x
    # When x>256, m=ceil(x)-1>=256, and (m+1)/x<(m+1)/m<=exterior.
    assert Q(257, 256) == Q(256+1, 256)
    lo = hi = 0
    for (r,k), share in recipe.cells.items():
        assert 5*r <= 4*k
        edge_l, edge_u = power(Q(k,r), CG)
        edge_mass = recipe.paid.histogram[r] * share * r
        lo += edge_mass*(edge_l-1)/CG
        hi += edge_mass*(edge_u-1)/CG
    axes = sum(k*n for k,n in recipe.targets.histogram.items())
    delta = Q(1, 2**128)
    a,b = power(scale*lower, CG)
    prefactor = (1+delta)*exterior/(1-delta)**4
    lower_factor = prefactor * a * (1+10*axes/((1-CG)*hi*lower)+delta)
    upper_factor = prefactor * b * (1+10*axes/((1-CG)*lo*lower)+delta)
    funding = power(2, DG)[0] - upper_factor
    adjacent = lower_factor - power(2, DG-Q(1,2**19))[1]
    coarse_low = lower_factor * (1+1/first_x) / exterior
    coarse_high = upper_factor * (1+1/first_x) / exterior
    old_reject = coarse_low-power(2,DG)[1]
    assert funding > Q(".000000232515772047") and adjacent > Q(".000001208067461857")
    assert old_reject > 0 and power(2,OLD_DG)[0] > coarse_high
    assert axes == 677246016 and len(recipe.cells) == 51
    typed = recipe.typed_cells()
    widths = [1,2]
    weights = [w.multiplicity for w in recipe.types()]
    assert weights == [5,451] and len(typed) == 88
    rows, loads = defaultdict(Q), defaultdict(Q)
    for (a,r,b,k), share in typed.items():
        assert 5*r <= 4*k
        rows[a,r] += share
        assert Counter(recipe.types()[a].paid) == recipe.paid.variants[a].histogram
        count = recipe.targets.variants[b].histogram[k]
        loads[b,k] += weights[a]*recipe.paid.variants[a].histogram[r]*share*power(r,1-CG)[1]/count
    assert set(rows) == {(a,r) for a,word in enumerate(recipe.paid.variants) for r in word.histogram}
    assert all(value == 1 for value in rows.values())
    for b, word in enumerate(recipe.targets.variants):
        for k in word.histogram:
            assert 0 < loads[b,k] <= weights[b]*power(k,1-CG)[0]
        assert Counter(recipe.types()[b].targets) == word.histogram
    target_counts = [len(word.targets) for word in recipe.types()]
    loan_counts = [len(word.paid) for word in recipe.types()]
    assert target_counts == result["real_targets"] == [52608,52608]
    assert loan_counts == result["real_loans"] == [282576,281568]
    assert sum(a*b for a,b in zip(weights,target_counts,strict=True)) == result["weighted_targets"] == 23989248
    assert sum(a*b for a,b in zip(weights,loan_counts,strict=True)) == result["weighted_loans"] == 128400048
    multiplier = (Q(47,20)*Q(256,255)*Q(4097,4096)*Q(1028,1024)
                  *(1+Q(64,18960)+delta)/((1-Q(10,18960))*(1-delta)**3))
    ord_lo, ord_hi = power(1024*134*18960, CB)
    ord_budget = 2*power(2,DB-1)[0]
    assert ord_budget > multiplier*ord_hi
    assert multiplier*ord_lo > 2*power(2,DB-1-Q(1,2**14))[1]
    assert Q(75,32)/Q(47,20) == Q(375,376)
    return dict(signed_word_width_scales=widths, weights=weights, targets=target_counts, loans=loan_counts,
                grade_cells=len(recipe.cells), typed_cells=len(typed), axes=axes,
                first_x=first_x, exterior_period=exterior, directed_grid_bits=208, funding_excess=funding,
                adjacent_shortfall=adjacent, old_factor_shortfall_at_new_booking=old_reject,
                ordinary_paid_upper_gap=ord_budget-multiplier*ord_hi)

def ordinary(heights):
    prior, rounded = Q(0), []
    for index, height in enumerate(heights):
        rate = min(ETA, Q(249,250)*(CB-DB/height)+prior/250)
        if index < len(heights)-1:
            prior = Q(floor(rate*10**21)-1,10**21)
            rounded.append(prior)
    return rate, rounded


def positive(g, debit):
    return CG-debit/g


def whole_stock(h, g):
    cuts = []
    for height in h:
        cuts.append(max(ceil(Q(250*(height+64),249)), height+64+cuts[-1] if cuts else 0))
    assert all(H>previous+2 for H,previous in zip(h[1:],cuts[:-1],strict=True))
    minimum = cuts[-1]+g+102
    s = minimum+7*(minimum-1).bit_length()
    while s-7*(s-1).bit_length() < minimum:
        s = minimum+7*(s-1).bit_length()
    jump = (s-1).bit_length()
    if 2**jump+1 < minimum+7*(jump+1):
        s = minimum+7*(jump+1)
    assert s-7*(s-1).bit_length() >= minimum
    assert (1<<((s-1).bit_length()))+1-7*((s-1).bit_length()+1) >= minimum
    exponent = s-1
    local = 25*32+32*32+4*(len(h)+1)+128
    return dict(binary_cuts=cuts, public_exponent_A=exponent, first_public_offset=(-pow(2,exponent,6))%6,
                initial_s=s, stage_and_outer_fixed_log_overhead=local,
                retimed_first_stripe_margin=s//2-2-local-4*(s+128).bit_length(),
                retimed_all_size_margin_floor=31*s//64-3-local,
                absolute_log2_private_control_envelope=1024*max(g,*h)+(len(h)+1).bit_length(),
                storage_upper="6.2 p T < 297.6 n bits")


def precision_fences(stock, expected, shape, actual_precision):
    exponent = stock["public_exponent_A"]
    offset = stock["first_public_offset"]
    public = (1<<exponent)+offset
    s = (public+1).bit_length()
    minimum = 128*(4*(s+1)+6)
    assert minimum == expected["minimum_width"] and public%6 == 0
    endpoints = []
    for adjustment in (4,5):
        extent = public//6+adjustment-exponent
        count = 1<<((extent//minimum).bit_length()-1)
        assert count == shape(public,extent).count
        width = -(-extent//count)
        cycles = 20000*(count+1)*(width+2)**6+2*count
        activity = max(1,count//(1024*s))
        bits = public+67+32768*activity*(width+6)+4*(cycles*(count+1)).bit_length()+(count+1).bit_length()
        assert bits == actual_precision(public,extent,count)
        endpoints.append(dict(extent_formula=f"public/6+{adjustment}-{exponent}", width=width,
                              log2_count=count.bit_length()-1, precision_bit_length=bits.bit_length(),
                              precision_integer_sha256=digest(bits.to_bytes((bits.bit_length()+7)//8,"big"))))
    assert endpoints[0]["log2_count"]==endpoints[1]["log2_count"]==expected["log2_axis_count"]
    assert max(end["width"] for end in endpoints) == expected["largest_axis_width"]
    return public, endpoints


def invoice(entries, receipt, debit, margins, shape, precision):
    tiers = {}
    for label, profile in entries.items():
        h,g,k = profile.rank_logs,profile.complex_log,profile.kappa
        literal = receipt[label]
        assert (h,g,k) == (tuple(literal["ordinary_H"]),literal["numerical_H"],Q(literal["kappa"]))
        assert profile.eta == ETA and profile.positive_stop_denominator == 10**18
        scalars = [k.numerator,k.denominator,ETA.numerator,ETA.denominator,profile.positive_stop_denominator]
        assert max(abs(x).bit_length() for x in scalars) <= 128
        assert all(1024 <= x < 2**25 for x in (*h,g))
        stock = whole_stock(h,g)
        assert stock == literal["stock"]
        public, endpoints = precision_fences(stock,literal["geometry"],shape,precision)
        ordinary_rate, rounded = ordinary(h)
        gaussian_rate = positive(g,debit)
        paid_rate = k+GUARD
        assert min(ordinary_rate,gaussian_rate) > paid_rate
        assert [Q(x) for x in literal["ordinary_rates"]] == [*rounded,paid_rate]
        assert Q(literal["gaussian_rate"]) == gaussian_rate
        strict,functional,funding = margins(k,GUARD/5,paid_rate,gaussian_rate)
        assert (len(strict),len(functional)) == (54,4)
        assert len(strict)==literal["signed"]["strict"] and len(functional)==literal["signed"]["functional"]
        assert min(*strict,*functional,funding)>0 and funding==Q(literal["signed"]["positive_margin"])
        bound_b = 40+17+16384*sum(h)+25818582 if label=="entry" else 128+320*sum(h)
        bound_c = max(84_500_001,1602+220*g+bound_b)
        assert (bound_b,bound_c)==(literal["log2_B"],literal["log2_C"])
        tiers[label] = dict(h=h,g=g,k=k,stock=stock,ordinary_limit=ordinary_rate,
                            gaussian_limit=gaussian_rate,ordinary_margin=ordinary_rate-paid_rate,
                            gaussian_margin=funding,strict=54,functional=4,min_strict=min(strict),
                            min_functional=min(functional),log2_b=bound_b,log2_c=bound_c,
                            exact_extent_precisions=endpoints)
    low,high = tiers["entry"],tiers["terminal"]
    conversion = ceil((high["k"]-low["k"])*high["stock"]["public_exponent_A"])
    whole = 1+max(low["log2_c"]+conversion,high["log2_c"])
    assert conversion==receipt["entry_price_surcharge"]==8744 and whole==receipt["complete_log2_C"]
    return dict(tiers=tiers,conversion=conversion,complete_recurring_log2_c=whole),public


def stopped_comparator(peer, candidate, matched):
    assert peer["complete_recurring_log2_c"] == PEER_COST == matched["complete_recurring_log2_C"]
    assert candidate["complete_recurring_log2_c"] == 4354317451
    old = peer["tiers"]["terminal"]
    new = candidate["tiers"]["terminal"]
    assert (old["h"],old["g"],old["k"]) == (PEER_H,PEER_G,PEER_K)
    assert (new["h"],new["g"],new["k"]) == ((8192,38102,604363),18845934,NOMINAL_K)
    assert positive(PEER_G-1,OLD_DG) < PEER_K+GUARD < positive(PEER_G,OLD_DG) < ordinary(PEER_H)[0]
    cap = positive(PEER_G,OLD_DG)-GUARD
    assert cap == Q(matched["exact_stopped_family_ceiling"])
    assert positive(PEER_G,OLD_DG)-cap-GUARD == 0
    # For any G at least one above the crossing, charge all tape terms first.
    sum_cap = (PEER_COST-1-1602-128-220*(PEER_G+1))//320
    assert sum_cap == 650655
    grid = 10**50
    directed = Q(isqrt(grid*grid//250),grid)
    assert directed**2<Q(1,250)<(directed+Q(1,grid))**2
    # Cauchy closes the last two reciprocal terms. The derivative at H1=8192
    # is positive, and the resulting function is convex on [8192,sum_cap).
    cauchy_weight = (1+directed)**2
    qprime = cauchy_weight/(sum_cap-8192)**2-Q(1,62500*8192**2)
    assert qprime > 0
    loss = Q(1,62500*8192) + cauchy_weight/(sum_cap-8192)
    old_next_g_upper = CB*(1-Q(1,250**3))-Q(249,250)*DB*loss
    assert old_next_g_upper < PEER_K+GUARD
    assert cap < NOMINAL_K
    assert old["ordinary_limit"] < NOMINAL_K+GUARD
    k,g = new["k"],new["g"]
    assert positive(g-2,DG)<k+GUARD<positive(g-1,DG)<positive(g,DG)
    assert positive(g,OLD_DG)<k+GUARD
    return dict(exact_cap=cap, gap_to_candidate=NOMINAL_K-cap,
                old_recurring_units_saved=PEER_COST-candidate["complete_recurring_log2_c"],
                next_peer_g_max_ordinary_sum=sum_cap, next_peer_g_relaxed_ordinary_upper=old_next_g_upper,
                next_peer_g_shortfall=PEER_K+GUARD-old_next_g_upper,
                same_peer_profile_is_known_good=True, new_g_minus_1_margin=positive(g-1,DG)-k-GUARD,
                new_g_minus_2_shortfall=k+GUARD-positive(g-2,DG))


def fixed_setup(receipt, actual_supplier):
    n,w = 2**68+2**40,2**38
    max_carrier_and_scalar_steps = 2*2048*(2**25+1)+7*2**24
    assert max_carrier_and_scalar_steps == 137556398080 < 2**40
    datum = 2*w+2
    lookup = 8*(4*w*n)*512*128
    arithmetic = 2**16*(datum+4)*(7*datum+9) + 8*2**16*(datum+4)**2
    total = (n+1)*(lookup+arithmetic+2**120)*2**32
    assert total == receipt["native_setup_transition_upper"] < 2**228
    assert 92*(2**25-1)<2**32 and 1024*(2**25-1)+3<2**35<w
    bits = actual_supplier.carrier.bit_length()
    assert bits == 18845935 and actual_supplier.carrier.bit_count() == 1
    return dict(indexed_actions=n, extra_actions=2**40, lookup=lookup, arithmetic=arithmetic,
                total_transitions=total, max_carrier_and_scalar_steps=max_carrier_and_scalar_steps,
                actual_carrier_bits=bits)


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("candidate","peer","stage","manifest","peer_receipt"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args()
    current,peer,stage = [p.resolve() for p in (args.candidate,args.peer,args.stage)]
    assert digest(args.manifest.read_bytes()) == "46591f0f0d4a5cbbc5620d7e2312b18f3b73147be456ceb1cf9f728ec13e4ed3"
    assert digest(args.peer_receipt.read_bytes()) == "09e18f17ac1dcdb40cd464c20f1e0a030ed57a1e9e3a07092d1e3a12b400802a"
    manifest, peer_replay = metadata(args.manifest), metadata(args.peer_receipt)
    new_data = bind(current,CANDIDATE,CANDIDATE_PACKAGE)
    old_data = bind(peer,PEER,PEER_PACKAGE)
    assert manifest["head"] == CANDIDATE
    assert {f:r["sha256"] for f,r in new_data.items()} == manifest["files"]
    assert {f:r["mode"] for f,r in new_data.items()} == manifest["modes"]
    new,old = current/CANDIDATE_PACKAGE,peer/PEER_PACKAGE
    source = bind_sources(new,old,peer_replay,args.peer_receipt.resolve().parent)
    current_runtime,peer_runtime = stage/"candidate"/"runtime",stage/"peer"/"runtime"
    a,b = image(current_runtime),image(peer_runtime)
    assert a.keys() == b.keys() and len(a)==106
    assert [path for path in a if a[path]!=b[path]] == ["installations.py"]
    line_old = 'TERMINAL = Profile((8192, 38102, 604362), 18845936, Q(".00389846"))'
    line_new = 'TERMINAL = Profile((8192, 38102, 604363), 18845934, Q(".003898460000505"))'
    text_old = (peer_runtime/"installations.py").read_text()
    assert text_old.count(line_old)==1
    assert text_old.replace(line_old,line_new) == (current_runtime/"installations.py").read_text()
    sys.path.insert(0,str(current_runtime))
    from upstream import install
    install()
    sys.path.append(str(stage/"candidate/archive/research/tiered-native-multiplier/source"))
    from band_product import precision, prepare_native, production_supplier
    from installations import ENTRY, TERMINAL, Profile, at_public
    from linear_geometry import public_shape
    from outer_budget import margins
    from outer_clock import financial_checks
    from strong_complex import load_changed
    assert financial_checks()["early_log2_C_bound"]==84500000
    graph,layout = load_changed(current_runtime/"inputs")
    assert len(graph["moves"]) == 5674 and len(graph["initial"])==1291
    assert len(graph["final"])==len(graph["initial"])
    new_rec,old_rec = (metadata(p/"RESULT-460.json") for p in (new,old))
    candidate,public = invoice(dict(entry=ENTRY,terminal=TERMINAL),new_rec,DG,margins,public_shape,precision)
    assert at_public(public-6) is ENTRY and at_public(public) is TERMINAL
    candidate_terms,peer_terms = candidate["tiers"]["terminal"],old_rec["terminal"]
    assert candidate_terms["log2_b"]-peer_terms["log2_B"]==320
    assert (candidate_terms["g"]-peer_terms["numerical_H"])*220==-440
    old_invoice,_ = invoice(dict(entry=ENTRY,terminal=Profile(PEER_H,PEER_G,PEER_K)),old_rec,OLD_DG,margins,public_shape,precision)
    compare = stopped_comparator(old_invoice,candidate,peer_replay)
    period = period_and_weights(current_runtime,prepare_native(TERMINAL)[-1],new_rec["gaussian"])
    setup = fixed_setup(new_rec,production_supplier(TERMINAL.complex_log,TERMINAL.positive_stop_denominator))
    result = dict(candidate_head=CANDIDATE,peer_head=PEER,historical_parent=HISTORY,files=new_data,
                  peer_files=old_data,source=source,runtime_candidate=a,runtime_peer=b,runtime_delta=["installations.py"],
                  literal_gaussian_graph=dict(roles=len(graph["initial"]),transfers=len(graph["moves"]),
                                              graph_sha256=digest(json.dumps(graph,separators=(",",":"),sort_keys=True).encode()),
                                              layout_sha256=digest(json.dumps(layout,separators=(",",":"),sort_keys=True).encode())),
                  candidate=candidate,peer=old_invoice,stopped_comparator=compare,period_and_weights=period,fixed_setup=setup)
    print(json.dumps(result,indent=2,default=str))


if __name__=="__main__":
    main()
