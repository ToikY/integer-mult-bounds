"""Reproduce both exact bounded Type B stage-7 paired seam checks."""
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


def replay(script, *args):
    result = run([executable, "-I", "-B", str(HERE / script), *map(str, args)],
                 capture_output=True, timeout=32, check=True)
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
        "7481-WORD.json.gz", "7481-APPLICATION.json", "7113-CALLER.json", "pricing.py"
    )}
    for relative, digest in inputs.items():
        assert sha256((root / relative).read_bytes()).hexdigest() == digest, relative
    lead = HERE / "receipts/PRIMARY.jsonl"
    forward = replay("next-stage7-pair/check_stage7_bilateral.py", root / "inputs")
    assert forward == lead.read_bytes()
    reverse = replay("independent/check_stage7_pair_independent.py", root, lead, sha256(forward).hexdigest())
    result = loads(reverse, object_pairs_hook=unique)
    assert 0 <= result.pop("seconds") < 30
    assert result == loads((HERE / "receipts/INDEPENDENT.json").read_bytes(), object_pairs_hook=unique)
    assert result["status"] == "PASS_INDEPENDENT_FIXED_BILATERAL_EXCLUSION" and result["unresolved"] == []
    assert result["survivor_parities"] == [] and result["old_endpoint_rows_and_columns_both_sectors"]
    assert all(v["forbidden_rank"] == 2 and v["forbidden_rows"] == 16
               for p in result["classes"].values() for v in p["sectors"].values())
    print("PASS_R284_TYPE_B_STAGE7_PAIR_HANDOFF: two parity classes, four full-rank ingress gates")


if __name__ == "__main__":
    main()
