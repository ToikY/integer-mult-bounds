"""Replay one eight-level transfer using the public R390 evidence."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

HEAD = "e4fccb224ce5d9bc530a8027d4f617a6a37d4562"
SEALED = "19a4795048fb16016801f17c8be6ad9d38715af8a3bd941ae2b44d8c5de43b06"
ONBOARDING = "round390/onboarding.log"
LOG_NAMES = ("preflight.log", "scientific.log", "scientific.exit", "onboarding.log", "onboarding.exit")


def main():
    source = Path(__file__).resolve().parent
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--comparator", type=Path, required=True)
    parser.add_argument("--round390-evidence", type=Path, default=source.parent / "r390")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    comparator = args.comparator.resolve(strict=True)
    prior = args.round390_evidence.resolve(strict=True)
    actual_head = subprocess.check_output(["git", "-C", str(comparator), "rev-parse", "HEAD"],
                                          text=True).strip()
    if actual_head != HEAD:
        raise ValueError(f"Expected Git HEAD {HEAD}, found {actual_head}")
    sealed = (source / "price" / "receipt.json").read_bytes()
    if sha256(sealed).hexdigest() != SEALED:
        raise ValueError("Unexpected sealed price receipt digest")
    expected = json.loads(sealed)
    paths = json.loads((source / "PATH-REDACTION.json").read_bytes())
    if set(paths) != {ONBOARDING}:
        raise ValueError("Unexpected traceback digest key")
    redaction = paths[ONBOARDING]
    original = (source / "price" / "check.py").read_text()
    if (original.count(redaction["sealed"]) != 1
            or expected["inputs_sha256"][ONBOARDING] != redaction["sealed"]
            or sha256((prior / "onboarding.log").read_bytes()).hexdigest() != redaction["public"]):
        raise ValueError("Unexpected onboarding traceback digest")
    expected["inputs_sha256"][ONBOARDING] = redaction["public"]
    with TemporaryDirectory(prefix="ordinary-transfer-price-") as directory:
        root = Path(directory)
        evidence = root / "evidence"
        predecessor = evidence / "round390"
        predecessor.mkdir(parents=True)
        for name in LOG_NAMES:
            copyfile(prior / name, predecessor / name)
        (predecessor / "exact-head").write_text(actual_head + "\n")
        (predecessor / "independent").mkdir()
        copyfile(prior / "verified.json", predecessor / "independent/verified.json")
        old_checker = "round378/independent/accept.py"
        (evidence / old_checker).parent.mkdir(parents=True)
        copyfile(prior / "evidence" / old_checker, evidence / old_checker)
        checker = root / "check.py"
        checker.write_text(original.replace(redaction["sealed"], redaction["public"]))
        receipt = root / "receipt.json"
        subprocess.run([sys.executable, "-IB", str(checker), "--inputs", str(evidence),
                        "--repo", str(comparator), "--out", str(receipt)], check=True)
        actual = receipt.read_bytes()
        if actual != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
            raise ValueError("Price receipt changed beyond the declared traceback digest")
        args.out.write_bytes(actual)


if __name__ == "__main__":
    main()
