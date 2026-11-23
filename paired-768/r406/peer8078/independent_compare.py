"""Check the actual #8078 materialized runtime and two-tier invoice against #8076."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor, isqrt
from pathlib import Path
import runpy
from subprocess import check_output, run
import sys
import tarfile
from tempfile import TemporaryDirectory
from types import SimpleNamespace

PEER = "b72d3fa097d2521939f6b8536029da674648d863"
PRIOR = "d502eb21637717fe22fc16d4c4e3ede6ec59a106"
SOURCE = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
PARENT = "0618e75a22cec54d1651394ef83d088551b7f026"
ARCHIVE_SHA = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
GENERATOR = "research/frequency-weighted-native-multiplier"


def digest(data):
    return sha256(data).hexdigest()


def git(path, *args):
    return check_output(["git", "-C", path, *args])


def unique_entries(entries):
    result = {}
    for name, value in entries:
        assert name not in result, name
        result[name] = value
    return result


def metadata(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_entries)


def checkout(path, head, package):
    assert git(path, "rev-parse", "HEAD").decode().strip() == head
    assert not git(path, "status", "--porcelain")
    committed = {}
    for row in git(path, "ls-tree", "-r", head, "--", package).decode().splitlines():
        entry, name = row.split("\t")
        mode, kind, oid = entry.split()
        assert name not in committed and kind == "blob" and mode in ("100644", "100755")
        observed = (path/name).read_bytes()
        assert git(path, "cat-file", "blob", oid) == observed
        assert bool((path/name).stat().st_mode & 0o100) == (mode == "100755")
        committed[name] = dict(git_blob=oid, mode=mode, sha256=digest(observed))
    assert committed
    return committed


def archive_members(package):
    manifest = metadata(package/"PEER-SOURCE.json")
    assert manifest["head"] == "cbe847a953b971f9c6c5a0a6661e2008acd29086"
    assert manifest["archive_sha256"] == digest((package/"peer8057.tar.gz").read_bytes()) == ARCHIVE_SHA
    found = {}
    with tarfile.open(package/"peer8057.tar.gz") as bundle:
        for member in bundle:
            if member.isdir():
                continue
            assert member.isfile() and member.name not in found
            found[member.name] = digest(bundle.extractfile(member).read())
    assert len(found) == 88 and found == manifest["files_sha256"]
    return found


def install(package, staging, expanded):
    restore_file = "upstream_verify.py" if expanded else "verify.py"
    peer = runpy.run_path(str(package/restore_file))["restore"](staging/"peer")
    runpy.run_path(str(package/"prepare.py"))["materialize"](peer)
    if expanded:
        runpy.run_path(str(package/"retune.py"))["install"](peer, "340")
    runtime = staging/"runtime"
    run([sys.executable, "-IB", peer/"bootstrap.py", runtime], check=True)
    return peer, runtime


def inventory(directory):
    return {path.relative_to(directory).as_posix(): digest(path.read_bytes())
            for path in sorted(directory.rglob("*")) if path.is_file()}


def price_invoices(peer, runtime, receipt):
    sys.path.insert(0, str(runtime))
    from upstream import install as load_runtime
    load_runtime()
    source_path = peer.parent/"tiered-native-multiplier"/"source"
    sys.path.append(str(source_path))
    from activation import resource_receipt
    from band_product import precision
    from installations import ENTRY, TERMINAL, at_public
    from linear_geometry import public_shape
    from outer_budget import margins
    from outer_clock import financial_checks

    c_b, c_g = Q(4391986206293, 1 << 50), Q(17145637307, 1 << 42)
    d_b, d_g = Q(11239, 8192), Q(64939, 524288)
    stop, eta = Q(5, 10**18), Q(39, 10000)

    def ordinary(heights):
        prior, marks = Q(0), []
        for index, h in enumerate(heights):
            upper = min(eta, (249*(c_b-d_b/h)+prior)/250)
            if index == len(heights)-1:
                return upper, marks
            prior = Q(floor(upper*10**21)-1, 10**21)
            marks.append(prior)

    def positive(g):
        return c_g-d_g/g

    tiers = []
    for profile, name in ((ENTRY,"entry"), (TERMINAL,"terminal")):
        h, g, k = profile.rank_logs, profile.complex_log, profile.kappa
        assert max(value.bit_length() for value in (*h,g)) <= 20
        paid = k+stop
        ordinary_hi, cuts_rates = ordinary(h)
        pos = positive(g)
        assert min(ordinary_hi,pos)>paid
        strict, functional, funding = margins(k,stop/5,paid,pos)
        assert len(strict)==54 and len(functional)==4 and min(*strict,*functional,funding)>0
        lit = receipt[name]
        assert tuple(lit["ordinary_H"])==h and lit["numerical_H"]==g and Q(lit["kappa"])==k
        assert [Q(entry) for entry in lit["ordinary_rates"]]==[*cuts_rates,paid]
        assert Q(lit["gaussian_rate"])==pos
        assert (lit["signed"]["strict"],lit["signed"]["functional"])==(54,4)
        bound_b = (40+17+16384*sum(h)+25818582) if name=="entry" else (128+320*sum(h))
        bound_c = max(1+financial_checks()["early_log2_C_bound"],1602+220*g+bound_b)
        assert (lit["log2_B"],lit["log2_C"])==(bound_b,bound_c)
        stock = resource_receipt(SimpleNamespace(rank_logs=h,complex_log=g,eta=eta))
        amount = stock["public_exponent_A"]
        offset = stock["first_public_offset"]
        assert json.loads(json.dumps(stock))==lit["stock"]
        header = 2**amount+offset
        endpoint_precision=[]
        for shift in (4,5):
            extent=header//6+shift-amount
            shape = public_shape(header,extent)
            count=shape.count
            width=-(-extent//count)
            active=max(1,count//(1024*(header+1).bit_length()))
            rounds=20000*(count+1)*(width+2)**6+2*count
            rebuilt=(header+67+32768*active*(width+6)
                     +4*(rounds*(count+1)).bit_length()+(count+1).bit_length())
            exact=precision(header,extent,count)
            assert exact==rebuilt
            data=exact.to_bytes((exact.bit_length()+7)//8,"big")
            endpoint_precision.append(dict(width=width,
                precision_bits=exact.bit_length(),precision_sha256=digest(data)))
        assert max(item["width"] for item in endpoint_precision)==lit["geometry"]["largest_axis_width"]
        tiers.append(dict(kappa=k,heights=h,gaussian_height=g,ordinary_upper=ordinary_hi,
                          gaussian_upper=pos,smallest_strict=min(strict),
                          smallest_functional=min(functional),positive_margin=funding,
                          entry_floor_rates=cuts_rates,stock=stock,endpoint_precision=endpoint_precision,
                          ordinary_log2_B=bound_b,log2_C=bound_c))
    low, high = tiers
    assert ENTRY.kappa == Q(".00345") and TERMINAL.kappa == Q(".00389834")
    assert TERMINAL.rank_logs == (8192,36220,575705) and TERMINAL.complex_log==978582
    exponent,off = high["stock"]["public_exponent_A"],high["stock"]["first_public_offset"]
    assert (exponent,off)==(1599173,4)
    terminal_header=(1<<exponent)+off
    assert at_public(terminal_header-6) is ENTRY and at_public(terminal_header) is TERMINAL
    conversion=ceil((TERMINAL.kappa-ENTRY.kappa)*exponent)
    assert conversion==receipt["entry_price_surcharge"]==717
    total=1+max(low["log2_C"]+conversion,high["log2_C"])
    assert total==receipt["complete_log2_C"]==413727211
    assert receipt["native_setup_transition_upper"]<2**228 and receipt["log2_fixed_setup_upper"]==228

    # Exact older optimum at this full recurring cap. Use a different legal
    # allocation to show the Gaussian cap is approachable at G=978582.
    current=TERMINAL.kappa
    assert positive(978581)<current+stop<positive(978582)
    witness=(8192,36222,575703)
    upper,_=ordinary(witness)
    assert upper>positive(978582)
    allowed_sum=(total-1731-220*978583)//320
    assert allowed_sum==620116 and sum(witness)==620117
    scale=10**41
    root_lower=Q(isqrt(scale**2//250),scale)
    assert root_lower**2<Q(1,250)<(root_lower+Q(1,scale))**2
    relaxed_factor=(1+root_lower)**2
    # The minimum lower reciprocal envelope over h1>=8192 occurs at
    # h1=8192 because the derivative there is positive and increasing.
    assert Q(1,62500*8192**2)<relaxed_factor/(allowed_sum-8192)**2
    reciprocal=Q(1,62500*8192)+relaxed_factor/(allowed_sum-8192)
    upper_b=c_b*(1-Q(1,250**3))-Q(249,250)*d_b*reciprocal
    assert upper_b<current+stop
    cap=positive(978582)-stop
    assert cap==Q(6400248450982567016889284269,1641788158771200000000000000000)
    cap_stock = resource_receipt(SimpleNamespace(rank_logs=witness,complex_log=978582,eta=eta))
    assert all(h>cut+2 for h,cut in zip(witness[1:],cap_stock["binary_cuts"][:-1],strict=True))
    assert min(witness)>=8192 and max(*witness,978582).bit_length()<=20
    assert ceil((cap-ENTRY.kappa)*cap_stock["public_exponent_A"])+low["log2_C"] < high["log2_C"]
    strict_at_cap,functional_at_cap,positive_at_cap=margins(cap,stop/5,cap+stop,positive(978582))
    assert positive_at_cap==0 and min(*strict_at_cap,*functional_at_cap)>0
    return dict(tiers=tiers,complete_recurring_log2_C=total,entry_rate_conversion=conversion,
                exact_stopped_cap=cap,placement_within_cap=witness,cap_stock=cap_stock,
                witness_ordinary_reserve_over_gaussian=upper-positive(978582),
                next_g_ordinary_relaxed_shortfall=current+stop-upper_b)


def main():
    parser=ArgumentParser(description=__doc__)
    for name in ("peer","prior","source"):
        parser.add_argument(name,type=Path)
    args=parser.parse_args()
    candidate_dir="research/p104-expanded-budget-signed"
    prior_dir="research/p104-weighted-child-tariff"
    source_dir="research/p104-weighted-capped-allocation-490950"
    candidate=args.peer.resolve()/candidate_dir
    prior=args.prior.resolve()/prior_dir
    source=args.source.resolve()/source_dir
    candidate_files=checkout(args.peer,PEER,candidate_dir)
    assert len(candidate_files)==23
    checkout(args.prior,PRIOR,prior_dir)
    checkout(args.source,SOURCE,source_dir)
    body=git(args.peer,"cat-file","commit",PEER)
    assert [line for line in body.split(b"\n\n",1)[0].splitlines() if line.startswith(b"parent ")]==[b"parent "+PARENT.encode()]
    declarations=metadata(candidate/"SOURCES.json")
    assert declarations["base_commit"]==PARENT
    source_provenance={}
    for row in declarations["files"]:
        name=row["path"]
        oid=git(args.peer,"rev-parse",f"{PARENT}:{name}").decode().strip()
        assert oid==row["git_blob"]
        assert digest(git(args.peer,"cat-file","blob",oid))==row["sha256"]
        assert name not in source_provenance
        source_provenance[name]=oid
    for name in ("prepare.py","check_cutoff.py","check_stage_seam.py","check_ordinary_floor.py",
                 "PEER-SOURCE.json","peer8057.tar.gz"):
        assert (candidate/name).read_bytes()==(source/name).read_bytes()
    for suffix,name in (("verify.py","upstream_verify.py"),("PROOF.md","UPSTREAM-PROOF.md"),
                        ("README.md","UPSTREAM-README.md"),("RESULT.json","UPSTREAM-RESULT.json"),
                        ("VERIFY.json","UPSTREAM-VERIFY.json")):
        assert (candidate/name).read_bytes()==(source/suffix).read_bytes()
    members=archive_members(candidate)
    assert (candidate/"PEER-SOURCE.json").read_bytes()==(prior/"PEER-SOURCE.json").read_bytes()
    assert (candidate/"peer8057.tar.gz").read_bytes()==(prior/"peer8057.tar.gz").read_bytes()
    with TemporaryDirectory(prefix="independent-8078-") as work:
        root=Path(work)
        current_peer,current=install(candidate,root/"candidate",True)
        _,previous=install(prior,root/"prior",False)
        first, second=inventory(current),inventory(previous)
        assert first.keys()==second.keys() and len(first)==106
        changed=[key for key in first if first[key]!=second[key]]
        assert changed==["installations.py"]
        main=(current/"installations.py").read_text()
        assert main.replace(
            'TERMINAL = Profile((8192, 36220, 575705), 978582, Q(".00389834"))',
            'TERMINAL = Profile((8192, 111681, 524288), 509812, Q(".003898223617430"))',
        )==(previous/"installations.py").read_text()
        price=price_invoices(current_peer,current,metadata(candidate/"RESULT-340.json"))
    print(json.dumps(dict(head=PEER,comparable_to=PRIOR,source=SOURCE,source_parent=PARENT,
        committed=candidate_files,source_provenance=source_provenance,archive_sha256=ARCHIVE_SHA,
        archive_members=members,current_runtime_sha256=first,prior_runtime_sha256=second,
        changed_runtime_names=changed,changed_runtime_scope="One literal terminal profile line",
        signed_premises="Same installed native words, caller, chronology, restoration, precision, tape and recovery",
        reconstructed=price),indent=2,default=str))


if __name__=="__main__":
    main()
