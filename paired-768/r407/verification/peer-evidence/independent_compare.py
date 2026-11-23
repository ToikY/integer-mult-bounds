"""Reconstruct #8081’s exact signed prices, setup charge and fixed-cap crossing."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor, isqrt
from pathlib import Path
import runpy
from subprocess import run
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

HEAD = "510113821774bb27f7ddaad4e8b94837a1c2cf52"
PRIOR = "b72d3fa097d2521939f6b8536029da674648d863"
SOURCE = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
PARENT = "0618e75a22cec54d1651394ef83d088551b7f026"
PACKAGE = "research/p104-expanded-budget-25bit"
PRIOR_PACKAGE = "research/p104-expanded-budget-signed"
SOURCE_PACKAGE = "research/p104-weighted-capped-allocation-490950"
HELPER_SHA = "2f856b9364c20675a9f288aa2779adeaa9a6b6b470672a00b7a0e46bc28523bc"


def installation(package, staging):
    source = runpy.run_path(str(package/"upstream_verify.py"))["restore"](staging/"peer")
    runpy.run_path(str(package/"prepare.py"))["materialize"](source)
    runpy.run_path(str(package/"retune.py"))["install"](source, "460")
    runtime = staging/"runtime"
    run([sys.executable, "-IB", source/"bootstrap.py", runtime], check=True)
    return source, runtime


def invoice(source, runtime, receipt):
    sys.path.insert(0,str(runtime))
    from upstream import install
    install()
    sys.path.append(str(source.parent/"tiered-native-multiplier"/"source"))
    from activation import resource_receipt
    from band_product import precision
    from installations import ENTRY, TERMINAL, at_public
    from linear_geometry import public_shape
    from outer_budget import margins
    from outer_clock import financial_checks

    c_b,c_g = Q(4391986206293,2**50),Q(17145637307,2**42)
    d_b,d_g = Q(11239,8192),Q(64939,524288)
    stop,eta = Q(5,10**18),Q(39,10000)
    heights = tuple(value for p in (ENTRY,TERMINAL) for value in (*p.rank_logs,p.complex_log))
    assert len(heights)==7 and min(heights)>=1024 and max(heights)<2**25

    def ordinary(values):
        prior, floors = Q(0), []
        for i,height in enumerate(values):
            rate = min(eta,(249*(c_b-d_b/height)+prior)/250)
            if i==len(values)-1:
                return rate,floors
            prior = Q(floor(rate*10**21)-1,10**21)
            floors.append(prior)

    def positive(height):
        return c_g-d_g/height

    tiers = []
    for name,profile in (("entry",ENTRY),("terminal",TERMINAL)):
        h,g,k = profile.rank_logs,profile.complex_log,profile.kappa
        encodings = (k.numerator,k.denominator,profile.eta.numerator,
                     profile.eta.denominator,profile.positive_stop_denominator)
        assert max(abs(v).bit_length() for v in encodings)<=128
        assert profile.positive_stop_denominator>0
        stock = resource_receipt(SimpleNamespace(rank_logs=h,complex_log=g,eta=eta))
        assert all(height>cut+2 for height,cut in zip(h[1:],stock["binary_cuts"][:-1],strict=True))
        literal = receipt[name]
        assert (h,g,k)==(tuple(literal["ordinary_H"]),literal["numerical_H"],Q(literal["kappa"]))
        assert json.loads(json.dumps(stock))==literal["stock"]
        limit,rounded = ordinary(h)
        gauss = positive(g)
        assert min(limit,gauss)>k+stop
        assert [Q(value) for value in literal["ordinary_rates"]]==[*rounded,k+stop]
        assert Q(literal["gaussian_rate"])==gauss
        strict,functional,paid = margins(k,stop/5,k+stop,gauss)
        assert (len(strict),len(functional))==(54,4)
        assert min(*strict,*functional,paid)>0
        assert (literal["signed"]["strict"],literal["signed"]["functional"])==(54,4)
        entry_cost = 40+17+16384*sum(h)+25818582
        bound_b = entry_cost if name=="entry" else 128+320*sum(h)
        bound_c = max(1+financial_checks()["early_log2_C_bound"],1602+220*g+bound_b)
        assert (bound_b,bound_c)==(literal["log2_B"],literal["log2_C"])
        exponent,offset = stock["public_exponent_A"],stock["first_public_offset"]
        public = (1<<exponent)+offset
        endpoint_precision = []
        for shift in (4,5):
            extent = public//6+shift-exponent
            count = public_shape(public,extent).count
            width = -(-extent//count)
            cycles = 20000*(count+1)*(width+2)**6+2*count
            activity = max(1,count//(1024*(public+1).bit_length()))
            exact = precision(public,extent,count)
            expected = (public+67+32768*activity*(width+6)
                       +4*(cycles*(count+1)).bit_length()+(count+1).bit_length())
            assert exact==expected
            endpoint_precision.append(dict(width=width,bits=exact.bit_length(),
                digest=sha256(exact.to_bytes((exact.bit_length()+7)//8,"big")).hexdigest()))
        assert max(row["width"] for row in endpoint_precision)==literal["geometry"]["largest_axis_width"]
        tiers.append(dict(name=name,kappa=k,heights=h,gaussian_height=g,ordinary_upper=limit,
                          gaussian_upper=gauss,positive_margin=paid,smallest_strict=min(strict),
                          smallest_functional=min(functional),stock=stock,ordinary_log2_B=bound_b,
                          recurring_before_conversion=bound_c,endpoint_precision=endpoint_precision,
                          largest_scalar_encoding_bits=max(abs(v).bit_length() for v in encodings)))

    early,late = tiers
    assert TERMINAL.kappa==Q(".00389846") and TERMINAL.rank_logs==(8192,38102,604362)
    g = TERMINAL.complex_log
    assert g==18845936
    exponent,offset = late["stock"]["public_exponent_A"],late["stock"]["first_public_offset"]
    assert (exponent,offset)==(19497094,2)
    public = (1<<exponent)+offset
    assert at_public(public-6) is ENTRY and at_public(public) is TERMINAL
    conversion = ceil((TERMINAL.kappa-ENTRY.kappa)*exponent)
    whole = 1+max(early["recurring_before_conversion"]+conversion,late["recurring_before_conversion"])
    assert (conversion,whole)==(8744,4354317571)
    assert whole==receipt["complete_log2_C"] and conversion==receipt["entry_price_surcharge"]

    # Same installed word and charged receipt, under the exact current cap.
    booked = TERMINAL.kappa
    cap = positive(g)-stop
    assert positive(g-1)<booked+stop<positive(g)<late["ordinary_upper"]
    assert cap==Q(15407802515941573408769828489,3952279237427200000000000000000)
    assert ceil((cap-ENTRY.kappa)*exponent)==conversion
    at_strict,at_functional,at_positive = margins(cap,stop/5,cap+stop,positive(g))
    assert min(*at_strict,*at_functional)>0 and at_positive==0
    smaller = (whole-1731-220*(g+1))//320
    assert smaller==650655
    scale=10**41
    root_bound=Q(isqrt(scale**2//250),scale)
    assert root_bound**2<Q(1,250)<(root_bound+Q(1,scale))**2
    envelope=(1+root_bound)**2
    assert Q(1,62500*8192**2)<envelope/(smaller-8192)**2
    relaxed=c_b*(1-Q(1,250**3))-Q(249,250)*d_b*(Q(1,62500*8192)+envelope/(smaller-8192))
    assert relaxed<booked+stop

    n,w = 2**68+2**40,2**38
    message_charge = 2*2048*(2**25+1)+7*2**24
    assert message_charge==137556398080<2**40
    assert 92*(2**25-1)<2**32 and 1024*(2**25-1)<2**35<w
    assert (1<<g).bit_length()==18845937<=2**25<w
    s,h = 4*w*n,2*w+2
    lookup=8*s*512*128
    arithmetic=2**16*(h+4)*(7*h+9)+8*2**16*(h+4)**2
    setup=(n+1)*(lookup+arithmetic+2**120)*2**32
    assert setup==receipt["native_setup_transition_upper"]<2**228
    return dict(tiers=tiers,entry_conversion=conversion,complete_recurring_log2_C=whole,
                exact_stopped_cap=cap,old_ordinary_shortfall_at_next_g=booked+stop-relaxed,
                height_guard_bits=25,scalar_guard_bits=128,fixed_setup=dict(indexed=n,lookup=lookup,
                    arithmetic=arithmetic,carrier_and_scalar_actions=message_charge,transitions=setup))


def main():
    parser=ArgumentParser(description=__doc__)
    for name in ("current","prior","source","peer_checker"):
        parser.add_argument(name,type=Path)
    args=parser.parse_args()
    assert sha256(args.peer_checker.read_bytes()).hexdigest()==HELPER_SHA
    prior=runpy.run_path(str(args.peer_checker))
    verify,read,git = (prior[key] for key in ("checkout","metadata","git"))
    p=args.current.resolve()/PACKAGE
    previous=args.prior.resolve()/PRIOR_PACKAGE
    base=args.source.resolve()/SOURCE_PACKAGE
    committed=verify(args.current,HEAD,PACKAGE)
    assert len(committed)==31
    verify(args.prior,PRIOR,PRIOR_PACKAGE)
    verify(args.source,SOURCE,SOURCE_PACKAGE)
    assert run(["git","-C",args.current,"merge-base","--is-ancestor",PARENT,HEAD]).returncode==0
    pins=read(p/"SOURCE-8072-PINS.json")
    assert pins["head"]==SOURCE and len(pins["files"])==10
    remap={"verify.py":"upstream_verify.py", **{name:"UPSTREAM-"+name for name in ("PROOF.md","NOTICE.md","README.md")}}
    for name,oid in pins["files"].items():
        item=Path(name).relative_to(SOURCE_PACKAGE).as_posix()
        assert git(args.source,"rev-parse",f"{SOURCE}:{name}").decode().strip()==oid
        assert (base/item).read_bytes()==(p/remap.get(item,item)).read_bytes()
    for name in ("check_cutoff.py","PEER-SOURCE.json","peer8057.tar.gz","prepare.py"):
        assert (p/name).read_bytes()==(previous/name).read_bytes()
    members=prior["archive_members"](p)
    with TemporaryDirectory(prefix="independent-8081-") as scratch:
        root=Path(scratch)
        source,runtime=installation(p,root/"current")
        _,old_runtime=prior["install"](previous,root/"last",True)
        hashes,prior_hashes=(prior["inventory"](item) for item in (runtime,old_runtime))
        assert hashes.keys()==prior_hashes.keys() and len(hashes)==106
        changes=[name for name in hashes if hashes[name]!=prior_hashes[name]]
        assert changes==["installations.py"]
        line='TERMINAL = Profile((8192, 38102, 604362), 18845936, Q(".00389846"))'
        prior_line='TERMINAL = Profile((8192, 36220, 575705), 978582, Q(".00389834"))'
        assert (runtime/"installations.py").read_text().replace(line,prior_line)==(old_runtime/"installations.py").read_text()
        result=invoice(source,runtime,read(p/"RESULT-460.json"))
    print(json.dumps(dict(head=HEAD,compared_head=PRIOR,exact_source=SOURCE,approved_history_parent=PARENT,
              committed=committed,archive_members=members,current_runtime=hashes,previous_runtime=prior_hashes,
              actual_runtime_delta=changes,independent=result),indent=2,default=str))


if __name__=="__main__":
    main()
