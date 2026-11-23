"""Exercise source and arithmetic of the seam overlay without native execution."""

from argparse import ArgumentParser
import ast
from dataclasses import dataclass, replace
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import runpy
import tarfile
from tempfile import TemporaryDirectory


def digest(data):
    return sha256(data).hexdigest()


def pinned(path, expected):
    data = path.read_bytes()
    assert digest(data) == expected, path
    return data


def member(bundle, name):
    with tarfile.open(fileobj=BytesIO(bundle)) as archive:
        item = archive.getmember(name)
        assert item.isfile()
        return archive.extractfile(item).read()


def calc_source(data, filename, name, **namespace):
    tree = ast.parse(data)
    function, = (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    exec(compile(ast.Module(body=[function], type_ignores=[]), filename, "exec"), namespace)
    return namespace[name]


@dataclass(frozen=True)
class Profile:
    rank_logs: tuple
    complex_log: int
    kappa: Q
    eta: Q

    @property
    def ordinary(self):
        return self.kappa + Q(5, 10**18)


def run(args):
    patch = runpy.run_path(str(Path(__file__).resolve().parent.parent / "overlay/seam_source.py"))
    original = pinned(args.composed / "check_stage_seam.py", patch["SOURCE_SHA256"])
    record = json.loads(pinned(args.composed / "RESULT.json",
                               "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6"))
    archive = pinned(args.archive, "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c")
    tiered = "research/tiered-native-multiplier/"
    setup = member(archive, tiered + "source/activation.py")
    outer = member(archive, tiered + "source/outer_budget.py")
    assert digest(setup) == "6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b"
    assert digest(outer) == "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02"
    source = {}
    exec(compile(setup, "activation.py", "exec"), source)
    exec(compile(outer, "outer_budget.py", "exec"), source)
    entry, term = (record[key] for key in ("entry", "terminal"))
    installer = member(archive, tiered + "source/installer.tar.gz")
    retimed = member(installer, "retimed-source.tar.gz")
    prior = member(retimed, "predecessor/predecessor-8030.tar.gz")
    staged = member(prior, "inputs/triangular/staged_carriers.py")
    geometry = member(prior, "linear_geometry.py")
    assert digest(staged) == "6c925ae4b39dc9999ac5891d1a27dcbb38e129a36e1473b2b418f27a806b6fc4"
    assert digest(geometry) == "6628fcddf1eed2ffa39c2d3256d79577b950e04c4a688161a66ba92baa3fb7c2"
    entrance_logs = calc_source(staged, "staged_carriers.py", "entrance_logs",
                                ceiling_ratio=lambda a, b: -(-a // b), RANK_LOGS=())
    connected_exponent = calc_source(geometry, "linear_geometry.py", "connected_exponent",
                                     ceil_log2=source["ceil_log2"])
    terminal = Profile(tuple(term["ordinary_H"]), term["numerical_H"], Q(".003900857269150"), Q(1, 256))
    source.update(
        Q=Q, replace=replace, entrance_logs=entrance_logs,
        ENTRY=Profile(tuple(entry["ordinary_H"]), entry["numerical_H"], Q(entry["kappa"]), Q(39, 10000)),
        TERMINAL=terminal, BINARY_C=Q(4391986206293, 2**50), GAUSSIAN_C=Q(17158764376, 2**42),
        activation=lambda p: connected_exponent(entrance_logs(p.rank_logs)[-1], p.complex_log),
    )
    with TemporaryDirectory() as temporary:
        path = Path(temporary) / "check_stage_seam.py"
        path.write_bytes(original)
        patch["patch_stage_checks"](path.parent)
        updated = path.read_bytes()
        path.write_bytes(original + b"\n")
        try:
            patch["patch_stage_checks"](path.parent)
        except ValueError:
            assert path.read_bytes() == original + b"\n"
        else:
            raise AssertionError("Altered predecessor was accepted")

    old, new = ast.parse(original), ast.parse(updated)
    source_functions = lambda tree: {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert all(ast.dump(source_functions(old)[name]) == ast.dump(source_functions(new)[name])
               for name in ("verify_stage", "verify_tape"))
    prefix = source_functions(new)["check"]
    boundary, = (i for i, node in enumerate(prefix.body) if isinstance(node, ast.Assert)
                 and ast.unparse(node).startswith("assert sha256((RUNTIME /"))
    # Stop before the physical archive and native tests, retaining the arithmetic controls.
    prefix.body = [node for node in prefix.body[1:boundary] if not isinstance(node, ast.ImportFrom)]
    prefix.body += [ast.Return(ast.Tuple(elts=[ast.Name(id=n, ctx=ast.Load())
                                              for n in ("controls", "conversion", "late", "old_crossing")],
                                         ctx=ast.Load()))]
    exec(compile(ast.fix_missing_locations(ast.Module(body=[prefix], type_ignores=[])),
                 "arithmetic-only stage check", "exec"), source)
    controls, conversion, late, old_crossing = source["check"]()
    assert len(set(controls)) == len(controls) == 17
    assert "next-displayed-kappa-at-fixed-gaussian-height" in controls
    assert "gaussian-height-minus-one" in controls
    assert conversion == 121121 and late == 85945126845
    return {"incoming_sha256": digest(original), "candidate_sha256": digest(updated),
            "old_guarded_crossing": str(old_crossing), "controls": controls,
            "entry_conversion": conversion, "terminal_bound": late, "physical_functions_unchanged": True,
            "native_and_signed_execution": "unrun"}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--composed", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    print(json.dumps(run(parser.parse_args()), indent=2))
