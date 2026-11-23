"""Price one fixed offset-8 matched-suffix transfer into #8081."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor, isqrt
from pathlib import Path
import signal
from subprocess import check_output
import tarfile
from types import SimpleNamespace

HEAD = "510113821774bb27f7ddaad4e8b94837a1c2cf52"
SUFFIX_HEAD = "dd2e2ff28102557f7c30619d6abd8a861e363d1d"
PACKAGE = "research/p104-expanded-budget-25bit"
PINS = {
    "RESULT-460.json": "4e173fd0a9f4b593baf706a00899cc1336dae5eab922c43e6551775256733f63",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "SETUP-PROOF.md": "e7955f69cdfae30a08a120ebc60c803aa2cc11b8a30c06ace6f29ccbba5fae8f",
    "prepare.py": "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3",
    "retune.py": "ceb036d4e2c375eea74a7d20e2aca5a99f432814d235372dd6ce4bc1adea7a3e",
}
INTEGRAL = "79f4d93bf8b39510c29c8648164c31e6fd730b72b20f5e807cfbd78cdf465683"
PRICER = "880bbfc11428cadc438722eb9d058f43e06f8990e81214fa20c27ebb628390c8"
C_B, C_G = Q(4391986206293, 2**50), Q(17145637307, 2**42)
D_B, OLD_D, NEW_D = Q(11239, 8192), Q(64939, 524288), Q(130699669, 2**30)
ETA, GUARD = Q(39, 10000), Q(5, 10**18)
OLD_H, OLD_G, OLD_K = (8192, 38102, 604362), 18845936, Q(".00389846")
H, ENTRY_H, ENTRY_G, ENTRY_K = (8192, 38102, 604363), (3000, 3080), 1024, Q(".00345")
CAP = 4354317571


def pin(path, expected):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == expected, path
    return data


def ordinary(heights):
    booked = Q(0)
    for index, height in enumerate(heights, 1):
        upper = min(ETA, (249 * (C_B - D_B / height) + booked) / 250)
        if index == len(heights):
            return upper
        booked = Q(floor(upper * 10**21) - 1, 10**21)


def power_interval(exponent):
    unit = 1 << 192
    root_lo = root_hi = 2 * unit
    lo = hi = unit
    assert exponent.denominator.bit_count() == 1
    for bit in range(exponent.denominator.bit_length() - 2, -1, -1):
        root_lo = isqrt(root_lo * unit)
        root_hi = isqrt(root_hi * unit - 1) + 1
        if exponent.numerator >> bit & 1:
            lo = lo * root_lo // unit
            hi = ceil(Q(hi * root_hi, unit))
    return Q(lo, unit), Q(hi, unit)


def inspect(args):
    archive_root = args.peer / PACKAGE

    def git(*command):
        return check_output(["git", "-C", args.peer, *command])

    assert git("rev-parse", "HEAD").decode().strip() == HEAD
    assert not git("status", "--porcelain")
    originals = {name: pin(archive_root / name, digest) for name, digest in PINS.items()}
    for name, data in originals.items():
        assert git("show", f"{HEAD}:{PACKAGE}/{name}") == data
    proof = pin(args.integral, INTEGRAL).decode()
    code = pin(args.pricer, PRICER).decode()
    assert "8, 1874" in proof and "130699669/2^{30}" in proof
    assert "1+1032/263772" in proof
    assert "does not change the installed calendar" in code
    assert "9 * (k - r) + t * r * r / (2 * k * lower)" in code
    assert "typed_transport.py" not in originals["prepare.py"].decode()
    assert "typed_transport.py" not in originals["retune.py"].decode()
    baseline = json.loads(originals["RESULT-460.json"])
    manifest = json.loads(originals["PEER-SOURCE.json"])
    assert manifest["head"] == "cbe847a953b971f9c6c5a0a6661e2008acd29086"
    assert manifest["archive_sha256"] == PINS["peer8057.tar.gz"]
    assert Q(baseline["ordinary_finite_debit"]) == D_B
    assert baseline["ordinary_child_contraction"] == "375/376"
    actual = baseline["gaussian"]
    assert Q(actual["raw_loss"]) == OLD_D and actual["weights"] == [5, 451]
    assert (actual["grade_cells"], actual["typed_cells"]) == (51, 88)
    assert (actual["finite_loss"]["lower_band"], actual["finite_loss"]["upper_scale"]) == (1874, 263772)
    with tarfile.open(archive_root / "peer8057.tar.gz") as bundle:
        def read(member):
            with bundle.extractfile(member) as source:
                data = source.read()
            assert sha256(data).hexdigest() == manifest["files_sha256"][member]
            return data

        calendar = read("research/frequency-weighted-native-multiplier/typed_transport.py")
        assert b"size = (e - 8) * k" in calendar
        assert b"period = 4 * ceil(Q(n, 4 * size))" in calendar
        functions = []
        for module, name in (("activation", "resource_receipt"), ("outer_budget", "margins"),
                             ("outer_clock", "financial_checks")):
            source = f"research/tiered-native-multiplier/source/{module}.py"
            ns = {"__name__": module}
            exec(compile(read(source), source, "exec"), ns)
            functions.append(ns[name])
    return baseline, functions


def price(args):
    baseline, (stock, margins, finance) = inspect(args)
    factor_lo, factor_hi = Q("1.088033933515"), Q("1.088033933516")
    allowance, _ = power_interval(NEW_D)
    _, lower_tick_upper = power_interval(NEW_D - Q(1, 2**30))
    assert lower_tick_upper < factor_lo < factor_hi < allowance
    prior = baseline["terminal"]
    old_gaussian = C_G - OLD_D / OLD_G
    old_stop = old_gaussian - GUARD
    assert (Q(prior["kappa"]), tuple(prior["ordinary_H"]), prior["numerical_H"]) == (OLD_K, OLD_H, OLD_G)
    assert old_stop == Q(15407802515941573408769828489, 3952279237427200000000000000000)
    assert Q(prior["gaussian_rate"]) == old_gaussian and ordinary(OLD_H) > old_gaussian
    assert C_G - OLD_D / (OLD_G - 1) < OLD_K + GUARD
    smaller = sum(OLD_H) - 1
    root = Q(6324555320336758663997787088865437067439, 10**41)
    w1 = Q(1, 62500)
    assert root**2 < Q(1, 250) < (root + Q(1, 10**41))**2
    assert w1 / (8192**2) < (1 + root)**2 / (smaller - 8192)**2
    relaxed = C_B * (1 - Q(1, 250**3)) - Q(249, 250) * D_B * (w1 / 8192 + (1+root)**2 / (smaller-8192))
    assert relaxed < OLD_K + GUARD
    assert 1731 + 320 * sum(OLD_H) + 220 * OLD_G == CAP == baseline["complete_log2_C"]

    ordinary_stop = ordinary(H) - GUARD
    k = Q(ceil(ordinary_stop * 10**15) - 1, 10**15)
    paid = k + GUARD
    g = floor(NEW_D / (C_G - paid)) + 1
    assert old_stop < k < ordinary_stop <= k + Q(1, 10**15)
    assert ordinary(OLD_H) < paid < ordinary(H)
    assert C_G - NEW_D / (g - 1) <= paid < C_G - NEW_D / g
    signed = {}
    for label, rate, heights, g_height in (("entry", ENTRY_K, ENTRY_H, ENTRY_G), ("terminal", k, H, g)):
        strict, functional, margin = margins(rate, GUARD / 5, rate + GUARD, C_G - NEW_D / g_height)
        assert len(strict) == 54 and len(functional) == 4 and min(*strict, *functional, margin) > 0
        resources = stock(SimpleNamespace(rank_logs=heights, complex_log=g_height, eta=ETA))
        assert all(cut + 2 < height for cut, height in zip(resources["binary_cuts"], heights[1:]))
        signed[label] = {"stock": resources, "strict": 54, "functional": 4, "paid_margin": str(margin)}
    terminal = signed["terminal"]["stock"]
    assert min(terminal["retimed_first_stripe_margin"], terminal["retimed_all_size_margin_floor"]) > 1024
    finite = 1 + finance()["early_log2_C_bound"]
    entry = max(finite, 1602 + 220 * ENTRY_G + 40 + 17 + 16384 * sum(ENTRY_H) + 25818582)
    premium = ceil((k - ENTRY_K) * terminal["public_exponent_A"])
    recurring = 1 + max(entry + premium, finite, 1602 + 220 * g + 128 + 320 * sum(H))
    assert (entry, finite) == (125660241, 84500001) and recurring < CAP
    assert all(1024 <= height < 2**25 for height in (*ENTRY_H, ENTRY_G, *H, g))
    assert 92 * (2**25 - 1) < 2**32 and 1024 * (2**25 - 1) + 3 < 2**35
    assert all(value.bit_length() <= 128 for rate in (k, ENTRY_K, ETA)
               for value in (rate.numerator, rate.denominator, 10**18))
    assert 2 * 2048 * (2**25 + 1) + 7 * 2**24 < 2**40
    n, w = 2**68 + 2**40, 2**38
    datum = 2*w + 2
    lookup = 8 * (4*w*n) * 512 * 128
    local = 2**16 * (datum+4) * (7*datum+9) + 8 * 2**16 * (datum+4)**2
    setup = (n+1) * (lookup+local+2**120) * 2**32
    assert setup == baseline["native_setup_transition_upper"] < 2**228
    text = str(int(k * 10**15)).zfill(15)
    receipt = dict(
        scope="one conditional price case; no full setup execution or signed replay",
        comparator=HEAD, suffix_proof=SUFFIX_HEAD, cases=1, wall_seconds_cap=30,
        exact_kappa=str(k), decimal_kappa="0." + text, exact_gain=str(k-OLD_K),
        exact_comparator_stop=str(old_stop), exact_stop_gap=str(k-old_stop),
        ordinary_stopped_upper=str(ordinary_stop), gaussian_gain_control=str(C_G-NEW_D/g-paid),
        predecessor_height_control=str(paid-(C_G-NEW_D/(g-1))),
        old_cap=CAP, recurring_log2_C=recurring, recurring_saving=CAP-recurring,
        ordinary_heights=H, gaussian_height=g, max_native_height=max(*H,g), entry_conversion=premium,
        gaussian_debit=str(NEW_D), ordinary_debit=str(D_B), offset=8, lower_band=1874,
        exterior_factor=str(1 + Q(1032,263772)), factor_upper=str(factor_hi),
        factor_reserve=str(allowance-factor_hi), smaller_debit_deficit=str(factor_lo-lower_tick_upper),
        setup_transition_upper=setup, setup_charged_additional_indexed_actions=2**40, signed=signed,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


def timeout(_signum, _frame):
    raise TimeoutError("one matched-suffix price case hit 30 seconds")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    for name in ("peer", "integral", "pricer"):
        parser.add_argument("--"+name, type=Path, required=True)
    assert __debug__
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    try:
        price(parser.parse_args())
    except TimeoutError as error:
        parser.exit(124, str(error) + "\n")
    finally:
        signal.alarm(0)
