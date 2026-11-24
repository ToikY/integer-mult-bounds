"""Bind the installed nine-recipe census to the exact tariff selector."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import runpy
import sys


BASE = "4af6910aefca5a150f16cbed8e08cb5b60d458af6c52e7c9f8e3fd435274ee0c"
IMAGE = "4793148b05ea33ef5140d9afe4f79c409ec7e9493314afec295ba810e03f13d8"


def extend(root):
    source = root / "r428/check_setup.py"
    if sha256(source.read_bytes()).hexdigest() != BASE:
        raise ValueError("The installed Round 428 census wrapper differs")
    census = runpy.run_path(str(source))["extend"](root)
    selectors = census["SELECTORS"]
    if set(selectors) != {"peer", "candidate", "period", "fringe"}:
        raise ValueError("The inherited installed census selectors differ")
    selectors["tariff"] = IMAGE, Fraction(".003900857313143")
    return census


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--handoff-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--portable", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    args = parser.parse_args()
    main = extend(args.handoff_root.resolve())["main"]
    sys.argv[1:] = ("--profile", "tariff", "--runtime", str(args.runtime),
                    "--portable", str(args.portable), "--scratch", str(args.scratch))
    main()
