"""Run an unchanged peer mode after checking actual hosted capacity."""
from argparse import ArgumentParser
from hashlib import sha256
import json
import os
from pathlib import Path
from shutil import disk_usage
from subprocess import run
import sys
from tempfile import gettempdir

HEAD = "c20a08dc0a79a989e3515068560d5da371c0a2a8"
PACKAGE = "research/p104-shortcut-word-eta-27bit-5stage"
MODES = ("price", "calendar", "raw", "exterior", "nested", "product", "setup")
RESERVE = 8 * 1024**3
HERE = Path(__file__).resolve().parent


def authenticate(package):
    pins = json.loads((HERE / "INPUTS.json").read_bytes())
    if pins["head"] != HEAD or pins["package"] != PACKAGE:
        raise ValueError("Wrong peer origin")
    for name, pin in pins["files"].items():
        if sha256((package / name).read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError(f"Wrong exact peer input {name}")


def admit(checkout, temp):
    free = {"checkout": disk_usage(checkout).free, "temporary": disk_usage(temp).free}
    print(json.dumps({"free_bytes": free, "required_free_bytes": RESERVE}, sort_keys=True), flush=True)
    if min(free.values()) < RESERVE:
        raise RuntimeError("8 GiB disk admission failed before scientific replay")
    if not hasattr(os, "sched_setaffinity"):
        raise RuntimeError("Use the documented Ubuntu hosted worker with CPU affinity")
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=MODES)
    args = parser.parse_args()
    root = HERE.parents[1]
    package = root / PACKAGE
    authenticate(package)
    admit(root, gettempdir())
    print(f"ADMITTED_EXACT_PEER_MODE {args.mode} {HEAD}", flush=True)
    run([sys.executable, "-IB", str(package / "verify.py"), args.mode], cwd=root, check=True)


if __name__ == "__main__":
    main()
