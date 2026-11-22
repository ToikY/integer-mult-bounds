"""Replay Round 394 from exact roots with path-normalized historical evidence."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from shutil import copytree
import subprocess
import sys
from tempfile import TemporaryDirectory

HEAD = "19e67d1b36210e3047bbf3d04625d1262cba672a"
PREVIOUS = "ffa64503646a62a7ac3cd2c47787d670da911f89"
MANIFEST = "round393/price/COMPLETE.json"
LOG = "round392/onboarding.log"


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("current", "previous", "sources", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    for path, head in ((args.current, HEAD), (args.previous, PREVIOUS)):
        actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
        if actual != head:
            raise ValueError(f"Expected exact {head}, received {actual}")
    with TemporaryDirectory(prefix="weighted-ordinary-debit-") as tmp:
        temp = Path(tmp)
        evidence = temp / "evidence"
        copytree(here / "evidence", evidence)
        (evidence / "round392/publish").symlink_to(args.previous.resolve(), target_is_directory=True)
        complete_file = evidence / MANIFEST
        original = sha256(complete_file.read_bytes()).hexdigest()
        contents = json.loads(complete_file.read_bytes())
        contents[LOG] = sha256((evidence / LOG).read_bytes()).hexdigest()
        complete_file.write_text(json.dumps(contents, indent=2, sort_keys=True) + "\n")
        normalized = sha256(complete_file.read_bytes()).hexdigest()
        script = (here / "accept.py").read_text()
        if script.count(original) != 1:
            raise ValueError("Expected one original predecessor completion hash")
        checker = temp / "accept.py"
        checker.write_text(script.replace(original, normalized))
        subprocess.run(
            [sys.executable, "-IB", str(checker),
             "--inputs", str(evidence),
             "--capsule", str(args.current.resolve() / "research/p104-weighted-ordinary-debit"),
             "--sources", str(args.sources.resolve()),
             "--log", str(here / "build.log"), "--frozen", str(here / "INPUTS.json"),
             "--out", str(args.out.resolve())],
            check=True,
        )


if __name__ == "__main__":
    main()
