"""Derive the period bound and paid invoices from exact runtime inputs."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from math import ceil, floor, isqrt
from pathlib import Path
import json
import sys

parser = ArgumentParser(description=__doc__)
parser.add_argument("runtime", type=Path)
parser.add_argument("signed_source", type=Path)
parser.add_argument("published_result", type=Path)
args = parser.parse_args()
sys.path.insert(0, str(args.runtime.resolve()))
sys.path.append(str(args.signed_source.resolve()))
from upstream import install

install()
from band_product import precision, prepare_native
from installations import ENTRY, TERMINAL, at_public, activation
from linear_geometry import public_shape
from outer_budget import margins as source_margins
from ordinary_carrier import stage_for_width_log
from staged_carriers import entrance_logs

C_B, C_G = Q(4391986206293, 2**50), Q(17145637307, 2**42)
D_B, D_G, D_OLD = Q(11239,8192), Q(64934,524288), Q(64939,524288)
g, eta, tick = Q(1,10**18), Q(39,10000), Q(1,10**21)
delta = Q(1,2**128)
grid = 1 << 224


def down(x):
    return Q(floor(x*grid),grid)


def up(x):
    return Q(ceil(x*grid),grid)


@cache
def log_unit(m):
    """Sum the atanh series and bound its positive geometric remainder."""
    assert 1 <= m <= 2
    z = (m-1)/(m+1)
    lo = hi = Q(0)
    term = z
    for j in range(96):
        increment = 2*term/(2*j+1)
        lo += down(increment)
        hi += up(increment)
        term *= z*z
    return lo, hi + up(2*term/((2*96+1)*(1-z*z)))


def power(base, exp):
    m, b = Q(base), 0
    assert m >= 1 and exp > 0
    while m >= 2:
        m /= 2
        b += 1
    p, q = log_unit(m)
    l2, u2 = log_unit(Q(2))
    lo, hi = down(exp*(p+b*l2)), up(exp*(q+b*u2))
    assert 0 <= lo <= hi < 1
    # For (0<=t<1), all omitted successive term ratios are <=1/81.
    bounds = []
    for t in (lo, hi):
        low_sum = high_sum = a = b = Q(1)
        for n in range(1, 80):
            a, b = down(a*t/n), up(b*t/n)
            low_sum += a
            high_sum += b
        bounds.append((low_sum, high_sum+up((b*t/80)*Q(81,80))))
    return bounds[0][0], bounds[1][1]


def check_period():
    recipe = prepare_native(TERMINAL)[-1]
    assert recipe.ambient == 306 and recipe.trial == C_G and recipe.rank_log >= 1024
    targets, paid, edges = recipe.targets.histogram, recipe.paid.histogram, recipe.cells
    assert len(edges) == 51 and len(recipe.typed_cells()) == 88
    assert min(paid) == Q(1,2) and max(targets) == 258
    assert all(k in targets and r in paid and p > 0 and 5*r <= 4*k and k/r <= 516
               for (r,k),p in edges.items())
    assert all(sum(p for (rr,k),p in edges.items() if rr == r) == 1 for r in paid)
    psi = [Q(0), Q(0)]
    for (r,k), share in edges.items():
        interval = power(Q(k)/r,C_G)
        for i,end in enumerate(interval):
            psi[i] += paid[r]*share*r*(end-1)/C_G
    axes = sum(k*n for k,n in targets.items())
    L, scale = 1874, 1724*recipe.ambient//2
    x0, sharp = Q(scale,4*max(targets)), Q(257,256)
    assert axes == 677246016 and scale == 263772
    assert 255 < x0 < 256 and Q(256)/x0 < sharp < 1+1/x0
    assert 65536*1032 < 257*263772
    M = 1 << 1024
    U = 2*(M//(2*scale))
    assert max(targets)*(U-8) < Q(M,4)
    assert U > 516*L and delta*U >= 5160
    assert scale*U >= (1-delta)*M and 516*(U+2) < M
    assert delta*M >= 1 and M % 4 == 0
    # The admitted H>=1024 doubles M at each step, never decreasing U.
    # All relative loss bounds become smaller, and q<=M for integral s'>=1.
    assert 2**46 < delta*M**4/16 and 2**20 < delta*M**4/16
    assert 2**30 < delta*M**5/16
    assert 2*52608 < M  # rounded complete exterior tickets below M^91
    fringe = [10*axes/((1-C_G)*rate) for rate in reversed(psi)]
    assert psi[0] > Q("926899828.8291") and fringe[1] < Q("7.335168")
    scale_term = power(scale*L,C_G)
    common = [(1+delta)*p*(1+f/L+delta)/(1-delta)**4
              for p,f in zip(scale_term,fringe,strict=True)]
    factor = [sharp*x for x in common]
    old_factor = [(1+1/x0)*x for x in common]
    book = power(2,D_G)
    adjacent = power(2,D_G-Q(1,524288))
    prior_book = power(2,D_OLD)
    reserve = book[0]-factor[1]
    shortfall = factor[0]-adjacent[1]
    assert reserve > Q(".000000232515772047")
    assert shortfall > Q(".000001208067461857")
    assert old_factor[0] > book[1] and old_factor[1] < prior_book[0]
    assert (1-delta)**4 < 1 < 1+delta
    ordinary = (Q(47,20)*Q(256,255)*Q(4097,4096)*Q(1028,1024)
                *(1+Q(64,18960)+delta)/((1-Q(10,18960))*(1-delta)**3))
    ordinary *= power(1024*134*18960,C_B)[1]
    assert ordinary < 2*power(2,D_B-1)[0] and Q(75,32)/Q(47,20)==Q(375,376)
    return dict(
        x_min=x0, x_below_256_upper=Q(256)/x0, x_above_256_upper=sharp,
        actual_period="4*ceil(M/(4*s'))", exterior_dyadic_delta=delta,
        outward_psi=psi, outward_fringe=fringe, axes=axes, gaussian_factor=factor,
        old_factor=old_factor, allowed=book, adjacent=adjacent,
        reserve_lower=reserve, adjacent_shortfall_lower=shortfall,
        old_factor_shortfall_lower=old_factor[0]-book[1], ordinary_factor_upper=ordinary,
        installed_edges=len(edges), installed_typed_edges=len(recipe.typed_cells()))


def rate_steps(heights):
    bank = Q(0)
    cuts = []
    for h in heights:
        cap = min(eta, (bank+249*(C_B-D_B/h))/250)
        cuts.append(cap)
        bank = (floor(cap/tick)-1)*tick
    return cuts[-1], [(floor(x/tick)-1)*tick for x in cuts[:-1]]


def signed(k, ordinary, gaussian):
    a, b, q = k+4*g, k+5*g, k+3*g
    epsilon, beta = 1-g, 1-3*g
    sigma, tau = 1-b, 1-a
    assert sigma < tau
    inside, leaf = tau, sigma+g*(1-sigma)
    bridge = 1-(q+a)/2
    xi = epsilon*(1+q)-Q(3,32)+g
    tail = [epsilon*q, a, g+q*beta, g+a*beta, g+beta, Q(3,32)+xi-epsilon,
            xi+Q(1,2)-epsilon, epsilon, 1-(epsilon+beta+48-128+2)]
    strict = [
        ordinary-a, b-a, q, b-q, a-q, g, 1-g, epsilon*b-a,
        1-inside-q, 1-leaf-q, bridge-tau, bridge-sigma, bridge-inside,
        1-q-bridge, 1-q-leaf, epsilon, g, xi-Q(1,2), epsilon-xi,
        beta, epsilon-beta, 3*g, 3-2*xi-g/10-beta, 3-2*xi-beta,
        9*g/10, g, g/10, 1-beta-g, 1-beta-2*g, 80-beta, g,
        epsilon-a, Q(1,32)-b, Q(2**45-7**16), Q(2), 2-xi, Q(5),
        3*g, 3*g, g, tail[2]-tail[0], g, k-Q(".001730970419199163702738"),
        g, Q(11,2),
    ] + [x-k for x in tail]
    functional = [3*g, beta*Q(997,1000), 79-epsilon-beta, beta*Q(249,250)]
    margin = gaussian-b
    assert len(strict)==54 and len(functional)==4 and min(*strict,*functional) > 0
    assert (strict, functional, margin) == source_margins(k,g,ordinary,gaussian)
    return strict,functional,margin


def logceil(n):
    return (n-1).bit_length()


def stock(heights,hg):
    cuts = []
    for h in heights:
        cuts.append(max(ceil(Q(250*(h+64),249)), cuts[-1]+h+64 if cuts else 0))
    goal = cuts[-1]+hg+102
    s = next(s for s in range(goal,goal+4096) if
             s-7*logceil(s) >= goal and (1<<logceil(s))+1-7*(logceil(s)+1) >= goal)
    assert all(h > c+2 for h,c in zip(heights[1:],cuts[:-1],strict=True))
    assert (12000*(34*s+9)).bit_length() <= s-2
    assert all(68+83*h<92*h<105*h and 92*h<448*h and (700*h).bit_length()<=h
               and (872*(4*h+1)).bit_length()<=h and (30*1024*h+120).bit_length()<=h-1
               for h in (*heights,hg))
    fixed = 25*32+32*32+4*(len(heights)+1)+128
    whole = 1024*max(hg,*heights)+(len(heights)+1).bit_length()
    tables = 2**21*(s+1)
    assert 64+8*(whole+1)+64*s+8*(tables+1)<(s+1)**8
    assert (12*(128*(s+130)*(s+1)**8+64)).bit_length()<=s-2
    assert (1200*(64*(128*s*s+s)+2*s+128)).bit_length()<=s-2
    assert (2000*(34*s+108)).bit_length()<=s-2 and 33**9<2*32**9
    assert 2*8*256*80*22*3<2**25 and 8*71*22*3*256*128*2<2**32
    first = s//2-2-fixed-4*(s+128).bit_length()
    cofinal = 31*s//64-3-fixed
    assert 64*(fixed+1028) <= 31*s and min(first,cofinal)>1024
    assert eta<Q(1,250) and Q("6.2")*48 == Q("297.6")
    exponent = s-1
    return dict(cuts=cuts, A=exponent, offset=(-pow(2,exponent,6))%6, s=s, private=whole,
                fixed=fixed, first_stripe_margin=first, cofinal_stripe_margin=cofinal)


def invoice(profile, published):
    assert profile.eta == eta and profile.positive_stop_denominator==g.denominator
    h, hg, k = profile.rank_logs, profile.complex_log, profile.kappa
    b = k+5*g
    ordinary, banks = rate_steps(h)
    gaussian = C_G-D_G/hg
    assert gaussian>b and ordinary>b
    strict, functional, positive_margin = signed(k,b,gaussian)
    assert positive_margin > 0
    resources = stock(h,hg)
    assert resources["A"] == activation(profile)
    assert resources["cuts"] == list(entrance_logs(h))
    for i,c in enumerate(resources["cuts"],1):
        assert [stage_for_width_log(c+d,len(h),h) for d in (-1,0,1)] == [i-1,i,i]
    A, offset = resources["A"], resources["offset"]
    public = (1<<A)+offset
    assert public%6==0 and (public-6)<(1<<A)<=public
    precision_rows = []
    for shift in (4,5):
        extent = public//6+shift-A
        shape = public_shape(public,extent)
        cap = extent//(128*(4*(A+2)+6))
        n = 1<<(cap.bit_length()-1)
        assert n == shape.count
        ell = -(-extent//n)
        active = max(1,n//(1024*(public+1).bit_length()))
        steps = 20000*(n+1)*(ell+2)**6+2*n
        exact = public+67+32768*active*(ell+6)+4*(steps*(n+1)).bit_length()+(n+1).bit_length()
        assert exact==precision(public,extent,n)
        encoded = exact.to_bytes((exact.bit_length()+7)//8,"big")
        precision_rows.append(dict(bits=exact.bit_length(),sha256=sha256(encoded).hexdigest(),
                                   width=ell,log2_axis_count=n.bit_length()-1))
    if len(h)==2:
        bound_B = 40+17+16384*sum(h)+25818582
    else:
        assert all(H>=8192 for H in h) and Q(39,10000)>Q(1,258)
        assert 2660000*32<2**30
        bound_B = 128+320*sum(h)
    bound_C = max(84500001, 1602+220*hg+bound_B)
    # Published results are checked only after independent derivation.
    assert [*h]==published["ordinary_H"] and hg==published["numerical_H"] and k==Q(published["kappa"])
    assert [*banks,b] == [Q(x) for x in published["ordinary_rates"]]
    assert gaussian == Q(published["gaussian_rate"])
    assert (bound_B,bound_C)==(published["log2_B"],published["log2_C"])
    ph=published["stock"]
    assert (ph["public_exponent_A"],ph["first_public_offset"],ph["absolute_log2_private_control_envelope"]) == (A,offset,resources["private"])
    assert max(x["width"] for x in precision_rows) == published["geometry"]["largest_axis_width"]
    return dict(heights=h,G=hg,k=k,paid_rate=b,ordinary=ordinary,ordinary_banks=banks,
                positive=gaussian,strict=strict,functional=functional,positive_margin=positive_margin,
                stock=resources,recovery=precision_rows,B=bound_B,C=bound_C)


def relaxed_ordinary(M):
    t = 10**41
    r = Q(isqrt(t*t//250),t)
    assert r**2<Q(1,250)<(r+Q(1,t))**2
    assert Q(1,62500*8192**2) < (1+r)**2/(M-8192)**2
    reciprocal = Q(1,62500*8192)+(1+r)**2/(M-8192)
    return (1-Q(1,250**3))*C_B-Q(249,250)*D_B*reciprocal


def cap_and_controls(entry, terminal, recurring):
    old_rate, old_G, old_C = Q(".00389834"), 978582, 413727211
    witness = (8192,36222,575703)
    old_gaussian = C_G-D_OLD/old_G
    assert (old_C-1731-220*(old_G+1))//320==620116
    assert C_G-D_OLD/(old_G-1)<old_rate+5*g < old_gaussian < rate_steps(witness)[0]
    assert relaxed_ordinary(620116)<old_rate+5*g
    old_ceiling = old_gaussian-5*g
    assert old_ceiling==Q(6400248450982567016889284269,1641788158771200000000000000000)
    assert terminal["k"] > old_ceiling and terminal["k"]-old_rate == Q(39,10**13)
    wstock=stock(witness,old_G)
    assert 1731+320*sum(witness)+220*old_G==old_C
    assert entry["C"]+ceil((old_ceiling-entry["k"])*wstock["A"]) < old_C-1
    assert signed(old_ceiling,old_ceiling+5*g,old_gaussian)[-1]==0
    h, G, paid = terminal["heights"],terminal["G"],terminal["paid_rate"]
    assert sum(h)==620117 and relaxed_ordinary(sum(h)-1)<paid
    assert floor(D_G/(C_G-paid))+1 == G
    assert C_G-D_G/(G-1)<paid and C_G-D_OLD/G<paid
    assert rate_steps((h[0],h[1]-1,h[2]))[0]<paid and rate_steps((*h[:2],h[2]-1))[0]<paid
    assert recurring==1731+320*sum(h)+220*G and old_C-recurring==9900
    assert C_G + D_G/G > C_G > terminal["positive"]  # sign-inverted debit violates spending
    return dict(old_cap=old_ceiling,gain_over_exact_old_cap=terminal["k"]-old_ceiling,
                old_witness=witness, old_witness_stock=wstock,
                old_shortfall_at_next_gaussian_height=old_rate+5*g-relaxed_ordinary(620116),
                controls=dict(G_minus_one=paid-(C_G-D_G/(G-1)), old_debit=paid-(C_G-D_OLD/G),
                              smaller_ordinary_sum=paid-relaxed_ordinary(620116),
                              flipped_debit_excess=(C_G+D_G/G)-terminal["positive"]))


def setup():
    width=2**38
    register=2*width+2
    local=2**16*(register+4)*(7*register+9)+8*2**16*(register+4)**2
    lookup=8*4*width*2**68*512*128
    assert local<2**110 and lookup==2**127
    all_setup=(2**68+1)*(local+lookup+2**120)*2**32
    assert all_setup<2**228
    rec=prepare_native(TERMINAL)[-1]
    roles=sum(len(x.targets)+len(x.paid) for x in rec.types())
    native=prepare_native(ENTRY)[-1]
    grades=len(native.paid.histogram)+len(native.targets.histogram)
    actions=2**20*256+2**8*256*8+32*(grades+2)**2+2**12
    assert roles<2**20 and grades<2**8 and actions<2**32 and len(ENTRY.rank_logs)+len(TERMINAL.rank_logs)+2==7
    assert max(x.bit_length() for x in (*ENTRY.rank_logs,ENTRY.complex_log,*TERMINAL.rank_logs,TERMINAL.complex_log))<=20
    return dict(total=all_setup, ceiling_exponent=228, grade_actions=actions, roles=roles, grades=grades)


period=check_period()
published=json.loads(args.published_result.read_text())
entry, terminal=(invoice(tier,published[name]) for name,tier in (("entry",ENTRY),("terminal",TERMINAL)))
exponent,offset=terminal["stock"]["A"],terminal["stock"]["offset"]
first_header=(1<<exponent)+offset
assert (exponent,offset)==(1599128,2) and terminal["stock"]["private"]==1002021891
assert at_public(first_header-6) is ENTRY and at_public(first_header) is TERMINAL
premium=ceil((terminal["k"]-entry["k"])*exponent)
recurring=1+max(entry["C"]+premium,terminal["C"],84500001)
assert premium==717 and recurring==413717311
assert (published["entry_price_surcharge"],published["complete_log2_C"])==(premium,recurring)
control=cap_and_controls(entry,terminal,recurring)
setup_cost=setup()
assert (setup_cost["total"],setup_cost["grade_actions"])==(published["native_setup_transition_upper"],published["native_setup_grade_actions"])
print(json.dumps(dict(period=period,entry=entry,terminal=terminal,premium=premium,recurring=recurring,
                      cap_and_controls=control,setup=setup_cost), indent=2, default=str))
