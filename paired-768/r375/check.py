"""Bound the exact compact candidate against #8057 and price a possible retune."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

# Paths are relative to the campaign evidence root.
PINS = {
    "round372/primary/receipt.json": "33854dce220483454d08bf242b4fec99424758ffd2ea21070ea21fda297a26f0",
    "round373/independent/verified.json": "64ee2fb61e6f3c55a6b06ac64b2d664c804a17b15eee903f5ab1af721aa71e77",
    "round374/publish/research/p104-compact-rounded-partitions/RESULT.json":
        "0d20d4607fd2d68dfe0aaf84e063d986cb2c8e614a89dcd3a825135d62e075c6",
}
PEER = Q(".00389821")
BINARY = Q(4391986206293, 2**50)
G = Q(1, 10**18)
H1 = 35327
H2 = 559462
HG = 680000


def ceiling(q):
    return -(-q.numerator // q.denominator)


def check(root):
    data = {}
    for path, expected in PINS.items():
        content = (root / path).read_bytes()
        assert sha256(content).hexdigest() == expected, path
        data[path] = json.loads(content)
    gaussian, retune, compact = data.values()
    literal = compact["terminal"]
    assert literal["binary_H"] == [H1, H2] and literal["gaussian_H"] == HG
    assert Q(literal["kappa"]) == Q(".003898202")
    assert compact["gaussian"]["transport_cells"] == gaussian["canonical_cells"] == 63
    factor = Q(gaussian["canonical_reserve_factor_millionths"], 10**6)
    assert factor == Q(compact["gaussian"]["physical_factor_upper_millionths"], 10**6)
    c = Q(gaussian["gaussian_candidate_c"])
    assert c == Q(retune["candidate_raw_trial"])
    old_debit = Q(43, 256)
    assert c - old_debit / HG == Q(literal["positive_rate"])
    raw_lo, raw_hi = map(Q, gaussian["gaussian_crossing"])
    assert c < raw_lo < raw_hi < Q(".004")
    assert gaussian["new_and_old_directed_derivative_upper"][0] < 0

    a1 = Q(249, 250) * (BINARY - Q(11, 8 * H1))
    first = Q(int(a1 * 10**21) - 1, 10**21)
    assert first == Q(literal["rates"][0])

    def ordinary_upper(h):
        return (249 * (BINARY - Q(11, 8 * h)) + first) / 250 - 5 * G

    fixed_pos = c - old_debit / HG - 5 * G
    repriced_pos = raw_hi - old_debit / HG - 5 * G
    fixed_ord = ordinary_upper(H2)
    assert fixed_ord < fixed_pos < repriced_pos < PEER
    assert fixed_ord - Q(literal["kappa"]) == Q(retune["ordinary_stage_margins"][-1])
    min_g_for_repriced = old_debit / (raw_hi - PEER - 5 * G)
    min_g_for_installed = old_debit / (c - PEER - 5 * G)
    min_h2 = Q(11, 8) / (BINARY - (250 * (PEER + 5 * G) - first) / 249)
    assert [ceiling(q) for q in (min_h2, min_g_for_repriced, min_g_for_installed)] == [
        561297, 689292, 698524
    ]

    # Enlarging only the dyadic input to the fixed factor multiplies its true value
    # by (1024*A*L)^(trial-c). Convexity from 0 to 1 bounds 2^x by 1+x.
    candidate = Q(".00389821005")
    trial = Q(1097317122991, 2**48)
    narrower_debit = Q(339, 2048)
    h2 = 561325
    assert 0 < trial - c < Q(1, 10**8) and trial < raw_lo
    assert 1024 * 12087 * 32768 < 1 << 39
    assert factor**2048 * (1 + Q(1, 10**6))**2048 < 1 << 339
    ordinary_margin = ordinary_upper(h2) - candidate
    gaussian_margin = trial - narrower_debit / HG - 5 * G - candidate
    assert ordinary_margin > 0 and gaussian_margin > 0 and candidate > PEER
    return {
        "pins": PINS,
        "peer_claim": "cbe847a953b971f9c6c5a0a6661e2008acd29086",
        "peer_kappa": str(PEER),
        "R374_exact_ordinary_ceiling": str(fixed_ord),
        "R374_shortfall": str(PEER - fixed_ord),
        "R374_exact_gaussian_ceiling": str(fixed_pos),
        "retuned_raw_upper_same_Gaussian_debit": str(repriced_pos),
        "retuned_raw_shortfall_same_Gaussian_debit": str(PEER - repriced_pos),
        "necessary_heights_same_price": {
            "binary_terminal_if_other_binary_stage_fixed": 561297,
            "gaussian_ideal_raw_limit": 689292,
            "gaussian_installed_dyadic": 698524,
        },
        "R375_outcome": "NO_VERIFIED_GAIN",
        "one_price_followup": {
            "trial_kappa": str(candidate),
            "gain_if_verified": str(candidate - PEER),
            "gaussian_trial": str(trial),
            "gaussian_debit": str(narrower_debit),
            "terminal_binary_H2": h2,
            "ordinary_margin": str(ordinary_margin),
            "gaussian_margin": str(gaussian_margin),
            "first_gate": "reprice literal compatible coupling and amended typed calendar",
        },
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.inputs)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
