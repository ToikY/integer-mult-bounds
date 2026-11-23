"""Recheck the same finite K7 counterexamples with modular chart actions."""
import gzip
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import signal
from sys import argv
import tarfile


def solve_column(frame, rhs, modulus):
    """Express one address direction in the installed chart basis."""
    vectors = frame["B"] + frame["A"]
    rows = [[x % modulus for x in row] + [value % modulus]
            for row, value in zip(zip(*vectors, strict=True), rhs, strict=True)]
    for col in range(8):
        lead = next(i for i in range(col, 8) if rows[i][col] % 3)
        rows[col], rows[lead] = rows[lead], rows[col]
        inverse = pow(rows[col][col], -1, modulus)
        rows[col] = [(inverse * x) % modulus for x in rows[col]]
        for row in range(8):
            if row != col:
                weight = rows[row][col]
                rows[row] = [(x - weight * y) % modulus for x, y in
                             zip(rows[row], rows[col], strict=True)]
    return [row[-1] for row in rows]


def projection(frame, rhs, modulus):
    coefficients = solve_column(frame, rhs, modulus)
    return tuple(sum(coeff * axis[i] for coeff, axis in
                     zip(coefficients, frame["B"])) % modulus for i in range(8))


def address_action(head, tail, projection_of_difference, modulus):
    return (tuple((x + v) % modulus for x, v in zip(head, projection_of_difference, strict=True)),
            tuple((x - v) % modulus for x, v in zip(tail, projection_of_difference, strict=True)))


def has_origin(program, clock, register, owner):
    """Propagate only the single independently supplied owner in this test."""
    live = {owner}
    for opcode, dest, *args in program[:clock]:
        if opcode == "ADD":
            if args[0] in live:
                live ^= {dest}
        elif opcode == "SWAP":
            source, = args
            if (dest in live) != (source in live):
                live ^= {dest, source}
        elif opcode == "CLEAR":
            live.discard(dest)
        else:
            assert opcode in ("INIT", "MOVE")
    return register in live


def main():
    assert __debug__
    signal.alarm(90)
    archive_path, receipt_path = map(Path, argv[1:])
    receipt = json.loads(receipt_path.read_text())
    raw = archive_path.read_bytes()
    assert sha256(raw).hexdigest() == receipt["archive_sha256"]
    with tarfile.open(fileobj=BytesIO(raw)) as handle:
        gz = handle.extractfile(receipt["word_path"]).read()
    assert sha256(gz).hexdigest() == receipt["word_sha256"]
    payload = gzip.decompress(gz)
    assert sha256(payload).hexdigest() == receipt["unpacked_word_sha256"]
    word = json.loads(payload)
    assert receipt["status"] == "EXHAUSTED_FIXED_64_NO_IDENTITY_MOVE"
    moves = [(int(i), row) for i, row in enumerate(word["program"]) if row[0] == "MOVE"]
    moves.sort(key=lambda entry: (
        -abs(word["frames"][str(entry[1][2])]["dim"] - word["frames"][str(entry[1][3])]["dim"]),
        entry[0],
    ))
    assert [case["clock"] for case in receipt["tested"]] == [i for i, _ in moves[:64]]
    clocks = []
    for case in receipt["tested"]:
        clock, dest = map(case.__getitem__, ("clock", "register"))
        assert word["program"][clock] == ["MOVE", dest, *case["charts"]]
        first, last = (word["frames"][str(i)] for i in case["charts"])
        witness = case["counterexample"]
        modulus = witness["modulus"]
        owner = witness["nonzero_input_owner"]
        assert has_origin(word["program"], clock, dest, owner)
        coord = witness["tail_coordinate_after_old_chart"]
        initial = (0,) * 8, tuple(int(i == coord) for i in range(8))
        old_projection = projection(first, initial[1], modulus)
        # The native source permutes addresses. Invert the old chart on the
        # chosen suffix address to obtain a valid normalized input address.
        normalized = address_action(*initial, old_projection, modulus)
        norm_diff = tuple((t - h) % modulus for h, t in zip(*normalized, strict=True))
        target = address_action(*normalized, projection(last, norm_diff, modulus), modulus)
        smaller, larger = sorted((first, last), key=lambda chart: chart["dim"])
        delta = tuple((v - u) % modulus for u, v in
                      zip(projection(smaller, initial[1], modulus),
                          projection(larger, initial[1], modulus), strict=True))
        actual = address_action(*initial, delta, modulus)
        assert target == actual and target != initial
        mod_values = []
        for value in witness["head_change_for_unit_weights"]:
            num, _, div = value.partition("/")
            mod_values.append(int(num) * pow(int(div or "1"), -1, modulus) % modulus)
        assert tuple(mod_values) == actual[0]
        clocks.append(clock)
    assert len(set(clocks)) == len(clocks) == 64
    first_case = receipt["tested"][0]
    false_origins = (i for i in range(len(word["start"]) - 1, -1, -1)
                     if not has_origin(word["program"], first_case["clock"], first_case["register"], i))
    false_origin = next(false_origins)
    assert false_origin != first_case["counterexample"]["nonzero_input_owner"]
    signal.alarm(0)
    print(json.dumps({
        "status": "PASS_INDEPENDENT_MODULAR_K7_WITNESSES",
        "checked_clocks": clocks,
        "negative_control": {"wrong_owner_id": false_origin, "clock": first_case["clock"], "rejected": True},
        "scope": "Each named independent-owner impulse reaches the listed register. At unit weights the original MOVE sends its impulse to the target chart address. Skipping MOVE leaves a different address.",
    }, indent=2))


if __name__ == "__main__":
    main()
