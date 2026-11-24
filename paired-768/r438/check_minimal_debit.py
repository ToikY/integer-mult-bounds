"""Bracket the first funded ordinary debit for two exact tariffs at fixed sources."""

from argparse import ArgumentParser
import ast
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, isqrt
import os
from pathlib import Path
from runpy import run_path
import sys
from tempfile import TemporaryDirectory, gettempdir


PINS = {
    "package/verify.py": "7bc8a5a2a6b90bdacc3dd89c57f14b380eea3530a7eaaa5e1be7e10ae6f5d3b2",
    "package/RESULT.json": "30f83c4820557c0ca3461928c5000da6a0c9fc4b98b3bf6539df8bdb18fb0d93",
    "handoff/paired-768/r437/SCREEN.json": "17f22f78bb86bc7d6dd152179fbdea96f0c344b96402b8e4fb61049f2c19f51b",
}
TARIFFS = {"peer8098": Q(10981863, 4703998), "N_at_least_16": Q(15009853977, 6430103800)}
DEN = 1 << 20
PROBE_CAP = 32


def checked(path, pin):
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[pin]:
        raise ValueError(f"Exact source differs at {pin}")
    return data


def get_powers(path):
    tree = ast.parse(path.read_bytes())
    fn, = (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "powers")
    scope = {"GRID": 2**192, "Q": Q, "ceil": ceil, "isqrt": isqrt}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "exact independent price", "exec"), scope)
    return scope["powers"]


def full_envelope(rate, lower, paid, cells, powers, ratio_powers):
    """Enclose both signs of the exact periodic-integral price computation."""
    t, delta = 1 - rate, Q(1, 2**128)
    psi_lo = psi_hi = num_lo = num_hi = Q(0)
    for (r, k), share in cells.items():
        assert 0 < r and 5*r <= 4*k and share > 0
        count = paid[r] * share
        lo, hi = ratio_powers(k, r, rate)
        psi_lo += count*r*(lo - 1)/rate
        psi_hi += count*r*(hi - 1)/rate
        rk_lo, rk_hi = ratio_powers(r, k, t)
        tail_lo, tail_hi = ratio_powers(lower*r, lower*k + 4*r, t)
        num_lo += count*((9*k - 8*r)*rk_lo - r*tail_hi + r*delta)
        num_hi += count*((9*k - 8*r)*rk_hi - r*tail_lo + r*delta)
    assert 0 < psi_lo <= psi_hi and 0 < num_lo <= num_hi
    fringe_lo, fringe_hi = num_lo/(t*psi_hi), num_hi/(t*psi_lo)
    lower_power, upper_power = powers(1024*134*lower, rate)
    common = Q(256, 255)*Q(4097, 4096)*Q(1028, 1024)/(1-delta)**4
    return (common*lower_power*(1 + fringe_lo/lower + delta),
            common*upper_power*(1 + fringe_hi/lower + delta))


def book(factor, powers, cap):
    lo, hi = factor
    assert 2 < lo <= hi < 4
    trials = {}

    def probe(tick):
        if tick not in trials:
            if len(trials) >= cap:
                raise RuntimeError("Debit probe budget exhausted")
            floor, ceiling = (2*p for p in powers(2, Q(tick, DEN) - 1))
            if hi < floor:
                trials[tick] = True
            elif lo > ceiling:
                trials[tick] = False
            else:
                raise ArithmeticError(f"Directed intervals overlap at tick {tick}")
        return trials[tick]

    rejected, accepted = 1411000, 1416000
    assert not probe(rejected) and probe(accepted)
    while accepted - rejected > 1:
        mid = (accepted + rejected)//2
        if probe(mid):
            accepted = mid
        else:
            rejected = mid
    assert probe(accepted) and not probe(accepted - 1)
    return {"first_funded_tick": accepted, "preceding_tick_rejected": rejected,
            "bisection_probes": len(trials)}


