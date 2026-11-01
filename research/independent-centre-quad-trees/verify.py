#!/usr/bin/env python3
"""Source-bound independent four-contact tree certificate. Apache-2.0."""

from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import importlib.util
import json
import tempfile

from geometry import (adjacency_from_edges, binary_rank, connected_shape_counts,
                      cycles_from_opposites, induced_cycles, induced_stars,
                      label_distance, need, neighbours, path_minimum,
                      paths_from_middle, paths_from_triples, star_minimum,
                      transform)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EXPECTED_MINIMA = (2, 1, 1, 1, 1, 1, 1, 0, 0)
STAR_MINIMA = (4, 3, 3, 3, 3, 3, 3, 2, 2)
SHARP_PATH = (11013, 11014, 11015, 11016)
SHARP_LABELS = (59, 59, 59, 59)
SHARP_DELTA = (-2, 3, -1, 0, 0, 0, 0, 1, -1, 0)
SHARP_STAR = (11014, 10945, 11013, 11015)
SHARP_STAR_DELTA = (-4, 5, -1, 0, 0, 0, 0, 1, -1, 0)
TRIPLE_ONLY_EDGE = ((11015, 11016, 0, 1),)
QUAD_ONLY_EDGES = ((10947, 11016, 0, 1), (11016, 11017, 0, 1), (11016, 11209, 1, 0))


def authenticate(root):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            actual = sha256((root / row["path"]).read_bytes()).hexdigest()
            need(actual == row["sha256"], "source bytes: " + row["path"])


def source_controls(directory):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [row["path"] for row in sources["files"] if row["usage"] == "input"]
    need(len(inputs) == 4, "complete source-control domain")
    root = directory / "source-controls"
    for name in inputs:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    authenticate(root)
    rejected = 0
    for name in inputs:
        target = root / name
        original = target.read_bytes()
        need(bool(original), "nonempty source input")
        target.write_bytes(original[:-1] + bytes((original[-1] ^ 1,)))
        try:
            authenticate(root)
        except ValueError:
            rejected += 1
        target.write_bytes(original)
    need(rejected == len(inputs), "each altered source rejects")
    return rejected


def load_graph(directory):
    path = ROOT / "research/sol1337-contact-frontier/build_graph.py"
    spec = importlib.util.spec_from_file_location("retained_centre_builder", path)
    need(spec is not None and spec.loader is not None, "source builder loader")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    metadata = builder.build(directory)
    lines = (directory / "center-contact-graph.txt").read_text().splitlines()
    n, f, m, e = map(int, lines[0].split())
    need((n, f, m, e) == (19197, 4429, 145, 34830), "exact graph dimensions")
    need(len(lines) == 1 + n + f + m + e, "complete graph payload")
    nodes = tuple(tuple(map(int, line.split())) for line in lines[1:1 + n])
    lags = tuple(tuple(map(int, line.split())) for line in lines[1 + n:1 + n + f])
    edges = tuple(tuple(map(int, line.split())) for line in lines[1 + n + f + m:])
    validate_graph(nodes, lags, edges)
    need(metadata["inputs"] == 640 and metadata["independent_center_reward"] == 0,
         "retained arbitrary inputs and no independent centre credit")
    need(metadata["helpers"] == {4: 28, 7: 7, 8: 47, 9: 326}, "unchanged helper credits")
    return nodes, lags, edges


def validate_graph(nodes, lags, edges):
    need(len(nodes) == 19197 and len(lags) == 4429 and len(edges) == 34830,
         "bounded original graph")
    need(all(len(row) == 2 and 0 <= row[0] < len(lags) and row[1] in (0, 1)
             for row in nodes), "node domain")
    need(all(len(row) == 9 and all(0 <= x < 1 << 18 for x in row)
             for row in lags), "nine-dimensional frame bases")
    need(lags[0] == tuple(1 << (9 + i) for i in range(9)), "literal empty chart")
    for row in edges:
        need(len(row) == 5, "edge shape")
        a, b, rank, sign, map_id = row
        need(0 <= a < len(nodes) and 0 <= b < len(nodes), "edge endpoints")
        need(0 <= rank <= 9 and sign == 1 and 0 <= map_id < 145, "paid edge domain")
        if nodes[a][1] == 0 or nodes[b][1] == 0:
            need(map_id == 0 and a != b, "identity-map contact edge")
    paid = Counter(r for _, _, r, _, _ in edges if r)
    need(paid == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}, "baseline bill")


