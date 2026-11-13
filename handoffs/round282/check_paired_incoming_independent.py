"""Independently census paired incoming transfer routes from exact donor history."""
import argparse
from bisect import bisect_left, bisect_right
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
CAP, CASE_CAP = 30, 64


def emit(**record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def unique_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def charts(word):
    result = []
    for basis in word["frames"]:
        span = {0}
        for vector in basis:
            assert vector not in span
            span |= {vector ^ x for x in span}
        result.append(span)
    return result


def metadata(word, spaces):
    contacts = defaultdict(list)
    writes = defaultdict(list)
    reads = defaultdict(list)
    owned = {}
    chart = dict(enumerate(word["initial"]))
    guards = Counter()
    for clock, event in enumerate(word["program"]):
        op, r, *args = event
        contacts[r].append(clock)
        writes[r].append(clock)
        if op == "INIT":
            assert r >= word["public"] and r not in chart and r not in owned
            chart[r], owned[r] = args[0], clock
        elif op == "CLEAR":
            assert r in owned and chart.pop(r) == args[0]
            del owned[r]
        elif op == "MOVE":
            a, b, owner = args
            assert chart[r] == a and owner == (r in owned) == (r >= word["public"])
            assert spaces[a] < spaces[b] or owner and spaces[b] < spaces[a]
            chart[r] = b
        elif op == "SCALE":
            assert chart[r] == args[-1] and Q(args[0])
        else:
            assert op in ("ADD", "COPY") and r != args[0]
            assert chart[r] == chart[args[0]] == args[-1] and Q(args[1])
            contacts[args[0]].append(clock)
            if op == "ADD":
                reads[args[0]].append(clock)
        guards[op] += 1
    assert not owned and chart == dict(enumerate(word["final"]))
    return contacts, writes, reads, guards


def scalar_control():
    # Rows are coefficient tuples on independent inputs (R, P, S).
    def add(a, b, q):
        return tuple(x + q*y for x, y in zip(a, b, strict=True))
    r, p, s = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    c, d = Q(-3, 2), Q(3)
    ratio = c / d
    old_r, old_p = add(r, s, c), add(p, s, d)
    encoded_r = add(r, p, -ratio)
    assert add(encoded_r, old_p, ratio) == old_r
    assert add(encoded_r, old_p, -ratio) != old_r
    return {"signed_dyadic_shear_identity": True, "wrong_decode_sign_rejected": True}


def check_scope(word, app, root, lead, started, progress):
    tape = word["program"]
    public = word["public"]
    assert len(tape) == 76475 and public == len(word["initial"]) == 1501
    protected = set(word["live"]) | {r + 112 for r in word["live"]}
    protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(protected) == 400
    allowed = set(range(public)) - protected - ALREADY_ACTIVE
    spaces = charts(word)
    contacts, writes, reads, guards = metadata(word, spaces)
    power = run_path(str(root / "inputs/pricing.py"))["power_bounds"]
    lo, hi = map(Q, app["directed_crossing_bracket"])

    def paid_delta(ranks):
        a, b, e = ranks
        old = Counter((a, a, b, b + e))
        new = Counter((a, a + b, b))
        if e:
            new[e] += 1
        removed = old.copy()
        removed.subtract(new)
        lower = upper = Q(0)
        for rank, count in removed.items():
            if count > 0:
                lower += count * power(rank, hi)[0]
                upper += count * power(rank, lo)[1]
            elif count < 0:
                lower += count * power(rank, lo)[1]
                upper += count * power(rank, hi)[0]
        assert sum(r * n for r, n in removed.items()) == 0
        return 17 * lower, 17 * upper

    control_lo, control_hi = paid_delta((4, 2, 1))
    assert 0 < control_lo <= control_hi

    def window(clock, source):
        event = tape[clock]
        role = event[1]
        if role not in allowed:
            return None
        seq = contacts[role]
        index = bisect_left(seq, clock)
        assert seq[index] == clock
        if index == 0 or index + 1 == len(seq):
            return None
        first, last = seq[index - 1], seq[index + 1]
        if tape[first][:2] != ["MOVE", role] or tape[last][:2] != ["MOVE", role]:
            return None
        assert event[:3] == ["ADD", role, source]
        assert tape[first][3] == tape[last][2] == event[-1]
        return role, first, last, index

    # Enumerate the reads of each source first. A monotone cursor in its exact
    # write/chart history partitions the eligible read stream by version.
    windows, pairs = 0, []
    for source in sorted(allowed):
        changes = writes[source]
        cursor = 0
        previous = None
        version = -1
        for clock in reads[source]:
            while cursor < len(changes) and changes[cursor] < clock:
                version = changes[cursor]
                cursor += 1
            info = window(clock, source)
            if info is None:
                continue
            windows += 1
            if previous is not None:
                last_clock, last_version, last_info = previous
                if last_version == version and last_info[0] != info[0]:
                    pairs.append((source, version, last_clock, clock, last_info, info))
            previous = clock, version, info

    routes, details = [], []
    rejections = Counter()
    for source, version, i, j, left, right in pairs:
        assert bisect_left(writes[source], i) == bisect_left(writes[source], j)
        for first, second in ((left, right), (right, left)):
            r, a, b, r_index = first
            p, c, d, p_index = second
            key = [i, j, r, p]
            progress["last_metadata_key"] = key
            begin, end = min(a, c), min(b, d)
            low, mid = tape[a][2:4]
            peer_low, peer_mid = tape[c][2:4]
            h, e = tape[b][3], tape[d][3]
            detail = {"key": key, "source_version": [source, version], "moves": [a, b, c, d],
                      "charts": [low, mid, h, peer_low, peer_mid, e]}
            if [low, mid] != [peer_low, peer_mid]:
                reason = "different_exact_entry"
            elif any(index >= 2 and contacts[role][index - 2] >= begin
                     for role, index in ((r, r_index), (p, p_index))):
                reason = "retained_contact_before_entry"
            elif not spaces[low] < spaces[mid] < spaces[h] <= spaces[e]:
                reason = "non_nested_detour"
            elif spaces[h] == spaces[e] and h != e:
                reason = "equal_span_different_chart"
            elif end <= j:
                reason = "departure_before_second_read"
            else:
                c_r = Q(tape[i if left[0] == r else j][3])
                c_p = Q(tape[i if left[0] == p else j][3])
                ratio = c_r / c_p
                if ratio.denominator & (ratio.denominator - 1):
                    reason = "non_dyadic_ratio"
                else:
                    rank = lambda chart: len(word["frames"][chart])
                    ranks = [rank(mid) - rank(low), rank(h) - rank(mid), rank(e) - rank(h)]
                    lower, upper = paid_delta(ranks)
                    detail.update(ranks=ranks, gross_raw=[lower, upper])
                    if ranks[0] <= ranks[2]:
                        reason = "nonpositive_concavity"
                    else:
                        first_r = bisect_right(contacts[r], b)
                        first_p = bisect_right(contacts[p], d)
                        routes.append({
                            "key": key, "moves": [a, b, c, d], "charts": [low, mid, h, e],
                            "ranks": ranks, "shared_cut": begin, "decode_cut": end,
                            "source_version": [source, version], "first_retained_contacts": {
                                r: contacts[r][first_r] if first_r < len(contacts[r]) else len(tape),
                                p: contacts[p][first_p] if first_p < len(contacts[p]) else len(tape),
                            },
                            "omitted_add": i if left[0] == r else j,
                            "retained_add": i if left[0] == p else j,
                            "encoding_coefficient": -ratio, "decoding_coefficient": ratio,
                            "gross_raw": [lower, upper],
                        })
                        reason = "eligible"
            detail["first_gate"] = reason
            details.append(detail)
            if reason != "eligible":
                rejections[reason] += 1

    routes.sort(key=lambda case: (-case["gross_raw"][1], case["key"]))
    tested, candidate = 0, None
    for case in routes[:CASE_CAP]:
        progress["first_unvisited_ranked_key"] = case["key"]
        tested += 1
        if case["gross_raw"][0] > 0:
            candidate = case
            break
    pending = [row["key"] for row in routes[tested:]]
    status = "ONE_PRICE_POSITIVE_GEOMETRY" if candidate else "CASE_CAP" if pending else "EXHAUSTED"
    counters = {"single_incoming_move_windows": windows, "eligible_funded_routes": len(routes)}
    if pairs:
        counters["matched_source_versions"] = len(pairs)
    if rejections["non_dyadic_ratio"]:
        counters["non_dyadic_ratio"] = rejections["non_dyadic_ratio"]
    assert status == lead["status"] and tested == lead["tested"] and pending == lead["unvisited"]
    assert counters == lead["counters"]
    if candidate:
        assert loads(dumps(candidate, default=str)) == lead["candidate"]
    return {
        "status": "PASS_INDEPENDENT_SOURCE_HISTORY_SCREEN", "lead_disposition": status,
        "counters": counters, "tested": tested, "unvisited": pending, "candidate": candidate,
        "paired_source_versions": [[s, v, i, j] for s, v, i, j, _, _ in pairs],
        "direction_details": details, "rejections": rejections, "activity_guards": guards,
        "normalized_algebra_control": scalar_control(), "positive_funded_price_control": [control_lo, control_hi],
        "case_cap": CASE_CAP, "cap_seconds": CAP, "seconds": perf_counter() - started,
    }


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()
    progress = {"last_metadata_key": None, "first_unvisited_ranked_key": None}

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", cap_seconds=CAP, case_cap=CASE_CAP,
             seconds=perf_counter() - started, **progress)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP)
    data = {p: (args.root / p).read_bytes() for p in PINS}
    assert {p: sha256(raw).hexdigest() for p, raw in data.items()} == PINS
    raw_word = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(raw_word).hexdigest() == NATIVE
    word = loads(raw_word, object_pairs_hook=unique_pairs)
    app = loads(data["inputs/7481-APPLICATION.json"], object_pairs_hook=unique_pairs)
    caller = loads(data["inputs/7113-CALLER.json"], object_pairs_hook=unique_pairs)
    assert app["candidate_canonical_sha256"] == NATIVE and app["caller_head"] == CALLER
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    lead_raw = args.lead_receipt.read_bytes()
    assert sha256(lead_raw).hexdigest() == args.lead_sha256
    lead = loads(lead_raw, object_pairs_hook=unique_pairs)
    result = check_scope(word, app, args.root, lead, started, progress)
    emit(**result, input_pins=PINS, native_sha256=NATIVE, caller_head=CALLER, lead_sha256=args.lead_sha256)
    alarm(0)


if __name__ == "__main__":
    main()
