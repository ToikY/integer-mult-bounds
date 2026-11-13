"""Price native owned MOVE runs, then check up to eight exact zero rows."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import signal

PINS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "ROLE902-APPLICATION.json": "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
CAP, CASES = 30, 8


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    obj = dict(pairs)
    assert len(obj) == len(pairs), "duplicate key"
    return obj


def load(raw):
    return json.loads(raw, object_pairs_hook=unique)


def emit(**obj):
    print(json.dumps(obj, sort_keys=True, default=str), flush=True)


def span(frame):
    result = {0}
    for vector in frame:
        assert vector not in result
        result |= {vector ^ other for other in result}
    return result


def enumerate_runs(word, position):
    tape = word["program"]
    public = word["public"]
    dimensions = [len(frame) for frame in word["frames"]]
    spans = list(map(span, word["frames"]))
    active = {}
    runs = []
    deferred = []
    lives = 0
    for clock, (op, dest, *args) in enumerate(tape):
        position[0] = clock
        if op == "INIT":
            assert dest >= public and dest not in active
            active[dest] = dict(owner=clock, previous=clock, chart=args[0], moves=[], cases=[], copy=False)
        elif op == "MOVE" and dest >= public:
            state = active[dest]
            a, b, owned = args
            assert owned and a == state["chart"] and (spans[a] < spans[b] or spans[b] < spans[a])
            state["moves"].append(clock)
            state["chart"] = b
        elif op != "MOVE":
            roles = {dest}
            if op in ("ADD", "COPY"):
                roles.add(args[0])
            for role in sorted(roles):
                if role < public:
                    continue
                state = active[role]
                assert state["chart"] == args[-1]
                if moves := state["moves"]:
                    old, new = tape[moves[0]][2], tape[moves[-1]][3]
                    ranks = [abs(dimensions[tape[i][2]] - dimensions[tape[i][3]]) for i in moves]
                    state["cases"].append(dict(
                        role=role, owner=state["owner"], previous_contact=state["previous"],
                        first_move=moves[0], moves=moves, ranks=ranks,
                        next_contact=clock, old_chart=old, next_chart=new,
                        kind="terminal_clear" if op == "CLEAR" else "fresh_init",
                    ))
                state["previous"], state["moves"] = clock, []
                if op == "COPY" and role == dest:
                    state["copy"] = True
                if op == "CLEAR":
                    (deferred if state["copy"] else runs).extend(state["cases"])
                    del active[role]
                    lives += 1
    assert not active and lives == 74 and len(tape) == 76490
    return runs, deferred


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("frozen", type=Path)
    args = parser.parse_args()
    phase, position, done = "authentication", [-1], []

    def timeout(_signum, _frame):
        emit(status="CAPPED", phase=phase, last_event=position[0], cases_completed=done)
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(CAP)
    raw = {key: (args.inputs / key).read_bytes() for key in PINS}
    assert {key: sha(value) for key, value in raw.items()} == PINS
    app, caller = (load(raw[k]) for k in ("ROLE902-APPLICATION.json", "7113-CALLER.json"))
    payload = gzip.decompress(raw["ROLE902-WORD.json.gz"])
    assert sha(payload) == app["candidate_canonical_sha256"] == WORD
    assert app["status"] == "PASS_ROLE902_FINAL_APPLICATION"
    assert app["caller_sha256"] == PINS["7113-CALLER.json"]
    calls = sum(event[0] == "J" for event in caller["events"])
    assert calls == caller["stages"] == 17
    word = load(payload)
    assert Fraction(app["claim"]) == Fraction("0.003648411294790")
    phase = "static census and directed price"
    runs, deferred = enumerate_runs(word, position)
    assert sum(len(run["moves"]) for run in runs + deferred) == 47
    low, high = map(Fraction, app["raw_crossing"])
    power = runpy.run_path(str(args.inputs / "pricing.py"))["power_bounds"]
    tariffs = {r: (power(r, high)[0], power(r, low)[1])
               for r in {r for item in runs for r in item["ranks"]}}
    for run in runs:
        run["signed_gross"] = [str(calls * sum(tariffs[r][i] for r in run["ranks"])) for i in (0, 1)]
        run["signed_paid_delta"] = {r: -n * calls for r, n in Counter(run["ranks"]).items()}
    runs.sort(key=lambda item: (-Fraction(item["signed_gross"][1]), item["first_move"],
                                item["role"], item["next_contact"]))
    frozen = json.dumps(runs[:CASES], sort_keys=True, indent=2) + "\n"
    args.frozen.write_text(frozen)
    emit(status="RANKED", cap_seconds=CAP, case_cap=CASES, eligible=len(runs), copy_deferred=deferred,
         tested_order=runs[:CASES], remaining_order=runs[CASES:], frozen_sha256=sha(frozen.encode()), pins=PINS)
    phase = "exact normalized row"
    rows = runpy.run_path(str(args.inputs / "gate.py"))["exact_cut_rows"]
    tape = word["program"]
    survivor = None
    for item in runs[:CASES]:
        k, role = item["first_move"], item["role"]
        position[0] = k
        row, = rows(tape[:k], [role], word["public"])
        after, = rows(tape[:item["next_contact"]], [role], word["public"])
        assert after == row
        case = dict(role=role, first_move=k, next_contact=item["next_contact"], terms=len(row))
        if row:
            key = min(row)
            case["nonzero_coefficient"] = [key, str(row[key])]
        else:
            survivor = item
        done.append(case)
        emit(status="ZERO_ROW" if not row else "NONZERO_ROW", **case)
        if survivor:
            break
    emit(status="ZERO_SURVIVOR_PENDING_CONTRACT" if survivor else "NO_ZERO_IN_TESTED_RUNS",
         cases_completed=done, survivor=survivor,
         unresolved=[[x["role"], x["first_move"]] for x in runs[len(done):]],
         copy_deferred=[[x["role"], x["first_move"]] for x in deferred])
    signal.alarm(0)


if __name__ == "__main__":
    assert __debug__
    main()
