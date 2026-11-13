"""Verify the pinned compiler exclusion from an explicit input directory."""
from hashlib import sha256
import json
from pathlib import Path
from subprocess import run
from sys import argv, executable, version_info

HERE = Path(__file__).resolve().parent


def checked_json(data):
    def unique(items):
        value = dict(items)
        assert len(value) == len(items), "duplicate key"
        return value
    return json.loads(data, object_pairs_hook=unique)


def execute(path, *args):
    proc = run([executable, "-I", "-B", str(HERE/path), *map(str, args)],
               check=True, capture_output=True, timeout=32)
    assert not proc.stderr
    return proc.stdout


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    root = Path(argv[1]).resolve()
    pins = {}
    for line in (HERE/"INPUT-SHA256").read_text().splitlines():
        digest, relative = line.split("  ")
        assert relative not in pins
        pins[relative] = digest
    for relative, digest in pins.items():
        assert sha256((root/relative).read_bytes()).hexdigest() == digest, relative
    primary = execute("lead/check_compiler.py", root)
    assert primary == (HERE/"receipts/PRIMARY.json").read_bytes()
    independent = checked_json(execute("independent/check_idle_grammar.py", root, root/"inputs", "--compiler-root"))
    assert 0 <= independent.pop("seconds") < 30
    expected = checked_json((HERE/"receipts/INDEPENDENT.json").read_bytes())
    expected.pop("seconds", None)
    assert independent == expected
    assert independent["old_paid_positions"] == 110519
    assert independent["old_rank_nine_positions"] == 32
    assert independent["one_call_rank13_volume_11_over_8"] is False
    print("PASS_R285_FIXED_SIGNED_IDLE_GRAMMAR")


if __name__ == "__main__":
    main()
