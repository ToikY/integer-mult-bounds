#!/usr/bin/env python3
"""Independent check of the #5718 input/output functionals and cleanup order.

The checker does not import the predecessor constructor, caller, native maps
or pricing adapter. It replays the pinned source and final words.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
"""
import gzip
import json
import tarfile
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR = ROOT / "research" / "p104-two-boundary-helper-split"
SOURCE_MEMBER = "research/p104-temporal-updates/WORD.json.gz"
SOURCE_SHA = "32adce6656e49aa020d3e6317f1c45c11fccadeeb67a8d506172d101703d2138"
WORD_SHA = "a1c8277189a811546bdc7b147d72e6a594504ff9585c9bf59a5681aa873abb01"
CUT = 14330
PIVOT = 708
PARTNER = 154
FRESH = 743
ANCHOR = ["ADD", FRESH, 146, "1/2", 127]
EARLY = [
    ["ADD", 126, FRESH, "2", 127],
    ["ADD", 188, FRESH, "-2", 127],
    ["ADD", FRESH, 146, "-1/2", 127],
]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_gzip(path):
    with gzip.open(path, "rb") as handle:
        return json.loads(handle.read())


def load_source():
    with tarfile.open(PREDECESSOR / "inputs" / "pr5713-source.tar") as archive:
        member = archive.extractfile(SOURCE_MEMBER)
        need(member is not None, "PR5713 source word is missing from the archive")
        return json.loads(gzip.decompress(member.read()))


def combine(left, right, coefficient):
    for index, value in tuple(right.items()):
        updated = left.get(index, Fraction(0)) + coefficient * value
        if updated:
            left[index] = updated
        else:
            left.pop(index, None)


def subtract(left, right):
    result = dict(left)
    combine(result, right, Fraction(-1))
    return result


def scale(row, coefficient):
    return {index: coefficient * value for index, value in row.items() if coefficient * value}


def apply(rows, event):
    operation, destination = event[:2]
    if operation == "MOVE":
        return
    if operation in ("INIT", "CLEAR"):
        rows[destination] = {}
    elif operation == "SCALE":
        rows[destination] = {index: Fraction(event[-2]) * value for index, value in rows[destination].items()}
    else:
        if operation == "COPY":
            rows[destination] = {}
        combine(rows[destination], rows[event[2]], Fraction(event[-2]))


def replay(word, program):
    width = word["public"] + word["owned_fields"]
    rows = [{index: Fraction(1)} for index in range(width)]
    for event in program:
        apply(rows, event)
    return rows


def endpoint_failures(word, program):
    rows = replay(word, program)
    live = set(word["live"])
    failures = []
    for index, row in enumerate(rows):
        expected = {index: Fraction(1)} if index < word["public"] else {}
        if index - 112 in live:
            expected[index - 112] = Fraction(1)
        if row != expected:
            failures.append(index)
    return failures


def fractions(mapping):
    return {int(index): Fraction(value) for index, value in mapping.items()}


def input_functionals(source):
    need(sha256(canonical(source)).hexdigest() == SOURCE_SHA, "Pinned PR5713 canonical source")
    need(source["program"][CUT] == ["MOVE", 119, 602, 684, False], "Pinned cut event")
    width = source["public"] + source["owned_fields"]
    rows = [{index: Fraction(1)} for index in range(width)]
    for event in source["program"][:CUT + 1]:
        apply(rows, event)
    carrier = dict(rows[PIVOT])
    combine(carrier, rows[PARTNER], Fraction(1, 2))
    nuisance = dict(carrier)
    combine(nuisance, {PIVOT: Fraction(1)}, Fraction(-1))
    half_partner = scale(rows[PARTNER], Fraction(1, 2))
    return carrier, nuisance, half_partner


def published_schedule(word):
    program = word["program"]
    need(program.count(ANCHOR) == 1, "The 146 correction has one live version")
    position = program.index(ANCHOR)
    need(position == 17523, "The 146 correction stays at event 17523")
    need(program[position + 1:position + 4] == EARLY, "Early cleanup keeps the published order")
    need(program.count(EARLY[0]) == program.count(EARLY[1]) == program.count(EARLY[2]) == 1,
         "Each early cleanup operation occurs once")
    for event in program[position + 4:]:
        need(not (event[0] in ("ADD", "COPY") and event[2] in (126, 188, FRESH)),
             "No later read of a normalized register")
        need(event[1] != FRESH, "No later write of the new helper")
        if event[1] in (126, 188):
            need(event[0] == "ADD" and event[-1] == 127, "Later 126/188 writes stay frame-127 ADDs")
    return position


