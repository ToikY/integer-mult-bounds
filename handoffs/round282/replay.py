"""Reproduce the exact bounded paired incoming route inventories."""
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import argv, executable, implementation, version_info

HERE = Path(__file__).resolve().parent


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate JSON key"
    return result


def parse(raw):
    return loads(raw, object_pairs_hook=unique)


def reproduce(script, *args):
    result = run([executable, "-I", "-B", str(HERE / script), *map(str, args)],
                 capture_output=True, timeout=32, check=True)
    assert not result.stderr
    return result.stdout


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    assert len(argv) == 2, "Usage: python3.12 -I -B replay.py replay-root"
    root = Path(argv[1]).resolve()
    input_pins = {}
    for line in (HERE / "INPUT-SHA256").read_text().splitlines():
        digest, relative = line.split("  ")
        assert relative not in input_pins, relative
        input_pins[relative] = digest
    assert set(input_pins) == {"inputs/" + filename for filename in (
        "7481-WORD.json.gz", "7481-APPLICATION.json", "7113-CALLER.json", "pricing.py"
    )}
    for relative, digest in input_pins.items():
        assert sha256((root / relative).read_bytes()).hexdigest() == digest, relative
    lead = HERE / "receipts/PRIMARY.json"
    forward = reproduce("check_paired_incoming.py", root / "inputs")
    assert forward == lead.read_bytes()
    independent = reproduce("check_paired_incoming_independent.py", root, lead, sha256(forward).hexdigest())
    actual = parse(independent)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((HERE / "receipts/INDEPENDENT.json").read_bytes())
    assert actual["status"] == "PASS_INDEPENDENT_SOURCE_HISTORY_SCREEN"
    assert actual["lead_disposition"] == "EXHAUSTED" and actual["unvisited"] == []
    assert actual["tested"] == 0 and actual["candidate"] is None
    assert actual["counters"] == {"single_incoming_move_windows": 264, "matched_source_versions": 6,
                                  "eligible_funded_routes": 0}
    assert actual["rejections"] == {"different_exact_entry": 10, "non_nested_detour": 2}
    assert len(actual["direction_details"]) == 12
    print("PASS_R282_PAIRED_INCOMING_HANDOFF: 264 windows, six source-version pairs, zero eligible orientations")


if __name__ == "__main__":
    main()
