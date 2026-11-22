"""Reconstruct the cut from its read clock and verify concrete rank obstructions."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json
import subprocess
import sys
import time


WORD = "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"


def need(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def owner_before(program, register, deadline):
    history = []
    for clock in range(deadline - 1, -1, -1):
        op, left, *args = program[clock]
        if op == "SWAP" and register in (left, args[0]):
            history.append((clock, op, register))
            register = args[0] if register == left else left
        elif register == left:
            history.append((clock, op, register, *args))
            if op in ("INIT", "CLEAR"):
                need(op == "INIT", "a retired owner cannot supply a value")
                return history[::-1]
    raise ValueError("expected a private initialization")


def forward_forms(word, cuts):
    banks = [1 << r for r in range(word["public"])] + [0] * word["owned_fields"]
    read_forms = {}
    for clock, (op, dest, *args) in enumerate(word["program"]):
        if clock in cuts:
            source = args[0] if op == "ADD" else dest
            bits = banks[source]
            read_forms[clock] = [i for i in range(word["public"]) if (bits >> i) & 1]
        if op in ("INIT", "CLEAR"):
            banks[dest] = 0
        elif op == "SWAP":
            other = args[0]
            banks[dest], banks[other] = banks[other], banks[dest]
        elif op == "ADD":
            banks[dest] ^= banks[args[0]]
    return read_forms


def rank(matrix):
    echelon = []
    for raw in matrix:
        row = list(map(Fraction, raw))
        for column, basis in echelon:
            scale = row[column]
            row = [r - scale * p for r, p in zip(row, basis)]
        column = next((i for i, number in enumerate(row) if number), None)
        if column is not None:
            echelon.append((column, [number / row[column] for number in row]))
    return len(echelon)


def verify(root, receipt):
    paths = receipt["dependencies"]
    need(paths["inputs/BINARY-CANDIDATE.json.gz"] == WORD and len(paths) == 3, "known source")
    for path, checksum in paths.items():
        need(sha256((root / path).read_bytes()).hexdigest() == checksum, f"pin {path}")
    word = json.loads(gzip.decompress((root / "inputs/BINARY-CANDIDATE.json.gz").read_bytes()))
    program = word["program"]
    cut = 8105
    need(program[cut] == ["MOVE", 2335, 330, 510], "paid deadline")
    history = owner_before(program, 2335, cut)
    need(history == [(8102, "INIT", 2335, 330), (8103, "ADD", 2335, 1902, 330),
                     (8104, "ADD", 2335, 1908, 330)], "complete backward ancestry")
    need(receipt["direct_arrival_count"] == 0 and receipt["direct_arrival_clocks"] == [],
         "zero-case direct source check")
    owners_and_arrivals = []
    for read, _, _, donor, _ in history[1:]:
        donor_trace = owner_before(program, donor, read)
        clock, opcode, owner, lower, upper = donor_trace[-1]
        need(opcode == "MOVE" and upper == 330, "last true feeder arrival")
        owners_and_arrivals.append([read, clock, owner, lower, upper])
    need(owners_and_arrivals == [[8103, 4759, 1902, 274, 330], [8104, 4800, 1908, 275, 330]],
         "enumeration of both already-paid donors")
    frame = word["frames"]
    upper_bad = frame["530"]
    upper_good = frame["510"]
    source_rows = frame["330"]["B"]
    bad_ranks = [rank(frame[str(c)]["B"] + upper_bad["B"]) for c in (274, 275, 330)]
    need(bad_ranks == [8, 8, 8], "three independent primal row rank failures")
    good_rank = rank(source_rows + upper_good["B"])
    need(good_rank == 7, "original MOVE containment control")
    need(rank(frame["274"]["B"] + source_rows) == 6 and
         rank(frame["275"]["B"] + source_rows) == 6, "original feeder containment control")
    form = forward_forms(word, {8103, 8104, 8105, 10038, 11015})
    need(set(form[8105]) == (set(form[8103]) ^ set(form[8104])) and form[8105],
         "cut carries nonzero full scalar expression")
    need(form[10038] == form[11015] == form[8105], "both later consumer obligations")
    need(form[8103] != form[8104] and all(form[i] for i in (8103, 8104)), "independent input forms")
    moved_bit = min(set(form[8103]) - set(form[8104]))
    need(moved_bit in form[10038], "single-donor corruption changes the first consumer value")
    return {
        "checked_native_word": WORD,
        "old_clock": cut,
        "backward_receiver_trace": history,
        "direct_arrival_count": 0,
        "feeders": owners_and_arrivals,
        "augmented_primal_ranks_for_target_530": bad_ranks,
        "target_dimension": upper_bad["dim"],
        "original_augmented_primal_rank": good_rank,
        "owner_value_public_bit_support_by_clock": form,
        "single_omitted_feeder_detecting_bit": moved_bit,
        "unresolved_direct_cases": 0,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        result = verify(args.inputs, json.loads(args.receipt.read_bytes()))
        args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return 0
    start = time.monotonic()
    try:
        exit_code = subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]],
                                   timeout=15).returncode
    except subprocess.TimeoutExpired:
        exit_code = 124
    print(f"replay exit={exit_code} elapsed={time.monotonic() - start:.6f} cap=15")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