def prepare(nodes, lags, edges):
    selected = {i for i, (_, fixed) in enumerate(nodes) if fixed == 0}
    empty = {i for i in selected if nodes[i][0] == 0}
    need(len(selected) == 184 and len(empty) == 176, "contact domains")
    incident = {i: [] for i in empty}
    internal = []
    for a, b, rank, _, _ in edges:
        if a in empty:
            incident[a].append((b, rank))
        if b in empty:
            incident[b].append((a, rank))
        if a in empty and b in empty:
            need(rank == 0, "old internal rank zero")
            if a < b:
                internal.append((a, b))
    need(len(internal) == 256 and all(len(es) == 4 for es in incident.values()),
         "complete empty-chart incident edges")
    adjacency = adjacency_from_edges(empty, internal)
    degrees = Counter(len(adjacency[v]) for v in empty)
    need(dict(degrees) == {2: 16, 3: 160}, "internal degrees are only 2 and 3")
    by_middle = paths_from_middle(adjacency, internal)
    by_triples = paths_from_triples(adjacency)
    need(by_middle == by_triples, "the two induced-path enumerations agree")
    paths = tuple(sorted(by_middle))
    stars = induced_stars(adjacency)
    by_side = induced_cycles(adjacency, internal)
    by_opposite = cycles_from_opposites(adjacency)
    need(by_side == by_opposite, "the two induced-cycle enumerations agree")
    shapes = connected_shape_counts(adjacency)
    need(shapes == {(3, (1, 1, 2, 2)): 716, (3, (1, 1, 1, 3)): 160,
                    (4, (2, 2, 2, 2)): 62},
         "every connected four-contact block is a path, claw or 4-cycle")
    need(len(paths) == 716 and len(stars) == 160 and len(by_side) == 62,
         "constructive census matches the connected classification")
    need(SHARP_PATH in by_middle, "sharp witness is an induced source path")
    images = neighbours(9)
    fids = {nodes[o][0] for es in incident.values() for o, _ in es}
    need(len(fids) == 31, "external frame cache domain")
    ranks = {f: tuple(binary_rank(image + lags[f], 9) - 9 for image in images)
             for f in sorted(fids)}
    unary = {}
    for node in sorted(empty):
        unary[node] = tuple(tuple(sum(min(ranks[nodes[o][0]][k], j) - min(r, j)
                                     for o, r in incident[node]) for k in range(1022))
                            for j in range(1, 10))
    index = {}
    for position, row in enumerate(edges):
        index.setdefault(row[0], []).append(position)
        index.setdefault(row[1], []).append(position)
    return paths, stars, unary, images, index


def direct_delta(block, labels, nodes, lags, edges, images, index):
    changed = {v: images[k] for v, k in zip(block, labels, strict=True)}
    seen = set()
    delta = [0] * 10
    for vertex in block:
        for position in index[vertex]:
            if position in seen:
                continue
            seen.add(position)
            a, b, old, _, map_id = edges[position]
            need(map_id == 0, "literal joint uses identity-map edges")
            left = changed[a] if a in changed else lags[nodes[a][0]]
            right = changed[b] if b in changed else lags[nodes[b][0]]
            new = binary_rank(left + right, 9) - 9
            delta[new] += 1
            delta[old] -= 1
    return tuple(delta)


def full_delta(block, labels, nodes, lags, edges, images):
    changed = {v: images[k] for v, k in zip(block, labels, strict=True)}
    delta = [0] * 10
    for a, b, old, _, map_id in edges:
        if a in changed or b in changed:
            need(map_id == 0, "full scan uses identity-map edges")
            left = changed[a] if a in changed else lags[nodes[a][0]]
            right = changed[b] if b in changed else lags[nodes[b][0]]
            new = binary_rank(left + right, 9) - 9
            delta[new] += 1
            delta[old] -= 1
    return tuple(delta)


