"""Verify the independent price and operator receipts using two exact clean checkouts."""

from hashlib import sha256
from pathlib import Path
import runpy
from shutil import copyfile
from subprocess import check_output, run
import sys
from tempfile import TemporaryDirectory

CANDIDATE = "cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e"
COMPARATOR = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
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
    package = candidate / "research/p104-weighted-k7-suffix"
    with TemporaryDirectory(prefix="round404-invoice-") as temp:
        root = Path(temp)
        work = root / "round404/independent"
        prior = root / "round403/independent"
        work.mkdir(parents=True)
        prior.mkdir(parents=True)
        (work / "checkout").symlink_to(candidate, target_is_directory=True)
        (prior / "checkout").symlink_to(comparator, target_is_directory=True)
        replay = HERE.parent.parent / "r403" / "verification"
        for name, digest in {
            "independent_invoice.py": "7b06abca74493ca369601c426574e60ef15f5a5c8c76b4cfea2a8387fe32557c",
            "REPLAY-RECEIPT.json": "1cb65536235c27fd2e5673de49a3d8a0c320358cf90dea3e7c491795d46a6025",
        }.items():
            source = replay / name
            if sha256(source.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Round 403 dependency changed at {name}")
            copyfile(source, prior / name)
        peer = work / "peer-source"
        runpy.run_path(str(package / "verify.py"))["restore"](peer)
        bootstrap = peer / "research/tiered-native-multiplier/bootstrap.py"
        run([sys.executable, "-IB", bootstrap, work / "original-runtime"], check=True)
        checks = (("independent_k7.py", "invoice.json"),
                  ("operator_images.py", "operator-images.json"))
        for script, receipt in checks:
            actual = check_output([sys.executable, "-IB", HERE / script], cwd=work)
            if actual != (HERE / receipt).read_bytes():
                raise ValueError(f"Independent result differs at {receipt}")
            print(f"PASS {receipt}", flush=True)


if __name__ == "__main__":
    main()
