"""Find one price-positive shared outward read with an exact early shear."""
from bisect import bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

PINS = {
    "7481-WORD.json.gz":"acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json":"1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
CAP = 64
stats = Counter()
state = {"last_window": None, "first_unvisited": None}
cases = []


def emit(record):
    print(json.dumps(record, default=str, sort_keys=True), flush=True)


def timeout(_sig, _frame):
    emit(dict(status="UNRESOLVED_CAP", cap_seconds=30, case_cap=CAP, counters=stats, **state))
    raise SystemExit(124)


def span(basis):
    values = {0}
    for vector in basis:
        assert vector not in values
        values |= {vector ^ old for old in values}
    return values


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    root = Path(sys.argv[1]).resolve()
    source = {name: (root/name).read_bytes() for name in PINS}
    assert {name:sha256(raw).hexdigest() for name,raw in source.items()} == PINS
    app = json.loads(source["7481-APPLICATION.json"])
    payload = decompress(source["7481-WORD.json.gz"])
    assert sha256(payload).hexdigest() == app["candidate_canonical_sha256"]
    word = json.loads(payload)
    caller = json.loads(source["7113-CALLER.json"])
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    tape = word["program"]
    public = word["public"]
    excluded = (set(word["live"]) | {r+112 for r in word["live"]} |
                set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    assert len(excluded) == 400
    excluded.update({54,319,449,485,1206,1311,1321,1322,1455,1477})
    chart = dict(enumerate(word["initial"]))
    arrival = defaultdict(lambda: -1)
    previous_for_move = {}
    contacts = defaultdict(list)
    for clock,event in enumerate(tape):
        op,role,*args = event
        contacts[role].append(clock)
        if op in ("ADD","COPY"):
            contacts[args[0]].append(clock)
            assert chart[role] == chart[args[0]] == args[-1]
        elif op == "MOVE":
            assert chart[role] == args[0] and args[2] == (role>=public)
            previous_for_move[clock] = arrival[role]
            chart[role] = args[1]
            arrival[role] = clock
        elif op == "INIT":
            assert role >= public and role not in chart
            chart[role] = args[0]
        elif op == "CLEAR":
            assert role >= public and chart.pop(role) == args[0]
        else:
            assert op == "SCALE" and chart[role] == args[-1]
    assert chart == dict(enumerate(word["final"]))
    spaces = [span(frame) for frame in word["frames"]]
    windows = {}
    for role, clocks in contacts.items():
        if role>=public or role in excluded:
            continue
        for first, add, last in zip(clocks,clocks[1:],clocks[2:]):
            source_move, scalar, target_move = (tape[i] for i in (first,add,last))
            if source_move[:2] != ["MOVE",role] or target_move[:2] != ["MOVE",role]:
                continue
            if scalar[0] != "ADD" or scalar[2] != role or scalar[1] in excluded or scalar[1]>=public:
                continue
            assert source_move[3] == scalar[-1] == target_move[2]
            windows[add] = (role, first, last)
    stats["single_outward_move_windows"] = len(windows)
    # The outward pair may be separated by events disjoint from all three roles.
    for i in sorted(windows):
        role, first, last = windows[i]
        dst = tape[i][1]
        seq = contacts[dst]
        following = bisect_right(seq,i)
        j = seq[following] if following < len(seq) else None
        if j not in windows or tape[j][1] != dst:
            continue
        peer, enter, exit = windows[j]
        if role == peer:
            continue
        stats["matched_receiver_contacts"] += 1
        for r,p,a,b,c,d in [(role,peer,first,last,enter,exit),(peer,role,enter,exit,first,last)]:
            state["last_window"] = [i,j,r,p]
            low, middle = tape[a][2:4]
            peer_low, peer_middle = tape[c][2:4]
            high, end = tape[b][3],tape[d][3]
            if (low,middle)!=(peer_low,peer_middle):
                continue
            shared_cut = min(a,c)
            if previous_for_move[a] >= shared_cut or previous_for_move[c] >= shared_cut:
                continue
            if not spaces[low] < spaces[middle] < spaces[high] <= spaces[end]:
                continue
            if len(word["frames"][high]) == len(word["frames"][end]) and high != end:
                continue
            # Decode at the early retimed detour only after both matched reads.
            if min(b,d) <= max(i,j) or min(a,c) > i or max(a,c) > j:
                continue
            if any(shared_cut <= k < move for rr,move in ((r,a),(p,c)) for k in contacts[rr]):
                continue
            entry = len(word["frames"][middle])-len(word["frames"][low])
            rung = len(word["frames"][high])-len(word["frames"][middle])
            tail = len(word["frames"][end])-len(word["frames"][high])
            if entry <= tail:
                continue
            cases.append(dict(key=[i,j,r,p], moves=[a,b,c,d], charts=[low,middle,high,end],
                              ranks=[entry,rung,tail], shared_cut=shared_cut))
    stats["eligible_funded_routes"] = len(cases)
    assert 17*(Q(3)+Q(4)-Q(6)-Q(1)) == 0  # #7481 rank-mass control
    lo,hi=map(Q,app["directed_crossing_bracket"])
    price=run_path(str(root/"pricing.py"))["power_bounds"]
    def bound(rank,k,side):
        return price(rank,k)[side] if rank else Q(0)
    ranked=[]
    for case in cases:
        a,b,e=case["ranks"]
        lower=17*(bound(a,hi,0)+bound(b+e,hi,0)-bound(a+b,lo,1)-bound(e,lo,1))
        upper=17*(bound(a,lo,1)+bound(b+e,lo,1)-bound(a+b,hi,0)-bound(e,hi,0))
        ranked.append((upper,case["key"],lower,case))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    for k,(upper,key,lower,case) in enumerate(ranked[:CAP]):
        state["first_unvisited"] = key
        i,j,r,p=key
        ratios={tape[q][2]:Q(tape[q][3]) for q in (i,j)}
        assert set(ratios)=={r,p} and all(ratios.values())
        case["encoding_coefficient"]=ratios[r]/ratios[p]
        case["gross_raw"]=[lower,upper]
        if lower>0:
            emit(dict(status="ONE_PRICE_POSITIVE_GEOMETRY",candidate=case,counters=stats,
                      tested=k+1,unvisited=[x[1] for x in ranked[k+1:]],pins=PINS))
            break
    else:
        emit(dict(status="EXHAUSTED" if len(ranked)<=CAP else "CASE_CAP",counters=stats,
                  tested=min(CAP,len(ranked)),unvisited=[x[1] for x in ranked[CAP:]],pins=PINS))
    signal.alarm(0)


if __name__ == "__main__":
    main()
