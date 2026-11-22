"""Replay the one-case ordinary debit with exact #8065 inputs."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

HEAD = "ffa64503646a62a7ac3cd2c47787d670da911f89"
SEALED_PRICE = "07645666c11fa427e8b039fec0eebf2e6b9858d1d43919ff117cad48292a891d"
SEALED_LOGS = "6989eb5749cde5e3343f81aaa4a98792af2fe852b37b9981e60ce36aa866ed48"
ONBOARDING = "round392/onboarding.log"


def main():
    source = Path(__file__).resolve().parent
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--comparator", required=True, type=Path)
    parser.add_argument("--evidence-root", type=Path, default=source.parent)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    prior = args.evidence_root.resolve(strict=True)
    comparator = args.comparator.resolve(strict=True)
    head = subprocess.check_output(["git", "-C", str(comparator), "rev-parse", "HEAD"],
                                   text=True).strip()
    if head != HEAD:
        raise ValueError(f"Expected Git HEAD {HEAD}, found {head}")
    price = source / "price"
    sealed = (price / "receipt.json").read_bytes()
    sealed_logs = (price / "COMPLETE.json").read_bytes()
    if sha256(sealed).hexdigest() != SEALED_PRICE or sha256(sealed_logs).hexdigest() != SEALED_LOGS:
        raise ValueError("Unexpected sealed price or completed-log digest")
    expected = json.loads(sealed)
    original = json.loads(sealed_logs)
    complete = price / "COMPLETE-public.json"
    public = json.loads(complete.read_bytes())
    if (public.keys() != original.keys()
            or {name for name in public if public[name] != original[name]} != {ONBOARDING}
            or expected["pinned_inputs_by_path"][ONBOARDING] != original[ONBOARDING]):
        raise ValueError("Unexpected traceback replacement key")
    expected["pinned_inputs_by_path"][ONBOARDING] = public[ONBOARDING]
    with TemporaryDirectory(prefix="ordinary-debit-price-") as directory:
        scratch = Path(directory)
        evidence = scratch / "evidence"
        base = evidence / "round392"
        base.mkdir(parents=True)
        (base / "publish").symlink_to(comparator, target_is_directory=True)
        (base / "exact-head").write_text(head + "\n")
        for name in ("preflight.log", *(Path(p).name for p in public)):
            copyfile(prior / "r392" / name, base / name)
        dependencies = {
            "round392/independent/verified.json": "r392/verified.json",
            "round378/independent/accept.py": "r390/evidence/round378/independent/accept.py",
            "round375/independent/coupling.py": "r390/evidence/round375/independent/coupling.py",
            "round391/price/check.py": "r391/price/check.py",
        }
        for destination, original_path in dependencies.items():
            target = evidence / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            copyfile(prior / original_path, target)
        receipt = scratch / "price.json"
        subprocess.run(
            [sys.executable, "-IB", str(price / "check.py"), "--inputs", str(evidence),
             "--complete", str(complete), "--out", str(receipt)],
            check=True,
        )
        actual = receipt.read_bytes()
        if actual != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
            raise ValueError("Receipt changed beyond the declared onboarding digest")
        args.out.write_bytes(actual)


if __name__ == "__main__":
    main()
