"""Check the two paid-request reversals on the authenticated native label stream.

The stand-in job tracks ownership, axis identity and order. This finite
pre-build check leaves the nonzero physical transport and outer replay open.
"""
from argparse import ArgumentParser
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import importlib
import json
import runpy
import subprocess
import sys
import tempfile
import time


@dataclass(frozen=True)
class Job:
    owner: tuple
    axes: range

    def select(self, indices):
        assert isinstance(indices, range) and indices.step == 1
        return Job(self.owner, self.axes[indices.start:indices.stop])


class Native:
    def __init__(self, tagged):
        self.tagged = tagged

    def raw(self, _inputs, width):
        for clock, label in enumerate(self.tagged.paid):
            start = 3 * clock + 1
            axes = range(start, start + 3 * width * label.rank, 3)
            yield (label.tag, Job((width, clock), axes))


def check(wrapper, expected, temporary):
    price = runpy.run_path(str(Path(__file__).with_name("price.py")))
    source = price["restore_fixed_carrier"](wrapper, temporary / "source")
    sys.path.insert(0, str(source))
    boot = importlib.import_module("bootstrap")
    work = temporary / "installed"
    boot.install(work)
    sys.path.insert(0, str(work))
    supplier = importlib.import_module("retimed_supplier")
    tagged = supplier.word(*importlib.import_module("strong_complex").load_changed(work/"inputs"))

    width = 4
    initial = [
        Job(("input", j), range(scale * label.rank * width))
        for scale in supplier.SCALES for j, label in enumerate(tagged.targets)
    ]
    # Both scales are live simultaneously and each port must be uniquely owned.
    initial = [Job(("input", j), job.axes) for j, job in enumerate(initial)]
    machine = supplier.Raw(tagged, Native(tagged))
    predecessor = machine.native(initial, width)
    successor = machine.native(initial, width)
    sentinel = object()

    def take_once(program, n):
        supplier.SMALL_SPLITS = n
        return next(program, sentinel)

    expected_changed = dict(expected["1006_literal_touched_paid_clock_and_tag"])
    changed = {}
    base_count = new_count = 0
    for scale in supplier.SCALES:
        unit_index = 0
        for clock, label in enumerate(tagged.paid):
            before = take_once(predecessor, 1008)
            after = take_once(successor, 1006)
            base_count += 1
            new_count += 1
            if scale == 1 and label.rank == 1:
                unit_index += 1
                if unit_index <= 1006:
                    base_count += 1
                    new_count += 1
                    assert before == after
                    assert take_once(predecessor, 1008) == take_once(successor, 1006)
                    continue
                if unit_index <= 1008:
                    tail = take_once(predecessor, 1008)
                    base_count += 1
                    assert before.owner == after.owner == tail.owner
                    assert list(before.axes) + list(tail.axes) == list(after.axes)
                    assert list(before.axes) + list(before.axes) != list(after.axes)
                    assert len(after.axes) == width and len(set(after.axes)) == width
                    changed[clock] = list(label.tag)
                    continue
            assert before == after and before.owner == (width*scale, clock)
    assert take_once(predecessor, 1008) is sentinel and take_once(successor, 1006) is sentinel
    supplier.SMALL_SPLITS = 1008
    assert changed == expected_changed and (base_count, new_count) == (564144, 564142)
    assert len(initial) == 105216
    return {
        "owners_axis_order_match": True,
        "duplicate_half_control_rejected": True,
        "productive": len(initial),
        "old_paid": base_count,
        "new_paid": new_count,
        "column_width": width,
        "changed_clock_and_tag": sorted(changed.items()),
        "new_trial": str(Fraction(expected["1006_fixed_c"])),
        "scope": "authenticated retimed emitter using jobs with exact symbolic ownership and ordered axes",
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--fixed-carrier", type=Path, required=True)
    parser.add_argument("--price", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        with tempfile.TemporaryDirectory(prefix="check-emitter-") as temporary:
            receipt = check(args.fixed_carrier.resolve(), json.loads(args.price.read_bytes()), Path(temporary))
        with args.out.open("x") as handle:
            json.dump(receipt, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        start = time.monotonic()
        proc = subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=15)
        print(f"exit={proc.returncode} elapsed={time.monotonic()-start:.3f}s")
        raise SystemExit(proc.returncode)
