"""Rebuild Round 402 arithmetic from the authenticated signed-source images."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
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
OLD = ((8192, 124864, 524288), 490638, F(".0038982141226643"))
NEW = ((8192, 124863, 524288), 490639, F(".00389821412325"))
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
    assert (t.total(), p.total(), len(shares), sum(r*n for r, n in p.items())) == (18906, 104652, 24, 284592)
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
    assert allowance_g[0]-factor_g[1] > F("0.000000684423")
    assert factor_g[0] > power_bounds(2, DEBIT_G-F(1, 524288))[1]
    assert gaussian_factor(2048*306//2, fringe_g)[0] > allowance_g[1]

    def mark_shares(values):
        return sha256("".join(f"{r} {k} {q}\n" for (r, k), q in sorted(values.items())).encode()).hexdigest()

    grade_actions = (2**20)*256 + (2**8)*256*8 + 32*(len(targets)+len(paid)+2)**2 + 2**12
    assert grade_actions == 269057152 < 2**32
    return {
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


def complete_profiles():
    sys.path.insert(0, str(SIGNED_SOURCE))
    from outer_budget import margins

    def invoice(profile, debit):
        heights, gaussian_height, kappa = profile
        ordinary, floors = ordinary_rates(heights, debit)
        gaussian = TRIAL_G-DEBIT_G/gaussian_height
        rate_chain = [0, *floors, kappa+GUARD]
        assert all(a < b for a,b in zip(rate_chain, rate_chain[1:]))
        assert ordinary > kappa+GUARD and gaussian > kappa+GUARD
        strict, functional, paid = margins(kappa, F(1, 10**18), kappa+GUARD, gaussian)
        assert (len(strict), len(functional)) == (54, 4) and min(*strict, *functional, paid) > 0

        minima = [ceil(F(250*(h+64),249)) for h in heights]
        cuts = [minima[0]]
        for floor_value, height in zip(minima[1:], heights[1:], strict=True):
            cuts.append(max(floor_value, cuts[-1]+height+64))
        required = cuts[-1]+gaussian_height+102
        s = next(width for width in range(max(512,required), required+500)
                 if width-7*(width-1).bit_length() >= required)
        assert 2**(s-1).bit_length()+1-7*((s-1).bit_length()+1) >= required
        exponent, offset = s-1, (-pow(2,s-1,6))%6
        assert (pow(2, exponent, 6)+offset)%6 == 0 and offset in (2,4)

        if min(heights) >= 8192:
            ordinary_bill, surcharge = 128+320*sum(heights), []
        else:
            assert heights == ENTRY[0]
            degree = 20*253
            costs = [20*24+degree*padding+2+term*(term-1).bit_length()
                     for padding, term in ((4,2*degree),(259,258*degree))]
            surcharge = [max(0,cost-944*h) for cost,h in zip(costs, heights, strict=True)]
            ordinary_bill = 57+16384*sum(heights)+sum(surcharge)
        gaussian_bill = 220*gaussian_height
        recurring = max(84500001, 1602+gaussian_bill+ordinary_bill)
        envelope = 1024*max(*heights, gaussian_height)+(len(heights)+1).bit_length()
        return dict(heights=heights, gaussian_height=gaussian_height, kappa=kappa,
                    ordinary_ceiling=ordinary, gaussian_ceiling=gaussian, intermediate_rates=floors,
                    ordinary_margin=ordinary-kappa-GUARD, gaussian_margin=gaussian-kappa-GUARD,
                    signed_strict_count=len(strict), signed_functional_count=len(functional),
                    min_signed_strict=min(strict), min_signed_functional=min(functional), min_signed_paid=paid,
                    cuts=cuts, activation_exponent=exponent, activation_offset=offset,
                    ordinary_log2_B=ordinary_bill, gaussian_height_log_charge=gaussian_bill,
                    log2_C_before_entry_and_selector=recurring, entry_ordinary_surcharges=surcharge,
                    absolute_private_envelope=envelope, max_native_height=max(*heights,gaussian_height))

    entry_old, entry_new = invoice(ENTRY, DEBIT_O_OLD), invoice(ENTRY, DEBIT_O_NEW)
    old, new = invoice(OLD, DEBIT_O_OLD), invoice(NEW, DEBIT_O_NEW)
    for base, terminal in ((entry_old, old), (entry_new, new)):
        premium = ceil((terminal["kappa"]-base["kappa"])*terminal["activation_exponent"])
        terminal["entry_conversion_bits"] = premium
        terminal["select_entry_after_conversion"] = base["log2_C_before_entry_and_selector"]+premium
        terminal["complete_log2_C"] = 1+max(terminal["select_entry_after_conversion"],
                                               terminal["log2_C_before_entry_and_selector"])
        assert premium == 515
        assert terminal["max_native_height"] == 524288
        assert terminal["activation_exponent"] == 1148456 and terminal["activation_offset"] == 2
        assert terminal["absolute_private_envelope"] == 536870915
    assert new["complete_log2_C"] == 318292071 and old["complete_log2_C"] == 318292171
    assert (new["ordinary_log2_B"]-old["ordinary_log2_B"],
            new["gaussian_height_log_charge"]-old["gaussian_height_log_charge"]) == (-320, 220)

    # Prove the comparator crossing under its broader inherited cap. The known
    # optimizer is also affordable at the comparator's own cost, so both caps
    # share this exact crossing.
    cap, h = 318292451, OLD[1]
    heights = OLD[0]
    assert sum(heights) == (cap-1731-220*h)//320
    weights = (F(1,250**2), F(1,250), F(1))
    ideal = F(249,250)*sum(w*(TRIAL_O-DEBIT_O_OLD/a) for a,w in zip(heights, weights, strict=True))
    gradients = [w/(a*a) for a,w in zip(heights, weights, strict=True)]
    alpha, beta, gamma = gradients
    assert 0 < alpha < beta < gamma
    rounding_loss = ideal-old["ordinary_ceiling"]
    tangent_loss = F(249,250)*DEBIT_O_OLD*min(beta-alpha,gamma-beta,beta)
    assert 0 < rounding_loss < tangent_loss
    assert TRIAL_G-DEBIT_G/(h-1) < old["ordinary_ceiling"] < old["gaussian_ceiling"]
    crossing = old["ordinary_ceiling"]-GUARD
    exact_gap = new["kappa"]-crossing
    fixed_new_ceiling = min(new["ordinary_ceiling"],new["gaussian_ceiling"])-GUARD
    old_ordinary_negative = new["kappa"]+GUARD-ordinary_rates(NEW[0], DEBIT_O_OLD)[0]
    old_gaussian_negative = new["kappa"]+GUARD-(TRIAL_G-DEBIT_G/OLD[1])
    assert crossing == F(523209442801521766233321100177,134217728000000000000000000000000)
    assert exact_gap > 0 and fixed_new_ceiling > new["kappa"]
    assert old_ordinary_negative > 0 and old_gaussian_negative > 0
    assert new["gaussian_ceiling"] < new["ordinary_ceiling"]

    # Fixed native setup pays a bounded lookup and scalar action on the
    # authenticated serial tape for each directory record and grade action.
    width = 2**38
    register = 2*width+2
    scalar = 2**16*(register+4)*(7*register+9)+8*2**16*(register+4)**2
    lookup = (4*width*2**68)*8*512*128
    setup = (2**68+1)*(lookup+scalar+2**120)*2**32
    assert scalar < 2**110 and lookup == 2**127 and setup < 2**228
    assert len(ENTRY[0])+1+len(NEW[0])+1 == 7 and max(NEW[0]).bit_length() == 20

    return dict(entry_old=entry_old, entry_new=entry_new, old_terminal=old, new_terminal=new,
                comparison_cap=cap, prior_family_crossing=crossing, prior_floor_loss=rounding_loss,
                prior_tangent_loss=tangent_loss, fixed_new_ceiling=fixed_new_ceiling,
                booked_gap_vs_peer_family_crossing=exact_gap, booked_gain_vs_comparator=new["kappa"]-old["kappa"],
                old_ordinary_debit_exact_shortfall=old_ordinary_negative,
                old_gaussian_height_exact_shortfall=old_gaussian_negative,
                conservative_fixed_native_setup=setup, setup_bit_bound=setup.bit_length())


if __name__ == "__main__":
    print(json.dumps({"arithmetic": complete_profiles(), "factors": transport_and_factors()},
                     default=str, indent=2, sort_keys=True))
