"""Independently bound the first transport cut for two Gaussian split removals."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

PINS = {
    "verify.py": "513229ad495efab7a738644d291eb19f84bc751d6a606e84183229d4549549ab",
    "RESULT.json": "3d85ccaf415b33702951ceb14b78fa1f7f0964ba3f201bf07b9e8a6e96882220",
    "peer8052.tar.gz": "37bf1d8c53553806ec7723b865a3e779be40d3b19a0466575adb9c5388c0198c",
}
ARITHMETIC_PIN = "bc2a8de7028287d6c816b8caed9b2b686e2b50449b7e8f67d55cd5dd958f381c"
HEIGHT = 20_000_000
STOP_DEN = 10**18
OLD = Q(".0038981721342")
CURRENT_C = Q(1071523491, 2**38)
DEBIT = Q(39, 256 * HEIGHT) + Q(5, STOP_DEN)
HALF = Q(1, 2)
TRIAL = Q(133940467, 2**35)
CLAIM = Q(".0038981730255")
MASSES = 2**112


def need(condition, message):
    if not condition:
        raise ValueError(message)


def checked_read(path, expected):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == expected, f"Pin differs: {path.name}")
    return data


def axis_census(native, splits):
    targets = Counter(scale * port.rank for scale in (1, 8) for port in native.targets)
    paid = Counter(scale * port.rank for scale in (1, 8) for port in native.paid)
    paid[1] -= splits
    paid[HALF] = 2 * splits
    return targets, paid


def quantile_cells(target, paid):
    """Intersect cumulative mass intervals from opposite ends of the Hall cuts."""
    available = sum(target.values())
    demand = sum(paid.values())
    left, right = Q(), Q()
    bands = {}
    shares = {}
    for rank, mass in sorted(target.items(), reverse=True):
        end = right + Q(mass * demand, available)
        bands[rank] = right, end
        right = end
    for rank, mass in sorted(paid.items(), reverse=True):
        end = left + mass
        for target_rank, (start, stop) in bands.items():
            overlap = min(end, stop) - max(left, start)
            if overlap > 0:
                need(4 * target_rank >= 5 * rank, "Invalid quantile support")
                shares[rank, target_rank] = overlap / mass
        left = end
    need(left == right, "All mass placed")
    for rank in paid:
        need(sum(q for (r, _), q in shares.items() if r == rank) == 1,
             f"All paid mass at {rank} was assigned")
    return shares


def as_interval(lower, upper):
    return [str(lower), str(upper)]


def discovery(package, arithmetic):
    for name, digest in PINS.items():
        checked_read(package / name, digest)
    checked_read(arithmetic, ARITHMETIC_PIN)
    dyadic_bounds = lru_cache()(runpy.run_path(str(arithmetic))["power_bounds"])
    restore = runpy.run_path(str(package / "verify.py"))
    with TemporaryDirectory(prefix="r368-independent-") as d:
        root = Path(d)
        restore["restore"](root)
        restore["edit_installation"](root)
        sys.path.insert(0, str(root))
        from bootstrap import install

        installed = root / "machine"
        install(installed)
        sys.path.insert(0, str(installed))
        from upstream import HERE, install as install_inputs

        install_inputs()
        from installations import BINARY_C, EXTENDED, GAUSSIAN_C
        from strong_complex import load_changed, word

        native = word(*load_changed(HERE / "inputs"))
        need((EXTENDED.kappa, EXTENDED.complex_log, EXTENDED.positive_stop_denominator, GAUSSIAN_C)
             == (OLD, HEIGHT, STOP_DEN, CURRENT_C), "Pinned complete installation")

    def moment(axis, c):
        intervals = [(n, dyadic_bounds(r, 1 - c)) for r, n in axis.items()]
        return (sum(n * t[0] for n, t in intervals),
                sum(n * t[1] for n, t in intervals))

    def margin(targets, paid, c):
        tl, th = moment(targets, c)
        pl, ph = moment(paid, c)
        return tl - ph, th - pl

    def first_cut(targets, paid, low, high):
        unit = targets[1]
        half_low = paid[HALF] * dyadic_bounds(HALF, 1 - low)[0]
        half_high = paid[HALF] * dyadic_bounds(HALF, 1 - high)[1]
        other = paid.copy()
        del other[HALF]
        p0, p1 = moment(other, high)[0], moment(other, low)[1]
        t0, t1 = moment(targets, high)[0], moment(targets, low)[1]
        return (half_low - unit * (half_high + p1) / t0,
                half_high - unit * (half_low + p0) / t1)

    def decreasing_on_window(targets, paid, low, high):
        from decimal import Context, Decimal

        ctx = Context(prec=82)
        delta = targets.copy()
        delta.subtract(paid)
        total = Q()
        for r, n in delta.items():
            if r == 1 or not n:
                continue
            r = Q(r)
            real = ctx.divide(Decimal(r.numerator), Decimal(r.denominator))
            log = ctx.ln(real)
            logs = Q(ctx.next_minus(log)), Q(ctx.next_plus(log))
            powers = (*dyadic_bounds(r, 1 - low), *dyadic_bounds(r, 1 - high))
            total += min(n * q * l for q in (min(powers), max(powers)) for l in logs)
        need(total > 0, "Raw signed margin decreases in c")
        return total

    unit_tags = [port.tag for port in native.paid if port.rank == 1]
    ballots = {}
    for splits in (1005, 1006, 1008):
        target, paid = axis_census(native, splits)
        need(target[1] == 1008 and sum(target.values()) == 105216,
             "Literal two-copy productive census")
        need(sum(paid.values()) == 564144 - (1008 - splits), "Literal padded payments")
        lo, hi = CURRENT_C, Q(".00389819")
        slope = decreasing_on_window(target, paid, lo, Q(".004"))
        need(margin(target, paid, lo)[0] > 0, "Positive old trial")
        need(margin(target, paid, hi)[1] < 0, "Negative upper trial")
        for _ in range(28):
            mid = (lo + hi) / 2
            lower, upper = margin(target, paid, mid)
            if lower > 0:
                lo = mid
            elif upper < 0:
                hi = mid
            else:
                raise ValueError("Directed sign indeterminate")
        cut = first_cut(target, paid, CURRENT_C, hi)
        need(cut[1] < 0 if splits == 1005 else cut[0] > 0, "Strict support decision")
        trials = [CURRENT_C] if splits != 1006 else [CURRENT_C, TRIAL]
        priced = {}
        for c in trials:
            raw = margin(target, paid, c)
            support = first_cut(target, paid, c, c)
            need((support[1] < 0) == (splits == 1005), "Support at tested dyadic")
            cert = {}
            if splits != 1005:
                a = {r: n * int(dyadic_bounds(r, 1 - c)[0] * MASSES) for r, n in target.items()}
                b = {r: n * (1 + int(dyadic_bounds(r, 1 - c)[1] * MASSES)) for r, n in paid.items()}
                need(sum(a.values()) > sum(b.values()), "Directed funding")
                cells = quantile_cells(a, b)
                minshare = min(cells.values()) / sum(paid.values())
                bits = max(max(q.numerator.bit_length(), q.denominator.bit_length())
                           for q in cells.values())
                need(minshare > Q(1, 2**64) and cells[448, 1032] == 1, "Transport floors")
                need(bits < 512, "Actual compiler fraction width envelope")
                need(Q(moment(paid, c)[0], moment(target, c)[1]) > Q(99, 100),
                     "Global lower paid/target ratio")
                cert = {"positive_cells": len(cells), "min_cell_over_paid_count": str(minshare),
                        "max_cell_bit_width": bits}
            priced[str(c)] = {"relative_supply": as_interval(*support),
                             "raw_signed_margin": as_interval(*raw), **cert}
        ballots[str(splits)] = {
            "at_trial": priced,
            "raw_crossing_bracket": as_interval(lo, hi),
            "optimistic_complete_bracket": as_interval(lo - DEBIT, hi - DEBIT),
            "cut_through_upper_crossing": as_interval(*cut),
            "raw_derivative_negated_lower": str(slope),
            "changed_base_copy_tags": unit_tags[splits:1008],
        }
    need(CLAIM > Q(ballots["1008"]["optimistic_complete_bracket"][1]), "Separates from old raw cap")
    need(CLAIM + DEBIT < TRIAL, "Candidate pays both declared signed debits")
    old_t, old_p = axis_census(native, 1008)
    negative_control = margin(old_t, old_p, TRIAL)
    need(negative_control[1] < 0, "Old inventory fails the candidate trial")

    stripe, guard, largest_rank = 32768, 1024, 1032
    rounding = Q(1, 2**128)
    factor = (
        Q(256, 255) * Q(4097, 4096) * Q(1028, 1024)
        * dyadic_bounds(guard * 1224 * stripe, TRIAL)[1]
        * (1 + Q(64, stripe) + rounding) / ((1 - Q(10, stripe)) * (1 - rounding)**3)
    )
    need(factor**256 < 2**39 and dyadic_bounds(largest_rank, TRIAL)[1] < Q(106, 100)
         and 1 - TRIAL > Q(996, 1000), "Independent analytic 39-bit debit")
    prior = Q()
    for height in EXTENDED.rank_logs:
        ceiling = min(EXTENDED.eta, (249 * (BINARY_C - Q(11, 8 * height)) + prior) / 250)
        prior = Q(int(ceiling * 10**21) - 1, 10**21)
    need(CLAIM + Q(5, STOP_DEN) < prior, "Fixed ordinary hierarchy has slack")
    return {
        "source_pins": PINS,
        "arithmetic_pin": ARITHMETIC_PIN,
        "height": HEIGHT,
        "stop_denominator": STOP_DEN,
        "head": "e25494616bf149217644ce08d949181ea3600e13",
        "debit": str(DEBIT),
        "old_claim": str(OLD),
        "provisional_c": str(TRIAL),
        "provisional_kappa": str(CLAIM),
        "provisional_gain": str(CLAIM - OLD),
        "old_inventory_at_new_trial": as_interval(*negative_control),
        "complete_positive_margin": str(TRIAL - DEBIT - CLAIM),
        "ordinary_strict_capacity_rounded_down": str(prior),
        "analytic_debit_factor_upper_rational": str(factor),
        "verdict": "1005 first cut excluded; 1006 transport viable, literal replay pending",
        "cases": ballots,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("package", "arithmetic", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        receipt = discovery(args.package.resolve(), args.arithmetic.resolve())
        args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    else:
        start = monotonic()
        result = subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]],
                                timeout=45)
        print("Discovery status", result.returncode, monotonic() - start)
        result.check_returncode()


if __name__ == "__main__":
    main()