def prefix_nuisance(word, nuisance):
    expected = [["ADD", PIVOT, index, str(-value), 3] for index, value in sorted(nuisance.items())]
    expected.extend([["ADD", 126, PIVOT, "-2", 3], ["ADD", 188, PIVOT, "2", 3]])
    need(word["program"][:len(expected)] == expected, "Frame-3 prefix implements the input nuisance")


def main():
    source = load_source()
    word = load_gzip(PREDECESSOR / "WORD.json.gz")
    witness = json.loads((PREDECESSOR / "WITNESS.json").read_text(encoding="utf-8"))
    need(sha256(canonical(word)).hexdigest() == WORD_SHA, "Pinned final word")
    need(word["public"] == 744 and word["owned_fields"] == 9, "Published inventory")
    carrier, nuisance, half_partner = input_functionals(source)
    need(carrier.get(PIVOT) == 1 and PIVOT not in nuisance, "Input carrier has pivot coefficient 1")
    main_inputs = set(source["live"]) | {index + 112 for index in source["live"]}
    need({index: carrier[index] for index in carrier if index in main_inputs} ==
         {PARTNER: Fraction(1, 4), 217: Fraction(1, 4)},
         "Input carrier reads only the stated main pair")
    need(half_partner not in ({}, nuisance), "The output shift is a nonzero covector")
    position = published_schedule(word)
    prefix_nuisance(word, nuisance)
    state = replay(word, word["program"][:position + 1])
    output = subtract({FRESH: Fraction(1)}, state[FRESH])
    need(FRESH not in output and output == subtract(nuisance, half_partner),
         "Output nuisance equals input nuisance minus the partner covector")
    need(output != nuisance, "The two boundary functionals differ")
    before = state
    published = deepcopy(before)
    for event in EARLY:
        apply(published, event)
    reversed_state = deepcopy(before)
    for event in (EARLY[2], EARLY[0], EARLY[1]):
        apply(reversed_state, event)
    gap = subtract(before[FRESH], {FRESH: Fraction(1)})
    need(gap == scale(output, Fraction(-1)) and gap != {}, "The 146 inverse removes the output nuisance")
    need(subtract(published[126], reversed_state[126]) == scale(gap, 2),
         "Reversing cleanup changes register 126 by twice the output gap")
    need(subtract(published[188], reversed_state[188]) == scale(gap, -2),
         "Reversing cleanup changes register 188 by twice the output gap")
    need(published[FRESH] == reversed_state[FRESH] == {FRESH: Fraction(1)},
         "Both orders restore the new helper")
    need(endpoint_failures(word, word["program"]) == [], "Published scalar endpoints hold")
    reversed_program = deepcopy(word["program"])
    reversed_program[position + 1:position + 4] = [EARLY[2], EARLY[0], EARLY[1]]
    need(endpoint_failures(word, reversed_program) == [126, 188],
         "Inverse-first cleanup fails exactly registers 126 and 188")
    wrong_sign = deepcopy(word["program"])
    wrong_sign[position + 3] = ["ADD", FRESH, 146, "1/2", 127]
    need(endpoint_failures(word, wrong_sign) == [FRESH],
         "The opposite 146 sign fails only the new helper")
    need(fractions(witness["h"]) == carrier, "Recorded input carrier matches the source replay")
    need(witness["early_cleanup"] == EARLY, "Recorded cleanup order matches the word")
    need(fractions(witness["terminal_full9_cleanup"]) == output,
         "Recorded 118-term output functional matches the replay")
    need(len(carrier) == 88 and len(nuisance) == 87 and len(output) == 118,
         "Carrier, input nuisance and output nuisance keep their term counts")
    print(
        "PASS_P104_BOUNDARY_FUNCTIONALS_DIFFER_AND_CLEANUP_ORDER "
        f"carrier={len(carrier)} input={len(nuisance)} output={len(output)} "
        f"partner={len(half_partner)} reversed=126,188"
    )


if __name__ == "__main__":
    main()
