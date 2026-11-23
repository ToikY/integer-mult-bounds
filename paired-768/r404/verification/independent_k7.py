"""Independent Round 404 reconstruction using pinned source and inherited Round 403 primitives."""

from hashlib import sha256
import json
from math import ceil
from pathlib import Path
import runpy
import sys

previous = Path("../../round403/independent/independent_invoice.py")
assert sha256(previous.read_bytes()).hexdigest() == "7b06abca74493ca369601c426574e60ef15f5a5c8c76b4cfea2a8387fe32557c"
sealed = json.loads(Path("../../round403/independent/REPLAY-RECEIPT.json").read_bytes())
tools = runpy.run_path(str(previous))
F = tools["F"]
entry_profile = tools["ENTRY"]
old_profile = tools["CANDIDATE"]
c = tools["TRIAL_O"]
gaussian_rate = tools["gaussian_rate"]
power_bounds = tools["power_bounds"]
ordinary_rates = tools["ordinary_rates"]
signed_invoice = tools["invoice"]
complete_selector = tools["add_entry_and_selector"]

TARGET = F(".003898219753506")
OLD_DEBIT = F(11239, 8192)
DEBIT = F(11204, 8192)
CAP = 318292011
HEIGHTS = (8192, 117168, 524288)
G = 501831
GUARD = F(5, 10**18)
L = 18960
A = 134
DELTA = F(1, 2**128)


def interval_decimal(pair, digits=18):
    return tools["enclosure"](pair, 10**digits)


def ordinary_factor(lower, suffix):
    fringe = 1 + F(suffix, lower) + DELTA
    exterior = 1 - F(10, lower)
    multiplier = F(47, 20) * F(256, 255) * F(4097, 4096) * F(1028, 1024)
    return tuple(multiplier*x*fringe/(exterior*(1-DELTA)**3)
                 for x in power_bounds(1024*A*lower, c))


