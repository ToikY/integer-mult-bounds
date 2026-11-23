"""One-case pre-build screen for the offset-8 Gaussian matched suffix."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from math import ceil, floor, gcd
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import runpy
from shutil import copyfile
import signal
from subprocess import TimeoutExpired, check_output, run
import sys

HEAD = "aea1699415250d865f7a635f4df0b76f406c47b4"
PACKAGE = "research/p104-period-debit-25bit"
SUFFIX_HEAD = "dd2e2ff28102557f7c30619d6abd8a861e363d1d"
PINS = {
    "RESULT-460.json": "8c8b7cebbdea179329d225d828f31e37e2fddfcfd177750803ae81e39726def8",
    "prepare.py": "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3",
    "retune.py": "4e38ee479f91faf4a9f648fa7136e7f3d13af24b911eff6479d943500f134a60",
    "upstream_verify.py": "10362de3ceaa651cde5b71c6599fd4683d9f1f4d76cc252178e915b43a098fee",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "SETUP-PROOF.md": "b248cef0c3bb68b36ab05dcea61aebd7efeea1a7dfdf46e0ec59f8795a3463d8",
    "verify.py": "e8df287ed405ddde74106a28b018686c8cb69d4777ffb153f192bbb4909f327e",
    "PREDECESSOR-RESULT.json": "4e173fd0a9f4b593baf706a00899cc1336dae5eab922c43e6551775256733f63",
}
PROOF_SHA = "79f4d93bf8b39510c29c8648164c31e6fd730b72b20f5e807cfbd78cdf465683"
PRICER_SHA = "880bbfc11428cadc438722eb9d058f43e06f8990e81214fa20c27ebb628390c8"
CALENDAR_SHA = "b76b9ad3dc0dd91473026c079585f830387eaa3c34c25a7820ee5057d5cbf941"
C_B, C_G = Q(4391986206293, 2**50), Q(17145637307, 2**42)
D_B, D_PRIOR, D_SUFFIX = Q(11239, 8192), Q(64934, 524288), Q(130699669, 2**30)
ETA, GUARD = Q(39, 10000), Q(5, 10**18)
K_PRIOR, K_TRIAL, CAP = Q(".003898460000505"), Q(".003898460003746"), 4354317451
ENTRY_H, ENTRY_G, ENTRY_K = (3000, 3080), 1024, Q(".00345")
HEIGHTS, PRIOR_G = (8192, 38102, 604363), 18845934
L, SCALE, OFFSET, DELTA = 1874, 263772, 8, Q(1, 2**128)
GRID = 1 << 224


def down(x):
    return Q(floor(x*GRID),GRID)


def up(x):
    return Q(ceil(x*GRID),GRID)


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


def pin(path, expected):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == expected, path.name
    return data


def bind(args):
    def git(*argv):
        return check_output(["git", "-C", args.baseline, *argv])

    assert git("rev-parse", "HEAD").decode().strip() == HEAD
    assert not git("status", "--porcelain")
    base = args.baseline / PACKAGE
    assert set(PINS) <= {path.name for path in base.iterdir() if path.is_file()}
    named = {}
    for item in git("ls-tree", "-r", "-z", "HEAD", "--", PACKAGE).split(b"\0"):
        if not item:
            continue
        record, raw_name = item.split(b"\t", 1)
        mode, kind, _ = record.split()
        assert kind == b"blob" and mode in (b"100644", b"100755")
        name = raw_name.decode()
        assert name not in named
        local = (args.baseline / name).read_bytes()
        assert local == git("show", f"{HEAD}:{name}")
        named[name] = sha256(local).hexdigest()
    for name, digest in PINS.items():
        assert named[f"{PACKAGE}/{name}"] == digest
    pin(args.integral, PROOF_SHA)
    pin(args.pricer, PRICER_SHA)
    named["peer8083/INTEGRAL.md"] = PROOF_SHA
    named["peer8083/appendix/weighted_suffix.py"] = PRICER_SHA
    return base, named


def cells(recipe):
    types = recipe.types()
    weights = [kind.multiplicity for kind in types]
    paid = [Counter(kind.paid) for kind in types]
    targets = [Counter(kind.targets) for kind in types]
    aggregate_paid, aggregate_targets = Counter(), Counter()
    for w, pc, tc in zip(weights, paid, targets, strict=True):
        for r, count in pc.items():
            aggregate_paid[r] += w * count
        for k, count in tc.items():
            aggregate_targets[k] += w * count
    assert weights == [5, 451]
    assert [sum(p.values()) for p in paid] == [282576, 281568]
    assert [sum(t.values()) for t in targets] == [52608, 52608]
    assert aggregate_paid == recipe.paid.histogram and aggregate_targets == recipe.targets.histogram
    assert min(aggregate_paid) == Q(1, 2) and max(aggregate_targets) == 258
    assert sum(k * n for k, n in aggregate_targets.items()) == 677246016

    typed = recipe.typed_cells()
    weighted_edges = Counter()
    per_issuer = Counter()
    assert len(typed) == 88
    for (a, r, b, k), share in typed.items():
        assert 0 < share and paid[a][r] and targets[b][k]
        assert share == recipe.cells[r, k] * weights[b] * targets[b][k] / aggregate_targets[k]
        weighted_edges[r, k] += weights[a] * paid[a][r] * share
        per_issuer[a, r] += share
    assert all(per_issuer[a, r] == 1 for a, counts in enumerate(paid) for r in counts)
    assert len(weighted_edges) == len(recipe.cells) == 51
    assert weighted_edges == {(r, k): share * aggregate_paid[r] for (r, k), share in recipe.cells.items()}
    return weighted_edges


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


def factor(recipe):
    assert recipe.ambient == 306 and recipe.trial == C_G and recipe.rank_log == PRIOR_G
    finite_boundaries()
    t = 1 - C_G
    psi, suffix = [Q(0), Q(0)], [Q(0), Q(0)]
    phase_count = 0
    for (r, k), coefficient in cells(recipe).items():
        pointwise, checked = phases(r, k)
        phase_count += checked
        z = Q(k) / r
        mean = (OFFSET + 1) * (k - r) + t * r / (2 * z * L)
        assert 0 < mean <= pointwise
        for index, endpoint in enumerate(power(z, C_G)):
            psi[index] += coefficient * r * (endpoint - 1) / C_G
            suffix[index] += coefficient * endpoint / z * mean
    fringe = [suffix[0] / (t * psi[1]), suffix[1] / (t * psi[0])]
    # The original exterior charge is kept in this price. No R407 tightening.
    exterior = 1 + Q(1032, SCALE)
    factors = [(1 + DELTA) * exterior * scale_power * (1 + term / L + DELTA) / (1 - DELTA)**4
               for scale_power, term in zip(power(SCALE * L, C_G), fringe, strict=True)]
    allowed = power(2, D_SUFFIX)
    assert factors[1] < allowed[0]
    assert power(2, D_SUFFIX - Q(1, 2**30))[1] < factors[0]
    return dict(typed_cells=88, grade_cells=51, phase_intervals=phase_count,
                psi=psi, fringe=fringe, factor=factors, cover=allowed,
                positive_factor_reserve=allowed[0] - factors[1],
                exterior_factor=exterior, gaussian_debit=D_SUFFIX)


def ordinary(heights):
    booked = Q(0)
    for index, height in enumerate(heights, 1):
        upper = min(ETA, (249 * (C_B - D_B / height) + booked) / 250)
        if index == len(heights):
            return upper
        booked = Q(floor(upper * 10**21) - 1, 10**21)
    raise ValueError("Expected ordinary stages")


def invoice(result, source):
    terminal = result["terminal"]
    assert (Q(terminal["kappa"]), tuple(terminal["ordinary_H"]), terminal["numerical_H"]) == (K_PRIOR, HEIGHTS, PRIOR_G)
    assert Q(result["gaussian"]["raw_loss"]) == D_PRIOR and result["complete_log2_C"] == CAP
    assert Q(result["ordinary_finite_debit"]) == D_B and result["ordinary_child_contraction"] == "375/376"
    assert Q(terminal["gaussian_rate"]) == C_G - D_PRIOR / PRIOR_G
    ordinary_stop = ordinary(HEIGHTS) - GUARD
    paid = K_TRIAL + GUARD
    assert K_PRIOR < K_TRIAL < ordinary_stop <= K_TRIAL + Q(1, 10**15)

    # Relax stages 2/3 by exact Cauchy. The relaxed upper rate decreases
    # over H1 >= 8192, so its maximum is at that floor.
    root = Q(6324555320336758663997787088865437067439, 10**41)
    assert root**2 < Q(1, 250) < (root + Q(1, 10**41))**2
    min_sum = 650656
    trial_sum = sum(HEIGHTS)
    assert trial_sum == 650657
    smaller = min_sum - 1
    w1 = Q(1, 62500)
    assert w1 / 8192**2 < (1 + root)**2 / (smaller - 8192)**2
    relaxed = C_B * (1 - Q(1, 250**3)) - Q(249, 250) * D_B * (w1 / 8192 + (1 + root)**2 / (smaller - 8192))
    assert relaxed < K_PRIOR + GUARD
    prior_g_max = (CAP - 1731 - 320 * min_sum) // 220
    assert prior_g_max == 18845935
    prior_stopped_upper = C_G - D_PRIOR / prior_g_max - GUARD
    assert K_TRIAL > max(K_PRIOR, prior_stopped_upper)

    new_g = floor(D_SUFFIX / (C_G - paid)) + 1
    assert new_g == 18531230
    assert C_G - D_SUFFIX / (new_g - 1) <= paid < C_G - D_SUFFIX / new_g
    stock = runpy.run_path(str(source / "activation.py"))["resource_receipt"]
    margins = runpy.run_path(str(source / "outer_budget.py"))["margins"]
    finance = runpy.run_path(str(source / "outer_clock.py"))["financial_checks"]
    all_profiles = {}
    for label, rate, heights, gaussian in (("entry", ENTRY_K, ENTRY_H, ENTRY_G),
                                            ("terminal", K_TRIAL, HEIGHTS, new_g)):
        strict, functional, margin = margins(rate, GUARD / 5, rate + GUARD, C_G - D_SUFFIX / gaussian)
        assert len(strict) == 54 and len(functional) == 4 and min(*strict, *functional, margin) > 0
        resources = stock(SimpleNamespace(rank_logs=heights, complex_log=gaussian, eta=ETA))
        assert min(resources["retimed_first_stripe_margin"], resources["retimed_all_size_margin_floor"]) > 1024
        assert all(cut + 2 < height for cut, height in zip(resources["binary_cuts"], heights[1:]))
        all_profiles[label] = dict(strict=54, functional=4, margin=margin, stock=resources)
    resource = all_profiles["terminal"]["stock"]
    finite = 1 + finance()["early_log2_C_bound"]
    entry = max(finite, 1602 + 220 * ENTRY_G + 40 + 17 + 16384 * sum(ENTRY_H) + 25818582)
    premium = ceil((K_TRIAL - ENTRY_K) * resource["public_exponent_A"])
    recurring = 1 + max(entry + premium, finite, 1730 + 320 * trial_sum + 220 * new_g)
    assert (entry, finite, premium, recurring) == (125660241, 84500001, 8603, 4285082571)
    assert resource["public_exponent_A"] == 19182389 and resource["first_public_offset"] == 4
    assert recurring < CAP
    assert all(1024 <= h < 2**25 for h in (*ENTRY_H, ENTRY_G, *HEIGHTS, new_g))
    assert 92 * (2**25 - 1) < 2**32 and 1024 * (2**25 - 1) + 3 < 2**35
    assert 2 * 2048 * (2**25 + 1) + 7 * 2**24 < 2**40
    assert all(value.bit_length() <= 128 for rate in (K_TRIAL, ENTRY_K, ETA)
               for value in (rate.numerator, rate.denominator, 10**18))
    n, w = 2**68 + 2**40, 2**38
    d = 2 * w + 2
    lookup = 8 * (4 * w * n) * 512 * 128
    local = 2**16 * (d + 4) * (7 * d + 9) + 8 * 2**16 * (d + 4)**2
    setup = (n + 1) * (lookup + local + 2**120) * 2**32
    assert setup == result["native_setup_transition_upper"] < 2**228
    return dict(comparator=HEAD, predecessor_cap=CAP, predecessor_ordinary_sum_lower=min_sum,
                predecessor_gaussian_height_upper=prior_g_max, predecessor_stopped_upper=prior_stopped_upper,
                trial_kappa=K_TRIAL, exact_projected_gain=K_TRIAL - K_PRIOR,
                trial_stopped_upper_gap=K_TRIAL - prior_stopped_upper,
                trial_ordinary_heights=HEIGHTS, trial_gaussian_height=new_g,
                trial_recurring_log2_C=recurring, trial_recurring_saving=CAP - recurring,
                entry_conversion=premium, setup_transition_upper=setup,
                setup_additional_indexed_actions=2**40, signed_arithmetic=all_profiles)


def check(args):
    base, pins = bind(args)
    result = json.loads((base / "RESULT-460.json").read_bytes())
    pins["gate/check_offset8.py"] = sha256(Path(__file__).read_bytes()).hexdigest()
    print("Authenticated exact comparator and provenance inputs", file=sys.stderr, flush=True)
    with TemporaryDirectory(prefix="offset8-first-gate-") as scratch:
        tree = Path(scratch)
        peer = runpy.run_path(str(base / "upstream_verify.py"))["restore"](tree)
        calendar = pin(peer / "typed_transport.py", CALENDAR_SHA)
        for literal in (b"size = (e - 8) * k", b"period = 4 * ceil(Q(n, 4 * size))",
                        b"scale_step=Q(6, 5)", b"share / len(owners)",
                        b"measure.mass(left_end, right_end)[0]"):
            assert literal in calendar
        pins["archive/research/frequency-weighted-native-multiplier/typed_transport.py"] = CALENDAR_SHA
        runpy.run_path(str(base / "prepare.py"))["materialize"](peer)
        runpy.run_path(str(base / "retune.py"))["install"](peer, "460")
        copyfile(base / "PREDECESSOR-RESULT.json", peer / "PREDECESSOR-RESULT.json")
        runtime = tree / "runtime"
        run([sys.executable, "-IB", str(peer / "bootstrap.py"), str(runtime)],
            check=True, timeout=30, capture_output=True, cwd=tree,
            env={**environ, "GIT_CEILING_DIRECTORIES": str(tree.parent)})
        assert pin(runtime / "typed_transport.py", CALENDAR_SHA) == calendar
        sys.path.insert(0, str(runtime))
        from upstream import install
        install()
        from grades import LOWER, UPPER_DIVISOR, numerical_recipe
        from installations import ENTRY, TERMINAL
        assert (LOWER, UPPER_DIVISOR) == (L, 1724)
        for profile, expected in ((ENTRY, (ENTRY_H, ENTRY_G, ENTRY_K)),
                                  (TERMINAL, (HEIGHTS, PRIOR_G, K_PRIOR))):
            assert (profile.rank_logs, profile.complex_log, profile.kappa) == expected
            assert (profile.eta, profile.positive_stop_denominator) == (ETA, 10**18)
        print("Restored the signed offset-8 allocator", file=sys.stderr, flush=True)
        priced = factor(numerical_recipe(TERMINAL.complex_log))
        print("Independently bounded the matched-suffix factor", file=sys.stderr, flush=True)
        priced.update(invoice(result, peer.parent / "tiered-native-multiplier" / "source"))
    priced.update(scope="One offset-8 price case; build and full independent replay remain separate gates",
                  cases=1, wall_seconds_cap=30, suffix_prior=SUFFIX_HEAD, source_pins=pins)
    print(json.dumps(priced, indent=2, sort_keys=True, default=str))


def timeout(_signum, _frame):
    raise TimeoutError("Offset-8 price screen reached its 30-second cap")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    for name in ("baseline", "integral", "pricer"):
        parser.add_argument("--" + name, type=Path, required=True)
    arguments = parser.parse_args()
    assert __debug__ and sys.version_info >= (3, 12)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    try:
        check(arguments)
    except (TimeoutError, TimeoutExpired):
        parser.exit(124, "Offset-8 price screen reached its 30-second cap\n")
    finally:
        signal.alarm(0)
