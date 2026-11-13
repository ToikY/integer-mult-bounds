"""Test one fixed Type B square through the ordinary interval between 1887 and 1940."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from runpy import run_path
import json
import signal

PINS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "COMPOSED-APPLICATION.json": "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
START, STOP, ROLE, CAP = 1887, 1940, 36, 30
MASK = [3, 4, 5, 6, 7, 8]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    args = parser.parse_args()
    phase = "authentication"

    def expired(_signal, _frame):
        print(json.dumps({"status": "CAP_UNRESOLVED", "phase": phase,
                          "clock_pair": [START, STOP], "cap_seconds": CAP}), flush=True)
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, expired)
    signal.alarm(CAP)
    try:
        for path, expected in PINS.items():
            assert sha256((args.inputs / path).read_bytes()).hexdigest() == expected, path
        caller = json.loads((args.inputs / "7113-CALLER.json").read_text())
        app = json.loads((args.inputs / "COMPOSED-APPLICATION.json").read_text())
        assert app["claim_decimal"] == "0.003647969120276"
        assert app["caller_sha256"] == PINS["7113-CALLER.json"]
        assert app["candidate_canonical_sha256"] == "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
        assert caller["types"]["B"]["offset"] == ROLE and caller["types"]["B"]["roles"] == 36
        ports = caller["types"]["B"]["ports"]
        assert ports == [15, 17, 27, 34, 35, 42, 47, 55]
        events = caller["events"]
        assert events[START] == events[STOP] == ["B", "IDLE_ONE", ROLE, MASK]
        ordinary = events[START + 1:STOP]
        assert len(ordinary) == 52 and all(e[0] == "B" for e in ordinary)
        assert sorted(e[1] for e in ordinary) == ["ADD"] * 31 + ["SCALE"] * 2 + ["SWAP"] * 19

        phase = "directed price"
        lo, hi = map(Q, app["raw_crossing"])
        power = run_path(str(args.inputs / "pricing.py"))["power_bounds"]
        gross = [2 * len(ports) * power(48, hi)[0], 2 * len(ports) * power(48, lo)[1]]
        print(json.dumps({
            "status": "START", "clock_pair": [START, STOP], "role": ROLE,
            "ports": ports, "cap_seconds": CAP, "mask": MASK,
            "specialization": {"width": 1, "q": 1, "B3": -1,
                                "other_bodies": 1, "minus_walsh_axes": [25, 26]},
            "signed_delta_paid": {"48": -16}, "signed_delta_productive": {},
            "optimistic_directed_saving": list(map(str, gross)),
        }), flush=True)

        phase = "full ordinary column and dual row"
        column = [Q(j == ROLE) for j in range(72)]
        row = column.copy()
        for _, op, dest, value, *args in ordinary:
            if op == "SWAP":
                column[dest], column[value] = column[value], column[dest]
            elif op == "ADD":
                column[dest] += Q(args[0]) * column[value]
            else:
                column[dest] *= Q(value)
        for _, op, dest, value, *args in reversed(ordinary):
            if op == "SWAP":
                row[dest], row[value] = row[value], row[dest]
            elif op == "ADD":
                row[value] += Q(args[0]) * row[dest]
            else:
                row[dest] *= Q(value)
        assert row[ROLE] == column[ROLE]
        assert all(not x for x in row[:ROLE] + column[:ROLE])
        # At either off-diagonal in the crossing row/column, DMD - M is -2M.
        witnesses = [(out_role, ROLE, str(x), str(-2 * x))
                     for out_role, x in enumerate(column) if out_role != ROLE and x]
        witnesses.extend((ROLE, in_role, str(x), str(-2 * x))
                         for in_role, x in enumerate(row) if in_role != ROLE and x)
        assert row[ROLE] or witnesses, "Role 36 cannot have a zero row in an invertible map"
        print(json.dumps({
            "status": ("EXCLUDED_FIXED_EQUAL_IDLE_SQUARE" if witnesses
                       else "PASS_ORDINARY_COMMUTATION_ONLY"),
            "tested_cases": 1, "unresolved": [],
            "complete_cross_entries": witnesses,
            "first_counterexample": witnesses[0] if witnesses else None,
            "central_entry": str(row[ROLE]),
        }), flush=True)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    assert __debug__
    main()
