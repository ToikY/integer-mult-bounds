"""Recheck the four remaining exact direct chart factors and their adjoints."""

from argparse import ArgumentParser
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path
import runpy
import signal

GRAPH_CHECK_SHA = "4550e49016c989e96d40bb2951a6d4673fb781a5e39e74354a6472817b38369e"
SIGNED_CHECK_SHA = "befc9fb22e975d3fcf6103b64bfd553996686394a334bd05f9e96732c4a09cb3"
PREVIOUSLY_CHECKED = 104493


def words(graph, source, word_path):
    authenticate, unique = graph["authenticate"], graph["unique"]
    raw = authenticate(word_path.read_bytes(), graph["GZIP"])
    git_blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert git_blob == graph["BLOB"]
    word = json.loads(gzip.decompress(raw), object_pairs_hook=unique)
    pins = json.loads(authenticate((source / "complex-source.json").read_bytes(), graph["SOURCE"]),
                      object_pairs_hook=unique)
    code = source / "complex-source"
    for path, digest in pins.items():
        authenticate((code / path).read_bytes(), digest)
    precursor, layout = runpy.run_path(str(code / "verify_split_helpers.py"))["rebuild"]()
    engine = runpy.run_path(str(code / "verify_bidirectional.py"))
    old, _ = engine["reconstruct"](precursor, engine["read"]("BANK-FACTORS.json.gz"))
    canonical = engine["canonical"]
    assert canonical(old) == graph["PREDECESSOR"] and canonical(word) == graph["WORD"]
    assert canonical(layout) == graph["LAYOUT"]
    assert all(old[key] == word[key] for key in ("initial", "final", "frames", "first_output"))
    return old, word, engine["inspect"].__globals__["frame_span"]


def sources(signed, archive_path):
    pinned, member, module = (signed[key] for key in ("pinned", "member", "module"))
    outer = pinned(archive_path.read_bytes(), signed["ARCHIVE"])
    installer = member(outer, "research/tiered-native-multiplier/source/installer.tar.gz")
    prior = member(member(installer, "retimed-source.tar.gz"), "predecessor/predecessor-8030.tar.gz")
    pins = signed["PIN"]
    for root, name in ((installer, "gauss_phase.py"), (prior, "inputs/review/clifford_exact.py")):
        module(Path(name).stem, pinned(member(root, name), pins[name]))
    name = "inputs/review/native_verify.py"
    proof = module(Path(name).stem, pinned(member(prior, name), pins[name]))
    name = "phase_atlas.py"
    return proof, pinned(member(installer, name), pins[name])


def witness(proof, direct, expected, label):
    for col in range(512):
        if proof.state(direct, col) != proof.state(expected, col):
            return col
    raise AssertionError(f"Never rejected {label}")


def verify_case(proof, lower, word, span, source, node, removed, charts):
    a, middle, b = charts
    widths = [span(word["frames"][k]) for k in charts]
    assert widths[0] < widths[1] < widths[2]
    dims = [len(s).bit_length() - 1 for s in widths]
    r1, r2 = dims[1] - dims[0], dims[2] - dims[1]
    rank = dims[2] - dims[0]
    assert rank == r1 + r2

    frame = {i: proof.frame(tuple(word["frames"][i]), 9) for i in charts}
    factors = [lower(source, word, x, y) for x, y in ((a, middle), (middle, b), (a, b))]
    assert [record["rank"] for record in factors] == [r1, r2, rank]
    first, second, direct = (proof.recipe(record) for record in factors)
    old = first + second
    canonical = proof.adjoint(frame[a]) + frame[b]
    reverse = proof.adjoint(direct)
    old_reverse = proof.adjoint(second) + proof.adjoint(first)
    canonical_reverse = proof.adjoint(frame[b]) + frame[a]
    for col in range(512):
        assert proof.state(direct, col) == proof.state(old, col) == proof.state(canonical, col), (node, col)
        assert proof.state(reverse, col) == proof.state(old_reverse, col) == proof.state(canonical_reverse, col), (node, col)

    wrong_phase = direct + (("phase", 1),)
    assert proof.tableau(wrong_phase) == proof.tableau(direct)
    record = factors[-1]
    wrong_adjoint = (proof.adjoint(proof.monomial(record["left"])) + proof.fourier(rank)
                     + proof.adjoint(proof.monomial(record["right"])))
    return {
        "inserted": node, "removed": removed, "charts": charts, "dimensions": dims,
        "paid_grades": [r1, r2, rank], "forward_columns": 512, "adjoint_columns": 512,
        "quarter_turn_detected_at_column": witness(proof, wrong_phase, canonical, "quarter turn"),
        "wrong_fourier_detected_at_column": witness(proof, wrong_adjoint, canonical_reverse, "wrong Fourier"),
    }


def run(word_path, archive_path, relay, signed_path):
    assert sha256((relay / "check.py").read_bytes()).hexdigest() == GRAPH_CHECK_SHA
    assert sha256(signed_path.read_bytes()).hexdigest() == SIGNED_CHECK_SHA
    graph = runpy.run_path(str(relay / "check.py"))
    signed = runpy.run_path(str(signed_path))
    old, word, span = words(graph, relay, word_path)
    old_moves, moves = map(graph["moves"], (old, word))
    retired = old_moves.items() - moves.items()
    added = moves.items() - old_moves.items()
    assert len(retired) == 10 and len(added) == 5
    old_rows = dict(old["forms"])
    cases = []
    for x, y, a, m, b in graph["RELAYS"]:
        assert (x, (a, m)) in retired and (y, (m, b)) in retired and x in dict(old_rows[y])
        node, = (i for i, pair in added if pair == (a, b))
        if node != PREVIOUSLY_CHECKED:
            cases.append((node, [x, y], [a, m, b]))
    assert [node for node, *_ in cases] == [104489, 104490, 104491, 104492]
    proof, source = sources(signed, archive_path)
    results = [verify_case(proof, signed["one_pair"], word, span, source, *case) for case in cases]
    return {
        "scope": "Four remaining literal chart factors, exact Gaussian dyadic columns; physical runs not performed",
        "head": graph["HEAD"], "archive_sha256": signed["ARCHIVE"], "word_sha256": graph["WORD"],
        "compressed_word_sha256": graph["GZIP"], "word_git_blob": graph["BLOB"],
        "predecessor_word_sha256": graph["PREDECESSOR"], "layout_sha256": graph["LAYOUT"],
        "predecessor_source_manifest_sha256": graph["SOURCE"],
        "source_sha256": signed["PIN"], "r411_check_sha256": GRAPH_CHECK_SHA,
        "r416_check_sha256": SIGNED_CHECK_SHA, "cases": results,
        "status": "PASS_FOUR_RELAY_FACTORS_AND_ADJOINTS",
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--relay-root", type=Path, required=True)
    parser.add_argument("--prior-signed-check", type=Path, required=True)
    args = parser.parse_args()
    signal.alarm(45)
    try:
        print(json.dumps(run(args.word, args.archive, args.relay_root, args.prior_signed_check),
                         indent=2, sort_keys=True))
    finally:
        signal.alarm(0)
