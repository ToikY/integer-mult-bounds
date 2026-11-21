"""Reproduce the frozen coefficient exclusion from the authenticated inputs."""
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

root = Path(__file__).resolve().parent
inputs = root / "inputs"
expected = "0239f7f69dea671a66a37e3bcaae61c16d23dc794812d519d1c020821332ad36"
if sys.version_info[:2] != (3, 12) or not __debug__:
    raise SystemExit("Use CPython 3.12 with assertions enabled")
with TemporaryDirectory() as temp:
    output = Path(temp) / "receipt.json"
    subprocess.run(
        [sys.executable, "-IB", str(root / "r349/audit.py"),
         "--application", str(inputs / "APPLICATION.json"),
         "--archive", str(inputs / "APPLICATION-SOURCES.tar.gz"),
         "--binary", str(inputs / "covered-BINARY.json"),
         "--prior-price", str(inputs / "normalized-PRICE.json"),
         "--accept", str(inputs / "normalized-ACCEPT.json"),
         "--weighted", str(inputs / "WEIGHTED-EXITS.md"),
         "--out", str(output)], timeout=45, check=True)
    for path in (root / "r349/receipt.json", output):
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit("R349 receipt mismatch")
print("PASS independent coefficient-8 exclusion on the fixed paired word")
