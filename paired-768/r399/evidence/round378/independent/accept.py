"""Independently check the exact R378 weighted result and fixed native setup."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path, PurePosixPath
import json
import runpy
import tarfile

HEAD = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
COMPARATOR = "4ff66ca09aa7727768aeaf24ac444e69675804de"
CAPSULE_PINS = {
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "prepare.py": "5d4e1346befab94568240d0357216911648f1af224fc119884404e355f84119d",
    "RESULT.json": "856fb47d247b553f3d65f4879a456d9dff7991c6af41b0cb31e9c941e8840775",
}
EVIDENCE_PINS = {
    "price/receipt.json": "1a3600d7f62b82986ea752a0f285be28a551b44b8e05e91a40e09642238ccbc7",
    "audit/receipt.json": "8a2099dd18818ab5f1df4d7d29d8cdbbf3df971ed567475309e35218ffe3eb71",
}
PACKAGE = "research/frequency-weighted-native-multiplier"
C = Q(17145637167, 2**42)
K = Q(".00389821030")
PREVIOUS = Q(".00389821005")
DEBIT = Q(65000, 524288)
DEBIT_OLD = Q(65081, 524288)
BINARY = Q(4391986206293, 2**50)
G = Q(1, 10**18)
UNIT = 2**112
DELTA = Q(1, 2**128)


def need(condition, claim):
    if not condition:
        raise ValueError(claim)


def sha(data):
    return sha256(data).hexdigest()


def pinned(path, expected):
    data = path.read_bytes()
    need(sha(data) == expected, f"source hash {path.name}")
    return data


def restore_reference(capsule):
    spec = json.loads(pinned(capsule / "PEER-SOURCE.json", CAPSULE_PINS["PEER-SOURCE.json"]))
    archive = capsule / "peer8057.tar.gz"
    pinned(archive, CAPSULE_PINS["peer8057.tar.gz"])
    need(spec["head"] == HEAD and spec["archive_sha256"] == CAPSULE_PINS[archive.name], "archive pin")
    data = {}
    with tarfile.open(archive) as entries:
        for member in entries:
            path = PurePosixPath(member.name)
            need(not path.is_absolute() and ".." not in path.parts, "relative archive path")
            if member.isdir():
                continue
            name = member.name
            need(member.isfile() and name not in data and name in spec["files_sha256"], "single pinned file")
            content = entries.extractfile(member).read()
            need(sha(content) == spec["files_sha256"][name], f"content {name}")
            data[name] = content
    need(data.keys() == spec["files_sha256"].keys(), "every authenticated source extracted")
    return data


def power(rank, exponent):
    """Outward 112-bit dyadic root-product enclosure."""
    whole, numerator = divmod(exponent.numerator, exponent.denominator)
    steps = exponent.denominator.bit_length() - 1
    need(exponent.denominator == 1 << steps, "dyadic trial")
    lower = upper = rank**whole * UNIT
    x = y = rank * UNIT
    for j in range(steps - 1, -1, -1):
        x = isqrt(x * UNIT)
        y = isqrt(y * UNIT - 1) + 1
        if numerator & (1 << j):
            lower = lower * x // UNIT
            upper = -(-(upper * y) // UNIT)
    return Q(lower, UNIT), Q(upper, UNIT)


def factor(fringe, upper):
    return ((1 + DELTA) * (1 + Q(4 * 258, 1024 * 306)) * power(1024 * 306 * 2048, C)[upper]
            * (1 + Q(fringe) / 2048 + DELTA) / (1 - DELTA)**4)


def setup(audit):
    w = 2**38
    z = 2 * w + 2
    scalar = 2**16 * (z + 4) * (7 * z + 9) + 8 * 2**16 * (z + 4)**2
    store = 4 * w * 2**68
    lookup = 8 * store * 512 * 128
    total = (2**68 + 1) * (lookup + scalar + 2**120) * 2**32
    book = 2**20 * 256 + 2**8 * 256 * 8 + 32 * (52 + 4)**2 + 2**12
    need(store == audit["fixed_native_record_store_upper"] and scalar < 2**110, "native record and arithmetic")
    need(total == audit["fixed_native_setup_clock_upper"] < 2**228, "complete fixed native tape")
    need(book == audit["fixed_grade_recipe_actions_upper"] < 2**32, "weighted descriptors inside budget")
    need(audit["max_share_bits_observed"] == 262 and audit["fixed_datum_bits_upper"] == w, "fixed exact data")
    return total, 2**20 * 256 + 2**8 * 256 * 8 + 32 * (52 + 2)**2 + 2**12


def verify_overlay(capsule, original):
    pinned(capsule / "prepare.py", CAPSULE_PINS["prepare.py"])
    edits = runpy.run_path(str(capsule / "prepare.py"))["EDITS"]
    need(set(edits) == {"runtime.patch", "positive_debit.py", "receipt.py", "independent_price.py"},
         "only expected literal edit points")
    for name, replacements in edits.items():
        source = original[PACKAGE + "/" + name].decode()
        for old, new in replacements:
            need(source.count(old) == 1, f"one archived change point in {name}")
            source = source.replace(old, new)
        if name == "runtime.patch":
            need(len(replacements) == 1 and ".00389821030" in replacements[0][1],
                 "runtime patch changes only the terminal profile")
    kept = ("grades.py", "typed_transport.py", "check_calendar.py", "check_raw.py",
            "check_ownership.py", "check_nested.py", "check_placement.py")
    need(not set(kept) & edits.keys(), "old calendar, phase and owner return paths remain literal")
    return {name: sha(original[PACKAGE + "/" + name]) for name in kept}


def ordinary(row, heights, rate):
    need(row["ordinary_H"] == heights and Q(row["kappa"]) == rate, "literal tier")
    previous = Q()
    for i, h in enumerate(heights):
        funded = min(Q(".0039"), (249 * (BINARY - Q(11, 8 * h)) + previous) / 250)
        actual = Q(row["ordinary_rates"][i])
        expected = Q(int(funded * 10**21) - 1, 10**21) if i + 1 < len(heights) else rate + 5 * G
        need(previous < actual == expected < funded, "exact ordinary stages")
        previous = actual
    return funded - actual


def compare(literal, baseline, price, audit):
    old_price, fresh_price = baseline["gaussian"], literal["gaussian"]
    for key in ("trial", "weights", "real_targets", "real_loans", "weighted_targets", "weighted_loans",
                "directed_margin", "grade_cells", "typed_cells", "min_individual_share", "capacity_cut"):
        need(fresh_price[key] == old_price[key], f"unaltered weighted word field {key}")
    need((fresh_price["grade_cells"], fresh_price["typed_cells"]) == (51, 88), "exact coupling counts")
    need(Q(fresh_price["trial"]) == C and Q(fresh_price["raw_loss"]) == DEBIT, "new installed price")
    old_loss, loss = (p["finite_loss"] for p in (old_price, fresh_price))
    axes = loss["weighted_target_axes"]
    need(loss["lower_band"] == old_loss["lower_band"] == 2048, "original band floor")
    need(axes == old_loss["weighted_target_axes"] == 135150528, "fixed physical axis price")
    psi, fringe = (Q(loss[key]) for key in ("psi_lower", "fringe"))
    need(psi > Q("184971191.2157") and fringe == 10 * axes / ((1-C) * psi), "exact edge integral")
    need(fringe < Q("7.335168"), "sharp fringe bound")
    fresh = factor(fringe, 1)
    need(fresh == Q(loss["upper_factor"]) < power(2, DEBIT)[0], "all terms charged under new debit")
    old_coarse = factor(old_loss["fringe"], 0)
    old_over_new_cap = old_coarse - power(2, DEBIT)[1]
    need(old_over_new_cap > Q(".0001163759132351"), "negative control rejects old coarse formula")
    need(C - DEBIT_OLD / 483871 < K + 5 * G, "old debit cannot fund new target")

    profiles = (("entry", [3000, 3080], 1024, Q(".00345")),
                ("terminal", [8192, 129414, 524349], 483871, K))
    for label, heights, hg, kappa in profiles:
        actual, independent = literal[label], audit[label]
        gap = ordinary(actual, heights, kappa)
        raw = C - DEBIT / hg
        need(actual["numerical_H"] == hg and Q(actual["gaussian_rate"]) == raw, "literal numerical tier")
        need(raw - kappa - 5 * G == Q(independent["gaussian_gap"]), "exact charged positive gap")
        need(gap == Q(independent["ordinary_final_gap"]), "exact charged ordinary gap")
        for key in ("stock", "geometry", "log2_B", "log2_C", "signed"):
            need(actual[key] == independent[key], f"independent {label} {key}")
    terminal_a = literal["terminal"]["stock"]["public_exponent_A"]
    delta = -pow(2, terminal_a, 6) % 6
    premium = (K-Q(".00345")) * terminal_a
    premium = -(-premium.numerator // premium.denominator)
    need(terminal_a == 1146300 and delta == 2 and premium == 514, "all-input early and late boundary")
    need(literal["entry_price_surcharge"] == premium, "complete finite entry premium in literal price")
    clock = 1 + max(literal["terminal"]["log2_C"], literal["entry"]["log2_C"] + premium)
    need(clock == literal["complete_log2_C"] == audit["complete_recurring_log2_C"] == 318278951,
         "fully charged recurring tape")
    need(price["comparison_8058_head"] == COMPARATOR and K-Q(price["installed_ceiling_8058"]) > 0,
         "strictly exceed exact installed prior upper")
    need(K-PREVIOUS == Q(1, 4_000_000_000) == Q(price["delta_over_8058"]), "same benchmark gain")
    total_setup, grade_actions = setup(audit)
    need(literal["log2_fixed_setup_upper"] == 228 and literal["native_setup_transition_upper"] == total_setup,
         "literal bound charges the full native tape setup")
    need(literal["native_setup_grade_actions"] == grade_actions <= audit["fixed_grade_recipe_actions_upper"],
         "literal weighted grade ledger covered by independent reservation")
    need(not any("portable_setup" in key or "full_store_setup" in key for key in literal),
         "no pricing reliance on previous portable measurements")
    return {"new_factor_upper": str(fresh), "old_coarse_negative_margin": str(old_over_new_cap),
            "native_setup_clock_exact_upper": total_setup, "native_setup_grade_actions": grade_actions,
            "terminal_ordinary_width": profiles[1][1][-1],
            "first_terminal_offset": delta, "complete_log2_C": clock}


def check(evidence, capsule):
    proof = {path: json.loads(pinned(evidence / path, digest)) for path, digest in EVIDENCE_PINS.items()}
    base = restore_reference(capsule)
    old_result = json.loads(base[PACKAGE + "/RESULT.json"])
    result_data = pinned(capsule / "RESULT.json", CAPSULE_PINS["RESULT.json"])
    result = json.loads(result_data)
    charges = compare(result, old_result, proof["price/receipt.json"], proof["audit/receipt.json"])
    return {"capsule_pins": CAPSULE_PINS, "evidence_pins": EVIDENCE_PINS,
            "literal_result_sha256": sha(result_data), "archive_pinned_files": len(base),
            "identical_paid_and_owned_source_hashes": verify_overlay(capsule, base),
            "checked_quantities": charges, "known_good_exact_8057": True,
            "three_term_negative_control": True, "old_debit_negative_control": True,
            "price_kappa": str(K), "exceeds_comparator": COMPARATOR,
            "status": "LITERAL_PRICE_ONLY; REGISTERED SCIENCE SEPARATE"}


if __name__ == "__main__":
    command = ArgumentParser(description=__doc__)
    command.add_argument("--evidence", type=Path, required=True)
    command.add_argument("--capsule", type=Path, required=True)
    command.add_argument("--out", type=Path, required=True)
    args = command.parse_args()
    report = check(args.evidence, args.capsule)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
