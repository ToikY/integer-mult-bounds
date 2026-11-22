"""Recreate the independent R390 receipt with the public traceback paths."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

RELEASE = "e4fccb224ce5d9bc530a8027d4f617a6a37d4562"
COMPARATOR = "682fd9512ccbf3035089d7e5f9cb4dedf9f746b4"
SEALED_RECEIPT = "d3725f1e0133c3111322ad9ef4f6381aa3d1c7d7173eecc6129874ce30e43980"


def check_head(root, expected):
    actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if actual != expected:
        raise ValueError(f"Expected Git HEAD {expected}, found {actual}")


def check_digest(path, expected):
    if sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Unexpected digest for {path.name}")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--comparator", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    candidate = args.candidate.resolve(strict=True)
    comparator = args.comparator.resolve(strict=True)
    check_head(candidate, RELEASE)
    check_head(comparator, COMPARATOR)
    lower_onboarding = "round388/onboarding.log"
    redactions = json.loads((source / "PATH-REDACTIONS.json").read_text())
    if set(redactions) != {"build.log", lower_onboarding}:
        raise ValueError("Unexpected traceback redaction keys")
    build = redactions["build.log"]
    onboarding = redactions[lower_onboarding]
    check_digest(source / "build.log", build["public"])
    check_digest(source / "evidence" / lower_onboarding, onboarding["public"])
    check_digest(source / "verified.json", SEALED_RECEIPT)
    expected = json.loads((source / "verified.json").read_bytes())
    frozen = json.loads((source / "INPUTS.json").read_bytes())
    original = (source / "accept.py").read_text()
    if (frozen["build.log"] != build["sealed"]
            or expected["candidate_and_gate_pins"]["build.log"] != build["sealed"]
            or expected["pinned_inputs"][lower_onboarding] != onboarding["sealed"]
            or original.count(onboarding["sealed"]) != 1):
        raise ValueError("Unexpected sealed traceback digests")
    frozen["build.log"] = build["public"]
    expected["candidate_and_gate_pins"]["build.log"] = build["public"]
    expected["pinned_inputs"][lower_onboarding] = onboarding["public"]
    with TemporaryDirectory(prefix="weighted-upper-band-accept-") as temp:
        scratch = Path(temp)
        evidence = scratch / "evidence"
        copytree(source / "evidence", evidence)
        (evidence / "round388" / "publish").symlink_to(comparator, target_is_directory=True)
        checker = scratch / "accept.py"
        checker.write_text(original.replace(onboarding["sealed"], onboarding["public"]))
        frozen_path = scratch / "INPUTS.json"
        frozen_path.write_text(json.dumps(frozen))
        result = scratch / "receipt.json"
        subprocess.run(
            [sys.executable, "-IB", str(checker), "--inputs", str(evidence),
             "--capsule", str(candidate / "research/p104-weighted-upper-band"),
             "--build-log", str(source / "build.log"), "--frozen", str(frozen_path),
             "--out", str(result)],
            check=True,
        )
        actual = result.read_bytes()
        if actual != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
            raise ValueError("Receipt changed beyond the two declared traceback digests")
        args.out.write_bytes(actual)


if __name__ == "__main__":
    main()
