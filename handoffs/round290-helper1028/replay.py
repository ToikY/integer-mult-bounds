"""Run the two exact repair exclusions from an explicit dependency root."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate manifest or receipt key"
    return result


def replay(script, inputs, receipt, *, measured=False):
    command = [sys.executable, "-I", "-B", str(HERE / script), str(inputs)]
    raw = subprocess.check_output(command, cwd=HERE, timeout=32)
    frozen = (HERE / "expected" / receipt).read_bytes()
    if measured:
        result = json.loads(raw, object_pairs_hook=unique)
        reference = json.loads(frozen, object_pairs_hook=unique)
        assert 0 <= result.pop("seconds") < 30
        reference.pop("seconds")
        assert result == reference, script
    else:
        assert raw == frozen, script


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12) and len(sys.argv) == 2
    inputs = Path(sys.argv[1]).resolve() / "inputs"
    replay("check_1028_suffix.py", inputs, "PRIMARY.jsonl")
    replay("independent/check_1028_forward.py", inputs, "INDEPENDENT-BASIS.json", measured=True)
    replay("independent/check_1028_terminal_pair.py", inputs, "TERMINAL.json", measured=True)
    replay("local/check_1028_local.py", inputs, "CHART23.json")
    print("PASS_1028_TWO_FIXED_REPAIR_EXCLUSIONS")


if __name__ == "__main__":
    main()
