"""Independent directed price and one transport placement on the exact #8052 word."""

from argparse import ArgumentParser
from collections import Counter
from decimal import Decimal, Context, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction as Q
from hashlib import sha256
from itertools import islice
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import time


PINS = {
    "bootstrap.py": "e7609488216e31baf99d3a9b6acaba0e45b1a4c97288d563c43bb414fd0eb183",
    "installations.py": "dfd94b6ea6abf014bb8319b809ac476f480bb62f3a5d947da15805cb57498fb4",
    "transport.py": "98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9",
    "unpowered_price.py": "c273f2bcd46a114595ee669021aa6cd7223488f87cee0fe10bd762bc92177424",
    "RESULT.json": "73516f60cc9ede03c93f18d0514b237e895316e545053e04e6776aae8d7f87ad",
    "predecessor/predecessor-8030.tar.gz": "769d5a05cc1373fa22ed5956af636992fcd19d7e5c1753a32033a73c358cd31c",
}
C_OLD, C_NEW = Q(2092819, 2**29), Q(1071523491, 2**38)
K_OLD, K_NEW = Q(".003898171"), Q(".0038981721342")
H, D = 20_000_000, 10**18
DECIMAL = Context(prec=82, rounding=ROUND_HALF_EVEN)
LOWER = DECIMAL.copy()
UPPER = DECIMAL.copy()
LOWER.rounding = ROUND_FLOOR
UPPER.rounding = ROUND_CEILING


def need(value, description):
    if not value:
        raise ValueError(description)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def power_bounds(rank, exponent):
    """Decimal ln/exp are correctly rounded to nearest; one neighboring value covers error."""
    rank = Q(rank)
    x = DECIMAL.divide(Decimal(rank.numerator), Decimal(rank.denominator))
    need(Q(x) == rank, "all ranks must be exactly representable")
    exponent = Q(exponent)
    numerator, denominator = Decimal(exponent.numerator), Decimal(exponent.denominator)
    t_lo, t_hi = LOWER.divide(numerator, denominator), UPPER.divide(numerator, denominator)
    log = DECIMAL.ln(x)
    logs = DECIMAL.next_minus(log), DECIMAL.next_plus(log)
    lo = min(LOWER.multiply(t, logarithm) for t in (t_lo, t_hi) for logarithm in logs)
    hi = max(UPPER.multiply(t, logarithm) for t in (t_lo, t_hi) for logarithm in logs)
    return Q(DECIMAL.next_minus(DECIMAL.exp(lo))), Q(DECIMAL.next_plus(DECIMAL.exp(hi)))


def margin(target, paid, c):
    delta = target.copy()
    delta.subtract(paid)
    minimum = maximum = Q()
    for rank, count in delta.items():
        lo, hi = power_bounds(rank, 1 - c)
        a, b = sorted((count * lo, count * hi))
        minimum += a
        maximum += b
    return [str(minimum), str(maximum)]


def dyadic_cell_fractions(peer, target, paid):
    """Recompute the literal compiler fractions from immutable source inputs."""
    from unpowered_price import certify

    old_margin, old = certify(C_OLD, (target, paid))
    new_margin, new = certify(C_NEW, (target, paid))
    need(len(old) == len(new) == 54 and old.keys() == new.keys(), "same 54 support cells")
    need(old[448, 1032] == new[448, 1032] == 1, "unit largest loan")
    need(0 < new_margin < old_margin, "tightened raw reserve")
    for cells in (old, new):
        need(min(cells.values()) / sum(target.values()) > Q(1, 2**64), "finite split floor")
        need(max(max(x.numerator.bit_length(), x.denominator.bit_length()) for x in cells.values()) < 512,
             "defined arithmetic fraction cap")
        need(all(4 * k >= 5 * r for r, k in cells), "strict downward loan")
    change = [(r, k) for r, k in sorted(old) if old[r, k] != new[r, k]]
    r, k = change[0]
    return old, new, {
        "changed_fractions": len(change),
        "changed_fraction_keys": [[str(r), str(k)] for r, k in change],
        "first_changed_fraction": [str(r), str(k), str(old[r, k]), str(new[r, k])],
        "old_max_fraction_bits": max(max(x.numerator.bit_length(), x.denominator.bit_length()) for x in old.values()),
        "new_max_fraction_bits": max(max(x.numerator.bit_length(), x.denominator.bit_length()) for x in new.values()),
    }