def changed_rank_edges(block, labels, nodes, lags, edges, images, index):
    changed = {v: images[k] for v, k in zip(block, labels, strict=True)}
    seen = set()
    rows = []
    for vertex in block:
        for position in index[vertex]:
            if position in seen:
                continue
            seen.add(position)
            a, b, old, _, _ = edges[position]
            left = changed[a] if a in changed else lags[nodes[a][0]]
            right = changed[b] if b in changed else lags[nodes[b][0]]
            new = binary_rank(left + right, 9) - 9
            if new != old:
                rows.append((a, b, old, new))
    return tuple(rows)


def prefix_values(delta):
    return tuple(sum(delta[r] * min(r, j) for r in range(10)) for j in range(1, 10))


def prove_blocks(paths, stars, unary, nodes, lags, edges, images, index):
    minima = [10 ** 9] * 9
    witnesses = [None] * 9
    classes = Counter()
    checked = 0
    for path in paths:
        values = []
        for j in range(1, 10):
            value, labels = path_minimum(*(unary[v][j - 1] for v in path), j)
            need(value >= EXPECTED_MINIMA[j - 1], "induced-path prefix floor")
            delta = direct_delta(path, labels, nodes, lags, edges, images, index)
            literal = prefix_values(delta)
            need(literal[j - 1] == value, "path reduction matches the literal invoice")
            values.append(value)
            checked += 1
            if value < minima[j - 1]:
                minima[j - 1] = value
                witnesses[j - 1] = (path, labels, delta)
        classes[tuple(values)] += 1
    need(tuple(minima) == EXPECTED_MINIMA, "attained componentwise path minima")
    sharp_delta = direct_delta(SHARP_PATH, SHARP_LABELS, nodes, lags, edges, images, index)
    need(sharp_delta == SHARP_DELTA, "named path histogram")
    need(prefix_values(sharp_delta) == EXPECTED_MINIMA, "one path attains every prefix")
    need(full_delta(SHARP_PATH, SHARP_LABELS, nodes, lags, edges, images) == sharp_delta,
         "incident index agrees with the full edge scan")
    triple_edges = changed_rank_edges(SHARP_PATH[:3], SHARP_LABELS[:3], nodes, lags, edges, images, index)
    quad_edges = changed_rank_edges(SHARP_PATH, SHARP_LABELS, nodes, lags, edges, images, index)
    need(tuple(sorted(set(triple_edges) - set(quad_edges))) == TRIPLE_ONLY_EDGE,
         "the fourth contact removes only the shared internal rise")
    need(tuple(sorted(set(quad_edges) - set(triple_edges))) == QUAD_ONLY_EDGES,
         "the fourth contact adds a cancelling rank triple")
    star_minima = [10 ** 9] * 9
    star_witnesses = [None] * 9
    star_classes = Counter()
    star_sharp = None
    for star in stars:
        values = []
        chosen = []
        for j in range(1, 10):
            value, labels = star_minimum(*(unary[v][j - 1] for v in star), j)
            need(value >= STAR_MINIMA[j - 1], "induced-claw prefix floor")
            delta = direct_delta(star, labels, nodes, lags, edges, images, index)
            literal = prefix_values(delta)
            need(literal[j - 1] == value, "claw reduction matches the literal invoice")
            values.append(value)
            chosen.append((labels, delta))
            checked += 1
            if value < star_minima[j - 1]:
                star_minima[j - 1] = value
                star_witnesses[j - 1] = {"prefix": j, "star": star, "labels": labels,
                                         "delta": delta, "prefixes": literal}
        if star_sharp is None and tuple(values) == STAR_MINIMA:
            seen = set()
            for labels, _delta in chosen:
                if labels in seen:
                    continue
                seen.add(labels)
                delta = direct_delta(star, labels, nodes, lags, edges, images, index)
                if prefix_values(delta) == STAR_MINIMA:
                    star_sharp = {"star": star, "labels": labels, "delta": delta}
                    break
        star_classes[tuple(values)] += 1
    need(tuple(star_minima) == STAR_MINIMA, "attained componentwise claw minima")
    need(all(star_minima[j] > EXPECTED_MINIMA[j] for j in range(9)),
         "no claw meets the path floor")
    need(star_sharp is not None, "one claw histogram attains every claw prefix")
    need(SHARP_STAR in stars, "sharp claw is an induced source claw")
    named_star = direct_delta(SHARP_STAR, SHARP_LABELS, nodes, lags, edges, images, index)
    need(named_star == SHARP_STAR_DELTA, "named claw histogram")
    need(prefix_values(named_star) == STAR_MINIMA, "named claw attains every claw prefix")
    return {"prefix_minima": minima,
            "attaining_witnesses": [{"prefix": j, "path": item[0], "labels": item[1],
                                     "delta": item[2]}
                                    for j, item in enumerate(witnesses, 1)],
            "sharp_witness": {"path": SHARP_PATH, "labels": SHARP_LABELS, "delta": sharp_delta},
            "path_prefix_classes": [{"minima": v, "paths": count}
                                    for v, count in sorted(classes.items())],
            "star_prefix_minima": star_minima,
            "star_sharp_witness": star_sharp,
            "star_attaining_witnesses": star_witnesses,
            "star_prefix_classes": [{"minima": v, "stars": count}
                                    for v, count in sorted(star_classes.items())],
            "literal_block_prefixes": checked}