def independent_k7():
    # Also recompute the inherited Gaussian factors with the old vetted
    # interval method. Reopen the actual ordinary word independently below.
    factors = tools["transport_and_factors"]()
    from raw_binary_stage import binary_word
    word = binary_word()
    targets = tools["Counter"](word.targets)
    paid = tools["Counter"](word.paid)
    shares = word.cells
    assert len(shares) == 24 and targets.total() == 18906 and paid.total() == 104652
    assert 0 < c < F(1,250) and all(5*r <= 4*k for r,k in shares)
    assert max(targets) <= A and min(paid) >= 1

    # Expand the grade shares by the actual paid counts. Independently round
    # k^c and r^c in opposite directions before dividing.
    endpoints = {k: power_bounds(k, c) for k in targets.keys() | paid.keys()}
    psi = tuple(sum(paid[r]*prob*r*(endpoints[k][i]/endpoints[r][1-i]-1)/c
                    for (r,k),prob in shares.items()) for i in (0,1))
    axes = sum(k*n for k,n in targets.items())
    t = 1 - c
    suffix_coefficient = tuple(10*axes/(t*end) for end in reversed(psi))
    assert axes == 286098 and psi[0] > 386067
    assert 0 < suffix_coefficient[0] < suffix_coefficient[1] < F("7.439580926465596639") < 8
    assert sum(shares[r,k] for r,k in shares) == len(paid)
    for r in paid:
        assert sum(prob for (source,_),prob in shares.items() if source == r) == 1
    for k, n in targets.items():
        available = n * power_bounds(k, t)[0]
        demanded = sum(paid[r]*prob*power_bounds(r,t)[1]
                       for (r,dest),prob in shares.items() if dest == k)
        assert 0 < demanded <= available

    # For x in [e,e+2) and y in [d,d+2), the seam is r*x = k*y.
    # The rounded columns e-8 and d-8 give a residual in
    # [8k-10r,10k-8r], hence in [0,10k) by r/k <= 4/5.
    assert all(8*k - 10*r >= 0 and 10*k - 8*r < 10*k for r,k in shares)
    assert L % 2 == 0 and 24*(L+2) < 25*L
    assert power_bounds(L,t)[0] > 1024

    # The exponents below prove all H >= 1024, the larger ordinary
    # activation floor is 3000. U grows with H and U/N is bounded above
    # by 1/(1024A). The relative floor error 2*1024A/N shrinks with H.
    h = 1024
    n = 1 << h
    v = n**6
    u = 2*(n//(2048*A))
    ratio = max(F(k,r) for r,k in shares)
    assert ratio*L < u
    assert ratio*(F(1,1024*A)+F(2,n)) < 1
    assert F(4*max(targets),1024*A) < 1
    assert u <= n and F(2*1024*A,n) < DELTA
    assert F(1,t*power_bounds(L,t)[0])+F(2,n**5) < 2  # sum m[e] < 2 V

    # The continuous terminal measure is V L^c Psi. The integral mass
    # contributes 10 sum(k)/(t Psi L), and the +2U stock rounding pays
    # a separate suffix-birth term 20 U sum(k)/(V L^c Psi).
    assert L > 1 and psi[0] > 1 and axes < 2**25
    birth_bound = F(20*u*axes,v)/psi[0]
    assert birth_bound < F(2**30,n**5)

    # Conservatively count three intersections per label pair per band.
    # Two terminal/externally normalized sides, integer floor/ceiling loss
    # below 2, and every physical or virtual axis length <= N.
    assert paid.total() < 2**20 and targets.total() < 2**17
    intersections_per_band = 3*paid.total()*targets.total()
    rounded_per_n2 = 2*(2*intersections_per_band + 2*paid.total())
    assert rounded_per_n2 < 2**46

    # Endpoint reciprocal range is [1/(258N),1]. Perturbed endpoints
    # stay above 1/(512N), where sqrt has derivative <= sqrt(512N)/2.
    # The stated 2*(4*sqrt(512N))^61 endpoint bound is < 2^(397+31H).
    # Multiply by at most 2 endpoints, 1/t < 2, sum both sides, estimate
    # all (at most N) bands and their intersections, and allow N axes
    # per unit of mass. V cancels from the normalized error.
    assert F(1,258*n) - F(1,2**(64*(h+1))) > F(1,512*n)
    assert (c.denominator.bit_length()-1) <= 60 and 1/t < 2
    assert 1+61*(2+F(9+h,2)) < 397+31*h
    assert 8*(intersections_per_band + paid.total()) < 2**42
    grid_exponent = 397+31*h - 64*(h+1) + 42 + 2*h

    # K=N^82 time slots. D[e] <= (e/L)^77 and Q D[e]+1<N^77
    # at both activated scales. With Q<2^19 and M<=N, the loss
    # 2VQM N^77/K per birth time divided by V is <2^20/N^4.
    assert F(6,5)**4 > 2 and F(6,5)**77 > 2**19
    assert paid.total() < 2**19
    assert F(2**19,(1024*A*L)**77) + F(1,n**77) < 1
    errors = (30-5*h, 46-4*h, grid_exponent, 20-4*h)
    assert max(errors) < -132 and 4*F(1,2**132) < DELTA
    assert (1-F(10,L))*psi[0] > 1
    assert 2**12*2*targets.total() < n**2
    assert F(1,n) < DELTA

    new = ordinary_factor(L, 8)
    old = ordinary_factor(L, 64)
    historical = ordinary_factor(32768, 64)
    allowance = power_bounds(2, DEBIT)
    one_tick_down = power_bounds(2, F(11203,8192))
    reserve = allowance[0]-new[1]
    finer_failure = new[0]-one_tick_down[1]
    old_failure = old[0]-allowance[1]
    assert new[1] < F("2.580517225032310287")
    assert reserve > F(".0000277614405947")
    assert finer_failure > F(".000190576182764755")
    assert old_failure > 0
    assert old[1] < power_bounds(2, OLD_DEBIT)[0]
    assert historical[0] > power_bounds(2, F(1405,1024))[1]
    assert historical[1] < power_bounds(2, F(703,512))[0]
    assert F(75,32)/F(47,20) == F(375,376)
    assert F(1,1-F(375,376)) == 376
    return dict(k7_target_labels=targets.total(), k7_paid_labels=paid.total(),
                k7_share_count=len(shares), k7_axes=axes, k7_shares_sha256=factors["k7_cell_sha256"],
                psi_interval=interval_decimal(psi), suffix_coefficient_interval=interval_decimal(suffix_coefficient),
                ordinary_factor=interval_decimal(new), ordinary_allowance=interval_decimal(allowance),
                next_finer_allowance=interval_decimal(one_tick_down), old_factor=interval_decimal(old),
                historical_32768_factor=interval_decimal(historical),
                booking_reserve_low=interval_decimal((reserve,reserve))[0],
                adjacent_shortfall_low=interval_decimal((finer_failure,finer_failure))[0],
                old_envelope_shortfall_low=interval_decimal((old_failure,old_failure))[0],
                normalized_error_exponents_at_h1024=dict(zip(
                    ("separate_suffix_birth","integer_mass","grid_mass","delay_end"),errors,strict=True)),
                normalized_error_exponent_slopes=(-5,-4,-31,-4),
                binary_floor=L, child_contraction=F(375,376), repeated_child_factor=376,
                gaussian_factor=factors["gaussian_factor"],
                gaussian_allowance=factors["gaussian_allowance"],
                gaussian_directed_reserve_lower=factors["gaussian_directed_reserve_lower"],
                gaussian_one_tick_shortfall_lower=factors["gaussian_one_tick_shortfall_lower"],
                gaussian_cells_sha256=factors["gaussian_cells_sha256"],
                setup_grade_actions=factors["setup_grade_actions"])


def tangent_slice(g, debit):
    # The actual constraints include the entry selector, finite control and
    # terminal costs. Retain the necessary terminal inequality here.
    budget = (CAP-1731-220*g)//320
    low, high = 8192, 524288
    vector = (low, budget-low-high, high)
    assert low < vector[1] < high and sum(vector) == budget
    weights = (F(1,62500), F(1,250), F(1))
    slope = tuple(w/b**2 for w,b in zip(weights,vector,strict=True))
    assert 0 < slope[0] < slope[1] < slope[2]
    # If b' = b + d, d0 >= 0, d2 <= 0 and sum(d) <= 0.
    # Sum a_i(-d_i) decomposes as the nonnegative sum
    # (a1-a0)d0 + (a2-a1)(-d2) + a1(-sum(d)). Every distinct
    # integer vector makes at least one of those units >=1.
    minimum_lost_tangent = F(249,250)*debit*min(
        slope[1]-slope[0], slope[2]-slope[1], slope[1])
    upper = F(249,250)*sum(w*(c-debit/b) for w,b in zip(weights,vector,strict=True))
    exact, ticks = ordinary_rates(vector, debit)
    assert 0 < upper-exact < minimum_lost_tangent
    assert max(*ticks,exact) < F(39,10000)
    return dict(heights=vector, gaussian_height=g, ordinary_ceiling=exact,
                gaussian_ceiling=gaussian_rate(g), relative_rounding_loss=upper-exact,
                alternate_minimum_loss=minimum_lost_tangent, intermediate_rates=ticks,
                max_funded_sum=budget, recurring_terminal_charge=1731+320*budget+220*g)


def capped_family(g, debit, installed, margins):
    lower, crossing, upper = (tangent_slice(h,debit) for h in (g-1,g,g+1))
    assert crossing["heights"] == installed["heights"]
    assert crossing["ordinary_ceiling"] == installed["ordinary_ceiling"]
    assert lower["gaussian_ceiling"] < crossing["ordinary_ceiling"] < crossing["gaussian_ceiling"]
    assert upper["ordinary_ceiling"] < installed["stopped_target"]
    assert lower["gaussian_ceiling"] < installed["stopped_target"]
    assert installed["complete_log2_C"] <= CAP
    endpoint = crossing["ordinary_ceiling"]-GUARD
    assert endpoint > installed["kappa"]
    strict, functional, pay = margins(endpoint,GUARD/5,endpoint+GUARD, crossing["gaussian_ceiling"])
    assert min(*strict,*functional,pay) > 0
    assert endpoint+GUARD > crossing["intermediate_rates"][-1]
    assert ceil((endpoint-entry_profile[2])*installed["activation_exponent"]) == installed["entry_conversion_bits"]
    # Gaussian is increasing, and greater g shrinks the available ordinary
    # sums. The endpoint margin and integral conversion bit stay valid
    # along approaches to the strictly stopped endpoint from below.
    return dict(stopped_supremum=endpoint, slices=(lower,crossing,upper),
                endpoint_signed_min=min(*strict,*functional,pay),
                lower_gaussian_stopped_shortfall=installed["stopped_target"]-lower["gaussian_ceiling"],
                higher_ordinary_stopped_shortfall=installed["stopped_target"]-upper["ordinary_ceiling"],
                booked_rate_reserve=endpoint-installed["kappa"])


def installed_profiles():
    sys.path.insert(0, str(tools["SIGNED_SOURCE"]))
    from outer_budget import margins
    from outer_clock import financial_checks
    assert financial_checks()["early_log2_C_bound"]+1 == 84500001
    old_entry = signed_invoice(entry_profile, margins, OLD_DEBIT)
    entry = signed_invoice(entry_profile, margins, DEBIT)
    prior = signed_invoice(old_profile, margins, OLD_DEBIT)
    new = signed_invoice((HEIGHTS,G,TARGET), margins, DEBIT)
    complete_selector(old_entry, prior)
    complete_selector(entry, new)
    for item, reference in ((old_entry,sealed["entry"]),(prior,sealed["terminal"])):
        actual = json.loads(json.dumps(item,default=str))
        assert actual == reference, (set(actual)-set(reference), set(reference)-set(actual))
    previous_ceiling = capped_family(old_profile[1], OLD_DEBIT, prior, margins)
    new_ceiling = capped_family(G, DEBIT, new, margins)
    assert previous_ceiling["stopped_supremum"] == F(sealed["new_family_ceiling"])
    assert new_ceiling["stopped_supremum"] == F(523210198560303585338978849681,134217728000000000000000000000000)
    assert TARGET-previous_ceiling["stopped_supremum"] == F(734213105999148080049263,134217728000000000000000000000000)
    assert entry["log2_C_before_entry_and_selector"] == 125660241
    assert entry["entry_ordinary_surcharges"] == [0,25818582]
    assert new["cuts"] == [8290,125522,649874]
    assert new["complete_log2_C"] == 318291911
    assert new["ordinary_log2_B"] == 207887488
    assert new["ordinary_log2_B"]-prior["ordinary_log2_B"] == -2393920
    assert new["gaussian_height_log_charge"]-prior["gaussian_height_log_charge"] == 2393820
    assert new["activation_exponent"] == 1151953 and new["activation_offset"] == 4
    assert new["entry_conversion_bits"] == 517 and new["max_native_height"] == 524288
    assert new["first_header_precision_and_tape"]["absolute_log2_private_control_envelope"] == 536870915
    width = 1 << 38
    register = 2*width+2
    arithmetic = 2**16*(register+4)*(7*register+9) + 8*2**16*(register+4)**2
    lookup = 4*width*2**68*8*512*128
    setup = (2**68+1)*(lookup+arithmetic+2**120)*2**32
    assert arithmetic < 2**110 and lookup == 2**127 and setup < 2**228
    assert setup == sealed["serial_setup"]["all_setup"]
    assert len(entry["heights"])+len(new["heights"])+2 == 7 and new["max_native_height"].bit_length() == 20
    return dict(entry=entry, prior_entry=old_entry, terminal=new, prior_terminal=prior, cap=CAP,
                old_family=previous_ceiling, new_family=new_ceiling,
                separation_from_old_ceiling=TARGET-previous_ceiling["stopped_supremum"],
                gain_over_prior=TARGET-prior["kappa"], gain_over_external=TARGET-F(".00389821"),
                setup_bound=setup, setup_lookup=lookup, setup_arithmetic=arithmetic,
                setup_exponent=228, previously_sealed_invoice_fields_matched=True)


if __name__ == "__main__":
    print(json.dumps(dict(factors=independent_k7(), arithmetic=installed_profiles()),
                     indent=2, sort_keys=True, default=str))
