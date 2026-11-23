"""Independent exact Round 401 calculations. Run from the evidence directory."""
from fractions import Fraction as F
import json
from math import ceil, floor
from pathlib import Path

BINARY_TRIAL = F(4391986206293, 2**50)
GAUSSIAN_TRIAL = F(17145637307, 2**42)
ORDINARY_DEBIT = F(1405, 1024)
OLD_DEBIT, NEW_DEBIT = F(64944, 524288), F(64939, 524288)
STOP = F(5, 10**18)
ENTRY = ((3000, 3080), 1024, F('.00345'))
PRIOR = ((8192, 124847, 524288), 490664, F('.0038982141167032'))
CANDIDATE = ((8192, 124864, 524288), 490638, F('.0038982141226643'))
ROOT = Path('peer-source/research')


def ordinary(heights, rounding=True, debit=ORDINARY_DEBIT):
    ticks = []
    upstream = 0
    for index, height in enumerate(heights):
        ceiling = min(F(39, 10000), (249 * (BINARY_TRIAL - debit / height) + upstream) / 250)
        if index < len(heights) - 1 and rounding:
            upstream = F(floor(10**21 * ceiling) - 1, 10**21)
            ticks.append(upstream)
        else:
            upstream = ceiling
    return upstream, ticks


def connected(heights, gaussian_height):
    cuts = []
    for height in heights:
        stateless = ceil(F(250 * (height + 64), 249))
        available = cuts[-1] + height + 64 if cuts else 0
        cuts.append(max(stateless, available))
    required = cuts[-1] + gaussian_height + 102
    s = next(x for x in range(required, required + 500) if x - 7 * (x-1).bit_length() >= required)
    assert 2**(s-1).bit_length() + 1 - 7 * ((s-1).bit_length()+1) >= required
    return cuts, s-1, (-pow(2, s-1, 6)) % 6


def recurring(profile):
    heights, gaussian_height, _ = profile
    if len(heights) == 2:
        degree = 20 * 253
        a, b = 2 * degree, 258 * degree
        degree_fees = [20*24 + 4*degree + 2 + a * (a-1).bit_length(),
                       20*24 + 259*degree + 2 + b * (b-1).bit_length()]
        surcharges = [max(0, fee - 944 * height) for fee, height in zip(degree_fees, heights, strict=True)]
        ordinary_bill = 57 + 16384 * sum(heights) + sum(surcharges)
    else:
        ordinary_bill = 128 + 320 * sum(heights)
        surcharges = []
    return ordinary_bill, max(84500001, 1602 + 220 * gaussian_height + ordinary_bill), surcharges


def tier(profile, debit):
    heights, height, kappa = profile
    ordinary_ceiling, intermediate_rates = ordinary(heights)
    cuts, exponent, offset = connected(heights, height)
    ordinary_bill, recurring_bill, surcharges = recurring(profile)
    gaussian_ceiling = GAUSSIAN_TRIAL - debit / height
    assert all(a < b for a,b in zip([0, *intermediate_rates], [*intermediate_rates, kappa + STOP], strict=True))
    assert ordinary_ceiling > kappa + STOP and gaussian_ceiling > kappa + STOP
    return dict(heights=heights, gaussian_height=height, kappa=kappa, intermediate_rates=intermediate_rates,
                ordinary_ceiling=ordinary_ceiling, gaussian_ceiling=gaussian_ceiling,
                ordinary_margin=ordinary_ceiling-kappa-STOP, gaussian_margin=gaussian_ceiling-kappa-STOP,
                binary_cuts=cuts, activation_exponent=exponent, activation_offset=offset,
                ordinary_bill=ordinary_bill, recurring_bill_before_selector=recurring_bill,
                entry_ordinary_surcharges=surcharges)


