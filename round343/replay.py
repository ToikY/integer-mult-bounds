"""Replay the sealed one-case proof with an explicit scientific checkout."""
import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

here = Path(__file__).resolve().parent
cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--scientific-root", required=True, type=Path)
cli.add_argument("--out", required=True, type=Path)
args = cli.parse_args()
pkg = args.scientific_root.resolve() / "research/bit-451-carrier-cover"
if sys.version_info[:2] != (3,12) or args.out.exists():
    cli.error("use CPython 3.12 and a new output path")
with TemporaryDirectory() as tmp:
    work = Path(tmp)
    archive = pkg / "source7863.tar.gz"
    if sha256(archive.read_bytes()).hexdigest() != "5f9d9c378a1bddccb2e42ac6453716fa950f19bd71f6181a9606f5eb68b022b3":
        raise ValueError("signed supplier archive")
    target = work / "round321/benchmark/producer/BIT-451.json"
    target.parent.mkdir(parents=True)
    with tarfile.open(archive) as bundle:
        target.write_bytes(bundle.extractfile("package-sanitized/BIT-451.json").read())
    inputs = {
        "round336/independent/receipt.json": pkg / "grid/RESULT.json",
        "round339/independent/receipt.json": pkg / "tensor/MEAN.json",
        "round341/independent/receipt-with-minimum.json": pkg / "tensor/SIBLING.json",
        "round342/screen.py": here.parent / "round342/screen.py",
        "round342/primary.json": here.parent / "round342/primary.json",
        "round342/independent/receipt.json": here.parent / "round342/independent/receipt.json",
        "round342/independent/outer-verified.json": here.parent / "round342/independent/outer-verified.json",
    }
    for relative, source in inputs.items():
        path = work / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source.read_bytes())
    subprocess.run([sys.executable, "-IB", here / "run.py", "--campaign-root", work,
                    "--out", args.out.resolve()], check=True)