def label_axis(label, width=9):
    normal = label // 2 + 1
    tag = label % 2
    pivot = (normal & -normal).bit_length() - 1
    axis = normal | (tag << (width + pivot))
    origin = tuple(1 << (width + j) for j in range(width))
    image = tuple(v ^ axis if (v >> width & normal).bit_count() % 2 else v for v in origin)
    return normal, tag, axis, image


def controls():
    geometry_cases = 0
    for width in range(1, 6):
        images = neighbours(width)
        for i, left in enumerate(images):
            for k, right in enumerate(images):
                need(binary_rank(left + right, width) - width == label_distance(i, k),
                     "literal paired-neighbour geometry")
                geometry_cases += 1
    normal, tag, axis, image = label_axis(59)
    need((normal, tag, axis) == (30, 1, 1054), "label 59 is normal 30, tag 1, axis 1054")
    need(neighbours(9)[59] == image, "label 59 matches its transvection image")
    transform_cases = 0
    for count in (4, 6, 14):
        for seed in range(11):
            values = tuple(((i + 1) * (seed + 3) + i * i) % 17 - 8 for i in range(count))
            for j in (1, 2, 9):
                actual = transform(values, j)
                brute = tuple(min((values[i] + min(label_distance(i, k), j) - 2, i)
                                  for i in range(count)) for k in range(count))
                need(actual == brute, "transform agrees with exhaustive independent labels")
                transform_cases += 1
    path_cases = 0
    star_cases = 0
    for width in (4, 6):
        for seed in range(4):
            costs = [tuple((seed * (i + 3) + 5 * i * i + offset) % 13 - 6
                           for i in range(width)) for offset in range(4)]
            for j in (1, 2, 9):
                brute_path = min(path_invoice(costs, labels, j)
                                 for labels in product(range(width), repeat=4))
                value, labels = path_minimum(*costs, j)
                need(value == brute_path == path_invoice(costs, labels, j),
                     "path reduction attains the full product")
                path_cases += 1
                brute_star = min(star_invoice(costs, labels, j)
                                 for labels in product(range(width), repeat=4))
                value, labels = star_minimum(*costs, j)
                need(value == brute_star == star_invoice(costs, labels, j),
                     "claw reduction attains the full product")
                star_cases += 1
    rejected = 0
    for values, j in (((0, 1), 1), ((0, 1, 2), 1), ((0, 0, 0, 0), 0),
                      ((0, 0, 0, 0), 10), ((0, 0, 0, 0.5), 1)):
        try:
            transform(values, j)
        except ValueError:
            rejected += 1
    need(rejected == 5, "invalid min-plus inputs reject")
    census = census_fixture()
    return {"geometry_cases": geometry_cases, "transform_oracles": transform_cases,
            "full_product_path_oracles": path_cases, "full_product_star_oracles": star_cases,
            "invalid_input_controls": rejected, "census_fixture": census}


