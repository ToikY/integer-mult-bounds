"""Authenticate and replay the fixed chart515 productive readout exclusion."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


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
    lead = run("check_1264_output.py", inputs)
    assert lead == (HERE / "expected/PRIMARY.jsonl").read_bytes()
    old = load(lead.splitlines()[1])
    received = load(run("independent/check_role1264_collision.py", inputs))
    expected = load((HERE / "expected/INDEPENDENT.json").read_bytes())
    assert 0 <= received.pop("seconds") < 30
    expected.pop("seconds")
    assert received == expected
    assert old["status"] == "EXCLUDED_FIXED_1264_READOUT"
    assert len(old["unsupplied_row"]) == 60
    assert received["complete_bank"] == old["bank"]
    zero, probe = received["probes"]
    assert probe["input"] == {"516": 2, "1264": 1}
    assert zero["chart515_bank"] == probe["chart515_bank"] == [0, 0, 0]
    assert (zero["required_original_x1264"], probe["required_original_x1264"]) == (0, 1)
    print("PASS_ROLE1264_FIXED_CHART515_READOUT_EXCLUSION")


if __name__ == "__main__":
    main()
