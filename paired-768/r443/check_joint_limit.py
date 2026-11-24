"""Bound the joint rank-domain and contraction limit of one fixed invoice."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import sys


HEAD = "fae237c8aee774bb2256d4e394fed9f3934147c2"
PINS = {
    "package/RESULT.json": "a674764a45ce4b974bfaaf80d17695b5a91590fa78e0008f4a2e2fc1bafed722",
    "handoff/paired-768/r441/SCREEN.json": "74791c2561cd37925d6b72c2b4e6696371583a34811ed0558827d240ac3f7029",
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate receipt key {key!r}")
        result[key] = value
    return result


def authenticate(path, name):
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError(f"Incorrect input at {name}")
    return json.loads(data, object_pairs_hook=unique_object)


def check(package, screen_path):
    result = authenticate(package / "RESULT.json", "package/RESULT.json")
    prior = authenticate(screen_path, "handoff/paired-768/r441/SCREEN.json")
    assert Q(result["terminal"]["kappa"]) == Q(".003900862349168") == Q(prior["provisional_kappa"])
    assert Q(result["ordinary_child_tariff"]) == Q(prior["tariff"]) == Q(5024210149, 2152336000)
    assert Q(result["ordinary_child_contraction"]) == Q(prior["contraction"]) == Q(2400, 2401)
    assert result["ordinary_reserve"] == prior["retained_reserve"] == "256/255"
    assert result["ordinary_child_geometric_sum"] == result["ordinary_child_geometric_budget"] == 2401
    assert prior["retained_recursive_budget"] == 2401 and prior["denominator"] == 2**20
    assert Q(result["ordinary_finite_debit"]) == Q(1411927, 2**20)

    maximum_contraction = 1 - Q(1, 2401)
    installed_mean = Q(prior["mean"])
    limiting_tariff = Q(7, 3) / maximum_contraction
    ratio = limiting_tariff / Q(result["ordinary_child_tariff"])
    assert installed_mean == Q(6277647, 2690420)
    assert ratio == Q(7, 3) / installed_mean == Q(18832940, 18832941)

    bounds = {}
    for precision in ("112", "192"):
        price = prior["directed_dyadic_prices"][precision]
        assert price["funded_tick"] == 1411927 and price["rejected_preceding_tick"] == 1411926
        row, = [p for p in price["probes"] if p["tick"] == 1411926]
        assert not row["funded"]
        lower, upper = price["charge"]
        charged = (floor(lower * ratio), ceil(upper * ratio))
        allowance_lower, allowance_upper = row["allowance"]
        bounds[precision] = {"optimistic_charge": charged, "allowance": row["allowance"],
                             "lower_charge_minus_upper_allowance": charged[0] - allowance_upper,
                             "upper_charge_minus_lower_allowance": charged[1] - allowance_lower}
    excluded = all(b["lower_charge_minus_upper_allowance"] > 0 for b in bounds.values())
    return {
        "scope": "Fixed periodic factor, 256/255 reserve, 2401 paid geometric budget and 2^-20 debit grid.",
        "head": HEAD,
        "inputs_sha256": PINS,
        "optimistic_mean": "7/3",
        "maximum_contraction": str(maximum_contraction),
        "limiting_tariff": str(limiting_tariff),
        "factor_ratio_to_verified": str(ratio),
        "target_debit_tick": 1411926,
        "dyadic_numerators": bounds,
        "excluded_at_both_precisions": excluded,
    }


if __name__ == "__main__":
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--screen", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.package.resolve(), args.screen.resolve()), indent=2))
