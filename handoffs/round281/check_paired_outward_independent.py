"""Independently enumerate fixed paired outward co-encoding routes from receivers."""
import argparse
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
ALREADY_ACTIVE = {54, 319, 449, 485, 1206, 1311, 1321, 1322, 1455, 1477}
CASE_CAP, CAP = 64, 30
ZERO = Q(0)


def emit(**record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def unique_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def charts(word):
    result = []
    for basis in word["frames"]:
        space = {0}
        for generator in basis:
            assert generator not in space
            space |= {x ^ generator for x in space}
        result.append(space)
    return result


def metadata(word, spaces):
    contacts = defaultdict(list)
    births = {}
    active = dict(enumerate(word["initial"]))
    guards = Counter()
    for clock, event in enumerate(word["program"]):
        op, r, *arg = event
        contacts[r].append(clock)
        if op == "INIT":
            assert r >= word["public"] and r not in active and r not in births
            active[r], births[r] = arg[0], clock
        elif op == "CLEAR":
            assert r in births and active.pop(r) == arg[0]
            del births[r]
        elif op == "MOVE":
            a, b, owned = arg
            assert active[r] == a and owned == (r in births) == (r >= word["public"])
            assert spaces[a] < spaces[b] or owned and spaces[b] < spaces[a]
            active[r] = b
        elif op == "SCALE":
            assert active[r] == arg[-1] and Q(arg[0])
        else:
            assert op in ("ADD", "COPY") and r != arg[0]
            assert active[r] == active[arg[0]] == arg[-1] and Q(arg[1])
            contacts[arg[0]].append(clock)
        guards[op] += 1
    assert not births and active == dict(enumerate(word["final"]))
    return contacts, guards


def check_scope(word, lead, root, started):
    tape = word["program"]
    n = word["public"]
    assert len(tape) == 76475 and n == len(word["initial"]) == 1501
    protected = set(word["live"]) | {r + 112 for r in word["live"]}
    protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(protected) == 400
    allowed = set(range(n)) - protected - ALREADY_ACTIVE
    spaces = charts(word)
    contacts, guards = metadata(word, spaces)

    def outward(clock, receiver):
        event = tape[clock]
        if event[:2] != ["ADD", receiver] or event[2] not in allowed:
            return None
        donor = event[2]
        seq = contacts[donor]
        pos = bisect_left(seq, clock)
        assert seq[pos] == clock
        if pos == 0 or pos + 1 == len(seq):
            return None
        before, after = seq[pos - 1], seq[pos + 1]
        if tape[before][:2] != ["MOVE", donor] or tape[after][:2] != ["MOVE", donor]:
            return None
        assert tape[before][3] == event[-1] == tape[after][2]
        return donor, before, after, pos

    # Select consecutive literal receiver contacts first. This differs from
    # the lead's source-window-first join.
    windows = {}
    matches = []
    for receiver in sorted(allowed):
        seq = contacts[receiver]
        previous = None
        for clock in seq:
            info = outward(clock, receiver)
            if info is not None:
                assert clock not in windows
                windows[clock] = info
                if previous is not None and previous[1][0] != info[0]:
                    matches.append((receiver, previous[0], clock, previous[1], info))
            previous = (clock, info) if info is not None else None

    price = run_path(str(root / "inputs/pricing.py"))["power_bounds"]
    application = loads((root / "inputs/7481-APPLICATION.json").read_bytes(), object_pairs_hook=unique_pairs)
    lo, hi = map(Q, application["directed_crossing_bracket"])

    def delta_for(ranks):
        a, b, e = ranks
        base, edit = Counter((a, a, b, b + e)), Counter((a, a + b, b))
        if e:
            edit[e] += 1
        difference = base.copy()
        difference.subtract(edit)
        assert sum(rank * value for rank, value in difference.items()) == 0
        lower = upper = ZERO
        for rank, count in difference.items():
            if count > 0:
                lower += count * price(rank, hi)[0]
                upper += count * price(rank, lo)[1]
            elif count < 0:
                lower += count * price(rank, lo)[1]
                upper += count * price(rank, hi)[0]
        return 17 * lower, 17 * upper, {r: -v for r, v in sorted(difference.items()) if v}

    control_lo, control_hi, control_paid = delta_for((4, 2, 1))
    assert 0 < control_lo <= control_hi and control_paid == {1: 1, 3: -1, 4: -1, 6: 1}
    stages = Counter()
    routes = []
    considered = []
    failures = []
    for receiver, i, j, first, second in matches:
        for left, right in ((first, second), (second, first)):
            r, a, b, rp = left
            p, c, d, pp = right
            key = [i, j, r, p]
            begin, end = min(a, c), min(b, d)
            low, mid = tape[a][2:4]
            high, final = tape[b][3], tape[d][3]
            reason = None
            if tape[c][2:4] != [low, mid]:
                reason = "different_exact_entry"
            elif end <= j:
                reason = "departure_before_second_read"
            else:
                # The old arrival to the source chart must already have happened
                # before the common cut, and every source contact before its
                # original entry is incompatible with changing its value.
                for role, enter, contact_index in ((r, a, rp), (p, c, pp)):
                    seq = contacts[role]
                    assert seq[contact_index - 1] == enter
                    prev = seq[contact_index - 2] if contact_index >= 2 else -1
                    if prev >= begin:
                        reason = "old_contact_before_entry"
                        break
                if reason is None and not spaces[low] < spaces[mid] < spaces[high] <= spaces[final]:
                    reason = "non_nested_detour"
                if reason is None and spaces[high] == spaces[final] and high != final:
                    reason = "equal_span_different_chart"
            if reason is not None:
                stages[reason] += 1
                failures.append([key, reason])
                continue
            rank = lambda x: len(word["frames"][x])
            a_rank, b_rank, e_rank = rank(mid) - rank(low), rank(high) - rank(mid), rank(final) - rank(high)
            lower, upper, paid = delta_for((a_rank, b_rank, e_rank))
            considered.append({"key": key, "ranks": [a_rank, b_rank, e_rank],
                               "gross_raw": [lower, upper], "native_paid_delta": paid})
            if a_rank <= e_rank:
                assert a_rank != e_rank or lower == upper == 0
                stages["nonpositive_concavity"] += 1
                failures.append([key, "nonpositive_concavity"])
                continue
            assert begin <= i and max(a, c) <= j
            weights = {tape[clock][2]: Q(tape[clock][3]) for clock in (i, j)}
            assert set(weights) == {r, p}
            routes.append({"key": key, "moves": [a, b, c, d], "charts": [low, mid, high, final],
                           "ranks": [a_rank, b_rank, e_rank], "shared_cut": begin,
                           "gross_raw": [lower, upper], "encoding_coefficient": weights[r] / weights[p]})
    routes.sort(key=lambda case: (-case["gross_raw"][1], case["key"]))
    nomination = next((k for k, case in enumerate(routes[:CASE_CAP]) if case["gross_raw"][0] > 0), None)
    tested = nomination + 1 if nomination is not None else min(CASE_CAP, len(routes))
    unvisited = [case["key"] for case in routes[tested:]]
    status = "ONE_PRICE_POSITIVE_GEOMETRY" if nomination is not None else "EXHAUSTED" if len(routes) <= CASE_CAP else "CASE_CAP"
    counters = {"single_outward_move_windows": len(windows), "eligible_funded_routes": len(routes)}
    if matches:
        counters["matched_receiver_contacts"] = len(matches)
    assert status == lead["status"] and counters == lead["counters"]
    assert tested == lead["tested"] and unvisited == lead["unvisited"]
    if nomination is not None:
        candidate = routes[nomination]
        assert loads(dumps(candidate, default=str)) == lead["candidate"]
    else:
        candidate = None
    return {
        "status": "PASS_INDEPENDENT_RECEIVER_FIRST_SCREEN", "lead_disposition": status,
        "counters": counters, "tested": tested, "unvisited": unvisited,
        "candidate": candidate, "receiver_pair_keys": [[r, i, j] for r, i, j, _, _ in matches],
        "route_rejections": failures, "rejection_counts": stages, "priced_directions": considered,
        "known_positive_funded_price_control": {"ranks": [4, 2, 1], "gross_raw": [control_lo, control_hi]},
        "activity_guards": guards, "case_cap": CASE_CAP, "cap_seconds": CAP,
        "seconds": perf_counter() - started,
    }


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", cap_seconds=CAP, case_cap=CASE_CAP, seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP)
    data = {p: (args.root / p).read_bytes() for p in PINS}
    assert {p: sha256(raw).hexdigest() for p, raw in data.items()} == PINS
    raw = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(raw).hexdigest() == NATIVE
    word = loads(raw, object_pairs_hook=unique_pairs)
    app = loads(data["inputs/7481-APPLICATION.json"], object_pairs_hook=unique_pairs)
    caller = loads(data["inputs/7113-CALLER.json"], object_pairs_hook=unique_pairs)
    assert app["candidate_canonical_sha256"] == NATIVE and app["caller_head"] == CALLER
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    assert caller["stages"] == sum(event[0] == "J" for event in caller["events"]) == 17
    lead_raw = args.lead_receipt.read_bytes()
    assert sha256(lead_raw).hexdigest() == args.lead_sha256
    lead = loads(lead_raw, object_pairs_hook=unique_pairs)
    result = check_scope(word, lead, args.root, started)
    emit(**result, input_pins=PINS, native_sha256=NATIVE, caller_head=CALLER, lead_sha256=args.lead_sha256)
    alarm(0)


if __name__ == "__main__":
    main()
