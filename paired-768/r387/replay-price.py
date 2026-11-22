"""Replay the price arithmetic from explicit pinned checkouts."""

from argparse import ArgumentParser
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import subprocess
import sys

ORIGINAL_ONBOARDING_HASH = "1186b2519df0e112a0a76b022140a080f3555bede9f247f33d863baeed43e287"
PUBLIC_ONBOARDING_HASH = "c30499282df76c447c1f601ccf71b531e88e983cff45d42b79aa5e0c128c6463"


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
    with TemporaryDirectory(prefix="weighted-cutoff-price-") as temp:
        evidence = Path(temp) / "evidence"
        copytree(source / "evidence", evidence)
        (evidence / "round385" / "publish").symlink_to(comparator, target_is_directory=True)
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
