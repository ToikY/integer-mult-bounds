"""Build authenticated runtime trees independently for byte comparison and inspection."""
from argparse import ArgumentParser
from pathlib import Path
import os
import runpy
from subprocess import run
import sys

def materialize(package, stage):
    peer = runpy.run_path(str(package / "upstream_verify.py"))["restore"](stage / "archive")
    runpy.run_path(str(package / "prepare.py"))["materialize"](peer)
    runpy.run_path(str(package / "retune.py"))["install"](peer, "460")
    runtime = stage / "runtime"
    run([sys.executable, "-IB", str(peer / "bootstrap.py"), str(runtime)], check=True, cwd=stage,
        env={**os.environ, "GIT_CEILING_DIRECTORIES": str(stage.parent)})
    return peer, runtime

if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("peer", type=Path)
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    for package, stage in (
        (args.candidate.resolve() / "research/p104-period-debit-25bit", args.stage / "candidate"),
        (args.peer.resolve() / "research/p104-expanded-budget-25bit", args.stage / "peer"),
    ):
        stage.mkdir(parents=True, exist_ok=False)
        print(*materialize(package, stage.resolve()))
