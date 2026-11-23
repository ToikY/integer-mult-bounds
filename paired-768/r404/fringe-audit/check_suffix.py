"""Recompute the exact K7 matched-suffix change from pinned source receipts."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor, isqrt
from pathlib import Path
import subprocess
import sys
import tarfile

COMPARATOR = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
FLOOR_HEAD = "04228ea5a1292cf8526a20037060f6fc6e15a858"
TRANSFER = "7164831a5dd9f5c6231bf4c3f4b2061d91cbfab559071a0a5d68966e3f7ac55c"
INVOICE = "d8b6844b4b10abdfe43cae6b37494b541006d0f194aa991647d337fe762409aa"
ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
K7 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
OLD_CELLS = "b4b855b293473f5c72b7042acf5963a0c66faa8637d3629376a3feb1cd62c0b8"
PACKAGE = "research/p104-weighted-capped-allocation-490950"
FLOOR_PACKAGE = "research/p104-weighted-ordinary-floor"
C = Q(4391986206293, 2**50)
T = 1 - C
L = 18960
DELTA = Q(1, 2**128)


def git(repository, *args):
    return subprocess.check_output(["git", "-C", repository, *args])


def bound_power(base, exponent, bits=192):
    """Inward and outward dyadic endpoints with no transcendental arithmetic."""
    assert base >= 1 and exponent >= 0 and exponent.denominator.bit_count() == 1
    unit = 1 << bits
    whole, rest = divmod(exponent.numerator, exponent.denominator)
    integer_power = Q(base) ** whole
    product_lo, product_hi = floor(unit * integer_power), ceil(unit * integer_power)
    root_lo, root_hi = floor(unit * base), ceil(unit * base)
    for place in range(exponent.denominator.bit_length() - 2, -1, -1):
        root_lo, root_hi = isqrt(root_lo * unit), isqrt(root_hi * unit - 1) + 1
        if rest & (1 << place):
            product_lo = product_lo * root_lo // unit
            product_hi = -(-product_hi * root_hi // unit)
    return Q(product_lo, unit), Q(product_hi, unit)


def independently_allocate(target, paid):
    lower = {k: n * bound_power(k, T, 112)[0] for k, n in target.items()}
    upper = {r: n * bound_power(r, T, 112)[1] for r, n in paid.items()}
    totals = sum(lower.values()), sum(upper.values())
    assert totals[0] > totals[1]
    remaining = {k: amount * totals[1] / totals[0] for k, amount in lower.items()}
    shares = {}
    for r in sorted(upper, reverse=True):
        demand = upper[r]
        for k in sorted(remaining, reverse=True):
            if 5 * r > 4 * k or demand == 0:
                break
            reserved = min(demand, remaining[k])
            if reserved:
                shares[r, k] = reserved / upper[r]
                demand -= reserved
                remaining[k] -= reserved
        assert demand == 0
    assert not any(remaining.values())
    assert len(shares) == 24
    assert all(sum(p for (outgoing, _), p in shares.items() if outgoing == r) == 1 for r in paid)
    assert all(sum(upper[r] * p for (r, incoming), p in shares.items() if incoming == k)
               <= lower[k] for k in target)
    canonical = "".join(f"{r} {k} {p}\n" for (r, k), p in sorted(shares.items()))
    assert sha256(canonical.encode()).hexdigest() == OLD_CELLS
    return shares


def outward(interval):
    scale = 10**18
    return [str(Q(floor(interval[0] * scale), scale)), str(Q(ceil(interval[1] * scale), scale))]


def exact_check(checkout, floor_checkout, transfer, invoice):
    for repository, head in ((checkout, COMPARATOR), (floor_checkout, FLOOR_HEAD)):
        assert git(repository, "rev-parse", "HEAD").decode().strip() == head
        assert git(repository, "status", "--porcelain") == b""
    old_floor_proof = git(floor_checkout, "show", f"{FLOOR_HEAD}:{FLOOR_PACKAGE}/PROOF.md")
    assert (b"below 7.439580927" in old_floor_proof and b"1+64/L" in old_floor_proof)
    assert sha256(transfer.read_bytes()).hexdigest() == TRANSFER
    assert all(needle in transfer.read_bytes() for needle in (
        b"V/(tL^t)+2U", b"10k residual axes", b"1+64/L", b"(1\xe2\x88\x9210/L)(1\xe2\x88\x92\xce\xb4)^3"))
    archive = checkout / PACKAGE / "peer8057.tar.gz"
    assert sha256(archive.read_bytes()).hexdigest() == ARCHIVE
    assert archive.read_bytes() == git(checkout, "show", f"{COMPARATOR}:{PACKAGE}/peer8057.tar.gz")
    assert archive.read_bytes() == git(floor_checkout, "show", f"{FLOOR_HEAD}:{FLOOR_PACKAGE}/peer8057.tar.gz")
    with tarfile.open(archive, "r:gz") as bundle:
        source = bundle.extractfile("research/tiered-native-multiplier/source/strong-bit-k7.json.gz")
        assert sha256(source.read()).hexdigest() == K7

    raw = invoice.read_bytes()
    assert sha256(raw).hexdigest() == INVOICE
    evidence = json.loads(raw)["factors"]
    assert evidence["k7_cell_sha256"] == OLD_CELLS
    target, paid = (Counter({int(k): v for k, v in evidence[name].items()})
                    for name in ("k7_target_by_label", "k7_paid_by_label"))
    assert target.total() == 18906 and paid.total() == 104652
    axes = sum(k * v for k, v in target.items())
    assert axes == 286098 < 2**25
    assert 0 < C < Q(4, 1000) and C + T == 1
    shares = independently_allocate(target, paid)
    ratio_powers = {pair: bound_power(Q(pair[1], pair[0]), C) for pair in shares}
    psi = tuple(sum(paid[r] * share * r * (ratio_powers[r, k][end] - 1) / C
                    for (r, k), share in shares.items()) for end in (0, 1))
    assert psi[0] > 386067
    fringe = 10 * axes / (T * psi[1]), 10 * axes / (T * psi[0])
    assert 7 < fringe[0] <= fringe[1] <= Q(evidence["k7_fringe"][1]) < 8

    min_height = 1024
    n = 2**min_height
    assert bound_power(L, T)[0] > 1024
    assert Q(n, 1024 * 134) - 2 > L * max(Q(k, r) for r, k in shares)
    assert max(Q(k, r) for r, k in shares) * (Q(n, 1024 * 134) + 2) < n
    assert 20 * axes < 2**30
    errors = Q(2**30, n**5), Q(2**46, n**4), Q(2**20, n**4)
    assert all(0 < error < Q(1, 2**132) for error in errors)
    assert sum(errors) < DELTA

    def factor(coefficient):
        multiplier = (Q(47, 20) * Q(256, 255) * Q(4097, 4096) * Q(1028, 1024)
                      * (1 + Q(coefficient, L) + DELTA) / ((1 - Q(10, L)) * (1 - DELTA)**3))
        return tuple(multiplier * endpoint for endpoint in bound_power(1024 * 134 * L, C))

    old, new, precise = factor(64), factor(8), tuple(
        factor(0)[i] * (1 + fringe[i] / L + DELTA) / (1 + DELTA) for i in (0, 1)
    )
    assert all(Q(observed[0]) <= exact[0] <= exact[1] <= Q(observed[1])
               for observed, exact in ((evidence["ordinary_factor"], old),))
    finer, booked = (bound_power(2, Q(numerator, 8192)) for numerator in (11203, 11204))
    assert finer[1] < precise[0] < precise[1] < new[0] <= new[1] < booked[0] < old[0]
    assert Q(75, 32) / Q(47, 20) == Q(375, 376)
    return dict(comparator=COMPARATOR, floor_source=FLOOR_HEAD, matched_axes=axes,
                k7_cells_sha256=OLD_CELLS, psi=outward(psi), fringe=outward(fringe),
                old_factor=outward(old), new_factor=outward(new), precise_factor=outward(precise),
                old_factor_fails_new_booking=True, sharper_grid_11203_fails_envelope=True,
                booking="11204/8192",
                booking_reserve=outward((booked[0] - new[1], booked[1] - new[0])),
                failed_finer_gap=outward((new[0] - finer[1], new[1] - finer[0])),
                normalized_error_log2_bounds=[30-5*min_height, 46-4*min_height, 20-4*min_height],
                delta="2^-128", exterior_width_guard="1-10/18960",
                qualification="exact conditional matched-suffix proof envelope only")


if __name__ == "__main__":
    paths = [Path(name).resolve() for name in sys.argv[1:]]
    result = exact_check(*paths)
    print(json.dumps(result, indent=2, sort_keys=True))
