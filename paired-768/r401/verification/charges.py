"""Rebuild raw charged censuses and exact directed invoice bounds from the pinned archive."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from math import ceil, floor, isqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path('.').resolve()))
from reconstruct import BINARY_TRIAL, GAUSSIAN_TRIAL, NEW_DEBIT, OLD_DEBIT, ENTRY, CANDIDATE, STOP

ARCHIVE = Path('archived-runtime').resolve()
PEER = Path('peer-source/research').resolve()


def dyadic_power(base, exponent, precision=224):
    """Outward bounding by an integer interval for each selected binary root."""
    quantum = 1 << precision
    n = exponent.denominator
    assert n.bit_count() == 1 and base > 0 and exponent >= 0
    whole, tail = divmod(exponent.numerator, n)
    lo = hi = F(base)**whole
    pair = (floor(base*quantum), ceil(base*quantum))
    for power in range(n.bit_length()-2, -1, -1):
        pair = (isqrt(pair[0]*quantum), 1 + isqrt(pair[1]*quantum-1))
        if tail & (1 << power):
            lo = F(floor(lo * pair[0]), quantum)
            hi = F(ceil(hi * pair[1]), quantum)
    return lo, hi


def protocol_mass(rank, exponent):
    # The literal transport prices grade mass on the published 112-bit grid.
    quantum = 2**112
    if rank == F(1, 2):
        low, high = dyadic_power(2, exponent, 112)
        return F(floor(quantum/high), quantum), F(ceil(quantum/low), quantum)
    return dyadic_power(rank, exponent, 112)


def transport(target, paid, trial):
    available = {r: n * protocol_mass(r, 1-trial)[0] for r,n in target.items()}
    demand = {r: n * protocol_mass(r, 1-trial)[1] for r,n in paid.items()}
    total, used = sum(available.values()), sum(demand.values())
    margin = (total-used)/total
    assert margin > 0
    remaining_mass = {r: mass * used / total for r,mass in available.items()}
    shares = {}
    receiving_grades = sorted(remaining_mass, reverse=True)
    for grade in sorted(demand, reverse=True):
        remaining = demand[grade]
        for receiver in receiving_grades:
            if 5*grade > 4*receiver:
                break
            transfer = min(remaining, remaining_mass[receiver])
            if transfer:
                shares[grade,receiver] = transfer/demand[grade]
                remaining_mass[receiver] -= transfer
                remaining -= transfer
            if not remaining:
                break
        assert not remaining
    assert not any(remaining_mass.values())
    return margin, shares


def port_receipt(ports):
    ranks = Counter()
    digest = sha256()
    identifiers = set()
    for port in ports:
        assert port.tag not in identifiers and port.rank > 0
        identifiers.add(port.tag)
        ranks[port.rank] += 1
        digest.update((json.dumps((port.tag, port.rank), separators=(',', ':'))+'\n').encode())
    return ranks, digest.hexdigest()


def source_data():
    sys.path.insert(0, str(ARCHIVE))
    from upstream import install, HERE
    install()
    from strong_binary import graph, caller
    from strong_complex import load_changed, word
    from tagged_sources import binary_ports
    binary = binary_ports(graph(), caller())
    gaussian = word(*load_changed(HERE / 'inputs'))
    sources = {}
    for name,data in [('ordinary', binary), ('gaussian', gaussian)]:
        target, target_hash = port_receipt(data.targets)
        paid, paid_hash = port_receipt(data.paid)
        sources[name] = dict(target=target, paid=paid, target_hash=target_hash, paid_hash=paid_hash,
                             ambient=data.ambient)
    return sources


def weighted_counts(gaussian, weights):
    original_t, original_p = gaussian['target'], gaussian['paid']
    assert original_p[1] >= 1008
    paid_split = original_p.copy()
    paid_split[1] -= 1008
    paid_split[F(1,2)] += 2016
    variants = [(original_t, paid_split),
                (Counter({2*r:n for r,n in original_t.items()}), Counter({2*r:n for r,n in original_p.items()}))]
    weighted = [Counter(), Counter()]
    for w, (targets, paid) in zip(weights, variants, strict=True):
        for index, ranks in enumerate((targets, paid)):
            weighted[index].update({r: n*w for r,n in ranks.items()})
    return variants, weighted


def finite_factor(scale, axes, paid, shares):
    lower_band, trial = 1874, GAUSSIAN_TRIAL
    delta = F(1, 2**128)
    psi = [sum(paid[r]*weight*r*(dyadic_power(F(k,r),trial)[i]-1)/trial
               for (r,k),weight in shares.items()) for i in (0,1)]
    fr = [F(10*axes, 1) / ((1-trial)*x) for x in psi[::-1]]
    assert psi[0] > F('926899828.8291') and fr[1] < F('7.335168')
    assert dyadic_power(lower_band, 1-trial)[0] > 1024
    scale_power = dyadic_power(scale*lower_band, trial)
    fixed = (1+delta) * (1 + F(4*258, scale)) / (1-delta)**4
    return [fixed * root * (1 + fringe/lower_band + delta) for root,fringe in zip(scale_power,fr,strict=True)]


def ordinary_factor(floor_height):
    delta = F(1, 2**128)
    fixed = (F(47,20)*F(256,255)*F(4097,4096)*F(257,256)*(1+F(64,floor_height)+delta)
             / ((1-F(10,floor_height))*(1-delta)**3))
    return [fixed*r for r in dyadic_power(1024*134*floor_height, BINARY_TRIAL)]


def outward(pair, digits):
    d = 10**digits
    return [F(floor(pair[0]*d), d), F(ceil(pair[1]*d), d)]


def inspect():
    source = source_data()
    b, g = source['ordinary'], source['gaussian']
    ordinary_margin, cells = transport(b['target'], b['paid'], BINARY_TRIAL)
    assert (b['target'].total(), b['paid'].total(), len(cells), b['ambient']) == (18906, 104652, 24, 134)
    assert ordinary_margin > 0
    o_factor = ordinary_factor(18960)
    assert o_factor[0]**1024 > 2**1404 and o_factor[1]**1024 < 2**1405
    assert F(75,32) * F(20,47) == F(375,376)
    assert ordinary_factor(32768)[0]**1024 > 2**1405

    weights = (5, 451)
    variants, (target, paid) = weighted_counts(g, weights)
    assert [x.total() for x,_ in variants] == [52608, 52608]
    assert [x.total() for _,x in variants] == [282576, 281568]
    assert (target.total(), paid.total()) == (23989248, 128400048)
    axes = sum(r*n for r,n in target.items())
    assert axes == 677246016 and max(target) == 258 and g['ambient'] == 153
    assert len(target)+len(paid) == 52
    gaussian_margin, shares = transport(target, paid, GAUSSIAN_TRIAL)
    assert len(shares) == 51
    assert gaussian_margin == F(50803612971593099397385261823,24054211488961849122338563785759685737032)
    typed = {(a,r,b,k): share*weights[b]*variants[b][0][k]/target[k]
             for (r,k),share in shares.items()
             for a in range(2) if r in variants[a][1]
             for b in range(2) if k in variants[b][0]}
    assert len(typed) == 88
    for a, (_,ranks) in enumerate(variants):
        assert all(sum(p for (ca,cr,_,_),p in typed.items() if ca==a and cr==r) == 1 for r in ranks)
    for b, (ranks,_) in enumerate(variants):
        for k,n in ranks.items():
            load = sum(weights[a]*variants[a][1][r]*F(share,n)*protocol_mass(r,1-GAUSSIAN_TRIAL)[1]
                       for (a,r,cb,ck),share in typed.items() if (cb,ck)==(b,k))
            assert 0 < load <= weights[b]*protocol_mass(k,1-GAUSSIAN_TRIAL)[0]
    exterior_share = typed[(1,112,1,258)] / variants[1][0][258]
    assert exterior_share == F(1,624)
    assert all(5*r <= 4*k for _,r,_,k in typed)
    grade_actions = 2**20*256 + 2**8*256*8 + 32*(len(target)+len(paid)+2)**2 + 2**12
    assert grade_actions == 269057152

    g_factor = finite_factor(1724*306//2, axes, paid, shares)
    old_scale_factor = finite_factor(2048*306//2, axes, paid, shares)
    old_allowance = dyadic_power(2, OLD_DEBIT)
    new_allowance = dyadic_power(2, NEW_DEBIT)
    inadequate = dyadic_power(2, NEW_DEBIT - F(1,524288))
    assert old_allowance[0] > new_allowance[1] > new_allowance[0] > g_factor[1] > g_factor[0] > inadequate[1]
    assert new_allowance[0] - g_factor[1] > F('0.000000684423')
    assert old_scale_factor[0] - new_allowance[1] > F('0.000051649827')

    # Evaluate all published signed caller margins using the authenticated source's
    # full expression list, with independently computed rates and debits.
    sys.path.insert(0, str(PEER/'tiered-native-multiplier'/'source'))
    from outer_budget import margins
    signed = {}
    for name, (_,h,k) in [('entry', ENTRY), ('terminal', CANDIDATE)]:
        strict, functional, paid_margin = margins(k,F(1,10**18),k+STOP,GAUSSIAN_TRIAL-NEW_DEBIT/h)
        assert len(strict)==54 and len(functional)==4 and min(*strict,*functional,paid_margin)>0
        signed[name] = {'strict_count':len(strict),'functional_count':len(functional),
                        'minimum_strict_margin':min(strict),'minimum_functional_margin':min(functional),
                        'gaussian_margin':paid_margin}

    public = json.loads((PEER/'frequency-weighted-native-multiplier'/'RESULT.json').read_bytes())
    assert public['complete_log2_C'] == 318259431 and public['log2_fixed_setup_upper'] == 113
    assert public['max_native_H'] == 524288
    current_price = json.loads(Path('reconstruction.json').read_bytes())['candidate']['recurring_bill']
    assert current_price > public['complete_log2_C']
    record = {'ordinary_factor_outward_12_places':outward(o_factor,12), 'ordinary_grade_cells':len(cells),
              'gaussian_factor_outward_18_places':outward(g_factor,18), 'gaussian_allowance_outward_18_places':outward(new_allowance,18),
              'gaussian_adjacent_shortfall_lower_outward_18_places':outward([g_factor[0]-inadequate[1],g_factor[1]-inadequate[0]],18),
              'gaussian_older_divisor_shortfall_lower_outward_18_places':outward([old_scale_factor[0]-new_allowance[1],old_scale_factor[1]-new_allowance[0]],18),
              'gaussian_reserve_outward_18_places':outward([new_allowance[0]-g_factor[1],new_allowance[1]-g_factor[0]],18),
              'gaussian_grade_cells':len(shares),'gaussian_typed_cells':len(typed),'gaussian_raw_census':[[x.total(),y.total()] for x,y in variants],
              'gaussian_weighted_census':[target.total(),paid.total()],'gaussian_weighted_target_axes':axes,
              'gaussian_transport_margin':gaussian_margin,'gaussian_first_exterior_share':exterior_share,
              'setup_grade_actions':grade_actions,'two_signed_tiers':signed,
              'peer_8057':{'recurring_bill':public['complete_log2_C'],'portable_measured_setup_exponent':public['log2_fixed_setup_upper'],
                           'height_cap':public['max_native_H'],'candidate_bill_excess':current_price-public['complete_log2_C']}}
    for name, census in source.items():
        record[name+'_raw'] = {key: {str(r):n for r,n in value.items()} if isinstance(value, Counter) else value
                                for key,value in census.items()}
    return record


if __name__ == '__main__':
    print(json.dumps(inspect(),default=str,sort_keys=True,indent=2))
