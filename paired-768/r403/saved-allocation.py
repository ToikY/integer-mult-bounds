"""Bound a single monotone allocation crossing inside a fixed height bracket."""

from fractions import Fraction as Q

CAP = 318292071
LOW, HIGH = 490639, 491151
MAX_EVALUATIONS = 14
PRIOR_RATE = Q("0.00389821412325")
ORDINARY_TRIAL = Q(4391986206293, 2**50)
GAUSSIAN_TRIAL = Q(17145637307, 2**42)
ORDINARY_DEBIT = Q(11239, 8192)
GAUSSIAN_DEBIT = Q(64939, 524288)
STOP = Q(5, 10**18)


def ordinary(heights):
    rate = Q(0)
    for i, height in enumerate(heights, 1):
        rate = min(Q(39, 10000), (249 * (ORDINARY_TRIAL - ORDINARY_DEBIT / height) + rate) / 250)
        if i != len(heights):
            rate = Q((rate * 10**21).__floor__() - 1, 10**21)
    return rate


def quote(gaussian_height):
    first, last = 8192, 524288
    middle = (CAP - 1731 - 220 * gaussian_height) // 320 - first - last
    heights = first, middle, last
    assert first <= middle <= last
    ordinary_ceiling = ordinary(heights)
    gaussian_ceiling = GAUSSIAN_TRIAL - GAUSSIAN_DEBIT / gaussian_height
    recurring = 1731 + 320 * sum(heights) + 220 * gaussian_height
    assert recurring <= CAP
    return heights, gaussian_height, ordinary_ceiling, gaussian_ceiling, recurring


def main():
    low, high = quote(LOW), quote(HIGH)
    assert low[2] > low[3] and high[2] <= high[3], "specified bracket does not straddle the crossing"
    evaluated = [low[1], high[1]]
    while high[1] - low[1] > 1:
        midpoint = quote((low[1] + high[1]) // 2)
        evaluated.append(midpoint[1])
        assert len(evaluated) <= MAX_EVALUATIONS
        if midpoint[2] > midpoint[3]:
            low = midpoint
        else:
            high = midpoint
    winner = max((low, high), key=lambda row: min(row[2:4]))
    ceiling = min(winner[2:4]) - STOP
    assert ceiling > PRIOR_RATE, "the two boundary allocations fail to clear the comparator"
    print("evaluated Gaussian heights", evaluated)
    print("adjacent exact boundary prices", low, high)
    print("candidate fixed-profile ceiling", ceiling)
    print("scope", (LOW, HIGH), "recurring cap", CAP, "selected heights", winner[:2])


if __name__ == "__main__":
    main()
