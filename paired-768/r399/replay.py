"""Reproduce both exact allocation receipts from a clean comparator checkout."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

SEALED = {
    "price/COMPLETE.json": "bf6595b97520131dabf71959f0a78c9fd0d471ca5167afe97d71ce8f925fa9dc",
    "price/receipt.json": "7a7492dc29fbacd3503ffe85730e7f768911e29533f7a546452fa9ecab66d42e",
    "price/check.py": "a3b7980163367be1a3033541c2cc4882e375b92ce80906a68f9f4513eeba5448",
    "audit/receipt.json": "12417796f9867fb1c1ae373ee8960b14931abebc18a16959e135dd7db3f62bfe",
    "audit/check.py": "a838c81ca86dfe8b6e3a2519437aafdaa85f16c3f253732f0d98cc3ee597244f",
}
REDACTED = "evidence/onboarding.log"


def digest(data):
    return sha256(data).hexdigest()


def exact(actual, expected, scope):
    if actual != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
        raise ValueError(f"{scope} changed beyond the declared traceback digests")


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--comparator", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    comparator = a.comparator.resolve(strict=True)
    root = Path(__file__).resolve().parent
    for name, claim in SEALED.items():
        if digest((root / name).read_bytes()) != claim:
            raise ValueError(f"Unexpected sealed bytes at {name}")
    old = json.loads((root / "price/COMPLETE.json").read_bytes())
    public = root / "price/COMPLETE-public.json"
    redacted_log = root / "evidence/round398/onboarding.log"
    changed_digest = digest(redacted_log.read_bytes())
    if old["sha256_by_path"][REDACTED] == changed_digest:
        raise ValueError("Expected the declared onboarding path redaction")
    old["sha256_by_path"][REDACTED] = changed_digest
    exact(public.read_bytes(), old, "Completion manifest")
    a.out.mkdir(parents=True, exist_ok=True)
    price_out = a.out / "price.json"
    audit_out = a.out / "audit.json"
    with TemporaryDirectory(prefix="matched-clock-bound-") as temp:
        evidence = Path(temp) / "evidence"
        copytree(root / "evidence", evidence)
        base = evidence / "round398"
        (base / "publish").symlink_to(comparator, target_is_directory=True)
        primary_script = root / "price/check.py"
        subprocess.run(
            [sys.executable, "-IB", str(primary_script), "--comparator", str(comparator),
             "--evidence", str(base), "--workspace", str(evidence), "--complete", str(public),
             "--out", str(price_out)], check=True,
        )
        first = json.loads((root / "price/receipt.json").read_bytes())
        first["pinned_inputs_by_path"][REDACTED] = changed_digest
        actual_price = price_out.read_bytes()
        exact(actual_price, first, "Primary receipt")
        public_price, public_complete = digest(actual_price), digest(public.read_bytes())
        subprocess.run(
            [sys.executable, "-IB", str(root / "audit/check.py"), "--inputs", str(evidence),
             "--primary", str(price_out), "--primary-sha256", public_price,
             "--primary-script", str(primary_script), "--primary-script-sha256", SEALED["price/check.py"],
             "--complete", str(public), "--complete-sha256", public_complete, "--out", str(audit_out)],
             check=True,
        )
        second = json.loads((root / "audit/receipt.json").read_bytes())
        second["pinned_exact_source_and_log_paths"][REDACTED] = changed_digest
        second["primary_receipt_sha256"] = public_price
        second["completed_manifest_sha256"] = public_complete
        exact(audit_out.read_bytes(), second, "Independent receipt")


if __name__ == "__main__":
    main()
