"""Replay the fixed pre30588 chart470 owned1521 fusion with exact rationals."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CUT, CAP, CHART = 30588, 30, 470
BANK = (727, 1164, 1536, 1546, 1547)
OMIT = {30520, 30532, 30534, 30537, 30538, 30541, 30543, 39947, 45355, 45357}
CHANGES = {
    30545: ["INIT", 1521, 1090], 30547: ["ADD", 1521, 1510, "-1/4", 1090],
    30551: ["MOVE", 1521, 1090, 601, True],
}


def emit(**fields):
    print(dumps(fields, sort_keys=True, default=str), flush=True)


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def span(basis):
    values = {0}
    for generator in basis:
        assert generator not in values
        values |= {generator ^ x for x in values}
    return values


def contacts(tape, role, start=0, end=None):
    return [i for i in range(start, end if end is not None else len(tape))
            if tape[i][1] == role or tape[i][0] in ("ADD", "COPY") and tape[i][2] == role]


def check_word(word):
    t = word["program"]
    assert len(t) == 76475 and len(word["initial"]) == word["public"] == 1501
    spaces = [span(frame) for frame in word["frames"]]
    assert spaces[601] < spaces[470] < spaces[1090]
    assert [len(spaces[i]) for i in (601,470,1090)] == [2,8,16]
    assert contacts(t, 1508) == [30520,30538,30541,30543,30547,39947]
    assert contacts(t, 1520) == [30532,30534,30537,30538,45355,45357]
    assert contacts(t, 1521) == [30545,30547,30551,30552,30558,30563,33691,39898]
    assert contacts(t, 1510, 30531, 30548) == [30534]
    assert contacts(t, 727, 30541, 45356) == [30541,30586,45355]
    assert contacts(t, 402, 30586, CUT + 1) == [30586,CUT]
    assert t[30537] == ["MOVE", 1520, 1090, 470, True]
    assert t[30551] == ["MOVE", 1521, 470, 601, True]
    assert t[30581] == ["MOVE", 1547, 601, 470, True]
    assert t[30586] == ["ADD", 402, 727, "-4", 470]
    assert t[CUT:CUT+1] == [["ADD", 1536, 402, "1/4", 470]]
    assert t[30590] == ["ADD", 1546, 1536, "1", 470]
    assert t[45355] == ["ADD", 727, 1520, "1/4", 470]
    return spaces


def add(left, right, weight=Q(1)):
    out = left.copy()
    for j, coefficient in right.items():
        total = out.get(j, 0) + weight * coefficient
        if total:
            out[j] = total
        else:
            out.pop(j, None)
    return out


def replay(word, spaces, initial, edited, weights=None):
    rows, active = initial.copy(), dict(enumerate(word["initial"]))
    owners = {}
    paid, ops = Counter(), Counter()
    guards, snapshots, first = {}, {}, {}
    empty = {}

    def get(r):
        return rows.get(r, empty)

    def apply(event, clock):
        op, r, *a = event
        old = get(r)
        ops[op] += 1
        if op == "INIT":
            assert r >= word["public"] and r not in active and r not in owners and not old
            active[r] = a[0]
            owners[r] = clock
            return
        if op == "CLEAR":
            assert r in owners and active.pop(r) == a[0]
            guards[clock] = (op, r, owners.pop(r), old)
            rows.pop(r, None)
            return
        if op == "MOVE":
            x, y, flag = a
            assert active[r] == x and flag == (r in owners) == (r >= word["public"])
            assert spaces[x] < spaces[y] or flag and spaces[y] < spaces[x]
            paid[abs(len(word["frames"][x])-len(word["frames"][y]))] += 1
            if flag:
                guards[clock] = (op, r, owners[r], old)
            active[r] = y
            return
        s = r if op == "SCALE" else a[0]
        assert op in ("ADD", "COPY", "SCALE") and active[r] == active[s] == a[-1]
        assert (s == r) == (op == "SCALE")
        source = get(s)
        if op == "COPY":
            assert not old
            guards[clock] = (op, r, owners.get(r), source)
        new = add({} if op == "SCALE" else old, source, Q(a[-2]))
        if new:
            rows[r] = new
        else:
            rows.pop(r, None)
        if clock in (CUT, 30590) and r in (1536,1546):
            first[clock] = (old, source, new)

    watches = {30531: (1510,), 30552: (1521,), 30582: (1547,), CUT: (402, 1536, 1546),
               45356: (727,), 45358: (727,)}
    tape = word["program"]
    stop = len(tape) if weights is not None else 45358
    for clock, event in enumerate(tape[:stop]):
        if clock in watches:
            snapshots[clock] = {r: get(r) for r in watches[clock]}
        if clock == CUT:
            bank = {r: get(r) for r, c in sorted(active.items()) if c == CHART and r != 402}
            assert tuple(bank) == (BANK if edited else (727, 1164, 1508, 1520, 1536, 1546, 1547))
            before_guards = guards.copy()
            if edited and weights is not None:
                for r, weight in weights.items():
                    if weight:
                        apply(["ADD", 402, r, weight, CHART], CUT)
        if edited and clock in OMIT:
            continue
        apply(CHANGES.get(clock, event) if edited else event, clock)
    if weights is not None:
        assert not owners and active == dict(enumerate(word["final"]))
    return {"snapshots": snapshots, "bank": bank, "guards": before_guards, "first": first,
            "paid": paid, "ops": ops, "final": rows if weights is not None else None}


def compare(word, spaces, initial, weights=None):
    old = replay(word, spaces, initial, False, {} if weights is not None else None)
    edited = replay(word, spaces, initial, True, weights)
    o, e = old["snapshots"], edited["snapshots"]
    u = o[30531][1510]
    assert u == e[30531][1510]
    assert o[30552][1521] == e[30552][1521] == add({}, u, Q(-1,4))
    assert o[30582][1547] == e[30582][1547]
    assert e[CUT][402] == add(o[CUT][402], u, Q(-1))
    assert e[CUT][1536] == o[CUT][1536] == add({}, edited["bank"][1547], Q(-1,4))
    assert not e[CUT][1546] and not o[CUT][1546]
    assert edited["bank"][727] == add(old["bank"][727], u, Q(1,4))
    assert all(edited["bank"][r] == old["bank"][r] for r in BANK if r != 727)
    assert o[45356][727] == e[45356][727]
    assert {i: v for i,v in old["guards"].items() if i != 30537} == edited["guards"]
    delta = edited["paid"].copy()
    delta.subtract(old["paid"])
    assert {r: v for r,v in delta.items() if v} == {1:-1, 2:-1, 3:1}
    if weights is None:
        for clock in (CUT,30590):
            assert edited["first"][clock][2] == add(old["first"][clock][2], u, Q(-1,4))
    else:
        assert old["first"] == edited["first"] and old["final"] == edited["final"]
    return old, edited, u


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def rationals(mapping):
    result = {int(k): Q(v) for k,v in mapping.items()}
    assert len(result) == len(mapping)
    return result


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()

    def cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", cut=CUT, cap_seconds=CAP, seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(CAP)
    data = {p: (args.root / p).read_bytes() for p in PINS}
    assert {p: sha256(b).hexdigest() for p,b in data.items()} == PINS
    native = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(native).hexdigest() == NATIVE
    word = loads(native, object_pairs_hook=unique)
    app = loads(data["inputs/7481-APPLICATION.json"], object_pairs_hook=unique)
    caller = loads(data["inputs/7113-CALLER.json"], object_pairs_hook=unique)
    assert app["candidate_canonical_sha256"] == NATIVE and app["caller_head"] == CALLER
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    assert caller["stages"] == sum(event[0] == "J" for event in caller["events"]) == 17
    spaces = check_word(word)
    raw = args.lead.read_bytes()
    assert sha256(raw).hexdigest() == args.lead_sha256
    lead = loads(raw, object_pairs_hook=unique)
    if "probe" in lead:
        probe = rationals(lead["probe"])
        assert probe and all(0 <= r < word["public"] and v for r,v in probe.items())
        old, edited, u = compare(word, spaces, {r: {0:v} for r,v in probe.items()})
        assert not any(edited["bank"].values()) and scalar(u) == 1
        record = {"status": "PASS_INDEPENDENT_OWNED1521_FIXED_BANK_SEPARATOR", "probe": probe,
                  "target_u": scalar(u), "edited_bank": {r:scalar(row) for r,row in edited["bank"].items()},
                  "old402": scalar(old["snapshots"][CUT][402]), "edited402": scalar(edited["snapshots"][CUT][402]),
                  "old_first_outputs": {i:scalar(row[2]) for i,row in old["first"].items()},
                  "edited_first_outputs": {i:scalar(row[2]) for i,row in edited["first"].items()},
                  "owner1547_at_return": scalar(old["snapshots"][30582][1547]),
                  "equal_727_after_old_return": scalar(old["snapshots"][45356][727]),
                  "earlier_numeric_guards_each_after_omission": len(edited["guards"])}
    else:
        weights = rationals(lead.get("representation", lead.get("coefficients")))
        assert weights.keys() <= set(BANK)
        initial = {r: {r:Q(1)} for r in range(word["public"])}
        old, edited, u = compare(word, spaces, initial, weights)
        recovered = {}
        for r,weight in weights.items():
            recovered = add(recovered, edited["bank"][r], weight)
        assert recovered == u
        record = {"status": "PASS_INDEPENDENT_RATIONAL_SUPPORT", "coefficients": weights,
                  "all_public_normalized_output_rows_match": True}
    emit(**record, cut=CUT, cap_seconds=CAP, input_pins=PINS, lead_sha256=args.lead_sha256,
         native_sha256=NATIVE, caller_head=CALLER, seconds=perf_counter()-started)
    alarm(0)


if __name__ == "__main__":
    main()
