"""Authenticate and replay the fixed Type A B9 paid transfer exclusion."""
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
    lead = run("check_type_a_b9_transfer.py", inputs)
    assert lead == (HERE / "expected/PRIMARY.jsonl").read_bytes()
    old = load(lead.splitlines()[1])
    received = load(run("independent/check_type_a_b9_reverse.py", inputs, inputs / "ROLE902-WORD.json.gz"))
    expected = load((HERE / "expected/INDEPENDENT.json").read_bytes())
    assert 0 <= received.pop("seconds") < 30
    expected.pop("seconds")
    assert received == expected
    assert old["status"] == "EXCLUDED_FIXED_TYPE_A_B9_TRANSFER"
    assert received["first_witness"] == old["witness"]
    assert len(received["all_difference_entries"]) == old["changed_entries"] == 3
    assert len(received["completed_rows"]) == len(old["completed_columns"]) == 36
    assert received["unit_body_full_matrix_equal"]
    assert received["one_omitted_1742_changed_entries"] == 2
    print("PASS_FIXED_TYPE_A_B9_TRANSFER_EXCLUSION")


if __name__ == "__main__":
    main()
