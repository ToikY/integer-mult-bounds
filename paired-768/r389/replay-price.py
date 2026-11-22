"""Replay the price arithmetic from explicit pinned checkouts."""

from argparse import ArgumentParser
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import subprocess
import sys

ORIGINAL_ONBOARDING_HASH = "128f901401ccbdeb1428d7cae5ffe055f044479e745d57767cce11daa9d6e654"
PUBLIC_ONBOARDING_HASH = "2a4b97cb7bf31e65932c9acacb2a5f1b3c55254916ff6704f1313ba85b29e2af"


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--peer", type=Path, required=True)
    parser.add_argument("--comparator", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    comparator = args.comparator.resolve(strict=True)
    peer = args.peer.resolve(strict=True)
    out = args.out.resolve()
    with TemporaryDirectory(prefix="weighted-upper-band-price-") as temp:
        evidence = Path(temp) / "evidence"
        copytree(source / "evidence", evidence)
        (evidence / "round388" / "publish").symlink_to(comparator, target_is_directory=True)
        checker = Path(temp) / "price.py"
        original = (source / "price" / "price.py").read_text()
        if original.count(ORIGINAL_ONBOARDING_HASH) != 1:
            raise ValueError("Expected one historical onboarding digest")
        checker.write_text(original.replace(ORIGINAL_ONBOARDING_HASH, PUBLIC_ONBOARDING_HASH))
        subprocess.run(
            [sys.executable, "-IB", str(checker),
             "--root", str(evidence), "--peer", str(peer), "--out", str(out)],
            check=True,
        )


if __name__ == "__main__":
    main()
