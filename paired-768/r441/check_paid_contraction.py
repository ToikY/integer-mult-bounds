"""Price the existing paid geometric budget with the unchanged N>=16 mean."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
from runpy import run_path
import sys


HEAD = "517eac577bc12a1519eaf346a6816ad91bc9df90"
PINS = {
    "package/RESULT.json": "4ae4c5332a66396a63c0732c5fb1f797f96ebae0e397665de382a3ea31861fa6",
    "peer8097/RESULT.json": "f3ff96fb44169735871b27c1a22dd3f499e20a77401896fe53845f546aa1c9f5",
    "round440/SCREEN.json": "b198cd1e358dc3566ee9dccf2ef29468d095bc3cfefadbecd6cc461d8dd03619",
    "handoff/r427/check_fringe.py": "63c8b56140e5f42f504ac98bb4824934e90e4a5ff26fa3065fe10c8e199640c4",
    "handoff/r431/check_tariff.py": "f5e258d3fe81b2a220e4458846c733649dd607fa3d0b07d1c1d4ff2a57d3cc8f",
}
DEN = 1 << 20
MIN, MAX = 1411924, 1411929


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Duplicate input key {name!r}")
        result[name] = value
    return result


def read_pinned(path, key):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[key]:
        raise ValueError(f"Pinned input differs at {key}")
    return raw


def read_json(path, key):
    return json.loads(read_pinned(path, key), object_pairs_hook=unique_object)


def outward(pair, bits):
    scale = 1 << bits
    return [floor(scale*pair[0]), ceil(scale*pair[1])]


def price(source_band, ratio, power, bits):
    charge = tuple(Q(endpoint, 1 << bits)*ratio for endpoint in source_band)
    assert 2 < charge[0] <= charge[1] < 4
    trials = []
    for tick in range(MIN - 1, MAX + 1):
        allowance = tuple(2*x for x in power(Q(tick, DEN) - 1, bits))
        if charge[1] < allowance[0]:
            assert trials and trials[-1]["tick"] == tick - 1 and not trials[-1]["funded"]
            trials.append({"tick": tick, "funded": True, "allowance": outward(allowance, bits)})
            return {"funded_tick": tick, "rejected_preceding_tick": tick - 1,
                    "charge": outward(charge, bits), "probes": trials}
        if charge[0] <= allowance[1]:
            raise ArithmeticError(f"Unresolved directed comparison at {bits} bits, tick {tick}")
        trials.append({"tick": tick, "funded": False, "allowance": outward(allowance, bits)})
    raise ArithmeticError(f"No funded tick in the declared {bits}-bit scope")


def check(package, peer_package, screen, handoff):
    result = read_json(package / "RESULT.json", "package/RESULT.json")
    peer = read_json(peer_package / "RESULT.json", "peer8097/RESULT.json")
    sealed = read_json(screen, "round440/SCREEN.json")
    power_path, recurrence_path = handoff / "r427/check_fringe.py", handoff / "r431/check_tariff.py"
    read_pinned(power_path, "handoff/r427/check_fringe.py")
    read_pinned(recurrence_path, "handoff/r431/check_tariff.py")
    power = run_path(str(power_path))["power_of_two"]
    guarded = run_path(str(recurrence_path))["checked_ordinary"]
    assert sealed["head"] == HEAD and sealed["excluded_at_both_precisions"] is True
    assert sealed["pinned_inputs"]["package/RESULT.json"] == PINS["package/RESULT.json"]
    assert Q(sealed["booked_debit"]) == Q(result["ordinary_finite_debit"]) == Q(MAX, DEN)
    assert Q(sealed["tested_lower_debit"]) == Q(MAX - 1, DEN)
    assert result["ordinary_floor"] == peer["ordinary_floor"] == 1156
    assert result["ordinary_reserve"] == peer["ordinary_reserve"] == "256/255"
    assert result["ordinary_child_geometric_budget"] == peer["ordinary_child_geometric_sum"] == 2401

    mean = Q(6277647, 2690420)
    old_contraction, new_contraction = Q(2390, 2391), Q(2400, 2401)
    assert Q(result["ordinary_child_tariff"])*old_contraction == mean
    assert Q(peer["ordinary_child_contraction"]) == new_contraction
    assert Q(75, 32)/Q(peer["ordinary_child_tariff"]) == new_contraction
    assert 1/(1 - old_contraction) == 2391 and 1/(1 - new_contraction) == 2401
    tariff = mean/new_contraction
    limit_tariff = Q(sealed["limiting_tariff"])
    assert limit_tariff == Q(7, 3)/old_contraction and tariff < limit_tariff
    ratio = tariff/limit_tariff
    assert MAX - MIN + 2 <= 8
    bounds = {}
    for bits in (112, 192):
        row = sealed["dyadic_interval_numerators"][str(bits)]
        assert row["limiting_charge"][0] > row["lower_debit_allowance"][1]
        bounds[str(bits)] = price(row["limiting_charge"], ratio, power, bits)
    funded = bounds["112"]["funded_tick"]
    assert MIN <= funded <= MAX and funded == bounds["192"]["funded_tick"]

    terminal, entry = result["terminal"], result["entry"]
    heights, g = terminal["ordinary_H"], terminal["numerical_H"]
    assert heights == peer["terminal"]["ordinary_H"] and g == peer["terminal"]["numerical_H"] == 52270
    assert result["gaussian"] == peer["gaussian"]
    stop = Q(1, 10**18)
    incumbent = Q(terminal["kappa"])
    old_ceiling = guarded(Q(MAX, DEN), heights, stop)
    new_ceiling = guarded(Q(funded, DEN), heights, stop)
    gaussian = Q(result["gaussian"]["trial"]) - Q(result["gaussian"]["raw_loss"])/g - 5*stop
    assert incumbent == Q(".003900862349161")
    assert incumbent < old_ceiling <= new_ceiling < gaussian
    proposed = Q(ceil(10**15*new_ceiling) - 1, 10**15)
    assert proposed < new_ceiling <= proposed + Q(1, 10**15)
    assert proposed >= incumbent
    a = terminal["stock"]["public_exponent_A"]
    conversion = ceil((proposed - Q(entry["kappa"]))*a)
    log_c = 1 + max(entry["log2_C"] + conversion, terminal["log2_C"])
    assert (a, conversion, log_c) == (536923552, 242079, result["complete_log2_C"]) and log_c == 171810078109
    return {"scope": "Fixed envelope and N>=16 mean, one contraction under the existing paid clock. No installed replay.",
            "head": HEAD, "inputs_sha256": PINS, "mean": str(mean), "tariff": str(tariff),
            "ratio_to_r440_limiting_tariff": str(ratio), "contraction": str(new_contraction),
            "retained_recursive_budget": 2401, "retained_reserve": "256/255", "denominator": DEN,
            "directed_dyadic_prices": bounds, "old_ordinary_ceiling": str(old_ceiling),
            "new_ordinary_ceiling": str(new_ceiling), "gaussian_ceiling": str(gaussian),
            "provisional_kappa": str(proposed), "provisional_delta": str(proposed - incumbent),
            "complete_log2_C": log_c}


if __name__ == "__main__":
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--peer-package", type=Path, required=True)
    parser.add_argument("--screen", type=Path, required=True)
    parser.add_argument("--handoff-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.package, args.peer_package, args.screen, args.handoff_root), indent=2))