def family_ceiling(profile, debit, cap):
    heights, h, _ = profile
    sum_cap = (cap - (1 + 1602 + 128) - 220 * h) // 320
    assert heights == (8192, sum_cap-8192-524288, 524288)
    exact = ordinary(heights)[0]
    relaxed = ordinary(heights, rounding=False)[0]
    weights = (F(1, 62500), F(1, 250), 1)
    slopes = [w / F(x*x) for w, x in zip(weights, heights, strict=True)]
    assert all(a < b for a,b in zip([0, *slopes[:-1]], slopes, strict=True))
    lower_tangent_gap = F(249, 250) * ORDINARY_DEBIT * min(slopes[1]-slopes[0], slopes[2]-slopes[1], slopes[1])
    assert relaxed == F(249, 250) * sum(w * (BINARY_TRIAL - ORDINARY_DEBIT / x) for w,x in zip(weights, heights, strict=True))
    assert 0 < relaxed - exact < lower_tangent_gap
    assert GAUSSIAN_TRIAL - debit / (h-1) < exact < GAUSSIAN_TRIAL - debit / h
    return exact - STOP, lower_tangent_gap


def setup_bound():
    width = 2**38
    h = 2 * width + 2
    price = 2**16 * (h+4) * (7*h+9 + 8*(h+4))
    lookup = 4*width*2**68 * 8*512*128
    return (2**68+1)*(price+lookup+2**120)*2**32


def reconstruct():
    result = {}
    for name, profile, debit in [('entry', ENTRY, NEW_DEBIT), ('prior', PRIOR, OLD_DEBIT), ('candidate', CANDIDATE, NEW_DEBIT)]:
        result[name] = values = tier(profile, debit)
        premium = ceil((profile[-1]-ENTRY[-1]) * values['activation_exponent'])
        entry_bill = recurring(ENTRY)[1] + premium
        values['entry_conversion_bits'] = premium
        values['recurring_bill'] = 1 + max(entry_bill, values['recurring_bill_before_selector'])
        values['private_address_bound'] = 1024 * max(*profile[0], profile[1]) + (len(profile[0])+1).bit_length()
    assert result['prior']['recurring_bill'] == 318292451
    assert result['candidate']['recurring_bill'] == 318292171
    assert result['candidate']['entry_conversion_bits'] == 515
    assert result['candidate']['binary_cuts'] == [8290, 133218, 657570]
    assert result['candidate']['activation_exponent'] == 1148456 and result['candidate']['activation_offset'] == 2
    assert result['candidate']['private_address_bound'] == 536870915
    assert max(*CANDIDATE[0], CANDIDATE[1]) == 524288
    new_ceiling, new_gap = family_ceiling(CANDIDATE, NEW_DEBIT, result['prior']['recurring_bill'])
    old_ceiling, old_gap = family_ceiling(PRIOR, OLD_DEBIT, 318292711)
    assert new_ceiling == F(523209442801521766233321100177, 134217728000000000000000000000000)
    assert old_ceiling == F(104641888400286240891629336349, 26843545600000000000000000000000)
    assert old_ceiling < CANDIDATE[-1] < new_ceiling
    old_on_new = CANDIDATE[-1] + STOP - (GAUSSIAN_TRIAL - OLD_DEBIT / CANDIDATE[1])
    assert old_on_new == F(5290830738777425573, 274384656793600000000000000000) > 0
    old_ordinary_shortfall = CANDIDATE[-1] + STOP - ordinary(PRIOR[0])[0]
    assert old_ordinary_shortfall > 0
    assert CANDIDATE[-1] - PRIOR[-1] == F(59611, 10**16)
    assert (result['candidate']['ordinary_bill']-result['prior']['ordinary_bill'], 220*(CANDIDATE[1]-PRIOR[1])) == (5440, -5720)
    setup = setup_bound()
    assert setup < 2**228
    result['controls'] = dict(old_ceiling=old_ceiling, new_family_ceiling=new_ceiling, old_debit_at_new_height_shortfall=old_on_new,
                              prior_ordinary_shortfall=old_ordinary_shortfall, old_tangent_gap=old_gap, new_tangent_gap=new_gap,
                              booked_rate_gain=CANDIDATE[-1]-PRIOR[-1], new_book_excess_over_old_ceiling=CANDIDATE[-1]-old_ceiling,
                              new_setup_transition_bound=setup,
                              ordinary_funding_height_floor=ceil(ORDINARY_DEBIT / (BINARY_TRIAL - CANDIDATE[-1] - STOP)),
                              gaussian_funding_height_floor=ceil(NEW_DEBIT / (GAUSSIAN_TRIAL - CANDIDATE[-1] - STOP)))
    return result


if __name__ == '__main__':
    print(json.dumps(reconstruct(), indent=2, default=str, sort_keys=True))
