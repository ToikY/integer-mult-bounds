"""Price and screen one exact productive cutoff on helper1264."""
import argparse
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal

CAP, CUT, ROLE = 30, 38880, 1264
BANK = [446, 1203, ROLE]
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
PINS = {
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "ROLE902-APPLICATION.json": "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
    "suffix_readout.py": "7514d10bc4a6c96a583f3619aaa869c360ffa80085d3bb2a732cb6b9f4821b67",
}


def show(row):
    return {str(k): str(v) for k, v in sorted(row.items()) if v}


def emit(**fields):
    print(json.dumps(fields, sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    args = parser.parse_args()
    phase = "source authentication"

    def expired(_signum, _frame):
        emit(status="CAP_UNRESOLVED", phase=phase, cut=CUT, cap_seconds=CAP)
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, expired)
    signal.alarm(CAP)
    try:
        sources = {name: (args.inputs / name).read_bytes() for name in PINS}
        for name, raw in sources.items():
            assert sha256(raw).hexdigest() == PINS[name], name
        app = json.loads(sources["ROLE902-APPLICATION.json"])
        assert app["status"] == "PASS_ROLE902_FINAL_APPLICATION"
        assert app["candidate_canonical_sha256"] == WORD
        assert app["caller_sha256"] == PINS["7113-CALLER.json"]
        assert (app["outer"]["strict_count"], app["outer"]["functional_count"]) == (54, 4)
        assert Q(app["claim"]) == Q("0.003648411294790")
        raw = decompress(sources["ROLE902-WORD.json.gz"])
        assert sha256(raw).hexdigest() == WORD
        word = json.loads(raw)
        tape = word["program"]
        main = set(word["live"]) | {r + 112 for r in word["live"]}
        main |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
        assert ROLE not in main and ROLE < word["public"]
        assert word["initial"][ROLE] == 3 and word["final"][ROLE] == 127
        assert tape[CUT - 1:CUT + 1] == [
            ["MOVE", ROLE, 3, 515, False], ["ADD", 1203, ROLE, "-1", 515]]
        assert [len(word["frames"][j]) for j in (3, 515, 127)] == [0, 3, 9]

        phase = "directed complete-price ceiling"
        lo, hi = map(Q, app["raw_crossing"])
        assert Q(app["claim"]) < lo < hi < Q(1, 32)
        power = run_path(str(args.inputs / "pricing.py"))["power_bounds"]
        gross = [17 * (power(3, hi)[0] + power(6, hi)[0] - power(9, lo)[1]),
                 17 * (power(3, lo)[1] + power(6, lo)[1] - power(9, hi)[0])]
        assert 0 < gross[0] < gross[1] < 1
        emit(status="START", cut=CUT, cap_seconds=CAP,
             comparator="0.003648411294790", paid_delta={},
             productive_delta={3: 17, 6: 17, 9: -17},
             optimistic_directed_saving=list(map(str, gross)), pins=PINS)

        phase = "exact prefix, chart bank and readout"
        contacts = [(i, e) for i, e in enumerate(tape[:CUT])
                    if e[1] == ROLE or e[0] in ("ADD", "COPY") and e[2] == ROLE]
        assert contacts == [
            (29218, ["ADD", ROLE, 917, "1", 3]),
            (32344, ["ADD", ROLE, 932, "1", 3]),
            (32479, ["ADD", ROLE, 899, "-1", 3]),
            (38879, ["MOVE", ROLE, 3, 515, False]),
        ]
        active = word["initial"] + [None] * word["owned_fields"]
        for op, dest, *rest in tape[:CUT]:
            if op == "MOVE":
                assert active[dest] == rest[0]
                active[dest] = rest[1]
            elif op == "INIT":
                assert active[dest] is None
                active[dest] = rest[0]
            elif op == "CLEAR":
                assert active[dest] == rest[0]
                active[dest] = None
        assert [r for r, chart in enumerate(active) if chart == 515] == BANK
        engine = run_path(str(args.inputs / "gate.py"))
        old = engine["exact_cut_rows"](tape[:CUT], BANK, word["public"])
        assert [r.get(ROLE, 0) for r in old] == [0, 0, 1]
        need = {ROLE: Q(1)}
        for j, v in old[BANK.index(ROLE)].items():
            engine["add"](need, j, -v)
        donors = old[:BANK.index(ROLE)]
        remainder, coefficients = engine["representation"](engine["basis"](donors), need)
        if remainder:
            emit(status="EXCLUDED_FIXED_1264_READOUT", cases_completed=1, unresolved=[],
                 cut=CUT, bank=BANK, unsupplied_row=show(remainder),
                 farther_gates="unrun after fixed readout failure")
            return
        readout = {BANK[j]: value for j, value in coefficients.items()}
        readout[ROLE] = Q(1)
        phase = "fixed suffix injection and guarded contacts"
        suffix = run_path(str(args.inputs / "suffix_readout.py"))
        smooth_denominators = all(suffix["scalar_smooth"](q.denominator)
                                  for q in readout.values())
        impulse = {ROLE: Q(1)}
        guards = []
        for i, e in enumerate(tape[CUT:], CUT):
            op, dest, *rest = e
            if op == "ADD" and dest >= word["public"] and impulse.get(rest[0]):
                guards.append([i, op, dest, str(impulse[rest[0]])])
            if op in ("CLEAR", "COPY") and impulse.get(dest):
                guards.append([i, op, dest, str(impulse[dest])])
            if op == "COPY" and impulse.get(rest[0]):
                guards.append([i, op + "_SOURCE", rest[0], str(impulse[rest[0]])])
            if guards:
                break
            impulse = suffix["forward"]([e], impulse)
        status = "PASSES_NORMALIZED_1264_GATE_ONLY"
        if guards or impulse != {ROLE: Q(1)}:
            status = "EXCLUDED_FIXED_1264_INJECTION"
        emit(status=status, cases_completed=1, unresolved=[], cut=CUT, bank=BANK,
             readout=show(readout), first_guard=guards[0] if guards else None,
             suffix_endpoint=show(impulse), smooth_denominators=smooth_denominators,
             physical_typed_admission="pending")
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    assert __debug__
    main()
