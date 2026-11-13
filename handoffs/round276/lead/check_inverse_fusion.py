"""Screen fixed inverse ADD pairs for a paid public two-MOVE fusion on #7481."""
from bisect import bisect_left, bisect_right
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
from sys import version_info
from time import monotonic

ROOT = Path(__file__).resolve().parent.parent
PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "next-chart115/7003-slide_stops.py": "64a69bcd5689e17a081187a17ef2913adece970da653afa606b47cf130f1aa04",
}
CAP = 256
WALL = 30


def interrupted(signum, frame):
    raise TimeoutError("30-second discovery cap")


def opposite(left, right):
    return (left[1:3] == right[1:3] and
            Fraction(left[3]) != 0 and Fraction(left[3]) == -Fraction(right[3]))


def stop_contacts(history, first, second):
    return history[bisect_right(history, first):bisect_left(history, second)]


def screen():
    stats = Counter()
    cases, tests = [], []
    stage = "authentication"
    started = monotonic()
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(WALL)
    try:
        for path, digest in PINS.items():
            assert sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
        app = json.loads((ROOT / "inputs/7481-APPLICATION.json").read_bytes())
        raw = gzip.decompress((ROOT / "inputs/7481-WORD.json.gz").read_bytes())
        assert sha256(raw).hexdigest() == app["candidate_canonical_sha256"]
        word = json.loads(raw)
        program = word["program"]
        assert len(program) == app["native_events"] == 76475
        comm = run_path(str(ROOT / "next-chart115/7003-slide_stops.py"))
        price = run_path(str(ROOT / "inputs/pricing.py"))["power_bounds"]
        k0, k1 = map(Fraction, app["directed_crossing_bracket"])
        public = len(word["initial"])
        protected = (set(word["live"]) | {r + 112 for r in word["live"]} |
                     set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
        assert len(protected) == 400
        stage = "literal inventory"
        spaces = tuple(comm["span"](basis) for basis in word["frames"])
        history, transitions, _ = comm["inventory"](word, spaces)

        def barrier(i, j):
            a, b = program[i][1:3]
            contacts = set(stop_contacts(history[a], i, j)) | set(stop_contacts(history[b], i, j))
            for clock in sorted(contacts):
                event = program[clock]
                touched = comm["roles"](event)
                if not comm["commute"](program[i], event):
                    return clock, "noncommuting contact"
                if (event[0] != "MOVE" and a in touched and
                        (event[0] == "COPY" or any(r >= public or r in protected for r in touched))):
                    return clock, "changed operand at protected or owned read"
            return None, None

        control = 36448, 38004
        a, b = (program[i] for i in control)
        assert opposite(a, b) and barrier(*control) == (None, None)
        assert all(len(transitions[r]) == 2 for r in a[1:3])
        assert not opposite(a, [*b[:3], "-1", b[-1]])
        assert not comm["commute"](a, ["SCALE", a[2], "2", a[-1]])
        assert not comm["commute"](a, ["ADD", 0, a[1], "1", a[-1]])
        assert set(stop_contacts([1, 2, 3, 4, 5], 1, 5)) - {2, 4} == {3}

        stage = "inverse-pair census"
        next_add = {}
        for i in range(len(program) - 1, -1, -1):
            event = program[i]
            if event[0] != "ADD":
                continue
            d, s = event[1:3]
            if max(d, s) >= public or {d, s} <= protected:
                continue
            stats["public_adds"] += 1
            j = next_add.get((d, s))
            next_add[(d, s)] = i
            if j is None or not opposite(event, program[j]):
                continue
            stats["opposite_pairs"] += 1
            for role in (d, s):
                if role in protected:
                    continue
                route = transitions[role]
                intervals = {bisect_left(route, x) for x in (i, j)}
                for ix in sorted(intervals):
                    if ix <= 1 or ix >= len(route):
                        continue
                    first, second = route[ix - 1:ix + 1]
                    touch = stop_contacts(history[role], first, second)
                    stats["pairs_with_interior_move_interval"] += 1
                    if not touch or set(touch) - {i, j}:
                        stats["other_middle_contacts"] += 1
                        continue
                    left, mid, private = program[first][2:]
                    old_mid, right, next_private = program[second][2:]
                    assert mid == old_mid and not private and not next_private
                    assert spaces[left] < spaces[mid] < spaces[right]
                    a = (len(spaces[mid]) // len(spaces[left])).bit_length() - 1
                    b = (len(spaces[right]) // len(spaces[mid])).bit_length() - 1
                    lower = 17 * (price(a, k1)[0] + price(b, k1)[0] - price(a+b, k0)[1])
                    upper = 17 * (price(a, k0)[1] + price(b, k0)[1] - price(a+b, k1)[0])
                    cases.append((upper, (first, second, i, j, role), lower, (left, mid, right), (a, b)))
        stage = "ranked gate"
        cases.sort(key=lambda c: (-c[0], c[1]))
        assert len({c[1] for c in cases}) == len(cases)
        for upper, key, lower, charts, ranks in cases[:CAP]:
            first, second, i, j, role = key
            conflict, obstruction = barrier(i, j)
            if conflict is not None:
                outcome = obstruction
            elif upper <= 0:
                outcome = "nonpositive gross upper bound"
            elif lower <= 0:
                outcome = "gross bracket unresolved"
            else:
                outcome = "nominate one literal build"
            tests.append({"key": key, "outcome": outcome, "barrier_clock": conflict,
                          "barrier_event": program[conflict] if conflict is not None else None})
            if outcome == "nominate one literal build":
                stage = "first surviving chain"
                break
        else:
            stage = "exhausted" if len(cases) <= CAP else "case cap"
    except TimeoutError:
        stage = "wall cap during " + stage
    finally:
        signal.alarm(0)

    return {
        "status": stage, "pins": PINS, "seconds": monotonic() - started, "case_cap": CAP,
        "wall_cap_seconds": WALL, "census": dict(stats), "tests": tests,
        "cases": [{"key": key, "charts": charts, "ranks": ranks, "gross_raw": [str(lower), str(upper)]}
                  for upper, key, lower, charts, ranks in cases],
        "unvisited_identified_keys": [c[1] for c in cases[len(tests):]],
        "controls": ("chart115 cancels and has no two-MOVE chain; wrong sign, "
                     "source write, and additional middle observer reject"),
    }


if __name__ == "__main__":
    assert __debug__ and version_info[:2] == (3, 12)
    print(json.dumps(screen(), indent=2, sort_keys=True))
