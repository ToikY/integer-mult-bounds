"""Replay the shipped allocation receipt from two exact clean Git checkouts."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from shutil import copytree
from subprocess import check_output, run
import sys
from tempfile import TemporaryDirectory

RELEASE = "8c800e1b6458526e1ce7a59150bba8a0d29d0027"
COMPARATOR = "04228ea5a1292cf8526a20037060f6fc6e15a858"
SEALED = "18a9c9a64506bbd107305db10f2fac3df42d32b299d0627baba8958ac5d59924"
COMPLETE = "round397/price/COMPLETE.json"
ONBOARDING = "round396/onboarding.log"
PACKAGE = "research/p104-weighted-capped-allocation"


def pinned(path, digest):
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"Unexpected digest for {path.name}")
    return data


def exact_checkout(root, commit):
    path = root.resolve(strict=True)
    found = check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if found != commit:
        raise ValueError(f"Expected Git HEAD {commit}, found {found}")
    return path


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("candidate", "comparator", "out"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    candidate = exact_checkout(args.candidate, RELEASE)
    comparator = exact_checkout(args.comparator, COMPARATOR)
    source = Path(__file__).resolve().parent
    changes = json.loads((source/"PATH-REDACTIONS.json").read_bytes())
    if changes.keys() != {COMPLETE, ONBOARDING}:
        raise ValueError("Unexpected traceback redaction keys")
    complete, onboarding = changes[COMPLETE], changes[ONBOARDING]
    expected = json.loads(pinned(source/"verified.json", SEALED))
    original = json.loads(pinned(source/"COMPLETE-sealed.json", complete["sealed"]))
    public = json.loads(pinned(source/"evidence"/COMPLETE, complete["public"]))
    pinned(source/"evidence"/ONBOARDING, onboarding["public"])
    checker = (source/"accept.py").read_text()
    prior = expected["pinned_prior_evidence"]
    if (original.get(ONBOARDING) != onboarding["sealed"]
            or original | {ONBOARDING: onboarding["public"]} != public
            or prior[COMPLETE] != complete["sealed"] or prior[ONBOARDING] != onboarding["sealed"]
            or checker.count(complete["sealed"]) != 1):
        raise ValueError("Unexpected change to the sealed predecessor receipts")
    prior.update({COMPLETE: complete["public"], ONBOARDING: onboarding["public"]})
    with TemporaryDirectory(prefix="capped-allocation-replay-") as directory:
        scratch = Path(directory)
        evidence = scratch/"evidence"
        copytree(source/"evidence", evidence)
        (evidence/"round396/publish").symlink_to(comparator, target_is_directory=True)
        replay = scratch/"accept.py"
        replay.write_text(checker.replace(complete["sealed"], complete["public"]))
        receipt = scratch/"receipt.json"
        run([sys.executable, "-IB", str(replay), "--inputs", str(evidence),
             "--capsule", str(candidate/PACKAGE), "--log", str(source/"build.log"),
             "--frozen", str(source/"INPUTS.json"), "--out", str(receipt)],
            check=True)
        data = receipt.read_bytes()
        if data != (json.dumps(expected, indent=2, sort_keys=True)+"\n").encode():
            raise ValueError("Receipt changed beyond the declared traceback path hash")
        with args.out.open("xb") as result:
            result.write(data)


if __name__ == "__main__":
    main()
