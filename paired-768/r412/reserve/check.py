"""Check the exact ordinary reserve accounting and its source anchors."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


SOURCES = {
    "TRANSFER.md": "7164831a5dd9f5c6231bf4c3f4b2061d91cbfab559071a0a5d68966e3f7ac55c",
    "ORDINARY-CLOCK.md": "4694db0b2218796e348c1128271cebb3fc779151a639b0e0fb5bbecf9f3ccb94",
    "RECEIVER.md": "f31089b6304fc5352feb9aa8a963cc5a950a828165d3426e16e8a973529d814e",
    "research/p104-shortcut-word-eta-27bit-5stage/prepare.py": "bc401e5c47d275617f3c7d162d56ea4c604ef3d4c6637ab2a8aa8627a570a9f6",
}


def authenticated(path, source_id):
    data = path.read_bytes()
    if sha256(data).hexdigest() != SOURCES[source_id]:
        raise ValueError(f"Incorrect digest for {source_id}")
    return data.decode()


def child_charge(max_child_volume, tariff):
    ratio = max_child_volume / tariff
    if ratio >= 1:
        raise ValueError("The same-stage child charge does not contract")
    return ratio, 1 / (1 - ratio)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof-root", required=True, type=Path)
    parser.add_argument("--prepare", required=True, type=Path)
    args = parser.parse_args()
    assert __debug__
    transfer, clock, receiver = (
        authenticated(args.proof_root / name, name)
        for name in ("TRANSFER.md", "ORDINARY-CLOCK.md", "RECEIVER.md")
    )
    peer = authenticated(args.prepare, "research/p104-shortcut-word-eta-27bit-5stage/prepare.py")
    assert "outward bound for $(256/255)F/N^t$" in transfer
    assert "Its bound includes the factor 256/255" in transfer
    assert "(75/32)(P(N)/B)N^(−s) at s=t and s=1" in clock
    assert "ratio is at most 375/376" in clock
    assert "(21x+3)/D" in receiver and "complete mean is below 75/32" in receiver
    assert "reserve=Q(1)" in peer
    assert "tape_factor(134, BINARY_C, 4474, Q(186, 25)) * Q(255, 256) * CHILD_TARIFF" in peer
    assert "128 + 3 * len(heights) + 320 * sum(heights)" in peer
    assert "40 + 22 + 16384 * sum(heights) + sum(additions)" in peer

    max_child_volume = Q(75, 32)
    old_tariff, new_tariff = Q(47, 20), Q(2401, 1024)
    old_ratio, old_sum = child_charge(max_child_volume, old_tariff)
    new_ratio, new_sum = child_charge(max_child_volume, new_tariff)
    assert (old_ratio, new_ratio) == (Q(375, 376), Q(2400, 2401))
    assert (old_sum, new_sum) == (376, 2401)
    assert old_sum < new_sum < 8 * old_sum
    assert 2**16 < (Q(7, 10) * old_sum)**2 < 2**17
    assert 2**21 < (Q(7, 10) * new_sum)**2 < 2**22
    assert (new_sum / old_sum)**5 < 2**15
    c_b = Q(4391986206293, 2**50)
    assert 0 < Q(1420718, 2**20) / 3000 < c_b < 1
    try:
        child_charge(max_child_volume, max_child_volume)
    except ValueError:
        pass
    else:
        raise AssertionError("Equal-volume tariff was not rejected")

    output = dict(
        proof_head="dfd25d553a843a946ca0b94130a5ff8943e98fdd",
        reserve_claim_head="3cb92cf5c07e98a96d298ee33a4d744c5e32f1ca",
        composed_head="c20a08dc0a79a989e3515068560d5da371c0a2a8",
        sources_sha256=SOURCES,
        paid_moments=["t=1-(c_B-debit/H)", "1"],
        old_child_ratio=old_ratio,
        composed_child_ratio=new_ratio,
        old_geometric_sum=old_sum,
        composed_geometric_sum=new_sum,
        terminal_extra_bits=15,
        entry_extra_bits=5,
        equal_volume_tariff_ratio=1,
        scope="Source anchors and exact ordinary clock margins; conditional on the inherited physical child bound and paid-leaf loss inequality.",
    )
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
