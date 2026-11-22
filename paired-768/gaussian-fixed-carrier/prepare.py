"""Materialize the fixed-carrier Gaussian price candidate from the exact peer commit."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HEAD = "baaec65bf8e4c7e92be110a00d5b06522177931f"
PACKAGE = "research/p104-k7-retimed-binary"
EDITS = {
    "installations.py": (
        ("Q(2092819, 2**29)", "Q(1071523491, 2**38)"),
        ('Q(".003898171")', 'Q(".0038981721342")'),
    ),
    "check_complete.py": (
        ('"gaussian_c_decimal": "0.003898179158568382"', '"gaussian_c_decimal": "0.003898179751558928"'),
        ('"extended_kappa": "0.003898171"', '"extended_kappa": "0.0038981721342"'),
    ),
    "check_extended_stop.py": (
        ("F(2092819,2**29)", "F(1071523491,2**38)"),
    ),
}


def materialize(peer: Path, output: Path) -> Path:
    output.mkdir()
    with tempfile.TemporaryFile() as packed:
        subprocess.run(
            ["git", "-C", str(peer), "archive", HEAD, PACKAGE],
            stdout=packed,
            check=True,
        )
        packed.seek(0)
        with tarfile.open(fileobj=packed) as contents:
            contents.extractall(output, filter="data")

    package = output / PACKAGE
    for filename, edits in EDITS.items():
        path = package / filename
        source = path.read_text()
        for old, new in edits:
            if source.count(old) != 1:
                raise ValueError(f"Expected one literal at {filename}")
            source = source.replace(old, new)
        path.write_text(source)
    return package


def regenerate(package: Path) -> None:
    sys.path.insert(0, str(package))
    from bootstrap import install

    with tempfile.TemporaryDirectory() as directory:
        tree = Path(directory) / "tree"
        install(tree)
        sys.path.insert(0, str(tree))
        from upstream import install as sources

        sources()
        from check_complete import all_results

        results = all_results()
    expected = Fraction(".0038981721342")
    assert Fraction(results["profiles"]["extended"]["kappa"]) == expected
    path = package / "RESULT.json"
    path.write_text(json.dumps(results, indent=2) + "\n")
    row = results["profiles"]["extended"]
    print("PASS_FIXED_CARRIER_PRICE", expected, row["signed_gate"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--peer", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    package = materialize(args.peer, args.output.resolve())
    regenerate(package)
