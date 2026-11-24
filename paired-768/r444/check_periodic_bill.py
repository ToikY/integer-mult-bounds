"""Price one periodic matched tail on the actual current signed ordinary envelope."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
import os
from pathlib import Path
from runpy import run_path
import sys
from tempfile import TemporaryDirectory, gettempdir


HEAD = "fae237c8aee774bb2256d4e394fed9f3934147c2"
PINS = {
    "package/verify.py": "01675d92b86bd5f96cde7dd9c4ba1884b60b4bf086750da34089ad65866962a0",
    "package/INPUTS.json": "066765506f21bd204408dcf4feaab9bf41c5a9d38ceb32faaf00d1a05bd60f2a",
    "package/RESULT.json": "a674764a45ce4b974bfaaf80d17695b5a91590fa78e0008f4a2e2fc1bafed722",
    "package/source/domain/ASSEMBLY.json": "fb712dd3ea6c929dec956bc8351271aec1297bf7e33c9f24ab6fd203c51ada3c",
    "assembled/receipt.py": "7720731fde6b8c2793bcd64d58d5d00e60eb05a22197fde12a9da927d89999bd",
    "assembled/independent_price.py": "f6d3533e7bae8f7cb7b4d6d8e70885ff79186398c72c96c100254c673f102cdc",
    "runtime/installations.py": "2d55f0269164878a6507c6756f2f27ccd6b3a6d2cbd5b3232e89ebc8e1b7a422",
    "handoff/round438/check_minimal_debit.py": "34c82423ef62ec15eae6ba1f68b0a9be8ca1a54e43fdd34cd46e3a2acfddf9e4",
    "handoff/r411/audit/README.md": "e64085d473a4839d9194edf50b23afe4a126006b6f9883fa9403c6ae41ee7fd3",
    "handoff/r410/bundle/overrides/matched_price_support.py": "4964fb80e4f2a449decbd35044808b3cc235c44405bfa926f6b12f95e9213c33",
    "handoff/r431/check_tariff.py": "f5e258d3fe81b2a220e4458846c733649dd607fa3d0b07d1c1d4ff2a57d3cc8f",
}
LOWER_DEBIT = Q(1411926, 2**20)
CURRENT_DEBIT = Q(1411927, 2**20)
TARIFF = Q(5024210149, 2152336000)
CONTRACTION = Q(2400, 2401)

def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Duplicate input key {name!r}")
        result[name] = value
    return result


def read_pinned(path, key):
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f"Pinned input differs at {key}")
    return data


def band(pair, bits):
    scale = 1 << bits
    return [floor(scale*pair[0]), ceil(scale*pair[1])]


def primitive_envelope(rate, lower, paid, cells, powers, ratios):
    """Retain the full finite factor and use just the transferred matched upper bound."""
    t, delta = 1 - rate, Q(1, 2**128)
    psi, numerator = [Q(0), Q(0)], [Q(0), Q(0)]
    assert lower > 8 and lower % 2 == 0
    upper = 2*((1 << 1024)//(2048*134))
    for (r, k), weight in cells.items():
        z = Q(k, r)
        assert 0 < r and 5*r <= 4*k and weight > 0
        assert 8*(k-r) - 2*r >= 0 and z*lower < upper
        bound = 9*(k-r) + t*r/(2*z*lower)
        assert 0 < bound < 9*k
        count = paid[r]*weight
        for i, zc in enumerate(ratios(k, r, rate)):
            psi[i] += count*r*(zc - 1)/rate
            numerator[i] += count*(zc/z*bound + r*delta)
    assert 0 < psi[0] <= psi[1] and 0 < numerator[0] <= numerator[1]
    fringe = (numerator[0]/(t*psi[1]), numerator[1]/(t*psi[0]))
    scale = powers(1024*134*lower, rate)
    common = Q(256,255)*Q(4097,4096)*Q(1028,1024)/(1 - delta)**4
    factor = tuple(common*s*(1 + f/lower + delta) for s, f in zip(scale, fringe, strict=True))
    return factor, fringe


def check(package, helper, handoff):
    for name in ("verify.py", "INPUTS.json", "source/domain/ASSEMBLY.json"):
        read_pinned(package / name, f"package/{name}")
    read_pinned(helper, "handoff/round438/check_minimal_debit.py")
    for name in ("r411/audit/README.md", "r410/bundle/overrides/matched_price_support.py", "r431/check_tariff.py"):
        read_pinned(handoff/name, f"handoff/{name}")
    data = json.loads(read_pinned(package / "RESULT.json", "package/RESULT.json"), object_pairs_hook=unique_object)
    assert Q(data["terminal"]["kappa"]) == Q(".003900862349168")
    assert Q(data["ordinary_finite_debit"]) == CURRENT_DEBIT
    assert Q(data["ordinary_child_tariff"]) == TARIFF
    assert Q(data["ordinary_child_contraction"]) == CONTRACTION
    assert data["ordinary_child_geometric_budget"] == 2401 and data["ordinary_reserve"] == "256/255"
    guarded = run_path(str(handoff/"r431/check_tariff.py"))["checked_ordinary"]
    loader = run_path(str(package / "verify.py"))
    loader["authenticate"]()
    tools = run_path(str(helper))
    loader["reserve"](Path(gettempdir()))
    with TemporaryDirectory(prefix="limiting-quotient-mean-") as temporary:
        scratch = Path(temporary).resolve()
        env = dict(os.environ, **loader["THREAD_ENV"], TMPDIR=str(scratch))
        peer = loader["prepare"](scratch, env)
        receipt, independent = peer / "receipt.py", peer / "independent_price.py"
        read_pinned(receipt, "assembled/receipt.py")
        read_pinned(independent, "assembled/independent_price.py")
        runtime = scratch / "runtime"
        loader["install"](peer, runtime, env)
        read_pinned(runtime / "installations.py", "runtime/installations.py")
        previous = sys.argv
        try:
            sys.argv = [str(receipt), str(runtime)]
            source = run_path(str(receipt))
        finally:
            sys.argv = previous
        target, paid = source["raw_moments"](source["graph"](), source["caller"]())
        rate, lower = source["BINARY_C"], source["ORDINARY_FLOOR"]
        margin, cells = source["certify"](rate, (target, paid))
        assert margin > 0 and lower == data["ordinary_floor"] == 1156
        assert (sum(target.values()), sum(paid.values()), len(cells)) == (18906, 104652, 24)
        power, unit = source["power_interval"], source["UNIT"]
        assert unit == 2**112

        def power112(base, exponent):
            assert Q(base).denominator == 1
            return tuple(Q(value, unit) for value in power(int(base), exponent))

        def ratio112(n, d, exponent):
            assert Q(n).denominator == Q(d).denominator == 1
            n_lo, n_hi = power(int(n), exponent)
            d_lo, d_hi = power(int(d), exponent)
            return Q(n_lo, d_hi), Q(n_hi, d_lo)

        power192 = tools["get_powers"](independent)

        def ratio192(n, d, exponent):
            return power192(Q(n, d), exponent)

        bounds = {}
        for bits, powers, ratio in ((112, power112, ratio112), (192, power192, ratio192)):
            lo, hi = tools["full_envelope"](rate, lower, paid, cells, powers, ratio)
            if bits == 112:
                direct = source["tape_factor_periodic"]
                assert (lo, hi) == (direct(134, rate, lower, paid, cells, upper=False),
                                    direct(134, rate, lower, paid, cells))
            changed, fringe = primitive_envelope(rate, lower, paid, cells, powers, ratio)
            debit = tuple(2*x for x in powers(2, LOWER_DEBIT - 1))
            booked = 2*powers(2, CURRENT_DEBIT - 1)[0]
            assert debit[1] < TARIFF*lo <= TARIFF*hi < booked
            assert 0 < changed[0] <= changed[1] < lo
            legacy_charge = band((lo*TARIFF, hi*TARIFF), bits)
            new_charge = band(tuple(x*TARIFF for x in changed), bits)
            allowance = band(debit, bits)
            bounds[str(bits)] = {"original_charge": legacy_charge, "primitive_charge": new_charge,
                                 "allowance": allowance, "fringe": band(fringe,bits),
                                 "lower_allowance_minus_upper_primitive": allowance[0] - new_charge[1]}
    funds = all(row["lower_allowance_minus_upper_primitive"] > 0 for row in bounds.values())
    terminal, entry = data["terminal"], data["entry"]
    heights, stop = terminal["ordinary_H"], Q(1,10**18)
    incumbent = Q(terminal["kappa"])
    old_ceiling = guarded(CURRENT_DEBIT, heights, stop)
    new_ceiling = guarded(LOWER_DEBIT, heights, stop)
    gaussian = Q(data["gaussian"]["trial"]) - Q(data["gaussian"]["raw_loss"])/terminal["numerical_H"] - 5*stop
    assert incumbent < old_ceiling < new_ceiling < gaussian
    receipt = {"scope":"One fixed matched-tail price on exact current signed sources. No candidate or complete replay.",
               "head":HEAD, "inputs_sha256":PINS, "tariff":str(TARIFF), "ordinary_reserve":"256/255",
               "paid_clock_budget":2401, "matched_cells":24, "threshold":str(LOWER_DEBIT),
               "dyadic_bounds":bounds, "funds_at_both_precisions":funds,
               "old_ordinary_ceiling":str(old_ceiling), "tested_ordinary_ceiling":str(new_ceiling),
               "gaussian_ceiling":str(gaussian)}
    if funds:
        projected = Q(ceil(new_ceiling*10**15) - 1, 10**15)
        assert old_ceiling < projected < new_ceiling <= projected + Q(1,10**15)
        a = terminal["stock"]["public_exponent_A"]
        conversion = ceil((projected - Q(entry["kappa"]))*a)
        log_c = 1 + max(entry["log2_C"] + conversion, terminal["log2_C"])
        assert (a, conversion, log_c) == (536923552, 242079, data["complete_log2_C"])
        receipt.update(provisional_kappa=str(projected), provisional_delta=str(projected-incumbent),
                       complete_log2_C=log_c)
    return receipt


if __name__ == "__main__":
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--helper", type=Path, required=True)
    parser.add_argument("--handoff-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.package.resolve(), args.helper.resolve(), args.handoff_root.resolve()), indent=2))
