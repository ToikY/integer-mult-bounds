"""Rebuild the zero-run order and cross-check the eight exact rows."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def pairs(items):
    obj = dict(items)
    assert len(obj) == len(items)
    return obj


def load(raw):
    return json.loads(raw, object_pairs_hook=pairs)


def run(path, *args, timeout):
    return subprocess.check_output([sys.executable, "-I", "-B", str(HERE / path),
                                    *map(str, args)], timeout=timeout)


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12) and len(sys.argv) == 2
    pin_names = set()
    for line in (HERE / "SHA256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        p = HERE / name
        assert name not in pin_names and p.resolve().is_relative_to(HERE)
        assert not p.is_symlink() and sha256(p.read_bytes()).hexdigest() == digest
        pin_names.add(name)
    inputs = Path(sys.argv[1]).resolve() / "inputs"
    with tempfile.TemporaryDirectory(prefix="zero-owned-replay-") as path:
        frozen = Path(path) / "frozen.json"
        primary = run("check_owned_zero_runs.py", inputs, frozen, timeout=32)
        assert primary == (HERE / "expected/RESULT.jsonl").read_bytes()
        frozen_bytes = frozen.read_bytes()
        assert frozen_bytes == (HERE / "expected/FROZEN.json").read_bytes()
        forward = load(run("independent/check_zero_runs_forward.py", inputs, frozen,
                           sha256(frozen_bytes).hexdigest(), timeout=32))
        expected = load((HERE / "expected/FORWARD.json").read_bytes())
        expected.pop("seconds")
        assert 0 <= forward.pop("seconds") < 30 and forward == expected
        logs = list(map(load, primary.splitlines()))
        end = logs[-1]
        assert len(end["cases_completed"]) == 8 and len(end["unresolved"]) == 39
        assert end["survivor"] is None and not forward["zero_pre_first_cases"]
        for a, b in zip(end["cases_completed"], forward["cases"], strict=True):
            assert (a["role"], a["first_move"], a["next_contact"], a["terms"]) == (
                b["role"], b["first_move"], b["next_contact"], b["pre_first_row_support"])
            assert a["nonzero_coefficient"] == [
                b["first_exact_nonzero"]["input"], b["first_exact_nonzero"]["coefficient"]]
            assert b["pre_next_row_unchanged"] and not b["pre_first_zero"]
    print("PASS_OWNED_ZERO_RUN_EIGHT_CASE_EXCLUSION")


if __name__ == "__main__":
    main()
