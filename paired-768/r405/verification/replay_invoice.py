"""Reproduce the independently constructed invoice and all runtime image hashes."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import runpy
from subprocess import check_output
import sys
from tempfile import TemporaryDirectory

CANDIDATE = "d502eb21637717fe22fc16d4c4e3ede6ec59a106"
COMPARATOR = "cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e"
HERE = Path(__file__).resolve().parent


def exact_checkout(checkout, head):
    def git(*args):
        return check_output(["git", "-C", checkout, *args])

    if git("rev-parse", "HEAD").decode().strip() != head or git("status", "--porcelain"):
        raise ValueError(f"Expected clean checkout at {head}")


def run_and_match(script, receipt, *args):
    actual = check_output([sys.executable, "-IB", HERE / script, *args])
    if actual != (HERE / receipt).read_bytes():
        raise ValueError(f"Independent reconstruction differs at {receipt}")
    print(f"PASS {receipt} {sha256(actual).hexdigest()}", flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("comparator", type=Path)
    parser.add_argument("handoff_root", type=Path)
    args = parser.parse_args()
    candidate, comparator = args.candidate.resolve(), args.comparator.resolve()
    exact_checkout(candidate, CANDIDATE)
    exact_checkout(comparator, COMPARATOR)
    new = candidate / "research/p104-weighted-child-tariff"
    old = comparator / "research/p104-weighted-k7-suffix"
    receipts = args.handoff_root.resolve() / "paired-768"
    with TemporaryDirectory(prefix="child-tariff-invoice-") as temporary:
        tree = Path(temporary)
        peer = tree / "peer"
        runpy.run_path(str(new/"verify.py"))["restore"](peer)
        images = tree / "images"
        run_and_match("operator_images.py", "operator-images.json",
                      "--peer", peer, "--old", old, "--new", new, "--output", images)
        run_and_match("independent_invoice.py", "independent-invoice.json",
                      "--runtime", images/"candidate-image/runtime",
                      "--signed-source", peer/"research/tiered-native-multiplier/source",
                      "--primitives", receipts/"r403/verification/independent_invoice.py",
                      "--comparator", receipts/"r404/verification/REPLAY-RECEIPT.json",
                      "--result", new/"RESULT.json")
        run_and_match("receiver_contract.py", "receiver-contract.json",
                      "--runtime", images/"candidate-image/runtime",
                      "--runtime-inventory", HERE/"operator-images.json")


if __name__ == "__main__":
    main()
