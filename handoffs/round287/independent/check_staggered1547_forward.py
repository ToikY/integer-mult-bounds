"""Replay the fixed owned1547 early cancellation and chart761 deadline."""
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
EARLY, OPTIONAL, CUT, CAP, CHART = 30588, 39897, 41950, 30, 761
BANK = (402, 569)
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
    assert contacts(t, 402, 30586, CUT + 1) == [30586,EARLY,41496,41949,CUT]
    assert contacts(t, 1547, 30581) == [30581,30582,OPTIONAL]
    assert t[OPTIONAL] == ["CLEAR",1547,470]
    assert t[41496] == ["ADD",402,1164,"4",470]
    assert t[41946:41952] == [
        ["ADD",569,1502,"-4",594], ["ADD",1531,569,"4",594],
        ["MOVE",569,594,761,False], ["MOVE",402,470,761,False],
        ["ADD",569,402,"1",761], ["MOVE",1164,470,761,False],
    ]
    assert t[30537] == ["MOVE", 1520, 1090, 470, True]
    assert t[30551] == ["MOVE", 1521, 470, 601, True]
    assert t[30581] == ["MOVE", 1547, 601, 470, True]
    assert t[30586] == ["ADD", 402, 727, "-4", 470]
    assert t[EARLY:EARLY+1] == [["ADD", 1536, 402, "1/4", 470]]
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


def replay(word, spaces, initial, edited, mandatory=None, optional=None):
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
        if clock in (EARLY, 30590, 30594, CUT) and r in (1536,1546,1537,569):
            first[clock] = (old, source, new)

    watches = {30531: (1510,), 30552: (1521,), 30582: (1547,), EARLY: (402,1536,1546),
               OPTIONAL: (1547,), 41947: (569,1531), CUT: BANK, 45356: (727,)}
    tape = word["program"]
    stop = len(tape) if mandatory is not None and optional is not None else 45356
    early_before = {}
    for clock, event in enumerate(tape[:stop]):
        if clock in watches:
            snapshots[clock] = {r: get(r) for r in watches[clock]}
        if edited and clock == 30581:
            apply(["ADD",1547,1521,"4",601], clock)
        if clock == OPTIONAL:
            chart470 = {r: get(r) for r,c in sorted(active.items()) if c == 470}
            assert tuple(chart470) == ((402,727,1164,1536,1547) if edited else
                                       (402,727,1164,1508,1520,1536,1547))
            if edited and optional is not None:
                scale, weights = optional
                if scale != 1:
                    apply(["SCALE",1547,scale,470], clock)
                for r,q in weights.items():
                    if q:
                        apply(["ADD",1547,r,q,470], clock)
        if clock == CUT:
            bank = {r: get(r) for r,c in sorted(active.items()) if c == CHART}
            assert tuple(bank) == BANK
            before_guards = guards.copy()
            if edited and mandatory is not None:
                scale, weight = mandatory
                if scale != 1:
                    apply(["SCALE",402,scale,CHART], CUT)
                if weight:
                    apply(["ADD",402,569,weight,CHART], CUT)
        if edited and clock in OMIT:
            continue
        apply(CHANGES.get(clock,event) if edited else event, clock)
        if clock == 30594:
            early_before = guards.copy()
    snapshots[45356] = {727: get(727)} if stop == 45356 else snapshots[45356]
    if stop == len(tape):
        assert not owners and active == dict(enumerate(word["final"]))
    return {"snapshots": snapshots, "bank": bank, "guards": before_guards, "first": first,
            "paid": paid, "ops": ops, "chart470": chart470, "early_guards": early_before,
            "final": rows if stop == len(tape) else None}


