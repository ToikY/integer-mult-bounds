"""Verify the independent price and operator receipts using two exact clean checkouts."""

from pathlib import Path
import runpy
from subprocess import check_output, run
import sys
from tempfile import TemporaryDirectory

CANDIDATE = "9555f2df027f4a182722f736c97e5efafa5382c6"
COMPARATOR = "7d65b2c6a19941b9922d5e4c86c495aa37073141"
HERE = Path(__file__).resolve().parent


def exact_checkout(checkout, revision):
    def git(*args):
        return check_output(["git", "-C", checkout, *args], text=True)
    if git("rev-parse", "HEAD").strip() != revision or git("status", "--porcelain"):
        raise ValueError(f"Expected clean checkout at {revision}")


def main():
    candidate, comparator = [Path(value).resolve() for value in sys.argv[1:]]
    exact_checkout(candidate, CANDIDATE)
    exact_checkout(comparator, COMPARATOR)
    package = candidate / "research/p104-weighted-ordinary-debit-11239"
    with TemporaryDirectory(prefix="round402-invoice-") as temp:
        root = Path(temp)
        work = root / "round402/independent"
        prior = root / "round401/independent"
        work.mkdir(parents=True)
        prior.mkdir(parents=True)
        (work / "checkout").symlink_to(candidate, target_is_directory=True)
        (prior / "checkout").symlink_to(comparator, target_is_directory=True)
        peer = work / "peer-source"
        runpy.run_path(str(package / "verify.py"))["restore"](peer)
        bootstrap = peer / "research/tiered-native-multiplier/bootstrap.py"
        run([sys.executable, "-IB", bootstrap, work / "original-runtime"], check=True)
        checks = (("independent_invoice.py", "invoice.json"),
                  ("operator_images.py", "operator-images.json"))
        for script, receipt in checks:
            actual = check_output([sys.executable, "-IB", HERE / script], cwd=work)
            if actual != (HERE / receipt).read_bytes():
                raise ValueError(f"Independent result differs at {receipt}")
            print(f"PASS {receipt}", flush=True)


if __name__ == "__main__":
    main()
