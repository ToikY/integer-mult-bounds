"""One paid bypass with fixed restoration banks for both 581/582 outputs."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

PINS = {
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "ROLE902-APPLICATION.json": "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
CAP = 30
OFF = {36510, 36511, 39905}
GATES = (
    (42252, 879, 581, [316, 581, 1078, 1258]),
    (42255, 880, 582, [582, 1080, 1259, 1398]),
)


def show(row):
    return {str(k): str(v) for k, v in sorted(row.items()) if v}


def emit(**fields):
    print(json.dumps(fields, sort_keys=True), flush=True)


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("inputs", type=Path)
    inp = p.parse_args().inputs
    phase = "authentication"

    def expired(_signum, _frame):
        emit(status="CAP_UNRESOLVED", cap_seconds=CAP, phase=phase, cases_completed=0)
        raise SystemExit(124)

    signal(SIGALRM, expired)
    alarm(CAP)
    try:
        inputs = {name: (inp / name).read_bytes() for name in PINS}
        assert all(sha256(raw).hexdigest() == PINS[name] for name, raw in inputs.items())
        app = json.loads(inputs["ROLE902-APPLICATION.json"])
        assert app["candidate_canonical_sha256"] == WORD
        assert app["status"] == "PASS_ROLE902_FINAL_APPLICATION"
        assert app["caller_sha256"] == PINS["7113-CALLER.json"]
        raw = decompress(inputs["ROLE902-WORD.json.gz"])
        assert sha256(raw).hexdigest() == WORD
        w = json.loads(raw)
        tape = w["program"]
        assert tape[36507:36512] == [
            ["ADD", 581, 582, "1", 3],
            ["MOVE", 581, 3, 595, False],
            ["ADD", 1556, 581, "1", 595],
            ["MOVE", 582, 3, 595, False],
            ["ADD", 1556, 582, "1", 595],
        ]
        assert tape[39904:39906] == [["ADD", 581, 1503, "2", 595],
                                    ["ADD", 582, 1503, "2", 595]]
        assert tape[41553:41555] == [["MOVE", 581, 595, 766, False],
                                    ["ADD", 581, 428, "1", 766]]
        assert tape[41558:41560] == [["MOVE", 582, 595, 767, False],
                                    ["ADD", 582, 430, "1", 767]]
        assert tape[42252] == ["ADD", 316, 581, "1", 879]
        assert tape[42255] == ["ADD", 1398, 582, "1", 880]
        assert [len(w["frames"][i]) for i in [3, 595, 767]] == [0, 1, 4]
        assert w["frames"][3] == []

        phase = "directed gross"
        lo, hi = map(Q, app["raw_crossing"])
        assert Q(app["claim"]) == Q("0.003648411294790") < lo < hi
        power = run_path(str(inp / "pricing.py"))["power_bounds"]
        gross = (17 * (1 + power(3, hi)[0] - power(4, lo)[1]),
                 17 * (1 + power(3, lo)[1] - power(4, hi)[0]))
        assert 0 < gross[0] < gross[1] < 1
        emit(status="START", cap_seconds=CAP, case_cap=1,
             paid_delta={1: -17, 3: -17, 4: 17},
             productive_delta={}, optimistic_gross=list(map(str, gross)))

        phase = "literal rewrite"
        patches = {
            36507: ["ADD", 581, 582, "2", 3],
            41558: ["MOVE", 582, 3, 767, False],
        }
        engine = run_path(str(inp / "gate.py"))
        rows = engine["exact_cut_rows"]
        cut = 36512
        prefix = tape[:cut]
        edited = [patches.get(i, e) for i, e in enumerate(prefix) if i not in OFF]
        assert rows(prefix, [1556], w["public"]) == rows(edited, [1556], w["public"])
        source = rows(tape[:36507], [582], w["public"])[0]
        late_source = rows(tape[:39905], [1503], w["public"])[0]

        for index, (cut, chart, r, bank) in enumerate(GATES):
            phase = f"fixed bank before {cut}"
            active = w["initial"] + [None] * w["owned_fields"]
            for op, role, *args in tape[:cut]:
                if op == "MOVE":
                    assert active[role] == args[0]
                    active[role] = args[1]
                elif op == "INIT":
                    assert active[role] is None
                    active[role] = args[0]
                elif op == "CLEAR":
                    assert active[role] == args[0]
                    active[role] = None
            assert [j for j, c in enumerate(active) if c == chart] == bank
            before = tape[:cut]
            edited = []
            for i, e in enumerate(before):
                if i not in OFF:
                    replacement = patches.get(i, e)
                    edited.extend(replacement if isinstance(replacement[0],list) else [replacement])
            old = rows(before, bank, w["public"])
            new = rows(edited, bank, w["public"])
            own = bank.index(r)
            assert all(x == y for j, (x, y) in enumerate(zip(old,new)) if j != own)
            diff = new[own].copy()
            for k, v in old[own].items():
                engine["add"](diff, k, -v)
            expected = source if r == 581 else {k: -2*v for k,v in late_source.items()}
            assert diff == expected
            donors = [v for j, v in enumerate(new) if j != own]
            pivot = engine["basis"](donors)
            want, have = [engine["representation"](pivot, x)[0] for x in (old[own], new[own])]
            self_coefficient = Q(1) if not (have or want) else None
            if have and want:
                j = min(have)
                x = want.get(j, 0)/have[j]
                if x and want == {k:x*v for k,v in have.items()}:
                    self_coefficient = x
            residual, _ = engine["representation"](engine["basis"](new), old[own])
            if self_coefficient is None:
                emit(status="EXCLUDED_FIXED_BANK", cases_completed=1,
                     cut=cut, bank=bank, role=r, unsupplied=show(residual),
                     wanted_quotient=show(want), supplied_quotient=show(have),
                     gates_unrun=[g[0] for g in GATES[index+1:]])
                return
            need = old[own].copy()
            for k, v in new[own].items():
                engine["add"](need, k, -self_coefficient*v)
            missing, supply = engine["representation"](pivot, need)
            assert not missing
            donor_roles = [j for j in bank if j != r]
            repairs = [["SCALE", r, str(self_coefficient), chart]]
            repairs.extend(["ADD",r,donor_roles[j],str(x),chart] for j,x in sorted(supply.items()))
            patches[cut] = [*repairs, tape[cut]]
        emit(status="PASSED_BOTH_FIXED_SUPPORT_GATES", cases_completed=1,
             repairs={str(i): patches[i][:-1] for i, *_ in GATES},
             full_physical_and_paid_application="pending")
    finally:
        alarm(0)


if __name__ == "__main__":
    assert __debug__
    main()
