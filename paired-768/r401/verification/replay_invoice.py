"""Reproduce the independent Round 401 invoice from the frozen clean checkout."""

from pathlib import Path
import runpy
from shutil import copyfile
from subprocess import check_output, run
import sys
from tempfile import TemporaryDirectory

HEAD = "7d65b2c6a19941b9922d5e4c86c495aa37073141"
HERE = Path(__file__).resolve().parent


def main():
    checkout = Path(sys.argv[1]).resolve()
    actual = check_output(["git", "-C", checkout, "rev-parse", "HEAD"], text=True).strip()
    if actual != HEAD:
        raise ValueError(f"Expected {HEAD}, got {actual}")
    package = checkout / "research/p104-weighted-gaussian-debit"
    with TemporaryDirectory(prefix="round401-invoice-") as temporary:
        root = Path(temporary)
        peer = root / "peer-source"
        runpy.run_path(str(package / "verify.py"))["restore"](peer)
        tiered = peer / "research/tiered-native-multiplier"
        run([sys.executable, "-IB", tiered / "bootstrap.py", root / "archived-runtime"], check=True)
        for name in ("reconstruct.py", "charges.py"):
            copyfile(HERE / name, root / name)
        for script, expected in (("reconstruct.py", "reconstruction.json"), ("charges.py", "charges.json")):
            data = check_output([sys.executable, "-IB", script], cwd=root)
            if data != (HERE / expected).read_bytes():
                raise ValueError(f"Independent receipt differs at {expected}")
            (root / expected).write_bytes(data)
            print(f"PASS {expected}", flush=True)


if __name__ == "__main__":
    main()
