"""Price the weighted Gaussian calendar from its installed edges and physical sizes."""

from fractions import Fraction as Q

from strict_moment import UNIT, power_interval
from unpowered_price import intervals
from grades import UPPER_DIVISOR

BAND_LOWER = 1874
POSITIVE_DEBIT = Q(130699669, 2**30)
DELTA = Q(1, 2**128)


def certify_loss(recipe, lower):
    """Return the exact finite price for this two-type numerical recipe."""
    c = recipe.trial
    t = 1 - c
    targets = recipe.targets.histogram
    paid = recipe.paid.histogram
    cells = recipe.cells
    assert lower == BAND_LOWER and recipe.ambient == 306
    assert max(targets) == 258 and min(paid) == Q(1, 2)
    assert all(w > 0 and 5 * r <= 4 * k for (r, k), w in cells.items())
    assert all(sum(w for (p, k), w in cells.items() if p == r) == 1 for r in paid)

    # Bound the matched interior suffix on its actual weighted half-line.
    # With z=k/r, the even-band primitive in #8083 gives mean
    # at most 9(k-r)+t*r/(2*z*lower). The unpublished profile
    # keeps the original conservative exterior period charge.
    psi = [Q(0), Q(0)]
    suffix = [Q(0), Q(0)]
    for (r, k), share in cells.items():
        l_k, h_k = intervals(k, c)
        l_r, h_r = intervals(r, c)
        power = (Q(l_k, h_r), Q(h_k, l_r))
        z = Q(k, r)
        mean = 9 * (k - r) + t * r / (2 * z * lower)
        assert min(power) > 1 and mean > 0
        for index, endpoint in enumerate(power):
            psi[index] += paid[r] * share * r * (endpoint - 1) / c
            suffix[index] += paid[r] * share * (endpoint / z) * mean
    target_axes = sum(count * k for k, count in targets.items())
    fringe_lower = suffix[0] / (t * psi[1])
    fringe = suffix[1] / (t * psi[0])
    assert target_axes == 677246016
    assert psi[0] > Q("926899828.8291")
    assert Q("4.550681666") < fringe_lower <= fringe < Q("4.550681667")

    # All bounds below improve as H grows. Check their smallest eligible H.
    M = 2**1024
    scale = UPPER_DIVISOR * recipe.ambient // 2
    upper = 2 * (M // (2 * scale))
    assert 4 * max(targets) * (upper - 8) < M and 516 * (upper + 2) < M
    assert 5160 <= DELTA * upper
    assert (1 - DELTA) * M <= scale * upper
    assert upper > 516 * lower and M * DELTA >= 1
    assert t > Q(996, 1000) and power_interval(lower, t)[0] > 1024 * UNIT
    assert sum((5, 451)) / (t * 2**10) + Q(2, M**5) < 2
    assert 2**46 < Q(M**4, 2**132)
    assert 2**20 < Q(M**4, 2**132)
    assert 2 * 52608 < M
    assert 4 * (lower + 2) * 6 < 5 * lower * 5
    assert 2**19 * (upper + lower) ** 77 + lower**77 < (M * lower) ** 77

    # Keep the upper physical period, complete group padding, both endpoint
    # roundings, and the endpoint of the integral's chosen upper band.
    exterior_period = 1 + Q(4 * max(targets), scale)
    factor_scale = (1 + DELTA) * exterior_period / (1 - DELTA) ** 4
    scale_lower, scale_upper = power_interval(scale * lower, c)
    finite_factor_lower = factor_scale * Q(scale_lower, UNIT) * (1 + fringe_lower / lower + DELTA)
    finite_factor = factor_scale * Q(scale_upper, UNIT) * (1 + fringe / lower + DELTA)
    assert UNIT * finite_factor < power_interval(2, POSITIVE_DEBIT)[0]
    assert UNIT * finite_factor_lower > power_interval(2, POSITIVE_DEBIT - Q(1, 2**30))[1]
    return {
        "debit": str(POSITIVE_DEBIT),
        "lower_band": lower,
        "upper_divisor": UPPER_DIVISOR,
        "upper_scale": scale,
        "weighted_target_axes": target_axes,
        "fringe": str(fringe),
        "psi_lower": str(psi[0]),
        "upper_factor": str(finite_factor),
        "exterior_period_factor": str(exterior_period),
    }
