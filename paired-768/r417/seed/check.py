"""Evaluate the chosen relay's normalized rational row on its exact cone."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
import json
from pathlib import Path
import runpy
import signal


def check(relay):
    prior = runpy.run_path(str(relay / "check.py"))
    pin = prior["authenticate"]
    manifest = json.loads(pin((relay / "complex-source.json").read_bytes(), prior["SOURCE"]))
    source = relay / "complex-source"
    for path, expected in manifest.items():
        pin((source / path).read_bytes(), expected)
    _, layout = runpy.run_path(str(source / "verify_split_helpers.py"))["rebuild"]()
    word = json.loads(decompress(pin((relay / "w5669_shortcut5.json.gz").read_bytes(), prior["GZIP"])))
    moves = prior["moves"](word)
    rows = prior["topology"](word, moves)
    node = 104493
    assert moves[node] == (365, 529) and rows[node] == [[94870, "1"]]
    todo, cone, leaves = [node], set(), set()
    while todo:
        label = todo.pop()
        if label < 0:
            leaves.add(~label)
        elif label not in cone:
            cone.add(label)
            todo.extend(donor for donor, _ in rows[label])
    stock = {~i: {i: Q(1)} for i in leaves}
    for label in word["schedule"]:
        if label not in cone:
            continue
        result = defaultdict(Q)
        for donor, text in rows[label]:
            weight = Q(text)
            for origin, coefficient in stock[donor].items():
                result[origin] += weight * coefficient
        stock[label] = {i: v for i, v in result.items() if v}
    labels = layout["source_labels"]
    controls = {label: labels.index(label) for label in (14, 1544)}
    assert len(cone) + len(leaves) == 275 and len(leaves) == 273
    assert not leaves.intersection(controls.values())
    live = stock[node]
    origin = min(live)
    return dict(scope="One normalized graph row; physical typed execution unrun",
                graph_vertices=len(cone) + len(leaves), computed_rows=len(cone), structural_inputs=len(leaves), nonzero_inputs=len(live),
                first_live=dict(index=origin, label=labels[origin], chart=word["initial"][origin],
                                coefficient=str(live[origin])),
                hosted_zero_controls=controls, relay=node,
                source_word_sha256=prior["GZIP"])


if __name__ == "__main__":
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("--relay", type=Path,
                   default=Path(__file__).resolve().parents[2] / "r411/relay")
    signal.alarm(30)
    try:
        print(json.dumps(check(p.parse_args().relay), indent=2))
    finally:
        signal.alarm(0)
