"""Exact Type A rank16→8 and rank56→64 paid-incidence transfer screen."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

PINS = {
    "ROLE902-APPLICATION.json": "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
START, STOP, CAP = 1448, 1746, 30


def emit(**s):
    print(json.dumps(s, sort_keys=True), flush=True)


def propagate(events, role, b9):
    x = [Q(r == role) for r in range(36)]
    for kind, op, r, *a in events:
        assert kind == "A"
        if op == "ADD":
            x[r] += Q(a[1]) * x[a[0]]
        elif op == "SWAP":
            x[r], x[a[0]] = x[a[0]], x[r]
        elif op == "QUERY":
            assert a[1] in (-1, 1)
            x[r] += x[a[0]]  # q = +1
        elif op == "LAMBDA":
            assert a[0] in (-1, 1)  # 1/2*(1+q²) + i/2*(1−q²), q²=1
        else:
            assert op == "IDLE_ONE"
            if 9 in a[0]:
                x[r] *= b9
    return tuple(x)


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("inputs", type=Path)
    root = p.parse_args().inputs
    stage = "authenticate"
    visited = []

    def expired(_signum, _frame):
        emit(status="CAP_UNRESOLVED", cap=CAP, stage=stage, completed=visited,
             unvisited=[r for r in range(36) if r not in visited])
        raise SystemExit(124)

    signal(SIGALRM, expired)
    alarm(CAP)
    try:
        source = {p:(root/p).read_bytes() for p in PINS}
        assert all(sha256(raw).hexdigest() == PINS[p] for p, raw in source.items())
        app = json.loads(source["ROLE902-APPLICATION.json"])
        c = json.loads(source["7113-CALLER.json"])
        assert app["status"] == "PASS_ROLE902_FINAL_APPLICATION"
        assert app["candidate_canonical_sha256"] == "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
        assert app["caller_sha256"] == PINS["7113-CALLER.json"]
        assert Q(app["claim"]) == Q("0.003648411294790")
        count = len(c["types"]["A"]["ports"])
        assert count == 96 and c["types"]["A"]["roles"] == 36 and c["types"]["A"]["offset"] == 0
        declared = c["events"]
        e = declared[START:STOP]
        assert e[0] == ["A", "IDLE_ONE", 1, [2,3,4,5,6,7,8]]
        assert e[-1] == ["A", "IDLE_ONE", 11, [9,10]]
        assert declared[1742] == ["A", "IDLE_ONE", 10, [9]]
        assert all(x[0] == "A" for x in e)
        assert Counter(x[1] for x in e) == {
            "ADD": 262, "IDLE_ONE": 16, "SWAP": 8, "LAMBDA": 8, "QUERY": 4}
        modified = e.copy()
        modified[0] = ["A", "IDLE_ONE", 1, [2,3,4,5,6,7,8,9]]
        modified[-1] = ["A", "IDLE_ONE", 11, [10]]
        stage = "price"
        power = run_path(str(root / "pricing.py"))["power_bounds"]
        lo, hi = map(Q, app["raw_crossing"])
        lower = count*(power(16,hi)[0]+power(56,hi)[0]-power(8,lo)[1]-power(64,lo)[1])
        upper = count*(power(16,lo)[1]+power(56,lo)[1]-power(8,hi)[0]-power(64,hi)[0])
        assert 0 < lower < upper < count
        emit(status="START", cap_seconds=CAP, case_cap=1,
             scope=[START, STOP], paid_delta={8:96,16:-96,56:-96,64:96},
             target_delta={}, directed_optimistic_gross=[str(lower),str(upper)],
             width_one={"q":1,"B9":-1,"other_bodies":1,"minus_walsh_axes":[73,74]})
        stage = "36 exact boundary columns"
        witness = None
        changed_entries = 0
        for r in range(36):
            old = propagate(e, r, -1)
            new = propagate(modified, r, -1)
            assert propagate(e, r, 1) == propagate(modified, r, 1)
            changed = [i for i,(a,b) in enumerate(zip(old,new)) if a != b]
            changed_entries += len(changed)
            if changed and witness is None:
                i = changed[0]
                witness = dict(input=r, output=i, before=str(old[i]), after=str(new[i]),
                               difference=str(new[i]-old[i]))
            visited.append(r)
        emit(status=("EXCLUDED_FIXED_TYPE_A_B9_TRANSFER" if witness
                     else "PASSES_ONE_SPECIALIZATION_ONLY"), cases_completed=1,
             completed_columns=visited, witness=witness,
             changed_entries=changed_entries, unit_body_control="passed", unresolved=[])
    finally:
        alarm(0)


if __name__ == "__main__":
    assert __debug__
    main()
