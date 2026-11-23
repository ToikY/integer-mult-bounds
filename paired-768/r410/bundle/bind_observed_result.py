"""Bind the actual native regenerate output without substituting a price projection."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

PACKAGE = "research/p104-matched-suffix-25bit"


def unique(entries):
    data = dict(entries)
    if len(data) != len(entries):
        raise ValueError("Duplicate receipt field")
    return data


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("assembly",type=Path)
    parser.add_argument("observed_result",type=Path)
    parser.add_argument("observed_exit",type=Path)
    args = parser.parse_args()
    assert __debug__
    root = args.assembly.resolve()
    manifest = json.loads((root/"SOURCE-ASSEMBLY.json").read_bytes(),object_pairs_hook=unique)
    assert manifest["candidate_package"] == PACKAGE
    for name,pin in manifest["files"].items():
        assert sha256((root/name).read_bytes()).hexdigest() == pin, name
    assert args.observed_exit.read_text().strip() == "0"
    raw = args.observed_result.read_bytes()
    report = json.loads(raw,object_pairs_hook=unique)
    entry,terminal,gaussian = (report[k] for k in ("entry","terminal","gaussian"))
    assert Q(report["previous_rate"]) == Q(".003898460000505")
    assert Q(report["rate_delta"]) == Q(3241,10**15)
    assert Q(entry["kappa"]) == Q(".00345") and Q(terminal["kappa"]) == Q(".003898460003746")
    assert terminal["ordinary_H"] == [8192,38102,604363]
    assert terminal["numerical_H"] == report["max_native_H"] == 18531230
    assert report["fixed_funding_height_floors"] == [569897,18531230]
    assert report["complete_log2_C"] == 4285082571 and report["entry_price_surcharge"] == 8603
    assert Q(gaussian["raw_loss"]) == Q(130699669,2**30)
    assert Q(gaussian["finite_loss"]["exterior_period_factor"]) == Q(22067,21981)
    assert (gaussian["grade_cells"],gaussian["typed_cells"]) == (51,88)
    assert report["native_setup_transition_upper"] < 2**228
    for tier in (entry,terminal):
        assert (tier["signed"]["strict"],tier["signed"]["functional"]) == (54,4)
        assert tier["geometry"] and tier["stock"]
    destination = root/PACKAGE/"RESULT-460.json"
    with destination.open("xb") as file:
        file.write(raw)
    print("PASS_OBSERVED_RESULT_BINDING",sha256(raw).hexdigest(),flush=True)


if __name__ == "__main__":
    main()
