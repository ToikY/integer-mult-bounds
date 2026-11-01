#!/usr/bin/env python3
"""Exact checks for the idle-helper span line bound.

PROOF.md is the argument. These controls check the two-update rank identity
by evaluation, the one-line property of a diagonal span, the direct word
with clean helpers, and the eight-call line pigeonhole.
"""

from itertools import combinations, product


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def idempotents(width):
    found = []
    for mask_x in range(1 << width):
        for mask_y in range(1 << width):
            if (mask_x & mask_y).bit_count() % 2 != 1:
                continue
            found.append(
                tuple(
                    tuple(((mask_x >> row) & 1) & ((mask_y >> col) & 1) for col in range(width))
                    for row in range(width)
                )
            )
    return found


def mat_mul(left, right):
    width = len(left)
    return tuple(
        tuple(sum(left[row][mid] * right[mid][col] for mid in range(width)) for col in range(width))
        for row in range(width)
    )


def scaled_update(projector, scalar):
    width = len(projector)
    return tuple(
        tuple((1 if row == col else 0) + scalar * projector[row][col] for col in range(width))
        for row in range(width)
    )


def det3(matrix):
    (a00, a01, a02), (a10, a11, a12), (a20, a21, a22) = matrix
    return (
        a00 * (a11 * a22 - a12 * a21)
        - a01 * (a10 * a22 - a12 * a20)
        + a02 * (a10 * a21 - a11 * a20)
    )


def check_pair_rank(projectors):
    width = len(projectors[0])
    samples = (1, 2, 3, 5)
    checked = 0
    for left, right in product(projectors, repeat=2):
        for scalar_a, scalar_b in product(samples, repeat=2):
            product_matrix = mat_mul(scaled_update(left, scalar_a), scaled_update(right, scalar_b))
            difference = tuple(
                tuple(product_matrix[row][col] - (1 if row == col else 0) for col in range(width))
                for row in range(width)
            )
            row_sets = list(combinations(range(width), 3))
            for row_set in row_sets:
                for col_set in row_sets:
                    minor = tuple(
                        tuple(difference[row][col] for col in col_set) for row in row_set
                    )
                    need(det3(minor) == 0, "two rank-one updates produced rank above 2")
        checked += 1
    return checked


def check_diagonal_lines():
    # Every nonzero rank-one matrix u v^T that is diagonal uses exactly one line.
    diagonal_rank_one = 0
    multi_line = 0
    for left in product(range(-2, 3), repeat=3):
        for right in product(range(-2, 3), repeat=3):
            matrix = tuple(tuple(left[row] * right[col] for col in range(3)) for row in range(3))
            if any(matrix[row][col] for row in range(3) for col in range(3) if row != col):
                continue
            if not any(matrix[row][row] for row in range(3)):
                continue
            diagonal_rank_one += 1
            if sum(matrix[row][row] != 0 for row in range(3)) != 1:
                multi_line += 1
    need(diagonal_rank_one > 0 and multi_line == 0, "diagonal rank-one matrix meets two lines")
    return diagonal_rank_one


def add_poly(left, right):
    out = set(left)
    for exponent in right:
        if exponent in out:
            out.remove(exponent)
        else:
            out.add(exponent)
    return frozenset(out)


def shift(poly, exponent):
    return frozenset(tuple(coord + extra for coord, extra in zip(term, exponent)) for term in poly)


def apply_call(state, projector, frame):
    width = int(len(state) ** 0.5)
    need(width * width == len(state), "state is not square")
    rows = [list(state[width * row : width * row + width]) for row in range(width)]
    image = None
    support = []
    for row in range(width):
        if any(projector[row]):
            if image is None:
                image = projector[row]
            need(projector[row] == image, "idempotent rows disagree")
            support.append(row)
    need(image is not None, "empty projector")
    acc = [frozenset() for _ in range(width)]
    for col, bit in enumerate(image):
        if bit:
            acc = [add_poly(acc[entry], rows[col][entry]) for entry in range(width)]
    delta = [add_poly(shift(part, frame), part) for part in acc]
    for row in support:
        rows[row] = [add_poly(rows[row][entry], delta[entry]) for entry in range(width)]
    return tuple(entry for row in rows for entry in row)


