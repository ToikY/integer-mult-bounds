#!/usr/bin/env python3
"""Two-round reuse of one typed-H inventory on the ell=2 witness."""

import hashlib
import importlib.util
import json
from pathlib import Path

import stock

ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "research" / "typed-actual-width-physical-h" / "physical_h.py"
SOURCES_PATH = Path(__file__).resolve().parent / "SOURCES.json"
TOKEN = "PASS_TWO_ROUND_CUBE_STOCK"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def rejected(call, reason):
    try:
        call()
    except ValueError as error:
        need(str(error) == reason, "unexpected rejection: " + str(error))
        return reason
    raise ValueError("missing rejection: " + reason)


def load_engine():
    raw = ENGINE_PATH.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    pinned = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    rows = [row for row in pinned["files"] if row["path"].endswith("physical_h.py")]
    need(len(rows) == 1, "engine pin")
    need(rows[0]["sha256"] == digest, "engine sha256")
    need(rows[0]["usage"] == "input", "engine usage")
    spec = importlib.util.spec_from_file_location("typed_actual_width_physical_h", ENGINE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cube_for(ell, slots, salt):
    records = 1 << len(slots)
    coeffs = 1 << ell
    rows = []
    for x in range(records):
        row = []
        for j in range(coeffs):
            real = ((17 * x + 5 * j + 3 + salt) % 7) - 3
            imag = ((11 * x + 7 * j + 2 + 3 * salt) % 7) - 3
            row.append((real, imag))
        rows.append(row)
    return rows


def oneshot(engine, ell, flags, k, p, h, cube):
    machine = engine.TypedActualWidthH(ell, flags, k, p)
    return machine.run(cube, h, source_order="physical")


def check_schedule(engine, ell, flags, k, p, rounds):
    expected = []
    for h, cube in rounds:
        decoded, ledger, info = oneshot(engine, ell, flags, k, p, h, cube)
        expected.append((decoded, ledger, info))
    report = stock.run_schedule(engine, ell, flags, k, p, rounds)
    need(len(report["rounds"]) == len(rounds), "round count")
    footprint = report["footprint"]
    need(report["inventory_cells"] == footprint["cells"] == footprint["formula_cells"],
         "simultaneous cells")
    need(report["inventory_cells"] < 2 * footprint["formula_cells"],
         "one inventory is below two retained footprints")
    for index, ((h, cube), row) in enumerate(zip(rounds, report["rounds"])):
        decoded, ledger, info = expected[index]
        need(row["h"] == h, "round height")
        need(row["decoded"] == decoded, "tensor")
        need(row["ledger"] == ledger, "ledger")
        need(row["info"]["selected_bits"] == info["selected_bits"], "selected bits")
        need(row["scratch_blank"], "scratch blank")
        need(not row["consumer_blank"], "consumer retained before the next reset")
        need(row["source_cells"] == engine._presented_cells(cube, info["packet_width"]),
             "borrowed source")
        if index == 0:
            need(row["reset"] is None, "no reset before the first round")
        else:
            for name in ("root", "consumer"):
                bill = stock.blank_bill(footprint["lengths"][name])
                need(row["reset"][name] == bill, "reset bill " + name)
    return report


def check_witness(engine):
    ell, flags, k, p = 2, (False,), 1, 4
    machine = engine.TypedActualWidthH(ell, flags, k, p)
    need(machine.levels == (0,), "short-axis witness has one layout round")
    need(machine.matched_bits(0) == (0,), "selected bit")
    cubes = [cube_for(ell, machine.original, salt) for salt in (0, 4)]
    need(cubes[0] != cubes[1], "distinct presentations")
    report = check_schedule(engine, ell, flags, k, p, [(0, cubes[0]), (0, cubes[1])])
    need(report["footprint"]["cells"] == 624, "witness footprint")
    need(report["rounds"][0]["decoded"] != report["rounds"][1]["decoded"], "second presentation")
    need(report["rounds"][0]["ledger"] == report["rounds"][1]["ledger"],
         "data-independent bill")
    fresh = engine.TypedActualWidthH(ell, flags, k, p)
    fresh.run(cubes[0], 0, source_order="physical")
    rejected(lambda: fresh.run(cubes[1], 0, source_order="physical"), "one-shot physical H")
    bad = [[(17, 0)] * (1 << ell) for _ in range(1 << len(machine.original))]
    rejected(
        lambda: stock.run_schedule(engine, ell, flags, k, p, [(0, bad)]),
        "unit disk",
    )
    return {
        "ell": ell,
        "flags": list(flags),
        "k": k,
        "p": p,
        "cells": report["footprint"]["cells"],
        "lengths": report["footprint"]["lengths"],
        "rounds": 2,
        "ledger": report["rounds"][0]["ledger"],
        "reset": report["rounds"][1]["reset"],
    }


def check_two_heights(engine):
    ell, flags, k, p = 2, (True,), 1, 4
    machine = engine.TypedActualWidthH(ell, flags, k, p)
    need(machine.levels == (1, 0), "long-axis ell=2 has two heights")
    cube = cube_for(ell, machine.original, 0)
    rounds = [(h, cube) for h in machine.levels]
    report = check_schedule(engine, ell, flags, k, p, rounds)
    need(report["footprint"]["cells"] == 1248, "two-height footprint")
    need(report["rounds"][0]["info"]["selected_bits"] == (1,), "height 1 bit")
    need(report["rounds"][1]["info"]["selected_bits"] == (0,), "height 0 bit")
    need(report["rounds"][0]["decoded"] != report["rounds"][1]["decoded"], "distinct heights")
    return {
        "flags": list(flags),
        "cells": report["footprint"]["cells"],
        "selected_bits": [list(row["info"]["selected_bits"]) for row in report["rounds"]],
    }


def main():
    engine = load_engine()
    witness = check_witness(engine)
    heights = check_two_heights(engine)
    need(witness["cells"] * 2 == 1248, "two retained witness inventories")
    need(heights["cells"] == 2 * witness["cells"], "record doubling")
    print(TOKEN)
    print(json.dumps({"witness": witness, "two_heights": heights}, sort_keys=True))


if __name__ == "__main__":
    main()
