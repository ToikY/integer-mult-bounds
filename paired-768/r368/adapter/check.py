"""Verify the exact return adapter at the two reduced Gaussian split sites."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from textwrap import dedent
import ast
import importlib
import inspect
import json
import runpy
import sys
import tempfile

OLD = b"SMALL_SPLITS = 1008\n"
NEW = b"SMALL_SPLITS = 1006\n"
EXPECTED = {
    1592: (("return", 9977, 0, 91990), (64, 445)),
    1593: (("return", 9977, 0, 91966), (59, 447)),
}


def sha(data):
    return sha256(data).hexdigest()


def partition_ok(job, halves):
    return (
        all(half.owner is job.owner for half in halves)
        and halves[0].axes + halves[1].axes == job.axes
        and len(set(halves[0].axes) & set(halves[1].axes)) == 0
    )


def check(wrapper, variant, temporary):
    price = runpy.run_path(str(Path(__file__).parents[1] / "primary" / "price.py"))
    base = price["restore_fixed_carrier"](wrapper, temporary / "source")
    old_adapter = (base/"retimed_supplier.py").read_bytes()
    new_adapter = (variant/"retimed_supplier.py").read_bytes()
    assert old_adapter.count(OLD) == 1 and old_adapter.replace(OLD, NEW) == new_adapter

    sys.path.insert(0, str(base))
    installed = temporary / "installed"
    importlib.import_module("bootstrap").install(installed)
    sys.path.insert(0, str(installed))
    supplier = importlib.import_module("retimed_supplier")
    complex_source = importlib.import_module("strong_complex")
    graph, layout = complex_source.load_changed(installed / "inputs")
    tagged = supplier.word(graph, layout)
    moves = {node:(left,right) for node,left,right in graph["moves"]}
    unit_sites = [i for i,label in enumerate(tagged.paid) if label.rank == 1]
    assert unit_sites[1006:1008] == list(EXPECTED)
    for index, (label, frames) in EXPECTED.items():
        assert (tagged.paid[index].tag, tagged.paid[index].rank) == (label,1)
        assert moves[label[-1]] == frames

    native_source = dedent(inspect.getsource(supplier.ComplexRaw.graph))
    graph_tree = ast.parse(native_source)
    moving = next(n for n in ast.walk(graph_tree) if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "node in a.moves")
    n = [ast.unparse(x) for x in moving.body]
    assert n == [
        "rank, right, left = a.factors[a.moves[node]]",
        "self.chart(value, right, centers, cols)",
        "token = self.scratch(value)",
        "yield (('return', clock, call, node), self.Job(token, self.axis_list(cols, range(rank))))",
        "value = self.fields.pop(token)",
        "self.chart(value, left, centers, cols)",
    ]
    native_adapter = dedent(inspect.getsource(supplier.Raw.native))
    adapter_tree = ast.parse(native_adapter)
    split = next(x for x in ast.walk(adapter_tree) if isinstance(x, ast.If)
                 and "splits < SMALL_SPLITS" in ast.unparse(x.test))
    assert [ast.unparse(x) for x in split.body] == [
        "yield job.select(range(width // 2))",
        "yield job.select(range(width // 2, width))",
        "splits += 1",
    ]
    assert [ast.unparse(x) for x in split.orelse] == ["yield job"]
    widths = (2, 4, 6, 14, 128)
    checked = 0
    for label, _ in EXPECTED.values():
        for width in widths:
            token = (label, object())
            contiguous = supplier.ComplexRaw.axis_list(width, range(1))
            original = supplier.Job(token, contiguous)
            # The second sequence verifies selection of arbitrary ordered basis positions.
            unusual = supplier.Job(token, tuple(7*k+3 for k in reversed(contiguous)))
            for job in (original, unusual):
                half = width//2
                parts = (job.select(range(half)),job.select(range(half,width)))
                assert partition_ok(job, parts)
                dropped = parts[1].select(range(half-1))
                swapped = supplier.Job(object(), parts[1].axes)
                assert not partition_ok(job, (parts[0], dropped))
                assert not partition_ok(job, (parts[0], swapped))
                assert not partition_ok(job, tuple(reversed(parts)))
                checked += 1

    return {
        "adapter_pins": {"old": sha(old_adapter), "new": sha(new_adapter)},
        "checked_samples": checked,
        "widths": widths,
        "graph_method_sha256": sha(native_source.encode()),
        "local_checks": {"ordered_partition": True, "same_owner": True,
                         "right_before_yield_left_after_return": True},
        "negative_controls": ["dropped axis", "different owner", "reordered halves"],
        "sites": [{"clock": c, "tag": tag, "source_dest_frames": frames}
                  for c,(tag,frames) in EXPECTED.items()],
        "scope": "adapter boundary proof and finite Job checks; production transport replays separate",
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--fixed-carrier", type=Path, required=True)
    parser.add_argument("--variant", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="gaussian-split-adapter-") as root:
        receipt = check(args.fixed_carrier.resolve(),args.variant.resolve(),Path(root))
    with args.out.open("x") as handle:
        json.dump(receipt,handle,indent=2,sort_keys=True)
        handle.write("\n")
