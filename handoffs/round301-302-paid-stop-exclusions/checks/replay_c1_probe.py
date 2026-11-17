"""Independent exact scalar forward probe of the fixed-prefix C1 separator."""
import argparse
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import signal

PINS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "FINAL7605.json": "f24baa73a60d084a6d613dad914f1237a5890a049a183b993af39c75dde99add",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "word7605.json.gz": "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d",
}
RESULT_PIN = "1c1f4c543c0260b3704612e73316a176e5f8b629ebfe1af7acf2c2d25bfe38f2"
CANONICAL_PIN = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
CUT = 42449


def authenticate(path, expected):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == expected, f"SHA-256 mismatch: {path.name}"
    return data


def step(state, event, public):
    op, dest, *args = event
    if op == "INIT":
        assert dest >= public and dest not in state
        state[dest] = (args[0], Fraction(0))
        return
    chart, value = state[dest]
    if op == "MOVE":
        assert chart == args[0] and args[2] == (dest >= public)
        chart = args[1]
    else:
        assert chart == args[-1]
        if op == "CLEAR":
            assert dest >= public
            del state[dest]
            return
        if op in ("ADD", "COPY"):
            sender_chart, sender_value = state[args[0]]
            assert chart == sender_chart
            term = sender_value * Fraction(args[1])
            value = value + term if op == "ADD" else term
        else:
            assert op == "SCALE"
            value *= Fraction(args[0])
    state[dest] = (chart, value)


def forward(word, x230, modified):
    program = word["program"]
    public = word["public"]
    state = {role: (chart, x230 if role == 230 else Fraction(0))
             for role, chart in enumerate(word["initial"])}
    for clock, event in enumerate(program[:CUT]):
        if modified:
            if clock in (38668, 42140, 42327):
                continue
            if clock == 38667:
                assert event == ["MOVE", 564, 3, 457, False]
                event = ["MOVE", 564, 3, 844, False]
            elif clock == 41706:
                step(state, ["ADD", 1158, 564, "-1", 844], public)
            elif clock == 42328:
                assert event == ["ADD", 396, 428, "1", 844]
                event = ["ADD", 564, 428, "1", 844]
            elif clock == 42448:
                assert event == ["MOVE", 564, 457, 895, False]
                event = ["MOVE", 396, 457, 895, False]
        if clock == 41706:
            assert event == ["ADD", 428, 1158, "-1", 844]
            earlier_chart, earlier = state[1158]
            assert earlier_chart == 844
        step(state, event, public)
    bank = sorted(role for role, (chart, _) in state.items() if chart == 895)
    assert bank == ([396, 504] if modified else [504, 564])
    return {"role1158_at_read41706": str(earlier),
            "chart895_at_cut42449": {str(role): str(state[role][1]) for role in bank}}


def retiming_contacts(word):
    tape = word["program"]
    rows = {564: [], 1158: []}
    for clock in range(38669, 41706):
        event = tape[clock]
        touched = event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]
        for role in rows:
            if role in touched:
                rows[role].append(clock)
    assert rows == {564: [], 1158: [41705]}
    assert tape[41705] == ["MOVE", 1158, 457, 844, False]
    return rows


def main():
    assert __debug__, "Run without -O"
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-root", type=Path, required=True)
    p.add_argument("--result", type=Path, required=True)
    args = p.parse_args()

    def timeout(_sig, _frame):
        print(json.dumps({"status": "TIME_CAP", "seconds_cap": 30}))
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    inp = {key: authenticate(args.input_root / key, pin) for key, pin in PINS.items()}
    primary = json.loads(authenticate(args.result, RESULT_PIN))
    assert primary["source_pins"] == PINS
    assert primary["status"] == "EXCLUDE_FIXED_PREFIX_C1_AT_FIRST_READ"
    assert primary["cut"] == CUT and primary["separator"] == {"230": "-1/2"}
    assert primary["fixed_bank"] == [396, 504] and primary["target"] == 564
    word_bytes = decompress(inp["word7605.json.gz"])
    final = json.loads(inp["FINAL7605.json"])
    assert sha256(word_bytes).hexdigest() == CANONICAL_PIN == final["candidate_canonical_sha256"]
    assert final["caller_sha256"] == PINS["7113-CALLER.json"]
    word = json.loads(word_bytes)
    assert word["program"][38668] == ["ADD", 1158, 564, "-1", 457]
    assert word["program"][CUT] == ["ADD", 504, 564, "1", 895]
    contacts = retiming_contacts(word)
    probes = {str(x): {"original": forward(word, x, False), "modified": forward(word, x, True)}
              for x in (Fraction(0), Fraction(primary["separator"]["230"]))}
    for probe in probes.values():
        assert probe["original"]["role1158_at_read41706"] == probe["modified"]["role1158_at_read41706"]
        assert probe["modified"]["chart895_at_cut42449"] == {"396": "0", "504": "0"}
    for key, expected in (("0", "0"), ("-1/2", "1")):
        assert probes[key]["original"]["chart895_at_cut42449"] == {"504": "0", "564": expected}
    print(json.dumps({"status": "PASS_EXACT_C1_FORWARD_SEPARATOR", "cut": CUT,
                      "input_pins": PINS, "result_sha256": RESULT_PIN, "word_canonical_sha256": CANONICAL_PIN,
                      "seconds_cap": 30, "probes": probes,
                      "retiming_intervening_contacts": contacts}, sort_keys=True))
    signal.alarm(0)


if __name__ == "__main__":
    main()
