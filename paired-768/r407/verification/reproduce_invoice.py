"""Rebuild the two pinned installed suppliers and compare the complete exact invoice."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEADS = (
    "aea1699415250d865f7a635f4df0b76f406c47b4",
    "510113821774bb27f7ddaad4e8b94837a1c2cf52",
)


def verify_checkout(root, head):
    def git(*args):
        return subprocess.check_output(["git", "-C", root, *args])
    if git("rev-parse", "HEAD").decode().strip() != head or git("status", "--porcelain"):
        raise ValueError(f"Expected a clean checkout at {head}")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("comparator", type=Path)
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        parser.error("CPython 3.12 is required")
    candidate, comparator = args.candidate.resolve(), args.comparator.resolve()
    for root, head in zip((candidate, comparator), HEADS, strict=True):
        verify_checkout(root, head)
    with TemporaryDirectory(prefix="period-25bit-") as scratch:
        output = Path(scratch)/"images"
        subprocess.run([sys.executable, "-IB", HERE/"materialize_trees.py",
                        candidate, comparator, output], check=True,
                       stdout=subprocess.DEVNULL)
        result = subprocess.check_output([
            sys.executable, "-IB", HERE/"independent_check.py",
            candidate, comparator, output, HERE/"CANDIDATE-INPUTS.json",
            HERE/"peer-evidence"/"REPLAY-RECEIPT.json",
        ])
    if result != (HERE/"independent-invoice.json").read_bytes():
        raise ValueError("The reconstructed exact invoice differs from the saved receipt")
    print(f"PASS_INDEPENDENT_25BIT_INVOICE {sha256(result).hexdigest()}")


if __name__ == "__main__":
    main()
