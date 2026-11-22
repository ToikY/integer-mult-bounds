"""Verify the final signed allocation with exact explicit Git roots."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

RELEASE = "2d0d7d378929269b00dcabfac1099b2bb23b3b3b"
PREDECESSOR = "8c800e1b6458526e1ce7a59150bba8a0d29d0027"
SEALED = "994d4bdd7c159b4f55a5a6d69a784ac4d7414ac4aa5e1056e3eea0cf5b2cdc67"
CHECKER = "dcfe74f706c67762ed3a7ad9f2a1a4b84ca43962d452029eb34f66fa8f63d2bb"
LOG = "round398/onboarding.log"
LOG_KEY = "evidence/onboarding.log"
COMPLETE = "round399/price/COMPLETE.json"
PRICE = "round399/price/receipt.json"
AUDIT = "round399/audit/receipt.json"


def pinned(path, claim):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != claim:
        raise ValueError(f"Unexpected digest at {path.name}")
    return raw


def check_head(path, claim):
    head = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if head != claim:
        raise ValueError(f"Expected Git HEAD {claim}, found {head}")


def exact(raw, expected):
    if raw != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
        raise ValueError("Unexpected difference beyond the declared traceback hashes")


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--comparator", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    candidate = a.candidate.resolve(strict=True)
    comparator = a.comparator.resolve(strict=True)
    check_head(candidate, RELEASE)
    check_head(comparator, PREDECESSOR)
    source = Path(__file__).resolve().parent
    expected = json.loads(pinned(source / "verified.json", SEALED))
    checker = pinned(source / "accept.py", CHECKER).decode()
    changes = json.loads((source / "PATH-REDACTIONS.json").read_bytes())
    if set(changes) != {LOG, COMPLETE, PRICE, AUDIT}:
        raise ValueError("Unexpected redaction path keys")
    for key, row in changes.items():
        if expected["pinned_predecessor_and_previous_checks"][key] != row["sealed"]:
            raise ValueError("Unexpected sealed evidence digest")
        expected["pinned_predecessor_and_previous_checks"][key] = row["public"]
        pinned(source / "evidence" / key, row["public"])
    sealed = {key: json.loads(pinned(source / "sealed" / key, changes[key]["sealed"]))
              for key in (COMPLETE, PRICE, AUDIT)}
    for key, field in ((COMPLETE, "sha256_by_path"), (PRICE, "pinned_inputs_by_path"),
                       (AUDIT, "pinned_exact_source_and_log_paths")):
        if sealed[key][field][LOG_KEY] != changes[LOG]["sealed"]:
            raise ValueError("Unexpected original onboarding traceback pin")
        sealed[key][field][LOG_KEY] = changes[LOG]["public"]
    if (sealed[AUDIT]["primary_receipt_sha256"] != changes[PRICE]["sealed"]
            or sealed[AUDIT]["completed_manifest_sha256"] != changes[COMPLETE]["sealed"]):
        raise ValueError("Unexpected original independent receipt provenance")
    sealed[AUDIT]["primary_receipt_sha256"] = changes[PRICE]["public"]
    sealed[AUDIT]["completed_manifest_sha256"] = changes[COMPLETE]["public"]
    for key in sealed:
        exact((source / "evidence" / key).read_bytes(), sealed[key])
        row = changes[key]
        if checker.count(row["sealed"]) != 1:
            raise ValueError("Expected one exact digest substitution in the checker")
        checker = checker.replace(row["sealed"], row["public"])
    with TemporaryDirectory(prefix="optimal-signed-allocation-") as temp:
        scratch = Path(temp)
        inputs = scratch / "evidence"
        copytree(source / "evidence", inputs)
        (inputs / "round398/publish").symlink_to(comparator, target_is_directory=True)
        check = scratch / "accept.py"
        check.write_text(checker)
        out = scratch / "receipt.json"
        subprocess.run(
            [sys.executable, "-IB", str(check), "--inputs", str(inputs),
             "--capsule", str(candidate / "research/p104-weighted-optimal-allocation"),
             "--log", str(source / "build.log"), "--frozen", str(source / "INPUTS.json"),
             "--out", str(out)], check=True,
        )
        raw = out.read_bytes()
        exact(raw, expected)
        a.out.write_bytes(raw)


if __name__ == "__main__":
    main()
