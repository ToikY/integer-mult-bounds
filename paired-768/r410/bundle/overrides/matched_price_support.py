"""Reconstruct the conservative matched interior bound in two directed forms.

The normalized phase identity and finite-error accounting use #8083's
offset-eight proof. Rooted powers are the independent R409 enclosure;
the atanh and exponential Taylor enclosures provide a second control.
"""
from fractions import Fraction as Q
from functools import cache
from math import ceil, floor, gcd, isqrt

CG = Q(17145637307, 2**42)
D0, D1 = Q(64934, 524288), Q(130699669, 2**30)
L, SCALE, OFFSET, DELTA = 1874, 263772, 8, Q(1, 2**128)
SERIES_GRID = 1 << 224
ROOT_GRID = 1 << 208


def down(x):
    return Q(floor(x*SERIES_GRID),SERIES_GRID)


def up(x):
    return Q(ceil(x*SERIES_GRID),SERIES_GRID)


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


def series_power(base, exp):
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


def phases(r, k):
    z = Q(k) / r
    assert 5 * r <= 4 * k and 1 < z <= 516
    doubled = (Q(2 * r), Q(2 * k))
    assert all(x.denominator == 1 for x in doubled)
    step = gcd(*(int(x) for x in doubled))
    suffix_min = OFFSET * (k - r) - 2 * r + step
    suffix_max = OFFSET * (k - r) + 2 * k - step
    assert suffix_min > 0
    period = 2 * z.denominator
    breaks = sorted({Q(2 * i) for i in range(z.denominator + 1)}
                    | {Q(2 * j) / z for j in range(z.numerator + 1)})
    integral = Q(0)
    for left, right in zip(breaks, breaks[1:]):
        middle = (left + right) / 2
        e, d = 2 * floor(z * middle / 2), 2 * floor(middle / 2)
        suffix = r * (e - OFFSET) - k * (d - OFFSET)
        assert suffix_min <= suffix <= suffix_max
        assert suffix == OFFSET * (k - r) + k * (middle - d) - r * (z * middle - e)
        integral += (right - left) * suffix
    assert integral == period * (OFFSET + 1) * (k - r)
    return suffix_max, len(breaks) - 1


def finite_boundaries():
    # The following worst-end checks are monotone as M doubles for H >= 1024.
    n = 2**1024
    upper = 2 * (n // (2 * SCALE))
    assert L % 2 == upper % 2 == n % 4 == 0 and OFFSET < L
    assert SCALE == 1724 * 306 // 2 and 258 * (upper - OFFSET) < Q(n, 4)
    assert upper > 516 * L and DELTA * upper >= 5160
    assert SCALE * upper >= (1 - DELTA) * n and 516 * (upper + 2) < n
    assert DELTA * n >= 1
    assert Q(4, 5) * (L + 2) < Q(5, 6) * L and Q(6, 5)**76 > 2**19
    assert 4 * 2**160 < n**36
    assert 2**46 < DELTA * n**4 / 16 and 2**20 < DELTA * n**4 / 16
    assert 2**30 < DELTA * n**5 / 16 and 2 * 52608 < n


@cache
def rooted_power(base, exponent):
    """Evaluate a nonnegative dyadic power on an independent positive grid."""
    base = Q(base)
    assert base >= 1 and 0 < exponent < 1 and exponent.denominator.bit_count() == 1
    lower, upper = floor(base*ROOT_GRID), ceil(base*ROOT_GRID)
    lo = hi = ROOT_GRID
    for bit in range(exponent.denominator.bit_length()-2, -1, -1):
        lower = isqrt(lower*ROOT_GRID)
        upper = 1 + isqrt(upper*ROOT_GRID-1)
        if exponent.numerator >> bit & 1:
            lo = lo*lower//ROOT_GRID
            hi = -(-hi*upper//ROOT_GRID)
    return Q(lo,ROOT_GRID), Q(hi,ROOT_GRID)


def factor(edges, power):
    t = 1 - CG
    phase_intervals = 0
    psi, matched = [Q(0), Q(0)], [Q(0), Q(0)]
    finite_boundaries()
    for (r,k), coefficient in edges.items():
        pointwise, count = phases(r,k)
        phase_intervals += count
        z = Q(k, r)
        average_upper = 9*(k-r) + t*r/(2*z*L)
        assert 0 < average_upper <= pointwise
        for i,end in enumerate(power(z,CG)):
            psi[i] += coefficient*r*(end-1)/CG
            matched[i] += coefficient*end/z*average_upper
    assert phase_intervals == 1971 and psi[0] > 1
    exterior = 1+Q(1032,SCALE)
    constant = (1+DELTA)*exterior/(1-DELTA)**4
    x = power(SCALE*L,CG)
    fringe = [matched[i]/(t*psi[1-i]) for i in range(2)]
    bounds = [constant*x[i]*(1+fringe[i]/L+DELTA) for i in range(2)]
    covering = power(2,D1)
    reserve = covering[0]-bounds[1]
    adjacent = bounds[0]-power(2,D1-Q(1,2**30))[1]
    coarse = [constant*x[i]*(1+10*677246016/(t*psi[1-i]*L)+DELTA) for i in range(2)]
    known_good = power(2,D0)[0] - coarse[1]*Q(257,256)/exterior
    assert reserve > 0 and adjacent > 0
    assert coarse[0] > covering[1] and known_good > 0
    return dict(psi=psi, phase_intervals=phase_intervals, fringe=fringe, factor=bounds,
                covering=covering, positive_reserve=reserve, adjacent_shortfall=adjacent,
                old_pointwise_shortfall_at_new_booking=coarse[0]-covering[1],
                predecessor_approved_booking_reserve=known_good, exterior_factor=exterior)
