"""Rebuild Round 403 arithmetic from the authenticated signed-source images."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from inspect import getsourcefile, unwrap
import json
from math import ceil, floor, isqrt
from pathlib import Path
import sys

TRIAL_O = F(4391986206293, 2**50)
TRIAL_G = F(17145637307, 2**42)
DEBIT_O_OLD = F(1405, 1024)
DEBIT_O_NEW = F(11239, 8192)
DEBIT_G = F(64939, 524288)
GUARD = F(5, 10**18)
ETA = F(39, 10000)
ENTRY = ((3000, 3080), 1024, F(".00345"))
R401 = ((8192, 124864, 524288), 490638, F(".0038982141226643"))
PRIOR = ((8192, 124863, 524288), 490639, F(".00389821412325"))
CANDIDATE = ((8192, 124649, 524288), 490950, F(".003898214283192"))
PEER_KAPPA = F(".00389821")
TERMINAL_CAP = 318292071
MIN_ORDINARY, MAX_HEIGHT, MIN_GAUSSIAN = 8192, 524288, 1024
ORD_CLOCK, GAUSS_CLOCK = 320, 220
RECURRING_FIXED, ORD_FIXED, SELECTOR = 1602, 128, 1
CLOCK_BASE = RECURRING_FIXED + ORD_FIXED + SELECTOR
ROOT = Path("original-runtime").resolve()
SIGNED_SOURCE = Path("peer-source/research/tiered-native-multiplier/source").resolve()


def power_bounds(base, exponent, bits=192):
    """Outward interval via repeated integer square roots and binary products."""
    assert base > 0 and exponent >= 0 and exponent.denominator.bit_count() == 1
    unit = 1 << bits
    integer, remainder = divmod(exponent.numerator, exponent.denominator)
    integer_power = F(base)**integer
    result = (floor(unit*integer_power), ceil(unit*integer_power))
    lower, upper = floor(unit*base), ceil(unit*base)
    for place in range(exponent.denominator.bit_length()-2, -1, -1):
        lower, upper = isqrt(lower*unit), isqrt(upper*unit-1)+1
        if remainder & (1 << place):
            result = (result[0]*lower//unit, -(-result[1]*upper//unit))
    return tuple(F(item, unit) for item in result)


def catalog(word):
    def histogram(ports):
        assert len({port.tag for port in ports}) == len(ports)
        return Counter(port.rank for port in ports)
    return histogram(word.targets), histogram(word.paid)


def mass_bounds(r, trial):
    grid = 2**112
    if r == F(1, 2):
        lower, upper = power_bounds(2, 1-trial, 112)
        return F(floor(grid/upper), grid), F(ceil(grid/lower), grid)
    return power_bounds(r, 1-trial, 112)


def checked_transport(target, paid, trial):
    t = {r: mass_bounds(r, trial) for r in target}
    p = {r: mass_bounds(r, trial) for r in paid}
    capacities = {r: n*t[r][0] for r, n in target.items()}
    demands = {r: n*p[r][1] for r, n in paid.items()}
    available, demand = sum(capacities.values()), sum(demands.values())
    assert available > demand
    assert 100*sum(n*p[r][0] for r, n in paid.items()) > 99*sum(n*t[r][1] for r, n in target.items())
    remaining = {r: c*demand/available for r, c in capacities.items()}
    shares = {}
    for r in sorted(demands, reverse=True):
        required = demands[r]
        for k in sorted(remaining, reverse=True):
            if 5*r > 4*k or not required:
                break
            mass = min(required, remaining[k])
            if mass:
                shares[r, k] = mass/demands[r]
                remaining[k] -= mass
                required -= mass
        assert required == 0
    assert not any(remaining.values())
    for r in paid:
        assert sum(q for (source, _), q in shares.items() if source == r) == 1
    for k in target:
        load = sum(demands[r]*q for (r, receiver), q in shares.items() if receiver == k)
        assert 0 < load <= capacities[k]
    return (available-demand)/available, shares


def boundary(target, paid, shares, trial):
    terms = [(paid[r]*q*r, power_bounds(F(k, r), trial)) for (r, k), q in shares.items()]
    psi = tuple(sum(weight*(bounds[i]-1)/trial for weight, bounds in terms) for i in (0, 1))
    assert psi[1] >= psi[0] > 0
    total_axes = sum(r*n for r, n in target.items())
    return psi, tuple(10*total_axes/((1-trial)*end) for end in reversed(psi))


def enclosure(interval, scale=10**18):
    return [F(floor(interval[0]*scale), scale), F(ceil(interval[1]*scale), scale)]


def ordinary_factor(lower):
    rounding = F(1, 2**128)
    fixed = (F(47, 20)*F(256, 255)*F(4097, 4096)*F(257, 256)
             * (1+F(64, lower)+rounding) / ((1-F(10, lower))*(1-rounding)**3))
    return tuple(fixed*end for end in power_bounds(1024*134*lower, TRIAL_O))


def gaussian_factor(scale, fringe):
    rounding = F(1, 2**128)
    lower = 1874
    fixed = (1+rounding)*(1+F(4*258, scale))/(1-rounding)**4
    return tuple(fixed*end*(1+edge/lower+rounding)
                 for end, edge in zip(power_bounds(scale*lower, TRIAL_G), fringe, strict=True))


def transport_and_factors():
    sys.path.insert(0, str(ROOT))
    from upstream import HERE, install
    install()
    from strong_binary import graph, caller
    from strong_complex import load_changed, word
    from tagged_sources import binary_ports
    from raw_binary_stage import binary_word

    raw = binary_ports(graph(), caller())
    t, p = catalog(raw)
    assert raw.ambient == 134
    margin, shares = checked_transport(t, p, TRIAL_O)
    installed = binary_word()
    assert (Counter(installed.targets), Counter(installed.paid), installed.cells) == (t, p, shares)
    assert (t.total(), p.total(), len(shares)) == (18906,104652,24)
    assert tuple(sum(r*n for r,n in labels.items()) for labels in (t,p)) == (286098,284592)
    psi_o, fringe_o = boundary(t, p, shares, TRIAL_O)
    assert psi_o[0] > 1 and fringe_o[1] < 64
    assert power_bounds(18960, 1-TRIAL_O)[0] > 1024
    assert F(75, 32)/F(47, 20) == F(375, 376)

    factor_o = ordinary_factor(18960)
    crossed = power_bounds(2, DEBIT_O_NEW)
    finer = power_bounds(2, F(22477, 16384))
    ordinary_reserve = crossed[0]-factor_o[1]
    finer_shortfall = factor_o[0]-finer[1]
    obsolete_floor = ordinary_factor(32768)
    old_allowance = power_bounds(2, DEBIT_O_OLD)
    assert ordinary_reserve > F("0.000062662376093595")
    assert finer_shortfall > F("0.000046832527238212")
    assert factor_o[1] < crossed[0] < old_allowance[0] < old_allowance[1] < obsolete_floor[0]
    assert obsolete_floor[1] < power_bounds(2, F(703, 512))[0]

    t0, p0 = catalog(word(*load_changed(HERE/"inputs")))
    t1, p1 = (Counter({2*r: n for r, n in s.items()}) for s in (t0, p0))
    p0[1] -= 1008
    p0[F(1, 2)] += 2016
    assert (t0.total(), p0.total(), t1.total(), p1.total()) == (52608, 282576, 52608, 281568)
    targets = Counter({r: 5*t0[r]+451*t1[r] for r in t0.keys() | t1.keys()})
    paid = Counter({r: 5*p0[r]+451*p1[r] for r in p0.keys() | p1.keys()})
    margin_g, shares_g = checked_transport(targets, paid, TRIAL_G)
    assert (targets.total(), paid.total(), len(shares_g), sum(r*n for r, n in targets.items())) == (
        23989248, 128400048, 51, 677246016
    )
    psi_g, fringe_g = boundary(targets, paid, shares_g, TRIAL_G)
    assert psi_g[0] > F("926899828.8291") and fringe_g[1] < F("7.335168")
    weights = (5, 451)
    typed = {(a, r, b, k): q*weights[b]*receiver[k]/targets[k]
             for (r, k), q in shares_g.items()
             for a, sender in enumerate((p0, p1)) if r in sender
             for b, receiver in enumerate((t0, t1)) if k in receiver}
    assert len(typed) == 88 and typed[1,112,1,258]/t1[258] == F(1,624)
    for a, sender in enumerate((p0, p1)):
        for r in sender:
            assert sum(q for (kind, grade, _, _), q in typed.items() if (kind, grade) == (a, r)) == 1
    paid_upper = {r: mass_bounds(r, TRIAL_G)[1] for r in paid}
    for b, receiver in enumerate((t0, t1)):
        for k, count in receiver.items():
            demand = sum(weights[a]*(p0, p1)[a][r]*q*paid_upper[r]
                         for (a, r, kind, grade), q in typed.items() if (kind, grade) == (b, k))
            assert 0 < demand <= weights[b]*count*mass_bounds(k, TRIAL_G)[0]
    factor_g = gaussian_factor(1724*306//2, fringe_g)
    allowance_g = power_bounds(2, DEBIT_G)
    gaussian_reserve = allowance_g[0]-factor_g[1]
    gaussian_one_tick_shortfall = factor_g[0]-power_bounds(2, DEBIT_G-F(1, 524288))[1]
    assert gaussian_reserve > F("0.000000684423")
    assert gaussian_one_tick_shortfall > 0
    assert gaussian_factor(2048*306//2, fringe_g)[0] > allowance_g[1]

    def mark_shares(values):
        return sha256("".join(f"{r} {k} {q}\n" for (r, k), q in sorted(values.items())).encode()).hexdigest()

    grade_actions = (2**20)*256 + (2**8)*256*8 + 32*(len(targets)+len(paid)+2)**2 + 2**12
    assert grade_actions == 269057152 < 2**32
    source_digests = {producer.__name__: sha256(Path(getsourcefile(unwrap(producer))).read_bytes()).hexdigest()
                      for producer in (graph, caller, word, binary_ports, binary_word)}
    return {
        "actual_operator_function_source_sha256": source_digests,
        "k7_target_by_label": dict(t), "k7_paid_by_label": dict(p),
        "k7_cells": len(shares), "k7_cell_sha256": mark_shares(shares),
        "k7_mass_margin": margin, "k7_fringe": enclosure(fringe_o), "k7_boundary": enclosure(psi_o),
        "k7_floor": 18960, "ordinary_factor": enclosure(factor_o),
        "ordinary_allowance": enclosure(crossed), "ordinary_reserve": enclosure((ordinary_reserve, ordinary_reserve)),
        "finer_upper_envelope_shortfall": enclosure((finer_shortfall, finer_shortfall)),
        "obsolete_32768_floor_factor": enclosure(obsolete_floor),
        "gaussian_margin": margin_g, "gaussian_cells": len(shares_g), "gaussian_typed_cells": len(typed),
        "gaussian_cells_sha256": mark_shares(shares_g), "gaussian_factor": enclosure(factor_g),
        "gaussian_allowance": enclosure(allowance_g), "gaussian_geometry": [1874, 1724, 306],
        "gaussian_directed_reserve_lower": enclosure((gaussian_reserve,gaussian_reserve))[0],
        "gaussian_one_tick_shortfall_lower": enclosure((gaussian_one_tick_shortfall,gaussian_one_tick_shortfall))[0],
        "setup_grade_actions": grade_actions
    }


def ordinary_rates(heights, debit):
    prior_rate = F(0)
    implemented = []
    for i, height in enumerate(heights):
        upper = min(ETA, (249*(TRIAL_O-debit/height)+prior_rate)/250)
        if i == len(heights)-1:
            return upper, implemented
        prior_rate = F(floor(upper*10**21)-1, 10**21)
        implemented.append(prior_rate)


def gaussian_rate(height):
    return TRIAL_G - DEBIT_G/height


def compute_precision(public, extent, count):
    """Rebuild the signed coefficient working precision for exact first-header spans."""
    block_width = ceil(F(extent, count))
    active = max(1, count//(1024*(public+1).bit_length()))
    rounds = 20000*(count+1)*(block_width+2)**6 + 2*count
    remainder = (67 + 32768*active*(block_width+6)
                 + 4*(rounds*(count+1)).bit_length() + (count+1).bit_length())
    return public+remainder


def value_hash(value):
    return sha256(value.to_bytes((value.bit_length()+7)//8, byteorder="big")).hexdigest()


def precision_and_tape(exponent, offset, height, rank_count):
    s = exponent+1
    minimum_window = 128*(4*(s+1)+6)
    axis_degree = (6*minimum_window-1).bit_length()
    assert exponent-axis_degree >= (6*exponent).bit_length()
    count_exponent = exponent-axis_degree
    count = 1 << count_exponent
    public = (1 << exponent)+offset
    b, residue = divmod(public, 6)
    assert residue == 0
    lo_extent, hi_extent = (b+constant-exponent for constant in (4, 5))
    assert lo_extent > 0 and hi_extent-lo_extent == 1
    assert (
        (lo_extent//minimum_window).bit_length()
        == (hi_extent//minimum_window).bit_length() == count_exponent+1
    )
    precision_lo = compute_precision(public, lo_extent, count)
    precision_hi = compute_precision(public, hi_extent, count)
    axis_width = max(ceil(F(lo_extent, count)), ceil(F(hi_extent, count)))
    assert axis_width == ceil(F(1 << axis_degree, 6))
    assert public < precision_lo <= precision_hi < 1 << (exponent+1)
    assert 17**16*10**(18*16) < 1 << 1182
    assert 400 + 1182 + 9 + 2 < RECURRING_FIXED
    # The inherited fixed-alphabet scans include both coefficient scales and
    # the same widening, compensation, padded payload, returns and scrubbing.
    local = 25*32 + 32*32 + 4*(rank_count+1) + 128
    first_stripe = s//2-2-local-4*(s+128).bit_length()
    cofinal_stripe = 31*s//64-3-local
    job_log = 1024*height+(rank_count+1).bit_length()
    assert first_stripe > 1024 and cofinal_stripe > 1024
    assert (12000*(34*s+9)).bit_length() <= s-2
    return dict(initial_s=s, minimum_width=minimum_window,
                log2_axis_count=count_exponent, largest_axis_width=axis_width,
                first_extent_bits_minus_b=4-exponent, last_extent_bits_minus_b=5-exponent,
                private_clock_log2_upper=1024*(axis_width+s+67)+s,
                actual_dense_root_entry_log2=2*axis_width,
                coefficient_precision_bit_lengths=[precision_lo.bit_length(), precision_hi.bit_length()],
                coefficient_precision_endpoints_sha256=[value_hash(precision_lo), value_hash(precision_hi)],
                stage_and_outer_fixed_log_overhead=local, retimed_first_stripe_margin=first_stripe,
                retimed_all_size_margin_floor=cofinal_stripe, absolute_log2_private_control_envelope=job_log,
                live_storage_multiplier=F(31,5), padded_input_storage_multiplier=F(1488,5))


def invoice(profile, signed_margins, debit=DEBIT_O_NEW, *, include_precision=True):
    heights, gaussian_height, kappa = profile
    ordinary, floors = ordinary_rates(heights, debit)
    gaussian = gaussian_rate(gaussian_height)
    stopped = kappa+GUARD
    chain = (F(0), *floors, stopped)
    assert all(a < b for a,b in zip(chain, chain[1:]))
    assert stopped < min(ordinary,gaussian)
    strict, functional, paid = signed_margins(kappa, GUARD/5, stopped, gaussian)
    assert (len(strict), len(functional)) == (54, 4) and min(*strict,*functional,paid) > 0

    minima = [ceil(F(250*(h+64),249)) for h in heights]
    cuts = [minima[0]]
    for floor_value, height in zip(minima[1:], heights[1:], strict=True):
        cuts.append(max(floor_value, cuts[-1]+height+64))
    assert all(cuts[i]+2 < heights[i+1] for i in range(len(cuts)-1))
    required = cuts[-1]+gaussian_height+102
    initial_s = next(s for s in range(max(512,required), required+500)
                     if s-7*(s-1).bit_length() >= required)
    after_jump = (1 << (initial_s-1).bit_length())+1
    assert after_jump-7*(after_jump-1).bit_length() >= required
    exponent = initial_s-1
    offset = (-pow(2,exponent,6)) % 6
    assert offset in (2,4) and (pow(2,exponent,6)+offset-6)%6 == 0
    assert (1 << exponent)+offset-6 < 1 << exponent

    max_height = max(*heights, gaussian_height)
    if min(heights) >= MIN_ORDINARY:
        assert 100+len(heights) <= ORD_FIXED
        assert 2660000*32 < 2**30 and 2660000*33 < 2*2660000*32
        ordinary_bill, surcharges = ORD_FIXED+ORD_CLOCK*sum(heights), []
    else:
        assert heights == ENTRY[0]
        degree = 20*253
        costs = [20*24+degree*padding+2+term*(term-1).bit_length()
                 for padding, term in ((4,2*degree),(259,258*degree))]
        surcharges = [max(0,cost-944*h) for cost,h in zip(costs, heights, strict=True)]
        ordinary_bill = 57+16384*sum(heights)+sum(surcharges)
    gaussian_bill = GAUSS_CLOCK*gaussian_height
    recurring = max(84500001, RECURRING_FIXED+gaussian_bill+ordinary_bill)
    tape = (precision_and_tape(exponent,offset,max_height,len(heights)) if include_precision else None)
    return dict(heights=heights, gaussian_height=gaussian_height, kappa=kappa,
                stopped_target=stopped, ordinary_ceiling=ordinary, gaussian_ceiling=gaussian,
                intermediate_rates=floors, ordinary_margin=ordinary-stopped, gaussian_margin=gaussian-stopped,
                signed_strict=strict, signed_functional=functional, signed_paid=paid,
                strict_min=min(strict), functional_min=min(functional), cuts=cuts,
                activation_exponent=exponent, activation_offset=offset, activation_width_required=required,
                first_header_precision_and_tape=tape, ordinary_log2_B=ordinary_bill,
                gaussian_height_log_charge=gaussian_bill, log2_C_before_entry_and_selector=recurring,
                entry_ordinary_surcharges=surcharges, max_native_height=max_height)


def add_entry_and_selector(entry, terminal):
    premium = ceil((terminal["kappa"]-entry["kappa"])*terminal["activation_exponent"])
    terminal.update(entry_conversion_bits=premium,
                    select_entry_after_conversion=entry["log2_C_before_entry_and_selector"]+premium)
    terminal["complete_log2_C"] = SELECTOR+max(terminal["select_entry_after_conversion"],
                                               terminal["log2_C_before_entry_and_selector"])


def discrete_slice(gaussian_height, cap, debit):
    # Use discrete one-bit paid marginal exchanges for an independent upper
    # bound. The maximum gain on any legal increase is strictly less than
    # the minimum loss on any legal decrease at the funded extremal vector.
    # Concavity makes both inequalities stronger with additional units.
    funded_total = (cap-CLOCK_BASE-GAUSS_CLOCK*gaussian_height)//ORD_CLOCK
    heights = (MIN_ORDINARY, funded_total-MIN_ORDINARY-MAX_HEIGHT, MAX_HEIGHT)
    assert MIN_ORDINARY < heights[1] < MAX_HEIGHT
    assert CLOCK_BASE+ORD_CLOCK*sum(heights)+GAUSS_CLOCK*gaussian_height <= cap
    assert CLOCK_BASE+ORD_CLOCK*(1+sum(heights))+GAUSS_CLOCK*gaussian_height > cap
    weights = (F(1, 250**2), F(1, 250), F(1))
    multiplier = F(249,250)
    ideal = multiplier*sum(w*(TRIAL_O-debit/h) for w,h in zip(weights,heights,strict=True))
    step_up = [w/(h*(h+1)) for h,w in zip(heights,weights,strict=True) if h < MAX_HEIGHT]
    step_down = [w/(h*(h-1)) for h,w in zip(heights,weights,strict=True) if h > MIN_ORDINARY]
    exchange_gap = multiplier*debit*(min(step_down)-max(step_up))
    actual, ticks = ordinary_rates(heights,debit)
    assert min(step_down) > max(step_up) > 0
    assert 0 < ideal-actual < exchange_gap
    return dict(heights=heights, cap=cap, gaussian_height=gaussian_height,
                retained_intermediate_ticks=ticks, gaussian_ceiling=gaussian_rate(gaussian_height),
                ordinary_ceiling=actual, relaxed_ordinary_ceiling=ideal,
                maximum_relaxed_gain_per_add=max(step_up)*multiplier*debit,
                minimum_relaxed_cost_per_drop=min(step_down)*multiplier*debit,
                rounding_loss=ideal-actual, alternate_loss_floor=exchange_gap)


def complete_profiles():
    sys.path.insert(0, str(SIGNED_SOURCE))
    from outer_budget import margins
    from outer_clock import financial_checks

    assert financial_checks()["early_log2_C_bound"]+1 == 84500001
    entry, prior, candidate = [invoice(profile, margins) for profile in (ENTRY, PRIOR, CANDIDATE)]
    add_entry_and_selector(entry, prior)
    add_entry_and_selector(entry, candidate)
    assert entry["log2_C_before_entry_and_selector"] == 125660241
    assert entry["entry_ordinary_surcharges"] == [0,25818582]
    assert candidate["entry_conversion_bits"] == prior["entry_conversion_bits"] == 515
    assert candidate["ordinary_log2_B"]-prior["ordinary_log2_B"] == -68480
    assert candidate["gaussian_height_log_charge"]-prior["gaussian_height_log_charge"] == 68420
    assert prior["complete_log2_C"] == TERMINAL_CAP and candidate["complete_log2_C"] == 318292011
    assert candidate["max_native_height"] == prior["max_native_height"] == MAX_HEIGHT

    fixed_prior_ceiling = min(prior["ordinary_ceiling"],prior["gaussian_ceiling"])-GUARD
    assert prior["gaussian_ceiling"] < prior["ordinary_ceiling"]
    assert fixed_prior_ceiling == F(6417673946269416969859534601,1646311296204800000000000000000)
    strict_gap = candidate["kappa"]-fixed_prior_ceiling
    assert strict_gap == F(263176469852170186999,1646311296204800000000000000000)
    historical_slice = discrete_slice(R401[1],318292451,DEBIT_O_OLD)
    historical_ceiling = historical_slice["ordinary_ceiling"]-GUARD
    assert gaussian_rate(R401[1]-1) < historical_slice["ordinary_ceiling"] < gaussian_rate(R401[1])
    assert historical_ceiling == F(523209442801521766233321100177,134217728000000000000000000000000)
    assert prior["kappa"] > historical_ceiling

    h = candidate["gaussian_height"]
    assert MIN_GAUSSIAN < h-1 < h+1 < MAX_HEIGHT
    lower, crossing, higher = (discrete_slice(g,TERMINAL_CAP,DEBIT_O_NEW) for g in (h-1,h,h+1))
    assert lower["heights"] == crossing["heights"] == candidate["heights"]
    assert crossing["ordinary_ceiling"] == candidate["ordinary_ceiling"]
    assert lower["gaussian_ceiling"] < crossing["ordinary_ceiling"] < crossing["gaussian_ceiling"]
    assert higher["ordinary_ceiling"] < candidate["stopped_target"]
    assert 0 < lower["gaussian_ceiling"] < candidate["stopped_target"]
    # All smaller Gaussian caps have a lower rate. All larger heights have an
    # ordinary feasible region contained in the crossing slice because the
    # Gaussian charge is positive. Full entry/tape feasibility at the bound
    # is checked at an exact endpoint and stays valid just below it.
    ceiling = crossing["ordinary_ceiling"]-GUARD
    assert ceiling == F(523209464347189355219919950737,134217728000000000000000000000000)
    endpoint = (candidate["heights"],h,ceiling)
    strict, functional, paid = margins(ceiling,GUARD/5,ceiling+GUARD,crossing["gaussian_ceiling"])
    assert min(*strict,*functional,paid) > 0
    assert (ceiling+GUARD) >= candidate["stopped_target"] > candidate["intermediate_rates"][-1]
    assert ceil((ceiling-entry["kappa"])*candidate["activation_exponent"]) == candidate["entry_conversion_bits"]
    assert candidate["complete_log2_C"] <= TERMINAL_CAP
    assert ceiling > candidate["kappa"]

    width = 1 << 38
    register = 2*width+2
    scalar = 2**16*(register+4)*(7*register+9)+8*2**16*(register+4)**2
    lookup = 4*width*2**68*8*512*128
    setup = (2**68+1)*(lookup+scalar+2**120)*2**32
    assert scalar < 2**110 and lookup == 2**127 and setup < 2**228
    assert len(ENTRY[0])+len(CANDIDATE[0])+2 == 7 and MAX_HEIGHT.bit_length() == 20
    return dict(entry=entry, prior_terminal=prior, new_terminal=candidate, invoice_cap=TERMINAL_CAP,
                prior_fixed_ceiling=fixed_prior_ceiling, strict_separation_from_prior_fixed_ceiling=strict_gap,
                old_family_ceiling=historical_ceiling, old_slice=historical_slice, new_family_ceiling=ceiling,
                booked_gain_vs_prior=candidate["kappa"]-prior["kappa"], booked_gain_vs_external=candidate["kappa"]-PEER_KAPPA,
                reserve_below_new_supremum=ceiling-candidate["kappa"], endpoint_profile=endpoint,
                endpoint_signed_min=min(*strict,*functional,paid), slices=[lower,crossing,higher],
                lower_adjacent_gaussian_raw_shortfall=candidate["kappa"]-lower["gaussian_ceiling"],
                lower_adjacent_gaussian_stopped_shortfall=candidate["stopped_target"]-lower["gaussian_ceiling"],
                higher_adjacent_ordinary_raw_shortfall=candidate["kappa"]-higher["ordinary_ceiling"],
                higher_adjacent_ordinary_stopped_shortfall=candidate["stopped_target"]-higher["ordinary_ceiling"],
                conservative_fixed_native_setup=setup, setup_bit_bound=setup.bit_length())


if __name__ == "__main__":
    print(json.dumps({"arithmetic": complete_profiles(), "factors": transport_and_factors()},
                     default=str, indent=2, sort_keys=True))