def placement():
    """Reconstruct the real H=20m root geometry and run its first nonidentity physical align."""
    from periodic import Job
    from raw48 import ComplexRaw
    from strong_complex import load_changed, word
    from transport import axes
    from upstream import HERE

    native = word(*load_changed(HERE / "inputs"))
    roots = [port for port in native.targets if port.rank == 129 and port.tag[:2] == ("root", "rotated")]
    need(len(roots) == 384, "literal scale-eight rotated roots")
    rank = 1 << H
    upper = 2 * (rank // (2048 * 1224))
    band = 2 * ((3 * upper) // 8)
    need(upper * 448 < band * 1032 < (band + 2) * 1032 < rank * 448, "external interval")
    size = 1032 * (band - 8)
    period = 4 * ((rank + 4 * size - 1) // (4 * size))
    five = (period * size - rank) // 4
    manual = tuple(ticket // 5 if ticket < 5 * five else ticket - 4 * five
                   for ticket in (0, period, 2 * period))
    need(manual == tuple(islice(axes(rank, size, period, 0), 3)), "periodic tickets")
    swaps = []

    class Tape:
        def swap(self, left, right, width, exchange):
            swaps.append((left, right, width))

    class Columns:
        window = 1
        swap = None

    body = ComplexRaw(None, {}, Columns(), low=0, bundle=1, slots=rank)
    route = body.align(Tape(), Job(0, manual), ComplexRaw.axis_list(3, (0,)))
    need(route and swaps[0] == (1, manual[1], 1), "physical first swap")
    return {"root_tag": list(roots[0].tag), "period": period, "first_tickets": manual,
            "first_physical_swap": swaps[0], "changed": False}


def first_band():
    """Directed normalized masses prove that the original and changed first epoch boundaries differ."""
    x, y = 32768, 32770
    i = []
    for c in (C_OLD, C_NEW):
        t = 1 - c
        x_lo, x_hi = power_bounds(x, -t)
        y_lo, y_hi = power_bounds(y, -t)
        i.append(((x_lo - y_hi) / t, (x_hi - y_lo) / t))
    gap = i[1][0] - i[0][1]
    need(gap > Q(1, 2**96), "first band grows by more than one production replica")
    return {"band": [x, y], "normalized_mass_increase_lower": str(gap),
            "production_volume_log2": 6 * H, "direction": "new ceiling of replica count is larger"}


def check(old, cand):
    for key, expected in PINS.items():
        need(digest(old / key) == expected, f"pin {key}")
    for key in ("predecessor/predecessor-8030.tar.gz", "transport.py", "unpowered_price.py",
                "strong-bit-k7.json.gz", "retimed_supplier.py", "machine.patch", "receiver.patch"):
        need(digest(old / key) == digest(cand / key), f"same physical source {key}")
    old_result, new_result = (json.loads((path / "RESULT.json").read_bytes()) for path in (old, cand))
    old_profile, new_profile = (result["profiles"]["extended"] for result in (old_result, new_result))
    for key in ("binary_H", "numerical_H", "width_logs", "geometry", "public_exponent_A",
                "log2_fixed_setup_and_install_le", "log2_ordinary_clock_le", "log2_C_le"):
        need(old_profile[key] == new_profile[key], f"same installed size {key}")
    need(Q(old_profile["kappa"]) == K_OLD and Q(new_profile["kappa"]) == K_NEW,
         "exact installed profile claims")
    need(old_result["first_numerical_placement"] == new_result["first_numerical_placement"],
         "same real physical ticket in serialized old and new installation")
    old_cap = C_OLD - Q(39, 256 * H) - Q(5, D)
    new_cap = C_NEW - Q(39, 256 * H) - Q(5, D)
    need(K_OLD < old_cap < K_NEW < new_cap, "positive and negative fixed-carrier controls")
    sys.path.insert(0, str(cand))
    from bootstrap import install as bootstrap
    with TemporaryDirectory(prefix="independent-price-") as temp:
        tree = Path(temp)
        bootstrap(tree)
        sys.path.insert(0, str(tree))
        from upstream import install as install_upstream
        install_upstream()
        from installations import EXTENDED, GAUSSIAN_C
        need(EXTENDED.kappa == K_NEW and GAUSSIAN_C == C_NEW and EXTENDED.complex_log == H and
             EXTENDED.positive_stop_denominator == D, "candidate installation interface")
        from strong_complex import load_changed, word
        from upstream import HERE
        raw = word(*load_changed(HERE / "inputs"))
        target = Counter(scale * p.rank for scale in (1, 8) for p in raw.targets)
        paid = Counter(scale * p.rank for scale in (1, 8) for p in raw.paid)
        paid[1] -= 1008
        paid[Q(1, 2)] += 2016
        need((sum(target.values()), sum(paid.values())) == (105216, 564144), "real inventory")
        old_margin, new_margin = (margin(target, paid, c) for c in (C_OLD, C_NEW))
        need(Q(old_margin[0]) > Q(new_margin[1]) > Q(new_margin[0]) > 0, "rigorous raw margins")
        _, _, cells = dyadic_cell_fractions(old, target, paid)
        ticket = placement()
        recorded = new_result["first_numerical_placement"]["placements"][str(H)]
        need(recorded["period"] == ticket["period"] and recorded["first_tickets"] == list(ticket["first_tickets"]),
             "rooted physical ticket matches receipt")
        band = first_band()
    return {"pins": PINS, "candidate_installation_sha256": digest(cand / "installations.py"),
            "candidate_result_sha256": digest(cand / "RESULT.json"),
            "old_margin_directed": old_margin, "new_margin_directed": new_margin,
            "old_fixed_carrier_ceiling": str(old_cap), "new_fixed_carrier_ceiling": str(new_cap),
            "gain_over_old_claim": str(K_NEW - K_OLD), "gain_over_old_cap": str(K_NEW - old_cap),
            "old_price_rejects_new_claim": True, "old_positive_control": True,
            "candidate_claim": str(K_NEW), "cells": cells, "production_placement": ticket,
            "first_replica_boundary": band,
            "authenticated_abstract_transport_only": True,
            "H": H, "D": D, "same_width_and_reported_clock_caps": True}


def main():
    parser = ArgumentParser(description=__doc__)
    for arg in ("old", "candidate", "out"):
        parser.add_argument("--" + arg, required=True, type=Path)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        info = check(args.old.resolve(), args.candidate.resolve())
        args.out.write_text(json.dumps(info, indent=2, sort_keys=True) + "\n")
        return 0
    start = time.monotonic()
    try:
        code = subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]], timeout=45).returncode
    except subprocess.TimeoutExpired:
        code = 124
    print(f"exit={code} elapsed={time.monotonic() - start:.6f}s cap=45")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
