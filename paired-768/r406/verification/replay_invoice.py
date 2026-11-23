"""Rebuild and compare the separate exact invoice, signed images and decoder controls."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from subprocess import check_output
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def check(script, receipt, *args, replace_archive_label=False):
    raw = check_output([sys.executable, "-IB", HERE/script, *args])
    if replace_archive_label:
        data = json.loads(raw)
        if Path(data["archive_tree_pin"]).name != "source-blobs.json":
            raise ValueError("Unexpected archive pin input")
        data["archive_tree_pin"] = "source-blobs.json"
        raw = (json.dumps(data, sort_keys=True, indent=2)+"\n").encode()
    if raw != (HERE/receipt).read_bytes():
        raise ValueError(f"Independent output differs at {receipt}")
    print(f"PASS {receipt} {sha256(raw).hexdigest()}", flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("candidate", "comparator", "historical_source"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="period-invoice-") as temporary:
        output = Path(temporary)
        check("bind_images.py", "source-binding.json",
              args.candidate, args.comparator, args.historical_source,
              HERE/"source-blobs.json", output, replace_archive_label=True)
        image = output/"candidate-image"
        installed = image/"runtime"
        signed_source = image/"source/research/tiered-native-multiplier/source"
        result = args.candidate/"research/p104-expanded-period-debit/RESULT.json"
        check("independent_invoice.py", "independent-invoice.json", installed, signed_source, result)
        weighted = image/"source/research/frequency-weighted-native-multiplier"
        check("decoder_controls.py", "decoder-controls.json", installed, weighted)


if __name__ == "__main__":
    main()
