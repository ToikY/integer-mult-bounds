"""Paired-label elimination for induced four-contact trees. Apache-2.0.

Binary Lagrangian geometry and min-plus elimination are classical.
The three-contact form is recorded in research/independent-centre-triples.
This file adds the induced four-vertex census and the path and claw reductions.
"""

from itertools import combinations


def need(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(rows, width):
    need(1 <= width <= 9 and len(rows) <= 2 * width, "bounded binary basis")
    need(all(0 <= x < 1 << (2 * width) for x in rows), "binary coordinate range")
    pivots = [0] * (2 * width)
    rank = 0
    for value in rows:
        for bit in range(2 * width - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    rank += 1
                    break
    return rank


def neighbours(width):
    """Two distinct neighbours for each nonzero normal, in paired label order."""
    need(1 <= width <= 9, "supported width")
    origin = tuple(1 << (width + j) for j in range(width))
    images = []
    for normal in range(1, 1 << width):
        pivot = (normal & -normal).bit_length() - 1
        for tag in range(2):
            axis = normal | (tag << (width + pivot))
            images.append(tuple(v ^ axis if (v >> width & normal).bit_count() % 2
                                else v for v in origin))
    need(len(images) == 2 * ((1 << width) - 1), "complete paired domain")
    return tuple(images)


def label_distance(left, right):
    if left == right:
        return 0
    return 1 if left // 2 == right // 2 else 2


def transform(values, prefix):
    """Return min_i(values[i] + min(distance(i,k), prefix) - 2), with witnesses."""
    need(4 <= len(values) <= 1022 and len(values) % 2 == 0, "paired label domain")
    need(1 <= prefix <= 9 and all(type(x) is int for x in values), "integer prefix cost")
    pair_minima = []
    for pair in range(len(values) // 2):
        index = min((2 * pair, 2 * pair + 1), key=lambda i: (values[i], i))
        pair_minima.append((values[index], index))
    best_two = sorted(pair_minima)[:2]
    result = []
    for label in range(len(values)):
        other = best_two[0] if best_two[0][1] // 2 != label // 2 else best_two[1]
        options = ((values[label] - 2, label),
                   (values[label ^ 1] - 1, label ^ 1),
                   (other[0] + min(2, prefix) - 2, other[1]))
        result.append(min(options))
    return tuple(result)


def adjacency_from_edges(vertices, edges):
    need(len(vertices) <= 184 and len(edges) <= 264, "bounded source graph")
    adjacency = {v: set() for v in vertices}
    for a, b in edges:
        need(a in vertices and b in vertices and a != b, "internal simple edge")
        need(b not in adjacency[a], "no duplicate internal edge")
        adjacency[a].add(b)
        adjacency[b].add(a)
    return adjacency


def canonical_path(a, b, c, d):
    if b > c:
        return (d, c, b, a)
    return (a, b, c, d)


def paths_from_middle(adjacency, edges):
    found = []
    seen = set()
    for left, right in edges:
        b, c = (left, right) if left < right else (right, left)
        if (b, c) in seen:
            continue
        seen.add((b, c))
        for a in adjacency[b]:
            if a == c:
                continue
            for d in adjacency[c]:
                if d == b or d == a or a in adjacency[c] or d in adjacency[b] or d in adjacency[a]:
                    continue
                found.append((a, b, c, d))
    need(len(found) == len(set(found)), "one orientation for each induced path")
    return set(found)


def paths_from_triples(adjacency):
    found = set()
    for middle in adjacency:
        for left, right in combinations(sorted(adjacency[middle]), 2):
            if right in adjacency[left]:
                continue
            for far in adjacency[right]:
                if far not in (middle, left) and far not in adjacency[middle] and far not in adjacency[left]:
                    found.add(canonical_path(left, middle, right, far))
            for far in adjacency[left]:
                if far not in (middle, right) and far not in adjacency[middle] and far not in adjacency[right]:
                    found.add(canonical_path(far, left, middle, right))
    return found


def induced_stars(adjacency):
    stars = []
    for center in sorted(adjacency):
        for leaves in combinations(sorted(adjacency[center]), 3):
            x, y, z = leaves
            if y not in adjacency[x] and z not in adjacency[x] and z not in adjacency[y]:
                stars.append((center, x, y, z))
    return tuple(stars)


def induced_cycles(adjacency, edges):
    """Induced 4-cycles, once per vertex set, by walking each edge as a side."""
    cycles = set()
    seen = set()
    for left, right in edges:
        b, c = (left, right) if left < right else (right, left)
        if (b, c) in seen:
            continue
        seen.add((b, c))
        for a in adjacency[b]:
            if a == c or a in adjacency[c]:
                continue
            for d in adjacency[c]:
                if d in (b, a) or d in adjacency[b] or d not in adjacency[a]:
                    continue
                cycles.add(tuple(sorted((a, b, c, d))))
    return cycles


def cycles_from_opposites(adjacency):
    """The same induced 4-cycles, recovered from nonadjacent opposite corners."""
    cycles = set()
    vertices = sorted(adjacency)
    for a, c in combinations(vertices, 2):
        if c in adjacency[a]:
            continue
        shared = sorted(adjacency[a] & adjacency[c])
        for b, d in combinations(shared, 2):
            if d not in adjacency[b]:
                cycles.add(tuple(sorted((a, b, c, d))))
    return cycles


def connected_shape_counts(adjacency):
    """Count connected induced 4-vertex subgraphs by degree sequence."""
    counts = {}
    for start in sorted(adjacency):
        ball = {start}
        layer = {start}
        for _ in range(3):
            nxt = set()
            for vertex in layer:
                nxt |= adjacency[vertex]
            layer = nxt - ball
            ball |= layer
        need(len(ball) <= 40, "radius-3 ball capacity")
        others = [vertex for vertex in ball if vertex > start]
        need(len(others) <= 24, "ball combination capacity")
        for triple in combinations(others, 3):
            group = (start, *triple)
            members = set(group)
            seen = {start}
            stack = [start]
            while stack:
                vertex = stack.pop()
                for nxt in adjacency[vertex]:
                    if nxt in members and nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)
            if len(seen) != 4:
                continue
            degrees = tuple(sorted(sum(1 for nxt in adjacency[vertex] if nxt in members)
                                    for vertex in group))
            edges = sum(degrees) // 2
            key = (edges, degrees)
            counts[key] = counts.get(key, 0) + 1
    return counts


def path_minimum(first, second, third, fourth, prefix):
    need(len(first) == len(second) == len(third) == len(fourth), "equal path domains")
    left = transform(first, prefix)
    width = len(first)
    g = tuple(second[k] + left[k][0] for k in range(width))
    middle = transform(g, prefix)
    h = tuple(third[l] + middle[l][0] for l in range(width))
    right = transform(h, prefix)
    value, end = min((fourth[m] + right[m][0], m) for m in range(width))
    third_label = right[end][1]
    second_label = middle[third_label][1]
    first_label = left[second_label][1]
    return value, (first_label, second_label, third_label, end)


def star_minimum(center, first, second, third, prefix):
    need(len(center) == len(first) == len(second) == len(third), "equal star domains")
    leaves = (transform(first, prefix), transform(second, prefix), transform(third, prefix))
    width = len(center)
    value, label = min((center[k] + leaves[0][k][0] + leaves[1][k][0] + leaves[2][k][0], k)
                       for k in range(width))
    return value, (label, leaves[0][label][1], leaves[1][label][1], leaves[2][label][1])
