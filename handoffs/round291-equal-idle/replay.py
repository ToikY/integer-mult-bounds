"""Replay and reconcile the two exact signed idle-square checks."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def unique(pairs):
    mapped = dict(pairs)
    assert len(mapped) == len(pairs), "duplicate receipt key"
    return mapped


def run(script, inputs):
    return subprocess.check_output(
        [sys.executable, "-I", "-B", str(HERE / script), str(inputs)],
        timeout=32,
    )


def load(raw):
    return json.loads(raw, object_pairs_hook=unique)


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12) and len(sys.argv) == 2
    inputs = Path(sys.argv[1]).resolve() / "inputs"
    primary = run("check_equal_idle_square.py", inputs)
    assert primary == (HERE / "expected/PRIMARY.jsonl").read_bytes()
    lead = load(primary.splitlines()[1])
    replay = load(run("independent/check_equal_idle_forward.py", inputs))
    saved = load((HERE / "expected/INDEPENDENT.json").read_bytes())
    assert 0 <= replay.pop("seconds") < 30
    saved.pop("seconds")
    assert replay == saved
    assert lead["status"] == "EXCLUDED_FIXED_EQUAL_IDLE_SQUARE"
    assert replay["status"] == "INDEPENDENT_FIXED_SQUARE_EXCLUSION"
    direct = {(a,b): Fraction(d) for a,b,_,d in lead["complete_cross_entries"]}
    independent = {(a,b): Fraction(d) for a,b,_,_,d in replay["mismatch_entries"]}
    assert independent == direct and all(36 in pair for pair in independent)
    assert -independent[36,37] * independent[37,36] == 4
    print("PASS_EQUAL_MASK_TYPEB_SQUARE_EXCLUSION rank=2 minor=4")


if __name__ == "__main__":
    main()
