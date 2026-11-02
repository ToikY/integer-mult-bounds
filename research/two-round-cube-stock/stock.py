"""One fixed tape inventory for two rounds of the typed actual-width H.

The predecessor allocates source, scratch, root, consumer and three butterfly
auxiliaries inside each call, then refuses a second call. This schedule keeps
those seven buffers and redirects every allocation back onto them.
"""

from __future__ import annotations

BUFFER_ORDER = ("source", "scratch", "root", "consumer", "low", "high", "paired")


def layout_footprint(engine, ell, flags, k, p):
    """Cell counts for one simultaneous round at this layout's maximum g."""
    machine = engine.TypedActualWidthH(ell, flags, k, p)
    widths = []
    for h in machine.levels:
        bits = machine.matched_bits(h)
        g = len(bits)
        records = 1 << len(machine.physical)
        coeffs = 1 << machine.ell
        work = machine.p + g + 2
        packet = machine.w
        widths.append({
            "h": h,
            "g": g,
            "records": records,
            "coefficients": coeffs,
            "work_width": work,
            "packet_width": packet,
        })
    g = max(row["g"] for row in widths)
    records = widths[0]["records"]
    coeffs = widths[0]["coefficients"]
    work = machine.p + g + 2
    packet = machine.w
    scratch = records * coeffs * 2 * work
    packet_cells = records * coeffs * 2 * packet
    lengths = {
        "source": packet_cells,
        "scratch": scratch,
        "root": packet_cells,
        "consumer": packet_cells,
        "low": (records // 2) * coeffs * 2 * work,
        "high": (records // 2) * coeffs * 2 * work,
        "paired": scratch,
    }
    if tuple(lengths) != BUFFER_ORDER:
        raise ValueError("buffer order")
    total = sum(lengths.values())
    closed = 6 * records * coeffs * (packet + work)
    if total != closed:
        raise ValueError("footprint formula")
    return {
        "levels": tuple(row["h"] for row in widths),
        "rounds": widths,
        "lengths": lengths,
        "cells": total,
        "formula_cells": closed,
    }


def blank_bill(n):
    """Writes and moves of _blank_tape on a head-at-zero tape of length n."""
    if n < 0:
        raise ValueError("tape length")
    return {"write": n, "move": 2 * (n - 1) if n else 0, "read": 0}


class Inventory:
    def __init__(self, engine, lengths):
        self.engine = engine
        self.lengths = dict(lengths)
        self.order = BUFFER_ORDER
        self.tapes = {name: engine.Tape(self.lengths[name]) for name in self.order}
        self.ids = {name: id(self.tapes[name]) for name in self.order}
        self.constructions = len(self.tapes)

    @property
    def cells(self):
        return sum(len(tape.cells) for tape in self.tapes.values())

    def zero_counters(self):
        for tape in self.tapes.values():
            tape.read = 0
            tape.write = 0
            tape.move = 0

    def counter_snapshot(self):
        return {
            name: (tape.read, tape.write, tape.move)
            for name, tape in self.tapes.items()
        }


class _Allocator:
    def __init__(self, inventory):
        self.inventory = inventory
        self.index = 0
        self.extra = 0

    def __call__(self, n):
        if self.index >= len(self.inventory.order):
            self.extra += 1
            raise ValueError("inventory exhausted")
        name = self.inventory.order[self.index]
        tape = self.inventory.tapes[name]
        self.index += 1
        if len(tape.cells) != n:
            raise ValueError("inventory length")
        return tape

    def reset_round(self):
        self.index = 0


def run_schedule(engine, ell, flags, k, p, rounds):
    """Run (h, cube) pairs on one inventory, resetting root and consumer between them.

    rounds must be nonempty. Each cube is presented by the unchanged run path.
    """
    if not rounds:
        raise ValueError("empty schedule")
    footprint = layout_footprint(engine, ell, flags, k, p)
    inventory = Inventory(engine, footprint["lengths"])
    allocator = _Allocator(inventory)
    real_tape = engine.Tape
    engine.Tape = allocator
    executed = []
    try:
        for step, (h, cube) in enumerate(rounds):
            if step:
                before = inventory.counter_snapshot()
                for name in ("root", "consumer"):
                    engine._blank_tape(inventory.tapes[name])
                after = inventory.counter_snapshot()
                reset = {}
                for name in ("root", "consumer"):
                    reset[name] = {
                        "read": after[name][0] - before[name][0],
                        "write": after[name][1] - before[name][1],
                        "move": after[name][2] - before[name][2],
                    }
                if any(inventory.tapes["root"].cells) or any(inventory.tapes["consumer"].cells):
                    raise ValueError("previous-output reset")
                if inventory.tapes["root"].head or inventory.tapes["consumer"].head:
                    raise ValueError("reset head")
            else:
                reset = None
            inventory.zero_counters()
            allocator.reset_round()
            machine = engine.TypedActualWidthH(ell, flags, k, p)
            decoded, ledger, info = machine.run(cube, h, source_order="physical")
            if allocator.index != len(BUFFER_ORDER) or allocator.extra:
                raise ValueError("allocation count")
            if inventory.cells != footprint["cells"]:
                raise ValueError("live cells changed")
            if any(id(inventory.tapes[name]) != inventory.ids[name] for name in BUFFER_ORDER):
                raise ValueError("tape identity")
            executed.append({
                "h": h,
                "decoded": decoded,
                "ledger": ledger,
                "info": info,
                "reset": reset,
                "consumer_blank": not any(inventory.tapes["consumer"].cells),
                "root_blank": not any(inventory.tapes["root"].cells),
                "scratch_blank": not any(inventory.tapes["scratch"].cells),
                "source_cells": list(inventory.tapes["source"].cells),
                "consumer_cells": list(inventory.tapes["consumer"].cells),
            })
    finally:
        engine.Tape = real_tape
    return {"footprint": footprint, "inventory_cells": inventory.cells, "rounds": executed}
