"""Check that the retimed allocator's first concrete replica count must change."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import runpy

TRANSPORT = "98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9"


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--transport", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if sha256(args.transport.read_bytes()).hexdigest() != TRANSPORT:
        raise ValueError("The compiler does not match #8052.")
    measure = runpy.run_path(str(args.transport))["Measure"]
    old = Fraction(2092819, 2**29)
    new = Fraction(1071523491, 2**38)
    lower, upper = 32_768, 32_770
    first = measure(1 - old, 1, 256).mass(lower, upper)
    second = measure(1 - new, 1, 256).mass(lower, upper)
    gap = second[0] - first[1]
    if gap <= Fraction(1, 2**96):
        raise ValueError("The coarse dyadic bounds do not separate the allocations.")
    data = {
        "transport_sha256": TRANSPORT,
        "lower_band": lower,
        "upper_band": upper,
        "old_normalized_mass_interval": list(map(str, first)),
        "new_normalized_mass_interval": list(map(str, second)),
        "normalized_separation": str(gap),
        "production_volume_log2": 120_000_000,
        "conclusion": "the first replica count is strictly larger",
    }
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
