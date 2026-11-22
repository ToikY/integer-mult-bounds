"""Replay the installed eight-level transfer with exact checkout roots."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

HEAD = "ffa64503646a62a7ac3cd2c47787d670da911f89"
OLD_HEAD = "e4fccb224ce5d9bc530a8027d4f617a6a37d4562"
RECEIPT = "dcf57d8bab8cfc76769b0f9d8b570d233e670032b8ab2aed481172ff21c3c2a9"
ONBOARDING = "round390/onboarding.log"
EVIDENCE = (
    "preflight.log", "scientific.log", "scientific.exit", "onboarding.log",
    "onboarding.exit", "historical.log", "historical.exit",
)
PREFLIGHT = ("price/check.py", "price/receipt.json", "audit/check_stage_transfer.py", "audit/receipt.json")


def git_head(root, expected):
    actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if actual != expected:
        raise ValueError(f"Expected Git HEAD {expected}, found {actual}")
    return actual


def main():
    source = Path(__file__).resolve().parent
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--comparator", required=True, type=Path)
    parser.add_argument("--round390-evidence", type=Path, default=source.parent / "r390")
    parser.add_argument("--round391-evidence", type=Path, default=source.parent / "r391")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    candidate = args.candidate.resolve(strict=True)
    comparator = args.comparator.resolve(strict=True)
    prior = args.round390_evidence.resolve(strict=True)
    preflight = args.round391_evidence.resolve(strict=True)
    git_head(candidate, HEAD)
    old_head = git_head(comparator, OLD_HEAD)
    raw = (source / "verified.json").read_bytes()
    if sha256(raw).hexdigest() != RECEIPT:
        raise ValueError("Unexpected sealed receipt digest")
    expected = json.loads(raw)
    changes = json.loads((source / "PATH-REDACTION.json").read_bytes())
    if set(changes) != {ONBOARDING}:
        raise ValueError("Unexpected traceback replacement key")
    digest = changes[ONBOARDING]
    original = (source / "accept.py").read_text()
    if (original.count(digest["sealed"]) != 1
            or expected["pinned_evidence"][ONBOARDING] != digest["sealed"]
            or sha256((prior / "onboarding.log").read_bytes()).hexdigest() != digest["public"]):
        raise ValueError("Unexpected onboarding traceback digest")
    expected["pinned_evidence"][ONBOARDING] = digest["public"]
    with TemporaryDirectory(prefix="ordinary-transfer-accept-") as directory:
        scratch = Path(directory)
        evidence = scratch / "evidence"
        previous = evidence / "round390"
        previous.mkdir(parents=True)
        for name in EVIDENCE:
            copyfile(prior / name, previous / name)
        (previous / "exact-head").write_text(old_head + "\n")
        (previous / "publish").symlink_to(comparator, target_is_directory=True)
        (previous / "independent").mkdir()
        copyfile(prior / "verified.json", previous / "independent/verified.json")
        supplier = "round378/independent/accept.py"
        (evidence / supplier).parent.mkdir(parents=True)
        copyfile(prior / "evidence" / supplier, evidence / supplier)
        for name in PREFLIGHT:
            relative = evidence / "round391" / name
            relative.parent.mkdir(parents=True, exist_ok=True)
            copyfile(preflight / name, relative)
        checker = scratch / "accept.py"
        checker.write_text(original.replace(digest["sealed"], digest["public"]))
        receipt = scratch / "receipt.json"
        subprocess.run(
            [sys.executable, "-IB", str(checker), "--inputs", str(evidence),
             "--capsule", str(candidate / "research/p104-weighted-ordinary-transfer"),
             "--log", str(source / "build.log"), "--frozen", str(source / "INPUTS.json"),
             "--out", str(receipt)],
            check=True,
        )
        actual = receipt.read_bytes()
        if actual != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
            raise ValueError("Receipt changed beyond the declared onboarding digest")
        args.out.write_bytes(actual)


if __name__ == "__main__":
    main()
