"""Project both directed prices onto the exact #8098 signed recurrence."""

from argparse import ArgumentParser
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil
from pathlib import Path
from runpy import run_path


PINS = {
    "package/RESULT.json": "30f83c4820557c0ca3461928c5000da6a0c9fc4b98b3bf6539df8bdb18fb0d93",
    "r438/SCREEN.json": "cb0c087e9814d17af15fae513e739dc03b21a1c8978adc02f5ee541cdb2ae23c",
    "r431/check_tariff.py": "f5e258d3fe81b2a220e4458846c733649dd607fa3d0b07d1c1d4ff2a57d3cc8f",
}


def pinned(path, name):
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError(f"Incorrect pinned bytes at {name}")
    return data


def decimal(value):
    with localcontext() as context:
        context.prec = 35
        return format(Decimal(value.numerator) / value.denominator, "f")


def check(package, handoff):
    baseline = json.loads(pinned(package / "RESULT.json", "package/RESULT.json"))
    scope = json.loads(pinned(handoff / "r438/SCREEN.json", "r438/SCREEN.json"))
    proof = handoff / "r431/check_tariff.py"
    pinned(proof, "r431/check_tariff.py")
    ordinary = run_path(str(proof))["checked_ordinary"]
    widths = scope["directed_results"]
    assert widths["112"] == widths["192"]
    ticks = widths["112"]
    profile, entry = baseline["terminal"], baseline["entry"]
    heights = profile["ordinary_H"]
    old_rate = Q(profile["kappa"])
    stop = Q(1, 10**18)
    gaussian = Q(baseline["gaussian"]["trial"]) - Q(baseline["gaussian"]["finite_loss"]["debit"]) / profile["numerical_H"] - 5*stop
    old_cap = ordinary(Q(baseline["ordinary_finite_debit"]), heights, stop)

    def price(record):
        cap = ordinary(Q(record["first_funded_tick"], scope["debit_denominator"]), heights, stop)
        tick = Q(ceil(10**15 * cap) - 1, 10**15)
        assert old_rate < old_cap < tick < cap < gaussian
        activation = profile["stock"]["public_exponent_A"]
        premium = ceil((tick - Q(entry["kappa"])) * activation)
        recurring = 1 + max(entry["log2_C"] + premium, profile["log2_C"])
        assert (activation, premium, recurring) == (536923552, 242079, 171810078109)
        return cap, tick

    prior_exact, prior_tick = price(ticks["peer8098"])
    new_exact, new_tick = price(ticks["N_at_least_16"])
    assert prior_tick < prior_exact < new_tick < new_exact
    return {
        "scope": "Fixed-profile price projection only; literal selector and complete signed replay remain unrun.",
        "existing_tariff_crossing": str(prior_exact),
        "existing_tariff_provisional_rate": decimal(prior_tick),
        "new_domain_crossing": str(new_exact),
        "new_domain_provisional_rate": decimal(new_tick),
        "provisional_delta_over_reproduced_8098": decimal(new_tick - old_rate),
        "provisional_delta_over_tightened_existing_tariff": decimal(new_tick - prior_tick),
        "gaussian_ceiling": str(gaussian),
        "binding": "ordinary",
        "log2_C": 171810078109,
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--handoff-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.package.resolve(), args.handoff_root.resolve()), indent=2))
