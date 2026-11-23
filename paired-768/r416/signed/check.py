"""Check all exact Gaussian columns of one compensated relay and its adjoint."""
from argparse import ArgumentParser
import ast
from hashlib import sha256
from io import BytesIO
import gzip
import json
from pathlib import Path
import signal
import sys
from tarfile import open as tar_open
from types import ModuleType

ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
WORD = "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149"
PIN = {
    "phase_atlas.py": "6425300f5d3d984290496df0ff411aca6879869b285298e553cd4d94ba02faa7",
    "gauss_phase.py": "a087d0dd5f448d39e6a2dfdc876be7238b75a55b8f9c350eda3907a1865bcb56",
    "inputs/review/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "inputs/review/clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
}


def pinned(data, expected):
    assert sha256(data).hexdigest() == expected, expected
    return data


def member(data, name):
    with tar_open(fileobj=BytesIO(data)) as archive:
        item = archive.getmember(name)
        assert item.isfile()
        return archive.extractfile(item).read()


def module(name, contents):
    result = ModuleType(name)
    sys.modules[name] = result
    exec(compile(contents, f"{name}.py", "exec"), vars(result))
    return result


def one_pair(source, word, old, new):
    """Reuse the exact producer's factorization with only one case selected."""
    tree = ast.parse(source)
    catalogue, = (node for node in tree.body
                  if isinstance(node, ast.FunctionDef) and node.name == "catalogue")
    start, = (index for index, node in enumerate(catalogue.body)
              if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "xports")
    catalogue.body = catalogue.body[:start] + ast.parse("return lower(back(a).then(frame(b)))").body
    env = {"a": old, "b": new}
    exec(compile(ast.fix_missing_locations(tree), "phase_atlas.py", "exec"), env)
    return env["catalogue"](word, {"frames": word["frames"]})


def timeout(_signum, _frame):
    raise TimeoutError("The single-relay test hit its 30 second cap")


def run(word_path, archive_path):
    outer = pinned(archive_path.read_bytes(), ARCHIVE)
    installer = member(outer, "research/tiered-native-multiplier/source/installer.tar.gz")
    retimed = member(installer, "retimed-source.tar.gz")
    prior = member(retimed, "predecessor/predecessor-8030.tar.gz")
    for path in ("gauss_phase.py", "inputs/review/clifford_exact.py"):
        root = prior if path.startswith("inputs/") else installer
        module(Path(path).stem, pinned(member(root, path), PIN[path]))
    proof = module("native_verify", pinned(member(prior, "inputs/review/native_verify.py"),
                                          PIN["inputs/review/native_verify.py"]))
    source = pinned(member(installer, "phase_atlas.py"), PIN["phase_atlas.py"])
    word = json.loads(gzip.decompress(pinned(word_path.read_bytes(), WORD)))
    a, middle, b = 365, 1028, 529
    node = 104493
    assert {i: (x, y) for i, x, y in word["moves"]}[node] == (a, b)
    assert dict(word["forms"])[node] == [[94870, "1"]]
    frames = {i: proof.frame(tuple(word["frames"][i]), 9) for i in (a, middle, b)}
    rec = one_pair(source, word, a, b)
    assert rec["rank"] == 5
    direct = proof.recipe(rec)
    reference = proof.adjoint(frames[a]) + frames[b]
    before = proof.adjoint(frames[a]) + frames[middle] + proof.adjoint(frames[middle]) + frames[b]
    reverse = proof.adjoint(direct)
    backward = proof.adjoint(frames[b]) + frames[a]
    for col in range(512):
        assert proof.state(direct, col) == proof.state(before, col) == proof.state(reference, col), col
        assert proof.state(reverse, col) == proof.state(backward, col), col
    wrong_phase = direct + (("phase", 1),)
    wrong_reverse = (proof.adjoint(proof.monomial(rec["left"])) + proof.fourier(5)
                     + proof.adjoint(proof.monomial(rec["right"])))
    assert proof.tableau(wrong_phase) == proof.tableau(direct)
    assert proof.state(wrong_phase) != proof.state(reference)
    assert any(proof.state(wrong_reverse, j) != proof.state(backward, j) for j in range(512))
    return {
        "base_head": "c20a08dc0a79a989e3515068560d5da371c0a2a8",
        "word_sha256": WORD,
        "archive_sha256": ARCHIVE,
        "source_sha256": PIN,
        "node": node, "charts": [a, middle, b], "rank": rec["rank"], "record": rec,
        "exact_columns_forward": 512, "exact_columns_adjoint": 512,
        "negative_controls": ["quarter-turn global phase", "forward Fourier in adjoint wrapper"],
        "scope": "One nine-axis compiled relay and its adjoint on the exact Gaussian dyadic grid.",
        "remaining": ["other four relay roles", "physical signed calls and owner restoration",
                      "lift to column bundles and spectator routes", "registered replay"],
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    assert __debug__
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    print(json.dumps(run(args.word, args.archive), indent=2))
    signal.alarm(0)
