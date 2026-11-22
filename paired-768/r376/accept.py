"""Bind a literal installed compact-retune receipt to independent signed evidence."""

from argparse import ArgumentParser
import ast
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import runpy

PINS = {
    "round375/independent/coupling.py":
        "fb54f24864288855e15e979549c64449ef350c1cebe008342dda946ba1d941e4",
    "round375/independent/coupling.json":
        "2828f5a208b24b3c556313601d6f05a62fef57509e58dc00d161c9f2d8023553",
    "round376/independent/peer8057/RESULT.json":
        "2f4faa6648592f589df22a8a0a07ba6856d20786294a44a7776c7d6e0efa14a5",
    "round376/independent/peer8057/receipt.py":
        "82d921fdc33006e2d356d8bf78f3c85777722322d716be44b42bc763a04c8095",
    "round374/publish/research/p104-compact-rounded-partitions/prepare.py":
        "6b6ab5c79ab959ddd147b992cae67a82cf549cd282b6e17433aa95b66ae9b2b9",
}
STAGED_FIXED = {
    "peer8055.tar.gz": "c28527d1ef80523191b3454fce6df3b43844db22277ffd16e1170369d2b8f14c",
    "PEER-SOURCE.json": "22a27f2da0cd412ba0e16ac17e0ebd4db3a5c4a919c0954c0ead9dbefe9a0cb6",
    "prepare.py": "9faf4e806b7e0fbb21450c5ee51661830f692b971e9b0aebcfa4ce8790243410",
    "RESULT.json": "fd3f0c95d397038a32ffbdca7c7c827a6fd5e97f1b5cf0f80c75c48b78ec5ae1",
}
C = Q(1097317122991, 2**48)
K = Q(".00389821005")
DEBIT = Q(339, 2048)
G = Q(1, 10**18)
B = Q(4391986206293, 2**50)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def pin(path, digest):
    data = path.read_bytes()
    require(sha256(data).hexdigest() == digest, str(path))
    return data


def literals(source):
    result = {}
    for statement in ast.parse(source).body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in ("PROGRAM", "EDIT"):
                    result[target.id] = ast.literal_eval(statement.value)
    return result


def verify_staged_source(stage, predecessor_source):
    previous = literals(predecessor_source)
    new = literals((stage / "prepare.py").read_bytes())
    require(new["PROGRAM"] == previous["PROGRAM"], "identical rounded axes emitter and paid-size decoder")
    require(new["EDIT"]["grades.py"] == previous["EDIT"]["grades.py"], "identical paid grade order and split count")
    installation = dict(new["EDIT"]["installations.py"])
    require("Q(1097317122991, 2**48)" in installation.values(), "installed trial literal")
    require('TERMINAL = Profile((35327, 561325), 680000, Q(".00389821005"))' in installation.values(),
            "installed terminal ranks and rate")
    receipt = dict(new["EDIT"]["receipt.py"])
    require(receipt["positive = GAUSSIAN_C-Q(43,256*num)"] == "positive = GAUSSIAN_C-Q(339,2048*num)",
            "installed debit literal")
    require("assert factor**2048 < 2**339" in receipt.values(), "literal certification of the amended debit")


def peer_limit(result):
    trial = Q(result["gaussian"]["trial"])
    debit = Q(result["gaussian"]["raw_loss"])
    terminal = result["terminal"]
    heights = terminal["ordinary_H"]
    require(heights == [8192, 129414, 524288], "fixed #8057 three stages")
    previous = Q()
    for index, height in enumerate(heights):
        cap = min(Q(".0039"), (249 * (B - Q(11, 8 * height)) + previous) / 250)
        booked = Q(terminal["ordinary_rates"][index])
        if index + 1 < len(heights):
            require(booked == Q(int(cap * 10**21) - 1, 10**21), "exact peer first-stage floor")
        else:
            require(booked == Q(terminal["kappa"]) + 5 * G and booked < cap, "peer signed upper stage")
        previous = booked
    numerical_cap = trial - debit / terminal["numerical_H"]
    require(numerical_cap == Q(terminal["gaussian_rate"]), "exact peer numerical rate")
    numerical_cap -= 5 * G
    ordinary_cap = cap - 5 * G
    require(ordinary_cap < numerical_cap < K, "strictly exceed both installed peer caps")
    return {"ordinary": str(ordinary_cap), "numerical": str(numerical_cap),
            "gain_over_installed_ceiling": str(K - min(ordinary_cap, numerical_cap))}


