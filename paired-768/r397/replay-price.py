"""Recheck the one matched-clock price using an exact pinned checkout."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

HEAD = "04228ea5a1292cf8526a20037060f6fc6e15a858"
SEALED = "285ccefc35ff461365557b41a5ceb123da1a0fc9e7991a06bf6294ff1dd31deb"
LOGS = "08c7d2499f25797f1a831cfee0028f003591c6cfe6d125b251b8e53e5c316158"
ONBOARDING = "round396/onboarding.log"


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--comparator", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    comparator = args.comparator.resolve(strict=True)
    actual = subprocess.check_output(["git", "-C", str(comparator), "rev-parse", "HEAD"],
                                     text=True).strip()
    if actual != HEAD:
        raise ValueError(f"Expected Git HEAD {HEAD}, found {actual}")
    root = Path(__file__).resolve().parent
    price = root / "price"
    old = (price / "receipt.json").read_bytes()
    logs = (price / "COMPLETE.json").read_bytes()
    if sha256(old).hexdigest() != SEALED or sha256(logs).hexdigest() != LOGS:
        raise ValueError("Unexpected sealed receipt or complete log digest")
    expected = json.loads(old)
    original = json.loads(logs)
    complete = price / "COMPLETE-public.json"
    public = json.loads(complete.read_bytes())
    if (original.keys() != public.keys()
            or {key for key in original if original[key] != public[key]} != {ONBOARDING}
            or expected["exact_path_pins"][ONBOARDING] != original[ONBOARDING]):
        raise ValueError("Unexpected evidence digest change")
    expected["exact_path_pins"][ONBOARDING] = public[ONBOARDING]
    with TemporaryDirectory(prefix="matched-clock-price-") as directory:
        scratch = Path(directory)
        evidence = scratch / "evidence"
        copytree(root / "evidence", evidence)
        (evidence / "round396/publish").symlink_to(comparator, target_is_directory=True)
        result = scratch / "receipt.json"
        subprocess.run([sys.executable, "-IB", str(price / "check.py"), "--inputs", str(evidence),
                        "--complete", str(complete), "--out", str(result)], check=True)
        actual = result.read_bytes()
        if actual != (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode():
            raise ValueError("Price receipt changed beyond the onboarding traceback digest")
        args.out.write_bytes(actual)


if __name__ == "__main__":
    main()