def check(package, screen_path):
    checked(package / "verify.py", "package/verify.py")
    result = json.loads(checked(package / "RESULT.json", "package/RESULT.json"))
    screen = json.loads(checked(screen_path, "handoff/paired-768/r437/SCREEN.json"))
    assert Q(result["ordinary_child_tariff"]) == TARIFFS["peer8098"]
    assert Q(screen["candidate_tariff"]) == TARIFFS["N_at_least_16"]
    assert screen["charged_geometric_budget"] == result["ordinary_child_geometric_budget"] == 2401
    assert screen["kept_reserve"] == result["ordinary_reserve"] == "256/255"
    heights = [*result["entry"]["ordinary_H"], *result["terminal"]["ordinary_H"]]
    assert min(heights) == screen["minimum_priced_H"] == 3000 and screen["used_domain_floor_N"] == 16
    loader = run_path(str(package / "verify.py"))
    loader["authenticate"]()
    loader["reserve"](Path(gettempdir()))
    with TemporaryDirectory(prefix="minimal-debit-") as temporary:
        scratch = Path(temporary).resolve()
        env = dict(os.environ, **loader["THREAD_ENV"], TMPDIR=str(scratch))
        peer = loader["prepare"](scratch, env)
        runtime = scratch / "runtime"
        loader["install"](peer, runtime, env)
        saved_argv = sys.argv
        try:
            sys.argv = [str(peer / "receipt.py"), str(runtime)]
            source = run_path(sys.argv[0])
        finally:
            sys.argv = saved_argv
        target, paid = source["raw_moments"](source["graph"](), source["caller"]())
        rate, lower = source["BINARY_C"], source["ORDINARY_FLOOR"]
        margin, cells = source["certify"](rate, (target, paid))
        assert margin > 0 and cells and lower == result["ordinary_floor"] == 1156
        assert (sum(target.values()), sum(paid.values()), len(cells)) == (18906, 104652, 24)
        power = source["power_interval"]
        unit = source["UNIT"]
        assert unit == 2**112

        def power112(base, exponent):
            assert Q(base).denominator == 1
            return tuple(Q(value, unit) for value in power(int(base), exponent))

        def ratio112(numerator, denominator, exponent):
            assert Q(numerator).denominator == Q(denominator).denominator == 1
            # The registered 112-bit proof rounds each original power first.
            n_lo, n_hi = power(int(numerator), exponent)
            d_lo, d_hi = power(int(denominator), exponent)
            return Q(n_lo, d_hi), Q(n_hi, d_lo)

        power192 = get_powers(peer / "independent_price.py")

        def ratio192(numerator, denominator, exponent):
            return power192(Q(numerator, denominator), exponent)

        results = {}
        source_upper = source["tape_factor_periodic"](134, rate, lower, paid, cells)
        for bits, powers, ratios in ((112, power112, ratio112), (192, power192, ratio192)):
            lo, hi = full_envelope(rate, lower, paid, cells, powers, ratios)
            assert 0 < lo <= hi <= source_upper
            if bits == 112:
                assert hi == source_upper
            remaining = PROBE_CAP
            directed = {}
            for name, price in TARIFFS.items():
                directed[name] = book((lo*price, hi*price), powers, remaining)
                remaining -= directed[name]["bisection_probes"]
            results[str(bits)] = directed
    first = {name: results["112"][name]["first_funded_tick"] for name in TARIFFS}
    assert all(first[name] == results["192"][name]["first_funded_tick"] for name in TARIFFS)
    return {"scope": "Fixed #8098 ordinary envelope and two tariffs only. No signed or full candidate replay.",
            "pinned_inputs": PINS, "tariffs": {name: str(value) for name, value in TARIFFS.items()},
            "kept_ordinary_reserve": "256/255", "charged_geometric_budget": 2401,
            "histogram_counts": [18906, 104652, 24], "maximum_probes_per_precision": PROBE_CAP,
            "debit_denominator": DEN, "directed_results": results,
            "distinct_funded_ticks": first["peer8098"] - first["N_at_least_16"]}


if __name__ == "__main__":
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--screen", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.package.resolve(), args.screen.resolve()), indent=2))
