"""Authenticate and replay the fixed chart912 bank exclusion."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
APPLICATION = "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f"


def unique(pairs):
    obj = dict(pairs)
    assert len(obj) == len(pairs), "duplicate key"
    return obj


def load(raw):
    return json.loads(raw, object_pairs_hook=unique)


def run(relative, *args):
    return subprocess.check_output(
        [sys.executable, "-I", "-B", str(HERE / relative), *map(str, args)],
        timeout=32,
    )


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12) and len(sys.argv) == 2
    pins = {}
    for line in (HERE / "SHA256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = HERE / name
        assert name not in pins and path.resolve().is_relative_to(HERE)
        assert not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == digest
        pins[name] = digest
    inputs = Path(sys.argv[1]).resolve() / "inputs"
    lead = run("check_496_first_bank.py", inputs, "--application-sha256", APPLICATION)
    assert lead == (HERE / "expected/PRIMARY.jsonl").read_bytes()
    old = load(lead.splitlines()[1])
    received = load(run("independent/check_role496_collision.py", inputs))
    expected = load((HERE / "expected/INDEPENDENT.json").read_bytes())
    assert 0 <= received.pop("seconds") < 30
    expected.pop("seconds")
    assert received == expected
    assert old["status"] == "EXCLUDED_FIXED_FIRST_BANK"
    assert old["full_bank_span_remainder"]["2"] == "-1"
    assert received["complete_bank"] == old["bank"]
    zero, probe = received["probes"]
    assert probe["input"] == {"2": "1"}
    assert zero["pre_read_edited_bank"] == probe["pre_read_edited_bank"]
    assert (zero["post_read_old220"], probe["post_read_old220"]) == ("0", "1/2")
    print("PASS_ROLE496_FIXED_CHART912_EXCLUSION")


if __name__ == "__main__":
    main()