def operand_count_and_sig(paid, cells, margin, expected):
    require(paid.total() == 564144 and paid[Q(1, 4)] == paid[Q(3, 4)] == 1008,
            "all paid quarters required")
    require(margin == Q(expected["raw_directed_relative_margin"]), "exact directed raw margin")
    rendered = [[str(r), str(k), str(p)] for (r, k), p in sorted(cells.items())]
    require(rendered == expected["transport_cells"], "all 63 exact routing shares")


def check(root, stage):
    for name, digest in STAGED_FIXED.items():
        pin(stage / name, digest)
    dependencies = {path: pin(root / path, digest) for path, digest in PINS.items()}
    scripts = runpy.run_path(str(root / next(iter(PINS))))
    independent = scripts["check"](root)
    expected = json.loads(dependencies["round375/independent/coupling.json"])
    require(independent == expected, "recompute pinned price and all 63 coupling shares")
    verify_staged_source(stage, dependencies["round374/publish/research/p104-compact-rounded-partitions/prepare.py"])
    result_bytes = (stage / "RESULT.json").read_bytes()
    result = json.loads(result_bytes)
    gaussian = result["gaussian"]
    require((gaussian["targets"], gaussian["paid"]) == (105216, 564144), "literal whole inventory")
    require(gaussian["transport_cells"] == 63, "literal complete support count")
    require(gaussian["physical_factor_upper_millionths"] == expected["retimed_factor_upper_in_millionths"],
            "measured factor enclosure agrees")
    require(Q(gaussian["margin"]) == Q(expected["raw_directed_relative_margin"]),
            "literal relative moment replays")
    for tier, rate, height_list, h in (("entry", Q(".00345"), [3000, 3080], 1024),
                                      ("terminal", K, [35327, 561325], 680000)):
        profile = result[tier]
        require(Q(profile["kappa"]) == rate, tier + " signed rate")
        require(profile["binary_H"] == height_list and profile["gaussian_H"] == h, tier + " literal heights")
        require(profile["width_exponents"] == [92 * h0 for h0 in (*height_list, h)], tier + " emitted row logs")
        require(Q(profile["positive_rate"]) == C - DEBIT / h, tier + " funded Gaussian rate")
        require(Q(profile["rates"][-1]) == rate + 5 * G, tier + " loaded ordinary rate")
        require(profile["signed"] == expected[tier]["signed"], tier + " exact 54+4 budget")
    require(result["terminal"]["stock"] == expected["terminal_stock"], "literal stock matches detached calculation")
    require((result["entry_premium"], result["complete_log2_C"]) ==
            (expected["entry_premium_bits"], expected["recurring_clock_log2_upper"]),
            "complete clock, including bounded entry interval")

    census = json.loads((root / "round366/gaussian/receipt.json").read_bytes())["ranks"]
    ht, hp = (Counter({Q(k): n for k, n in census[key].items()}) for key in ("target", "paid"))
    hp[1] += hp.pop(Q(1, 2)) // 2
    target, paid = (scripts["dual_copy"](scripts["base_copy"](hist)) for hist in (ht, hp))
    paid[1] -= 1008
    paid.update({Q(1, 4): 1008, Q(3, 4): 1008})
    margin, cells = scripts["allocate"](C, target, paid)
    operand_count_and_sig(paid, cells, margin, expected)
    damaged = paid.copy()
    damaged[Q(1, 4)] -= 1
    corrupt_margin, corrupt_cells = scripts["allocate"](C, target, damaged)
    require(corrupt_margin > margin, "missing-charge control falsely improves raw score")
    for count, label in ((damaged, "counter"), (paid, "forged counter")):
        try:
            operand_count_and_sig(count, corrupt_cells, corrupt_margin, expected)
        except ValueError:
            pass
        else:
            raise AssertionError("One omitted paid quarter escaped " + label)

    old = C - Q(43, 256 * 680000) - 5 * G
    require(old < K, "original debit rejects strengthened κ")
    return {
        "dependencies_by_path": PINS,
        "literal_dependencies_by_path": {**STAGED_FIXED, "prepare.py": sha256((stage / "prepare.py").read_bytes()).hexdigest(),
                                         "RESULT.json": sha256(result_bytes).hexdigest()},
        "kappa": str(K),
        "known_good_exact_8055_and_R374": True,
        "exact_transport_cells": len(cells),
        "old_debit_rejects_new_claim": True,
        "omitted_one_quarter_rejected_even_with_forged_count": True,
        "peer_exact_head": "cbe847a953b971f9c6c5a0a6661e2008acd29086",
        "peer_installed_caps": peer_limit(json.loads(dependencies[
            "round376/independent/peer8057/RESULT.json"
        ])),
        "scope": "installed price/invoice/shape only, registered signed runtime evidence is separate",
    }


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--literal", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = check(args.inputs, args.literal)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
