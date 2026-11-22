"""Replay the literal K7 floor against two exact Git checkouts."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

RELEASE = "04228ea5a1292cf8526a20037060f6fc6e15a858"
PREDECESSOR = "19e67d1b36210e3047bbf3d04625d1262cba672a"
SEALED = "79042dce46983afdcf6891d410cfb72bcbc897229c7d05d22c67cfe7b61459fb"
ONBOARDING = "round394/onboarding.log"
COMPLETE = "round395/price/COMPLETE.json"


def pinned(path, claim):
    data = path.read_bytes()
    if sha256(data).hexdigest() != claim:
        raise ValueError(f"Unexpected digest for {path.name}")
    return data


def head(path, claim):
    actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if actual != claim:
        raise ValueError(f"Expected Git HEAD {claim}, found {actual}")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--comparator", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate.resolve(strict=True)
    comparator = args.comparator.resolve(strict=True)
    head(candidate, RELEASE)
    head(comparator, PREDECESSOR)
    source = Path(__file__).resolve().parent
    changes = json.loads((source / "PATH-REDACTIONS.json").read_bytes())
    if set(changes) != {"build.log", ONBOARDING, COMPLETE}:
        raise ValueError("Unexpected traceback redaction keys")
    build, on, complete = (changes[key] for key in ("build.log", ONBOARDING, COMPLETE))
    expected = json.loads(pinned(source / "verified.json", SEALED))
    original_complete = json.loads(pinned(source / "COMPLETE-sealed.json", complete["sealed"]))
    public_complete = json.loads(pinned(source / "evidence" / COMPLETE, complete["public"]))
    if (original_complete.get(ONBOARDING) != on["sealed"]
            or public_complete.get(ONBOARDING) != on["public"]
            or original_complete | {ONBOARDING: on["public"]} != public_complete):
        raise ValueError("Unexpected completed-log map change")
    pinned(source / "evidence" / ONBOARDING, on["public"])
    pinned(source / "build.log", build["public"])
    frozen = json.loads((source / "INPUTS.json").read_bytes())
    checker = (source / "accept.py").read_text()
    if (expected["sealed_prior"][COMPLETE] != complete["sealed"]
            or expected["sealed_prior"][ONBOARDING] != on["sealed"]
            or expected["literal_pins"]["build.log"] != build["sealed"]
            or frozen["build.log"] != build["sealed"] or checker.count(complete["sealed"]) != 1):
        raise ValueError("Unexpected original evidence digest")
    expected["sealed_prior"][COMPLETE] = complete["public"]
    expected["sealed_prior"][ONBOARDING] = on["public"]
    expected["literal_pins"]["build.log"] = frozen["build.log"] = build["public"]
    with TemporaryDirectory(prefix="ordinary-floor-literal-replay-") as directory:
        scratch = Path(directory)
        evidence = scratch / "evidence"
        copytree(source / "evidence", evidence)
        (evidence / "round394/publish").symlink_to(comparator, target_is_directory=True)
        check = scratch / "check.py"
        check.write_text(checker.replace(complete["sealed"], complete["public"]))
        frozen_path = scratch / "INPUTS.json"
        frozen_path.write_text(json.dumps(frozen))
        receipt = scratch / "receipt.json"
        subprocess.run(
            [sys.executable, "-IB", str(check), "--inputs", str(evidence),
             "--capsule", str(candidate / "research/p104-weighted-ordinary-floor"),
             "--sources", str(source / "sources"), "--log", str(source / "build.log"),
             "--frozen", str(frozen_path), "--out", str(receipt)], check=True,
        )
        actual = receipt.read_bytes()
        if actual != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
            raise ValueError("Receipt changed beyond the declared traceback path hashes")
        args.out.write_bytes(actual)


if __name__ == "__main__":
    main()
