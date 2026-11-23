"""Check the literal price expressions with authenticated receipt inputs."""
from argparse import ArgumentParser
from contextlib import redirect_stdout
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO, StringIO
from math import ceil, isqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import ast
import json
import runpy
import signal
import tarfile

ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
PEER = "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6"
STRICT = "899ce86a0e5ae0455ea6cf97934658b2fd31b81d7111cb2bd636ce10e3e7264d"


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate(path, expected):
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise ValueError(f"Unexpected source {path.name}")
    return raw


def member(data, name):
    with tarfile.open(fileobj=BytesIO(data)) as archive:
        item = archive.getmember(name)
        assert item.isfile()
        return archive.extractfile(item).read()


def take_function(raw, name):
    found, = (node for node in ast.parse(raw).body
              if isinstance(node, ast.FunctionDef) and node.name == name)
    return found


def assignments(body, first, last):
    start, = (index for index, node in enumerate(body)
              if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == first)
    end, = (index for index, node in enumerate(body)
            if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == last)
    assert start < end
    return body[start:end]


def execute(body, namespace):
    exec(compile(ast.Module(body=body, type_ignores=[]), "price-source-slice", "exec"), namespace)


def replay(prepared, corrected, package):
    changes = runpy.run_path(str(Path(__file__).resolve().parents[1] / "overlay/price.py"))
    raw = authenticate(package / "peer8057.tar.gz", ARCHIVE)
    installer = member(raw, "research/tiered-native-multiplier/source/installer.tar.gz")
    retimed = member(installer, "retimed-source.tar.gz")
    predecessor = member(retimed, "predecessor/predecessor-8030.tar.gz")
    strict = member(predecessor, "strict_moment.py")
    assert digest(strict) == STRICT
    source = {"UNIT": 2**112, "isqrt": isqrt, "ceiling": lambda x, y: -(-x // y)}
    execute([take_function(strict, "power_interval")], source)
    peer = json.loads(authenticate(package / "RESULT.json", PEER))
    finite = peer["gaussian"]["finite_loss"]
    with TemporaryDirectory(prefix="r420-price-source-") as path:
        stage = Path(path)
        for name, expected in changes["BASE_PINS"].items():
            original = corrected if name == "receipt.py" else prepared / name
            (stage / name).write_bytes(authenticate(original, expected))
        changes["patch_price"](stage)
        results = {name: (stage / name).read_bytes() for name in changes["BASE_PINS"]}
        # Prove transformed/polluted preimages are rejected before any edit.
        try:
            changes["patch_price"](stage)
        except ValueError:
            assert all((stage / name).read_bytes() == data for name, data in results.items())
        else:
            raise AssertionError("A transformed preimage was accepted")
    namespace = dict(source, Q=Q, DELTA=Q(1, 2**128), POSITIVE_DEBIT=Q(1039701, 2**23),
                     scale=finite["upper_scale"], lower=finite["lower_band"],
                     c=Q(peer["gaussian"]["trial"]), targets={258: 1}, fringe=Q(finite["fringe"]))
    fn = take_function(results["positive_debit.py"], "certify_loss")
    start, = (i for i, n in enumerate(fn.body) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "x_lower")
    execute(fn.body[start:-1], namespace)
    old = Q(finite["upper_factor"])
    assert old == namespace["coarse_factor"]
    lower_failed = dict(namespace, POSITIVE_DEBIT=Q(1039700, 2**23))
    try:
        execute(fn.body[start:-1], lower_failed)
    except AssertionError:
        pass
    else:
        raise AssertionError("Adjacent lower debit was accepted")

    raw = results["independent_price.py"]
    shared = dict(namespace, GRID=2**192, ceil=ceil, LOWER=finite["lower_band"], UPPER_DIVISOR=1724,
                  recipe=SimpleNamespace(ambient=306, targets=SimpleNamespace(histogram={258: 1})))
    execute([take_function(raw, "powers")], shared)
    marker = StringIO()
    with redirect_stdout(marker):
        execute(assignments(take_function(raw, "weighted").body, "delta", "psi_hi"), shared)
    assert marker.getvalue() == "PASS_SHARPER_POSITIVE_PERIOD 257/256 1039701/8388608\n"
    assert shared["upper"] > 1

    terminal = SimpleNamespace(kappa=Q(".003900857312000"), complex_log=208653,
                               positive_stop_denominator=10**18)
    terminal.ordinary = terminal.kappa + Q(5, terminal.positive_stop_denominator)
    receipt_namespace = dict(Q=Q, ceil=ceil, TERMINAL=terminal, DEBIT=Q(1039701, 2**23),
                             ORDINARY_DEBIT=Q(1414404, 2**20),
                             GAUSSIAN_C=Q(peer["gaussian"]["trial"]), BINARY_C=Q(4391986206293, 2**50))
    receipt_slice = assignments(take_function(results["receipt.py"], "check").body,
                                "ordinary_floor", "setup")
    signed, = (index for index, node in enumerate(receipt_slice) if isinstance(node, ast.For))
    execute(receipt_slice[:signed], receipt_namespace)
    assert receipt_namespace["positive_ceiling"] > terminal.kappa
    return {
        "scope": "Literal 112-bit and 192-bit price slices with retained receipt inputs. No installed replay.",
        "upstream_positive_envelope_reproduced": old == namespace["coarse_factor"],
        "next_lower_debit_refused": True,
        "prepared_inputs": changes["BASE_PINS"],
        "transformed_sources": {name: digest(data) for name, data in results.items()},
        "four_aligned_factor": str(namespace["period_upper"]),
        "positive_debit": str(namespace["POSITIVE_DEBIT"]),
        "same_profile_rate": str(terminal.kappa),
        "minimum_funding_heights": [134136243, 208653],
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", required=True, type=Path)
    parser.add_argument("--corrected", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    args = parser.parse_args()
    signal.alarm(30)
    try:
        print(json.dumps(replay(args.prepared, args.corrected, args.package), indent=2))
    finally:
        signal.alarm(0)
