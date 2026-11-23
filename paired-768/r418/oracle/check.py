"""Compute the canonical sparse owner and paid-boundary oracle for helper 173."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import runpy
import signal

WORD = "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149"
UPSTREAM_RELAY = "4550e49016c989e96d40bb2951a6d4673fb781a5e39e74354a6472817b38369e"
UPSTREAM_SIGNED = "befc9fb22e975d3fcf6103b64bfd553996686394a334bd05f9e96732c4a09cb3"
SIGNED_RECORD = "316bb1a57ea8aa87fb2b565a4899c9b0b5a64ff1513c89e14a19d83ecd58e8e1"
ODD = 154113755636630124932500335624192000 >> 30
NODE, DONOR = 104493, 94870


def pinned(path, expected):
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"Incorrect pinned input {path.name}")
    return data


def normalized(values, exponent, factor=Q(1)):
    first = min(values)
    pivot = values[first]
    a, b = (factor * Q(x, 2**exponent) for x in pivot)
    phases = {z: j for j, z in enumerate((pivot, (-pivot[1], pivot[0]),
                                         (-pivot[0], -pivot[1]), (pivot[1], -pivot[0])))}
    return {"first": first, "support": len(values), "pivot": [str(a), str(b)],
            "phases": [phases[values[i]] if i in values else -1 for i in range(512)]}


def verify(root, archive):
    relay_path = root / "r411/relay"
    pinned(relay_path / "check.py", UPSTREAM_RELAY)
    relay = runpy.run_path(str(relay_path / "check.py"))
    signal_check = root / "r416/signed/check.py"
    pinned(signal_check, UPSTREAM_SIGNED)
    signed = runpy.run_path(str(signal_check))
    rec = json.loads(pinned(root / "r416/signed/RECEIPT.json", SIGNED_RECORD))["record"]
    source = relay_path / "complex-source"
    manifest = json.loads(pinned(relay_path / "complex-source.json", relay["SOURCE"]))
    for name, digest in manifest.items():
        pinned(source / name, digest)
    _, layout = runpy.run_path(str(source / "verify_split_helpers.py"))["rebuild"]()
    word = json.loads(decompress(pinned(relay_path / "w5669_shortcut5.json.gz", WORD)))
    rows = relay["topology"](word, relay["moves"](word))
    assert rows[NODE] == [[DONOR, "1"]]
    assert all(j < 0 for j, _ in rows[DONOR])
    origins = {~j: Q(s) for j, s in rows[DONOR]}
    expected, main = runpy.run_path(str(source / "verify_component.py"))["expected_columns"](
        layout, len(word["initial"]))
    assert 164 in main and origins[164] == Q(1, 2)
    helper = min(set(origins) - main)
    assert (helper, layout["source_labels"][helper], origins[helper]) == (173, 173, -2)
    initial, terminal = word["initial"][helper], word["final"][helper]
    assert (initial, terminal) == (3, 127)
    assert expected[helper] == {helper: (1, 1)}
    live = {~i: Q(int(i == helper)) for i in range(len(word["initial"]))}
    for row in word["schedule"]:
        live[row] = sum(Q(s) * live[j] for j, s in rows[row] if live[j])
    first = word["first_output"]
    outputs = {j: str(live[first + j]) for j in range(len(word["final"])) if live[first + j]}
    assert outputs == {173: "1"} and live[NODE] == -2

    member = signed["member"]
    outer = member(pinned(archive, signed["ARCHIVE"]),
                   "research/tiered-native-multiplier/source/installer.tar.gz")
    retimed = member(outer, "retimed-source.tar.gz")
    prior = member(retimed, "predecessor/predecessor-8030.tar.gz")
    for name in ("gauss_phase.py", "inputs/review/clifford_exact.py", "inputs/review/native_verify.py"):
        src = prior if name.startswith("inputs/") else outer
        payload = signed["pinned"](member(src, name), signed["PIN"][name])
        module = signed["module"](Path(name).stem, payload)
    engine = module
    compiler = signed["pinned"](member(outer, "phase_atlas.py"), signed["PIN"]["phase_atlas.py"])
    endpoint = signed["one_pair"](compiler, word, initial, terminal)
    assert endpoint["rank"] == 9
    frames = {j: engine.frame(tuple(word["frames"][j]), 9) for j in (3, 127, 365, 529)}
    assert len(frames[3]) == 0
    align = engine.adjoint(engine.monomial(endpoint["right"]))
    pre = align + frames[365] + engine.monomial(rec["right"])
    direct = align + frames[529]
    returned = direct + engine.adjoint(engine.monomial(rec["left"]))
    terminal_actions = align + frames[127] + engine.adjoint(engine.monomial(endpoint["left"]))

    samples = {}
    for kind, width in ((0, 2), (1, 4)):
        cases = []
        for i in range(width):
            seed = (37*i + 11 + 17*kind) % 512
            loan = engine.state(pre, seed)
            after = engine.state(returned, seed)
            final = engine.state(terminal_actions, seed)
            assert after == engine.state(pre + engine.fourier(5), seed)
            assert final == engine.state(engine.fourier(9), seed)
            assert engine.state(terminal_actions + (("phase", 1),), seed) != final
            cases.append({"basis": seed, "before_paid": normalized(*loan),
                          "after_paid_before_left": normalized(*after),
                          "terminal": normalized(*final)})
        samples[str(kind)] = cases
    # The odd producer scale and rational row coefficient multiply the whole
    # field once, whereas column-ray pivots multiply once per column.
    return {"scope": "Exact source-only chart, paid boundary and terminal rays; installed run unvisited",
            "source_label": helper, "initial_terminal_charts": [initial, terminal],
            "relay": NODE, "relay_coefficient": "-2", "pre_child_global_factor": str(-2*ODD),
            "nonmain_cone_origins": len(set(origins) - main), "normalized_terminals": outputs,
            "endpoint_rank": endpoint["rank"], "endpoint_record": endpoint,
            "kind_oracles": samples}


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--archive", type=Path, required=True)
    signal.alarm(30)
    try:
        args = parser.parse_args()
        print(json.dumps(verify(args.root, args.archive), separators=(",", ":")))
    finally:
        signal.alarm(0)
