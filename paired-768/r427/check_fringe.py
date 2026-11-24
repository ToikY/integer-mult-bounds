"""Price an integral bound on the existing Gaussian interior loan suffix."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor, isqrt
import os
from pathlib import Path
import runpy
import signal
import sys
from tempfile import TemporaryDirectory


PINS = {
    "package/RESULT.json": "ad6ca3a20b296033ed586821db1f42ffee2d9b5cd9723dbcb1720605f143f609",
    "runtime/grades.py": "6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d",
    "runtime/transport.py": "9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818",
    "runtime/typed_transport.py": "b76b9ad3dc0dd91473026c079585f830387eaa3c34c25a7820ee5057d5cbf941",
}


def read_pinned(roots, key):
    root, trailer = key.split("/", 1)
    path = roots[root] / trailer
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f"Unexpected pinned input {key}")
    return data


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key {key!r}")
        result[key] = value
    return result


def power_of_two(exponent, precision):
    """Bound 2**exponent on a positive fixed grid using integer roots."""
    assert 0 < exponent < 1 and exponent.denominator.bit_count() == 1
    grid = 1 << precision
    bottom = top = 2 * grid
    lower = upper = grid
    for position in range(exponent.denominator.bit_length() - 2, -1, -1):
        bottom = isqrt(bottom * grid)
        top = 1 + isqrt(top * grid - 1)
        if exponent.numerator >> position & 1:
            lower = lower * bottom // grid
            upper = ceil(Q(upper * top, grid))
    return Q(lower, grid), Q(upper, grid)


def check(package, runtime):
    roots = {"package": package, "runtime": runtime}
    inputs = {key: read_pinned(roots, key) for key in PINS}
    result = json.loads(inputs["package/RESULT.json"], object_pairs_hook=unique_object)
    terminal = result["terminal"]
    gaussian = result["gaussian"]
    finite = gaussian["finite_loss"]
    old = Q(terminal["kappa"])
    previous_debit = Q(finite["debit"])
    fringe = Q(finite["fringe"])
    previous_factor = Q(finite["upper_factor"])
    target_axes = finite["weighted_target_axes"]
    lower_band = finite["lower_band"]
    assert (old, previous_debit, target_axes, lower_band) == (
        Q(".003900857312000"), Q(1039701, 2**23), 677246016, 1874)
    assert finite["upper_scale"] == 263772
    assert fringe == 10 * target_axes / ((1 - Q(gaussian["trial"])) * Q(finite["psi_lower"]))

    # A positive grant requires e*r < (d+2)*k. Thus the actual integer
    # suffix r*(e-8)-k*(d-8) is below 10*k-8*r and at most 10*k-5.
    # The lower bound on the weighted number of owner slots is A/258.
    fractional_fringe_saving = Q(5, 10 * 258)
    new_fringe = fringe * (1 - fractional_fringe_saving)
    delta = Q(1, 2**128)
    factor = previous_factor * ((1 + new_fringe / lower_band + delta) /
                                (1 + fringe / lower_band + delta))
    proposed_debit = previous_debit - Q(2, 2**23)
    for bits in (112, 192):
        assert previous_factor < power_of_two(previous_debit, bits)[0]
        assert power_of_two(proposed_debit, bits)[1] < previous_factor
        assert factor < power_of_two(proposed_debit, bits)[0]

    c_bit = Q(4391986206293, 2**50)
    ordinary_debit = Q(1414404, 2**20)
    eta = Q(1, 256)
    stop = Q(1, 10**18)
    prior = Q(0)
    heights = terminal["ordinary_H"]
    assert heights == [31808, 502922, 7951907, 125730703, 134217727]
    for h in heights:
        ordinary = min(eta, (249 * (c_bit - ordinary_debit / h) + prior) / 250)
        prior = Q(floor(10**21 * ordinary) - 1, 10**21)
    ordinary -= 5 * stop
    height = terminal["numerical_H"]
    assert height == 208653
    old_gaussian = Q(gaussian["trial"]) - previous_debit / height - 5 * stop
    new_gaussian = Q(gaussian["trial"]) - proposed_debit / height - 5 * stop
    assert old < old_gaussian < ordinary < new_gaussian
    chosen = Q(ceil(ordinary * 10**15) - 1, 10**15)
    assert old < chosen < ordinary <= chosen + Q(1, 10**15)
    activation = terminal["stock"]["public_exponent_A"]
    entry = result["entry"]
    conversion = ceil((chosen - Q(entry["kappa"])) * activation)
    recurring = 1 + max(entry["log2_C"] + conversion, terminal["log2_C"])
    assert (activation, conversion, recurring) == (268644472, 121121, 85945126846)
    return {
        "scope": "One fixed profile, source geometry and directed price only",
        "inputs_sha256": PINS,
        "integer_suffix_bound": "10*k - 5",
        "weighted_slot_count_lower": str(Q(target_axes, 258)),
        "fringe_reduction_lower_fraction": str(fractional_fringe_saving),
        "old_debit": str(previous_debit),
        "tested_debit": str(proposed_debit),
        "directed_precisions": [112, 192],
        "old_factor_negative_control": "rejected at tested debit",
        "old_gaussian_guarded": str(old_gaussian),
        "new_gaussian_guarded": str(new_gaussian),
        "ordinary_guarded": str(ordinary),
        "binding_after_two_ticks": "ordinary",
        "projected_kappa": str(chosen),
        "projected_delta": str(chosen - old),
        "complete_log2_C": recurring,
    }


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--runtime", type=Path)
    args = parser.parse_args()
    signal.alarm(45)
    try:
        if args.runtime is not None:
            result = check(args.package, args.runtime)
        else:
            verifier = runpy.run_path(str(args.package.resolve() / "verify.py"))
            verifier["authenticate"]()
            with TemporaryDirectory(prefix="croc-fringe-screen-") as directory:
                scratch = Path(directory).resolve()
                env = dict(os.environ, **verifier["THREAD_ENV"], TMPDIR=str(scratch))
                peer = verifier["prepare"](scratch, env)
                runtime = scratch / "runtime"
                verifier["install"](peer, runtime, env)
                result = check(args.package, runtime)
        print(json.dumps(result, indent=2))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
