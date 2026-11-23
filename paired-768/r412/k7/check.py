"""Bounded exact identity-MOVE gate on the arbitrary-input K7 register graph."""
from argparse import ArgumentParser
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from io import BytesIO
import json
from math import isqrt
from pathlib import Path
import signal
import tarfile


ARCHIVE_SHA = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
WORD_PATH = "research/tiered-native-multiplier/source/strong-bit-k7.json.gz"
WORD_SHA = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
PAYLOAD_SHA = "f4a43e4e36ac734dea10a73dca496bf4a4f4a9804b903ea379483d0513d7abc3"
RANK_CAP = 64
SECONDS = 90
N = 8
GRID = 1 << 112
EXPONENT = 1 - Q(4391986206293, 1 << 50)


def digest(data):
    return sha256(data).hexdigest()


def load_word(path):
    data = path.read_bytes()
    assert digest(data) == ARCHIVE_SHA
    with tarfile.open(fileobj=BytesIO(data)) as archive:
        member = archive.getmember(WORD_PATH)
        assert member.isfile()
        packed = archive.extractfile(member).read()
    assert digest(packed) == WORD_SHA
    literal = gzip.decompress(packed)
    assert digest(literal) == PAYLOAD_SHA
    return json.loads(literal)


def product(left, right):
    cols = list(zip(*right, strict=True))
    return [[sum(a * b for a, b in zip(row, col, strict=True))
             for col in cols] for row in left]


def invert(matrix):
    work = [[Q(v) for v in row] + [Q(i == j) for j in range(N)]
            for i, row in enumerate(matrix)]
    for col in range(N):
        lead = next(i for i in range(col, N) if work[i][col])
        work[col], work[lead] = work[lead], work[col]
        pivot = work[col][col]
        work[col] = [x / pivot for x in work[col]]
        for row in range(N):
            if row != col and work[row][col]:
                multiple = work[row][col]
                work[row] = [x - multiple * y for x, y in
                             zip(work[row], work[col], strict=True)]
    return [row[N:] for row in work]


def projector(frame):
    basis = list(zip(*(frame["B"] + frame["A"]), strict=True))
    inv = invert(basis)
    dim = frame["dim"]
    p = product([row[:dim] for row in basis], inv[:dim]) if dim else [[Q(0)] * N for _ in range(N)]
    assert all(x.denominator % 3 for row in p for x in row)
    assert product(p, p) == p
    return p


def outward_power(rank):
    whole, remainder = divmod(EXPONENT.numerator, EXPONENT.denominator)
    low = high = rank ** whole * GRID
    lo_root = hi_root = rank * GRID
    divisor = EXPONENT.denominator
    while divisor > 1:
        divisor //= 2
        lo_root = isqrt(lo_root * GRID)
        hi_root = 1 + isqrt(hi_root * GRID - 1)
        if remainder & divisor:
            low = low * lo_root // GRID
            high = -(-high * hi_root // GRID)
    return [str(Q(36 * x, GRID)) for x in (low, high)]


def screen(literal, completed):
    program = literal["program"]
    frames = {int(i): value for i, value in literal["frames"].items()}
    moves = [(abs(frames[row[2]]["dim"] - frames[row[3]]["dim"]), clock)
             for clock, row in enumerate(program) if row[0] == "MOVE"]
    assert len(moves) == 2796
    shortlist = dict((clock, rank) for rank, clock in
                     sorted(moves, key=lambda item: (-item[0], item[1]))[:RANK_CAP])
    assert all(rank > 0 for rank in shortlist.values())
    p_cache, observations = {}, {}
    active = dict(enumerate(literal["start"]))
    supports = {i: 1 << i for i in active}
    assert len(active) == 630

    # One chronological propagation supplies exactly the saved case inputs.
    for clock, (kind, dest, *args) in enumerate(program):
        if kind == "MOVE":
            first, last = args
            assert active[dest] == first
            if clock in shortlist:
                observations[clock] = supports[dest]
            active[dest] = last
        elif kind == "ADD":
            source, chart = args
            assert active[dest] == active[source] == chart
            supports[dest] ^= supports[source]
        elif kind == "SWAP":
            source, = args
            active[dest], active[source] = active[source], active[dest]
            supports[dest], supports[source] = supports[source], supports[dest]
        elif kind == "INIT":
            assert dest >= 630 and dest not in active
            active[dest] = args[0]
            supports[dest] = 0
        elif kind == "CLEAR":
            assert dest >= 630 and active.pop(dest) == args[0]
            supports.pop(dest)
        else:
            raise ValueError(kind)
    assert active == dict(enumerate(literal["final"]))
    for i, v in supports.items():
        assert v == ((1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0))

    for clock, rank in shortlist.items():
        _, dest, first, last = program[clock]
        a, b = sorted((first, last), key=lambda i: frames[i]["dim"])
        for i in (a, b):
            if i not in p_cache:
                p_cache[i] = projector(frames[i])
        p, q = p_cache[a], p_cache[b]
        assert product(p, q) == product(q, p) == p
        delta = [[y - x for x, y in zip(p_row, q_row, strict=True)]
                 for p_row, q_row in zip(p, q, strict=True)]
        assert product(delta, delta) == delta
        assert sum(delta[i][i] for i in range(N)) == rank
        coord = next(j for j in range(N) if any(row[j] for row in delta))
        head_change = [row[coord] for row in delta]
        # Over a sufficiently high power of three, at least this coordinate
        # witnesses the nonidentity on the independently supplied input.
        v = next(x for x in head_change if x)
        needed_modulus = 3
        while v.numerator % needed_modulus == 0:
            needed_modulus *= 3
        normalized = observations[clock]
        record = {
            "clock": clock, "register": dest, "charts": [first, last],
            "rank": rank, "normalized_support_size": normalized.bit_count(),
            "gross_moment_interval_if_deleted": outward_power(rank),
        }
        if normalized:
            independent_owner = (normalized & -normalized).bit_length() - 1
            record["counterexample"] = {
                "nonzero_input_owner": independent_owner,
                "tail_coordinate_after_old_chart": coord,
                "head_change_for_unit_weights": [str(x) for x in head_change],
                "modulus": needed_modulus,
            }
        completed.append(record)
        if not normalized:
            break
    if len(completed) == RANK_CAP and all("counterexample" in r for r in completed):
        outcome = "EXHAUSTED_FIXED_64_NO_IDENTITY_MOVE"
    else:
        outcome = "ZERO_SUPPORT_NEEDS_LITERAL_OWNER_REPLAY"
    return shortlist, outcome


class Deadline(TimeoutError):
    pass


def expired(*_):
    raise Deadline()


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    completed = []
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(SECONDS)
    try:
        shortlist, outcome = screen(load_word(args.archive), completed)
    except Deadline:
        print(json.dumps({"status": "CAPPED", "tested": completed}, indent=2))
        return 124
    finally:
        signal.alarm(0)
    print(json.dumps({
        "status": outcome, "case_cap": RANK_CAP, "seconds_cap": SECONDS,
        "tested": completed, "remaining_in_fixed_scope": list(shortlist)[len(completed):],
        "other_move_clocks_unresolved": 2796 - RANK_CAP,
        "archive_sha256": ARCHIVE_SHA, "word_path": WORD_PATH,
        "word_sha256": WORD_SHA, "unpacked_word_sha256": PAYLOAD_SHA,
        "price_trial_exponent": str(EXPONENT),
        "scope": "arbitrary input contract of the 630-role normalized K7 word",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