def path_invoice(costs, labels, prefix):
    i, k, l, m = labels
    return (costs[0][i] + costs[1][k] + costs[2][l] + costs[3][m]
            + min(label_distance(i, k), prefix) + min(label_distance(k, l), prefix)
            + min(label_distance(l, m), prefix) - 6)


def star_invoice(costs, labels, prefix):
    k, i, l, m = labels
    return (costs[0][k] + costs[1][i] + costs[2][l] + costs[3][m]
            + min(label_distance(i, k), prefix) + min(label_distance(l, k), prefix)
            + min(label_distance(m, k), prefix) - 6)


def census_fixture():
    vertices = {0, 1, 2, 3, 4, 5, 6, 7}
    path_edges = ((0, 1), (1, 2), (2, 3))
    claw_edges = ((4, 5), (4, 6), (4, 7))
    cycle_edges = ((1, 2), (2, 3), (3, 0), (0, 1))
    chord_edges = ((0, 1), (1, 2), (2, 3), (0, 2))
    path = paths_from_middle(adjacency_from_edges(vertices, path_edges), path_edges)
    need(path == {(0, 1, 2, 3)}, "induced path fixture")
    claw = induced_stars(adjacency_from_edges({4, 5, 6, 7}, claw_edges))
    need(claw == ((4, 5, 6, 7),), "induced claw fixture")
    chord = paths_from_middle(adjacency_from_edges({0, 1, 2, 3}, chord_edges), chord_edges)
    need(chord == set(), "a chord excludes the path")
    cycle = induced_cycles(adjacency_from_edges({0, 1, 2, 3}, cycle_edges), cycle_edges)
    need(cycle == {(0, 1, 2, 3)} == cycles_from_opposites(
        adjacency_from_edges({0, 1, 2, 3}, cycle_edges)), "induced cycle fixture")
    mixed = path_edges + claw_edges
    adjacency = adjacency_from_edges(vertices, mixed)
    need(connected_shape_counts(adjacency) == {(3, (1, 1, 2, 2)): 1, (3, (1, 1, 1, 3)): 1},
         "fixture separates the path and the claw")
    try:
        adjacency_from_edges({0, 1}, ((0, 1), (1, 0)))
    except ValueError:
        return {"fixtures": 6}
    raise ValueError("duplicate internal edge did not reject")


def graph_controls(nodes, lags, edges):
    index = next(i for i, (a, b, _, _, _) in enumerate(edges)
                 if nodes[a][1] == 0 or nodes[b][1] == 0)
    rejected = 0
    for field, value in ((3, -1), (4, 1), (2, 10)):
        bad = list(edges)
        row = list(bad[index])
        row[field] = value
        bad[index] = tuple(row)
        try:
            validate_graph(nodes, lags, bad)
        except ValueError:
            rejected += 1
    need(rejected == 3, "negative charge, changed map and invalid rank reject")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None:
        need(not args.output.resolve().is_relative_to(ROOT), "receipt must stay outside checkout")
    authenticate(ROOT)
    checked = controls()
    with tempfile.TemporaryDirectory(prefix="independent-centre-quad-trees-") as raw:
        nodes, lags, edges = load_graph(Path(raw))
        paths, stars, unary, images, index = prepare(nodes, lags, edges)
        result = prove_blocks(paths, stars, unary, nodes, lags, edges, images, index)
        checked["graph_rejection_controls"] = graph_controls(nodes, lags, edges)
        checked["source_rejection_controls"] = source_controls(Path(raw))
    result.update(status="PASS_INDEPENDENT_CENTRE_QUAD_TREES", paths=len(paths), stars=len(stars),
                  induced_cycles=62, labels=1022, literal_block_prefixes=result["literal_block_prefixes"],
                  controls=checked, claim_type="scoped proof with exact finite certificate",
                  moment_lower_bound="3-2^theta+7^theta-8^theta", theta_domain="0<theta<1")
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                                for p in sorted(HERE.iterdir()) if p.is_file()}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
