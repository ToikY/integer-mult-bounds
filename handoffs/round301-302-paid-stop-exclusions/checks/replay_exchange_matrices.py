"""Verify the eight frozen #7605 exchange matrices by basis propagation."""
import argparse
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import signal

WORD_PIN = "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d"
CANONICAL_PIN = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
EXCHANGE_PIN = "41cca0f2c6f01905b0ab601d3a13191125dd158628a2cfeb336c2ed3330ec0ac"


def authenticate(path, expected):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == expected, f"SHA-256 mismatch: {path.name}"
    return data


def roles_touched(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def propagate(events, roles, nonzero_role):
    state = {role: Fraction(role == nonzero_role) for role in roles}
    for event in events:
        if event[0] == "ADD":
            _, destination, source, coefficient, _ = event
            state[destination] += Fraction(coefficient) * state[source]
        else:
            assert event[0] == "SCALE"
            _, destination, coefficient, _ = event
            state[destination] *= Fraction(coefficient)
    return [state[role] for role in roles]


def verify_case(tape, frozen):
    case = frozen["case"]
    roles = case["roles"]
    incoming, outgoing = roles
    low, middle, high = case["charts"]
    entry, exit_ = case["entry"], case["exit"]
    assert tape[entry][:4] == ["MOVE", incoming, low, middle]
    assert tape[exit_][:4] == ["MOVE", outgoing, middle, high]

    first, last = case["block"][0], case["block"][-1]
    actual_contacts = [
        clock for clock in range(first, last + 1)
        if set(roles).intersection(roles_touched(tape[clock]))
    ]
    assert actual_contacts == case["block"]
    assert all(incoming not in roles_touched(tape[clock]) for clock in range(entry + 1, first))
    assert all(outgoing not in roles_touched(tape[clock]) for clock in range(last + 1, exit_))
    block = [tape[clock] for clock in actual_contacts]
    assert all(event[-1] == middle and set(roles_touched(event)) <= set(roles) for event in block)
    columns = [propagate(block, roles, basis_role) for basis_role in roles]
    a, c = columns[0]
    b, d = columns[1]
    matrix = [[str(a), str(b)], [str(c), str(d)]]
    survives = a == d == 0 and b != 0 and c != 0
    assert matrix == frozen["matrix"] and survives == frozen["survives"]
    return {
        "block": actual_contacts, "entry": entry, "exit": exit_, "roles": roles,
        "charts": case["charts"], "matrix": matrix, "survives": survives,
        "mutual_adds": sum(event[0] == "ADD" for event in block),
    }


def main():
    assert __debug__, "Run without -O"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--frozen", type=Path, required=True)
    args = parser.parse_args()

    def timeout(_sig, _frame):
        print(json.dumps({"status": "TIME_CAP", "seconds_cap": 30}))
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    canonical_word = decompress(authenticate(args.word, WORD_PIN))
    assert sha256(canonical_word).hexdigest() == CANONICAL_PIN
    tape = json.loads(canonical_word)["program"]
    records = authenticate(args.frozen, EXCHANGE_PIN).splitlines()
    assert len(records) == 2
    frozen = json.loads(records[1])["tested"]
    assert len(frozen) == 8
    checked = [verify_case(tape, row) for row in frozen]
    result = {
        "status": "PASS_FROZEN_MATRICES", "case_count": len(checked), "seconds_cap": 30,
        "word_gzip_sha256": WORD_PIN, "word_canonical_sha256": CANONICAL_PIN,
        "frozen_sha256": EXCHANGE_PIN, "tested": checked,
        "antidiagonal_count": sum(row["survives"] for row in checked),
        "would_skip_with_minimum_three_mutual_adds": sum(row["mutual_adds"] < 3 for row in checked),
    }
    print(json.dumps(result, sort_keys=True))
    signal.alarm(0)


if __name__ == "__main__":
    main()
