"""Count signed k7 endpoint and payment grades from the two literal words."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import runpy

OLD = "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"
NEW = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
APPLICATION = "587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f"
DIRECTED = "798589c4bcdd19413bb270367b08862482d827191b66344810d1c05c7186be41"
MODES = (("reported_kappa", Fraction("0.003898171")),
         ("binary_c", Fraction(4391986206293, 2**50)))


def pinned(path, expected):
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"Unexpected source digest: {path.name}")
    return data


def dimension_histograms(word):
    dims = {int(key): value["dim"] for key, value in word["frames"].items()}
    paid = Counter(abs(dims[row[3]] - dims[row[2]])
                   for row in word["program"] if row[0] == "MOVE")
    productive = Counter(dims[dst] - dims[src]
                         for src, dst in zip(word["start"][222:],
                                             word["final"][222:], strict=True))
    assert min(paid) > 0 and min(productive) > 0
    return paid, productive


def change_full_invoice(complete, old, new):
    changed = Counter({int(k): v for k, v in complete.items()})
    for grade in old.keys() | new.keys():
        changed[grade] += 36 * (new[grade] - old[grade])
    assert all(count >= 0 for count in changed.values())
    return +changed


def linear(histogram):
    return sum(grade * count for grade, count in histogram.items())


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--peer-package", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    old = json.loads(gzip.decompress(pinned(args.handoff / "inputs/BINARY-CANDIDATE.json.gz", OLD)))
    new = json.loads(gzip.decompress(pinned(args.peer_package / "strong-bit-k7.json.gz", NEW)))
    ordinary = json.loads(pinned(args.handoff / "inputs/APPLICATION.json", APPLICATION))["binary_native"]
    assert old["public"] == new["public"] == 630
    assert all(old[key][:222] == new[key][:222] for key in ("start", "final"))
    old_p, old_t = dimension_histograms(old)
    new_p, new_t = dimension_histograms(new)
    changed_slots = [i for i in range(old["public"]) if
                     any(old[key][i] != new[key][i] for key in ("start", "final"))]
    old_full_p = Counter({int(k): v for k, v in ordinary["paid_all"].items()})
    old_full_t = Counter({int(k): v for k, v in ordinary["productive_all"].items()})
    full_p = change_full_invoice(ordinary["paid_all"], old_p, new_p)
    full_t = change_full_invoice(ordinary["productive_all"], old_t, new_t)
    balances = (linear(old_full_t), linear(old_full_p), linear(full_t), linear(full_p))
    assert balances == (287106, 285600, 286098, 284592)
    assert changed_slots == list(range(222, 229))
    assert sum(full_t.values()) == sum(old_full_t.values()) == 18906
    assert sum(old_full_p.values()) == 104904 and sum(full_p.values()) == 104652
    assert (sum(old_p.values()), sum(new_p.values())) == (2803, 2796)
    signed = full_t.copy()
    signed.subtract(full_p)
    directed_path = args.handoff / "r360/directed.py"
    pinned(directed_path, DIRECTED)
    directed = runpy.run_path(str(directed_path))
    brackets = {}
    for name, candidate in MODES:
        lower, upper = directed["moment"](signed, 1 - candidate)
        assert lower > 0
        brackets[name] = [str(Fraction(mark, directed["SCALE"])) for mark in (lower, upper)]
    args.out.write_text(json.dumps({
        "input_pins": {"old/inputs/BINARY-CANDIDATE.json.gz": OLD,
                       "old/inputs/APPLICATION.json": APPLICATION,
                       "old/r360/directed.py": DIRECTED,
                       "peer/strong-bit-k7.json.gz": NEW},
        "changed_endpoint_slots": changed_slots,
        "old_full_paid": old_full_p, "old_full_productive": old_full_t,
        "new_full_paid": full_p, "new_full_productive": full_t,
        "old_linear_productive_paid": balances[:2],
        "new_linear_productive_paid": balances[2:],
        "raw_signed_margins": brackets
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
