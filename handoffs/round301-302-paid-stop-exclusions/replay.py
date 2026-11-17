"""Replay the frozen finite exclusions using a pinned #7605 source checkout."""
import argparse
from gzip import decompress
from pathlib import Path
from shutil import copyfile
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent
CHECKS = ROOT / "checks"
RECEIPTS = ROOT / "receipts"
PACKAGE = Path("research/p104-timed-helper757")


def checked_run(script, args, expected):
    command = [sys.executable, "-I", "-B", str(CHECKS / script), *map(str, args)]
    result = subprocess.run(command, stdout=subprocess.PIPE, check=True, timeout=31)
    if result.stdout != expected:
        raise ValueError(f"{script}: replay differs from frozen receipt")
    print(f"PASS {script}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkout", type=Path, required=True)
    args = parser.parse_args()
    package = args.source_checkout / PACKAGE
    with TemporaryDirectory(prefix="p104-exchange-replay-") as tmp:
        inputs = Path(tmp)
        sources = {
            "word.json.gz": package / "data/word.json.gz",
            "FINAL.json": package / "data/FINAL.json",
            "7113-CALLER.json": package / "retained/role902/bench/inputs/7113-CALLER.json",
            "pricing.py": ROOT / "tariffs/pricing.py",
            "gate.py": CHECKS / "gate.py",
        }
        for name, source in sources.items():
            copyfile(source, inputs / name)
        for short, specific in (("word.json.gz", "word7605.json.gz"), ("FINAL.json", "FINAL7605.json")):
            copyfile(inputs / short, inputs / specific)

        frozen = decompress((RECEIPTS / "EXCHANGE.jsonl.gz").read_bytes())
        frozen_path = inputs / "EXCHANGE.jsonl"
        frozen_path.write_bytes(frozen)
        checked_run("check_exchange.py", [inputs], frozen)
        exchange_args = ["--word", inputs / "word.json.gz", "--frozen", frozen_path]
        checked_run("replay_exchange_matrices.py", exchange_args, (RECEIPTS / "MATRIX.json").read_bytes())
        checked_run("verify_exchange_shear_bound.py", exchange_args, (RECEIPTS / "SHEAR.json").read_bytes())

        primary = RECEIPTS / "RESULT.json"
        checked_run("check_c1.py", [inputs], primary.read_bytes())
        checked_run("replay_c1_probe.py", ["--input-root", inputs, "--result", primary],
                    (RECEIPTS / "PROBE.json").read_bytes())

    print("PASS rounds 301–302 finite scope")


if __name__ == "__main__":
    main()
