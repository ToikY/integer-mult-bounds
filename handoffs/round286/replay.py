"""Reproduce both exact bounded owned1521 fixed-bank checks."""
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import argv, executable, implementation, version_info

HERE = Path(__file__).resolve().parent


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON key"
    return result


def replay(script, *args, cwd=None):
    result = run([executable, "-I", "-B", str(HERE / script), *map(str, args)],
                 capture_output=True, timeout=32, check=True, cwd=cwd)
    assert not result.stderr
    return result.stdout


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    assert len(argv) == 2, "Usage: python3.12 -I -B replay.py replay-root"
    root = Path(argv[1]).resolve()
    inputs = {}
    for line in (HERE / "INPUT-SHA256").read_text().splitlines():
        digest, relative = line.split("  ")
        assert relative not in inputs
        inputs[relative] = digest
    assert set(inputs) == {"inputs/" + name for name in (
        "7481-WORD.json.gz", "7481-APPLICATION.json", "7113-CALLER.json", "pricing.py", "gate.py"
    )}
    for relative, digest in inputs.items():
        assert sha256((root / relative).read_bytes()).hexdigest() == digest, relative
    lead = HERE / "receipts/PRIMARY.json"
    forward = replay("lead/check_fusion.py", cwd=root)
    assert forward == lead.read_bytes()
    reverse = replay("independent/check_owned1521_forward.py", root, lead, sha256(forward).hexdigest())
    result = loads(reverse, object_pairs_hook=unique)
    assert 0 <= result.pop("seconds") < 30
    assert result == loads((HERE / "receipts/INDEPENDENT.json").read_bytes(), object_pairs_hook=unique)
    assert result["status"] == "PASS_INDEPENDENT_OWNED1521_FIXED_BANK_SEPARATOR"
    assert result["old402"] == result["target_u"] == "1" and result["edited402"] == "0"
    assert all(v == "0" for v in result["edited_bank"].values())
    print("PASS_R286_OWNED1521_FIXED_BANK_HANDOFF: exact six-row collision and first read divergence")


if __name__ == "__main__":
    main()
