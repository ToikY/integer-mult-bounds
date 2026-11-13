"""Independent chronology and sparse commutator check of one capped #7481 census."""
import bisect
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "next-chart115/7003-slide_stops.py": "64a69bcd5689e17a081187a17ef2913adece970da653afa606b47cf130f1aa04",
}


def read_pin(path, expected):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == expected, path
    return raw


def xor_span(basis):
    out = {0}
    for vector in basis:
        assert 0 < vector < 512 and vector not in out
        out |= {vector ^ row for row in out}
    return out


def operands(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def commute_shear(dest, source, event):
    if event[0] == "MOVE" or not ({dest, source} & set(operands(event))):
        return True
    if event[0] != "ADD":
        return False
    target, reader = event[1:3]
    # Compare the two products E_dest,source E_target,reader and its reverse.
    left = (dest, reader) if source == target else None
    right = (target, source) if reader == dest else None
    return left == right


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    signal.alarm(30)
    root, receipt = (Path(p).resolve() for p in sys.argv[1:3])
    source = {path: read_pin(root / path, digest) for path, digest in PINS.items()}
    lead = json.loads(read_pin(receipt, sys.argv[3]))
    assert lead["pins"] == PINS and lead["case_cap"] == 256 and lead["wall_cap_seconds"] == 30
    assert lead["status"] in ("exhausted", "case cap", "first surviving chain"), lead["status"]
    word = json.loads(gzip.decompress(source["inputs/7481-WORD.json.gz"]))
    app = json.loads(source["inputs/7481-APPLICATION.json"])
    assert sha256(gzip.decompress(source["inputs/7481-WORD.json.gz"])).hexdigest() == app["candidate_canonical_sha256"]
    caller = json.loads(source["inputs/7113-CALLER.json"])
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    tape = word["program"]
    public = word["public"]
    protected = (set(word["live"]) | {r+112 for r in word["live"]} |
                 set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    assert len(protected) == 400
    spaces = [xor_span(frame) for frame in word["frames"]]
    active = dict(enumerate(word["initial"]))
    history, moves, adds = defaultdict(list), defaultdict(list), defaultdict(list)
    for clock, event in enumerate(tape):
        op, role, *args = event
        for r in operands(event):
            history[r].append(clock)
        if op == "MOVE":
            a, b, private = args
            assert active[role] == a and private == (role >= public)
            assert spaces[a] < spaces[b] or (private and spaces[b] < spaces[a])
            active[role] = b
            if not private:
                moves[role].append(clock)
        elif op == "INIT":
            assert role not in active and role >= public
            active[role] = args[0]
        elif op == "CLEAR":
            assert role >= public and active.pop(role) == args[0]
        else:
            assert op in ("ADD", "COPY", "SCALE")
            assert all(active[r] == event[-1] for r in operands(event))
            if op == "ADD" and max(event[1:3]) < public and not set(event[1:3]) <= protected:
                adds[tuple(event[1:3])].append(clock)
    assert active == dict(enumerate(word["final"]))

    stats = Counter(public_adds=sum(map(len, adds.values())))
    opposites = []
    for pair, clocks in adds.items():
        for i, j in zip(clocks, clocks[1:]):
            if Q(tape[i][3]) and Q(tape[i][3]) == -Q(tape[j][3]):
                opposites.append((*pair, i, j))
    stats["opposite_pairs"] = len(opposites)
    assert (1276, 751, 36448, 38004) in opposites
    price = run_path(str(root / "inputs/pricing.py"))["power_bounds"]
    k0, k1 = map(Q, app["directed_crossing_bracket"])
    candidates = {}
    for d, s, i, j in opposites:
        for role in (d, s):
            if role in protected:
                continue
            route = moves[role]
            indices = {bisect.bisect_right(route, clock) for clock in (i, j)}
            for p in indices & set(range(1, len(route))):
                first, second = route[p-1:p+1]
                middle = {clock for clock in history[role] if first < clock < second}
                assert middle & {i, j}
                stats["pairs_with_interior_move_interval"] += 1
                if middle - {i, j}:
                    stats["other_middle_contacts"] += 1
                    continue
                charts = [tape[first][2], tape[first][3], tape[second][3]]
                a, b = (len(word["frames"][y])-len(word["frames"][x]) for x, y in zip(charts, charts[1:]))
                low = 17 * (price(a, k1)[0] + price(b, k1)[0] - price(a+b, k0)[1])
                high = 17 * (price(a, k0)[1] + price(b, k0)[1] - price(a+b, k1)[0])
                key = first, second, i, j, role
                assert key not in candidates
                candidates[key] = dict(key=list(key), charts=charts, ranks=[a, b], gross_raw=[str(low), str(high)])
    assert dict(stats) == lead["census"]
    ranked = sorted(candidates.values(), key=lambda c: (-Q(c["gross_raw"][1]), c["key"]))
    assert ranked == lead["cases"]

    tests = []
    for case in ranked[:256]:
        first, second, i, j, role = case["key"]
        d, s = tape[i][1:3]
        barrier = None
        outcome = "nominate one literal build"
        for clock in sorted(set(history[d]) | set(history[s])):
            if not i < clock < j:
                continue
            event = tape[clock]
            touched = operands(event)
            if not commute_shear(d, s, event):
                barrier, outcome = clock, "noncommuting contact"
                break
            if event[0] != "MOVE" and d in touched and (event[0] == "COPY" or any(r >= public or r in protected for r in touched)):
                barrier, outcome = clock, "changed operand at protected or owned read"
                break
        if barrier is None:
            lo, hi = map(Q, case["gross_raw"])
            if hi <= 0:
                outcome = "nonpositive gross upper bound"
            elif lo <= 0:
                outcome = "gross bracket unresolved"
        tests.append(dict(key=case["key"], outcome=outcome, barrier_clock=barrier,
                          barrier_event=tape[barrier] if barrier is not None else None))
        if outcome == "nominate one literal build":
            break
    assert tests == lead["tests"]
    unvisited = [c["key"] for c in ranked[len(tests):]]
    assert unvisited == lead["unvisited_identified_keys"]
    print(json.dumps(dict(status="PASS_INDEPENDENT_INVERSE_FUSION_CENSUS", census=stats,
                          tested=len(tests), unvisited=unvisited), sort_keys=True))
    signal.alarm(0)


if __name__ == "__main__":
    main()
