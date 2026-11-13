"""Replay the exact chart117 exclusion and compare the old causal rows."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def command(path, *args):
    return subprocess.check_output([sys.executable, "-I", "-B", str(HERE / path),
                                   *map(str, args)], timeout=32)


def pairs(items):
    result = dict(items)
    assert len(result) == len(items)
    return result


def read(raw):
    return json.loads(raw, object_pairs_hook=pairs)


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12) and len(sys.argv) == 2
    seen = set()
    for line in (HERE / "SHA256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        source = HERE / name
        assert name not in seen and source.resolve().is_relative_to(HERE)
        assert not source.is_symlink() and sha256(source.read_bytes()).hexdigest() == digest
        seen.add(name)
    inputs = Path(sys.argv[1]).resolve() / "inputs"
    primary = command("check_1531.py", inputs)
    assert primary == (HERE / "expected/RESULT.json").read_bytes()
    compared = command("compare_7355.py", inputs)
    assert compared == (HERE / "expected/COMPARE.json").read_bytes()
    assert not read(compared)["changed_row_ids"]
    with tempfile.TemporaryDirectory(prefix="1531-replay-") as tmp:
        receipt = Path(tmp) / "primary.json"
        receipt.write_bytes(primary)
        checked = read(command("independent/check_1531_forward.py", inputs,
                               receipt, sha256(primary).hexdigest()))
    expected = read((HERE / "expected/FORWARD.json").read_bytes())
    expected.pop("seconds")
    assert 0 <= checked.pop("seconds") < 30 and checked == expected
    assert checked["full_bank_including_host_collision"]
    assert checked["old917_after_outward"] == "-2"
    print("PASS_1531_CHART117_COLLISION_AND_7355_ROW_RECONCILIATION")


if __name__ == "__main__":
    main()