def compare(word, spaces, initial, mandatory=None, optional=None):
    full = mandatory is not None and optional is not None
    old = replay(word,spaces,initial,False,(Q(1),Q(0)) if full else None,(Q(1),{}) if full else None)
    edit = replay(word,spaces,initial,True,mandatory,optional)
    o,e = old["snapshots"],edit["snapshots"]
    u = o[30531][1510]
    assert u == e[30531][1510]
    assert o[30552][1521] == e[30552][1521] == add({},u,Q(-1,4))
    assert e[30582][1547] == add(o[30582][1547],u,Q(-1))
    assert e[EARLY][402] == add(o[EARLY][402],u,Q(-1))
    assert e[EARLY][1536] == add(o[EARLY][1536],u,Q(1,4))
    assert not o[EARLY][1546] and not e[EARLY][1546]
    assert all(old["first"][i][2] == edit["first"][i][2] for i in (EARLY,30590,30594))
    assert e[OPTIONAL][1547] == add(o[OPTIONAL][1547],u,Q(-1))
    assert edit["guards"][OPTIONAL][3] == (o[OPTIONAL][1547] if optional is not None else e[OPTIONAL][1547])
    assert o[41947] == e[41947]
    assert o[CUT][569] == e[CUT][569] and e[CUT][402] == add(o[CUT][402],u,Q(-1))
    assert o[45356][727] == e[45356][727]
    ignored = {30537,30581,39897,39947}
    assert {i:v for i,v in old["guards"].items() if i not in ignored} == {
        i:v for i,v in edit["guards"].items() if i not in ignored
    }
    delta = edit["paid"].copy()
    delta.subtract(old["paid"])
    assert {r:v for r,v in delta.items() if v} == {1:-1,2:-1,3:1}
    if mandatory is None:
        assert edit["first"][CUT][2] == add(old["first"][CUT][2],u,Q(-1))
    else:
        assert edit["first"][CUT] == old["first"][CUT]
    if full:
        assert old["final"] == edit["final"]
    return old,edit,u


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
    assert lead["cut"] == CUT if "cut" in lead else True
    gate = lead.get("mandatory", lead)
    raw_probe = gate.get("probe") or gate.get("separator")
    if raw_probe:
        probe = rationals(raw_probe)
        assert probe and all(0 <= r < word["public"] and v for r,v in probe.items())
        old,edit,u = compare(word,spaces,{r:{0:v} for r,v in probe.items()})
        assert not any(edit["bank"].values()) and scalar(old["bank"][402]) != 0
        record = {
            "status":"PASS_INDEPENDENT_STAGGERED_MANDATORY_SEPARATOR","probe":probe,
            "target_u":scalar(u),"edited_chart761_bank":{r:scalar(v) for r,v in edit["bank"].items()},
            "old402":scalar(old["bank"][402]),"old569":scalar(old["bank"][569]),
            "old_read_outputs":{i:scalar(v[2]) for i,v in old["first"].items()},
            "edited_read_outputs":{i:scalar(v[2]) for i,v in edit["first"].items()},
            "old1547_retirement":scalar(old["snapshots"][OPTIONAL][1547]),
            "edited1547_retirement":scalar(edit["snapshots"][OPTIONAL][1547]),
            "unchanged_numeric_guards":len(edit["guards"])-2,
            "optional_restore_solve_unrun":True,
        }
    else:
        scale = Q(gate["self_coefficient"])
        assert scale
        weights = rationals(gate["coefficients"])
        optional_gate = lead.get("optional")
        optional = None
        if optional_gate and optional_gate.get("self_coefficient"):
            opt_scale = Q(optional_gate["self_coefficient"])
            assert opt_scale
            optional = opt_scale,rationals(optional_gate["coefficients"])
        initial = {r:{r:Q(1)} for r in range(word["public"])}
        old,edit,_u = compare(word,spaces,initial,(scale,weights.get(569,Q(0))),optional)
        record = {"status":"PASS_INDEPENDENT_STAGGERED_RATIONAL_SUPPORT","mandatory_coefficients":weights,
                  "mandatory_scale":scale,"optional_normalized_restore_verified":optional is not None}
    emit(**record, cut=CUT, cap_seconds=CAP, input_pins=PINS, lead_sha256=args.lead_sha256,
         native_sha256=NATIVE, caller_head=CALLER, seconds=perf_counter()-started)
    alarm(0)


if __name__ == "__main__":
    main()