def identity_state(width, degree):
    zero = frozenset()
    one = frozenset([tuple(0 for _ in range(degree))])
    return tuple(one if row == col else zero for row in range(width) for col in range(width))


def coordinate_projector(width, index):
    return tuple(
        tuple(1 if row == index and col == index else 0 for col in range(width))
        for row in range(width)
    )


def direct_word(data, helpers, address):
    width = data + helpers
    state = identity_state(width, address)
    for register in range(data):
        for axis in range(address):
            frame = tuple(1 if coord == axis else 0 for coord in range(address))
            state = apply_call(state, coordinate_projector(width, register), frame)
    return state


def expect_direct(state, data, helpers, address):
    width = data + helpers
    zero = frozenset()
    full = frozenset([tuple(1 for _ in range(address))])
    one = frozenset([tuple(0 for _ in range(address))])
    for row in range(width):
        for col in range(width):
            entry = state[width * row + col]
            if row != col:
                need(entry == zero, "direct word created an off-diagonal entry")
            elif row < data:
                need(entry == full, "direct word missed a data target")
            else:
                need(entry == one, "clean helper was not restored")


def short_register_fails(address=3):
    width = 4
    state = identity_state(width, address)
    plan = (3, 3, 2, 0)
    for register, count in enumerate(plan):
        for axis in range(count):
            frame = tuple(1 if coord == (axis % address) else 0 for coord in range(address))
            state = apply_call(state, coordinate_projector(width, register), frame)
    exponent = next(iter(state[2 * width + 2]))
    need(sum(exponent) == 2, "two calls did not leave rank 2")
    need(exponent != tuple(1 for _ in range(address)), "two calls produced I")
    return exponent


def block_projector_is_not_three_multiplies():
    width = 4
    degree = 3
    mask = 0b0111
    projector = tuple(
        tuple(((mask >> row) & 1) & ((mask >> col) & 1) for col in range(width))
        for row in range(width)
    )
    state = apply_call(identity_state(width, degree), projector, (1, 0, 0))
    need(state != direct_word(3, 1, degree), "one block call reproduced the direct word")
    return len(state[0])


def pigeonhole():
    solutions = [
        counts
        for counts in product(range(9), repeat=3)
        if sum(counts) == 8 and all(count >= 3 for count in counts)
    ]
    need(solutions == [], "eight calls cover three lines")
    attained = [
        counts
        for counts in product(range(10), repeat=3)
        if sum(counts) == 9 and all(count >= 3 for count in counts)
    ]
    need(attained == [(3, 3, 3)], "the direct line split is not the unique nine-call cover")
    return len(solutions)


def main():
    three = idempotents(3)
    four = idempotents(4)
    need(len(three) == 28, "three-register idempotent count")
    need(len(four) == 120, "four-register idempotent count")
    pairs = check_pair_rank(four)
    diagonal = check_diagonal_lines()
    for helpers in (0, 1, 2):
        expect_direct(direct_word(3, helpers, 3), 3, helpers, 3)
    short = short_register_fails()
    block_terms = block_projector_is_not_three_multiplies()
    empty = pigeonhole()
    print(
        "PASS_SPAN_LEMMA_IDLE_HELPERS"
        f" idempotents_w3={len(three)} idempotents_w4={len(four)}"
        f" pair_products={pairs} diagonal_grid={diagonal}"
        f" short_exponent={short} block_entry_terms={block_terms}"
        f" eight_call_line_covers={empty} bound=m*t sharp=true no_new_kappa"
    )


if __name__ == "__main__":
    main()
