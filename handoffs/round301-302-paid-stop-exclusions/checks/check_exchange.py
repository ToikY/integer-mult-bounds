"""Bounded census of two-field exchanges between already paid moves."""
import argparse
from bisect import bisect_left, bisect_right
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal

PINS = {
    "word.json.gz": "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d",
    "FINAL.json": "f24baa73a60d084a6d613dad914f1237a5890a049a183b993af39c75dde99add",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
EVENT_CAP, CONTACT_CAP, CASE_CAP, SECONDS = 24, 12, 8, 30


def emit(**fields):
    print(json.dumps(fields, default=str, sort_keys=True), flush=True)


def chart_span(frame):
    subspace = {0}
    for v in frame:
        assert v not in subspace
        subspace |= {v ^ x for x in subspace}
    return subspace


def touched(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def local_matrix(tape, roles, block):
    rows = {roles[0]: [Q(1), Q(0)], roles[1]: [Q(0), Q(1)]}
    for clock in block:
        op, dst, *tail = tape[clock]
        algebra = Q(tail[-2])
        a,b = rows[dst]
        if op == "SCALE":
            rows[dst] = [algebra*a, algebra*b]
        else:
            assert op == "ADD"
            c,d = rows[tail[0]]
            rows[dst] = [a+algebra*c,b+algebra*d]
    return [rows[role] for role in roles]


def windows(word, progress):
    tape = word["program"]
    hosted = word["hosted"]
    excluded = (set(word["live"]) | {r + 112 for r in word["live"]}
                | set(hosted["X2"]) | set(hosted["Y2"]))
    contacts, chart_pairs = defaultdict(list), defaultdict(list)
    eligible = set(range(word["public"])) - excluded
    for clock,event in enumerate(tape):
        progress[0] = clock
        roles = touched(event)
        for role in roles:
            contacts[role].append(clock)
        if event[0] == "ADD" and all(role in eligible for role in roles):
            a,b = sorted(roles)
            if (word["initial"][a],word["final"][a]) == (word["initial"][b],word["final"][b]):
                chart_pairs[(a,b,event[-1])].append(clock)
    subspaces = list(map(chart_span,word["frames"]))
    structural, lead = 0, []
    for (a,b,middle), add_clocks in chart_pairs.items():
        for anchor in add_clocks:
            progress[0] = anchor
            window_lo, window_hi = anchor-EVENT_CAP+1,anchor+EVENT_CAP-1
            merged = sorted(set(i for role in (a,b) for i in contacts[role][
                            bisect_left(contacts[role],window_lo):bisect_right(contacts[role],window_hi)]))
            at = merged.index(anchor)
            for i in range(max(0,at-CONTACT_CAP+1),at+1):
                first = merged[i]
                if not all(tape[j][0] in ("ADD","SCALE") and tape[j][-1] == middle
                           and set(touched(tape[j])) <= {a,b} for j in merged[i:at+1]):
                    continue
                # Count a window from its first mutual ADD only.
                if any(tape[j][0] == "ADD" for j in merged[i:at]):
                    continue
                for end_index in range(at,min(i+CONTACT_CAP,len(merged))):
                    last = merged[end_index]
                    if last-first+1 > EVENT_CAP:
                        break
                    event = tape[last]
                    if event[0] not in ("ADD","SCALE") or event[-1] != middle or not set(touched(event)) <= {a,b}:
                        break
                    block = merged[i:end_index+1]
                    structural += 1
                    for incoming,outgoing in ((a,b),(b,a)):
                        in_contacts, out_contacts = contacts[incoming],contacts[outgoing]
                        before = bisect_left(in_contacts,first)-1
                        after = bisect_right(out_contacts,last)
                        if before < 0 or after == len(out_contacts):
                            continue
                        enter,leave = in_contacts[before],out_contacts[after]
                        e,f = tape[enter],tape[leave]
                        if (e[0],f[0]) != ("MOVE","MOVE") or e[3] != middle or f[2] != middle:
                            continue
                        low,high = e[2],f[3]
                        if not subspaces[low] < subspaces[middle] < subspaces[high]:
                            continue
                        d = [len(word["frames"][chart]) for chart in (low,middle,high)]
                        lead.append(dict(roles=[incoming,outgoing], block=block,
                                         ranks=[d[1]-d[0],d[2]-d[1]], charts=[low,middle,high],
                                         entry=enter, exit=leave))
    return structural,lead


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs",type=Path)
    root=parser.parse_args().inputs
    progress=[-1]
    done=[]
    def cap(_sig,_frame):
        emit(status="TIME_CAP",last_clock=progress[0],tested=done)
        raise SystemExit(124)
    signal.signal(signal.SIGALRM,cap)
    signal.alarm(SECONDS)
    data={name:(root/name).read_bytes() for name in PINS}
    assert {name:sha256(raw).hexdigest() for name,raw in data.items()}==PINS
    word=json.loads(decompress(data["word.json.gz"]))
    app=json.loads(data["FINAL.json"])
    assert sha256(decompress(data["word.json.gz"])).hexdigest()==app["candidate_canonical_sha256"]
    caller=json.loads(data["7113-CALLER.json"])
    calls=sum(event[0] == "J" for event in caller["events"])
    assert app["caller_sha256"]==PINS["7113-CALLER.json"] and calls==17
    structural,lead=windows(word,progress)
    lo,hi=map(Q,app["raw_crossing"])
    power=run_path(str(root/"pricing.py"))["power_bounds"]
    for case in lead:
        a,b=case["ranks"]
        gross=(calls*(power(a,hi)[0]+power(b,hi)[0]-power(a+b,lo)[1]),
               calls*(power(a,lo)[1]+power(b,lo)[1]-power(a+b,hi)[0]))
        assert 0 < gross[0] <= gross[1] < calls
        case["gross"]=list(map(str,gross))
    lead.sort(key=lambda row:(row["block"][0],row["block"][-1],row["roles"]))
    emit(status="CENSUS", events=len(word["program"]), role_pair_windows=structural, priced=lead,
         max_clocks=EVENT_CAP,max_contacts=CONTACT_CAP,case_cap=CASE_CAP,seconds_cap=SECONDS)
    for case in lead[:CASE_CAP]:
        matrix=local_matrix(word["program"],case["roles"],case["block"])
        exact=not matrix[0][0] and not matrix[1][1] and matrix[0][1] and matrix[1][0]
        done.append(dict(case=case,matrix=matrix,survives=bool(exact)))
        if exact:
            break
    emit(status="SURVIVOR_REQUIRES_FULL_LOWERING" if any(x["survives"] for x in done)
         else "NO_ANTIDIAGONAL_IN_TESTED_SCOPE",tested=done,unresolved=lead[len(done):])
    signal.alarm(0)


if __name__=="__main__":
    main()
