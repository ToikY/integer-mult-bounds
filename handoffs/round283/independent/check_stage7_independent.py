"""Check the Type B seam by independent exact forward columns and reverse pullback rows."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
}
HEAD = "89eaa9d8cae37c1540de98f2d29a3abaabb96a2b"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
OFFSET, COUNT, ROLE, CUT, CAP = 36, 36, 50, 1215, 30
ZERO, ONE = (Q(0), Q(0)), (Q(1), Q(0))


def emit(**result):
    print(dumps(result, sort_keys=True, default=str), flush=True)


def unique_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def gmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def accumulate(out, source, sector, coefficient=ONE, phase=0, factors=()):
    for (old_phase, old_factors), value in source.items():
        quotient, parity = divmod(old_phase + phase, 2)
        key = parity, tuple(sorted(old_factors + factors))
        a, b = gmul(coefficient, value)
        if sector == -1 and quotient % 2:
            a, b = -a, -b
        x, y = out.get(key, ZERO)
        new = x + a, y + b
        if new == ZERO:
            out.pop(key, None)
        else:
            out[key] = new


def operator(event, sector):
    """Return affected role list and a sparse local matrix of exact monomial entries."""
    if event[0] == "A":
        return (), ()
    if event[0] == "J":
        _, stage, a_roles, (r, s, alpha, beta) = event
        assert all(i < OFFSET for i in a_roles) and (Q(alpha), Q(beta)) == (Q(-1), Q(1, 2))
        f = (stage,)
        return (r, s), ((0, 0, ONE, 0, f), (0, 1, (-1, 0), 1, f),
                        (1, 0, (Q(1, 2), 0), -1, f), (1, 1, (Q(1, 2), 0), 0, f))
    tag, op, r, *args = event
    assert tag == "B"
    if op == "ADD":
        s, coefficient = args
        assert r != s
        return (r, s), ((0, 0, ONE, 0, ()), (1, 1, ONE, 0, ()),
                        (0, 1, (Q(coefficient), 0), 0, ()))
    if op == "SWAP":
        s, = args
        assert r != s
        return (r, s), ((0, 1, ONE, 0, ()), (1, 0, ONE, 0, ()))
    if op == "SCALE":
        coefficient = (Q(args[0]), 0)
        phase, factors = 0, ()
    elif op == "LAMBDA":
        sign, = args
        assert sign in (1, -1)
        coefficient = ONE if sector == 1 else (0, Q(sign))
        phase, factors = 0, ()
    else:
        assert op in ("IDLE_ONE", "IDLE_ODD")
        coefficient = ONE
        phase = args[1] if op == "IDLE_ODD" else 0
        factors = tuple(args[0])
    return (r,), ((0, 0, coefficient, phase, factors),)


def propagate(rows, event, sector, pullback=False):
    roles, entries = operator(event, sector)
    assert all(OFFSET <= r < OFFSET + COUNT for r in roles)
    before = [rows[r - OFFSET] for r in roles]
    result = [{} for _ in roles]
    for out, inp, coefficient, phase, factors in entries:
        if pullback:
            out, inp = inp, out
        accumulate(result[out], before[inp], sector, coefficient, phase, factors)
    for r, values in zip(roles, result, strict=True):
        rows[r - OFFSET] = values


def unit(role, phase=0, factors=(), value=ONE):
    rows = [{} for _ in range(COUNT)]
    rows[role - OFFSET][phase, factors] = value
    return rows


def literal_action(tape, sector, pullback=False, phase=0, factors=(), coefficient=ONE):
    rows = unit(ROLE, phase, factors, coefficient)
    for event in reversed(tape) if pullback else tape:
        propagate(rows, event, sector, pullback)
    return rows


def encoded(entries):
    return [[r, parity, list(factors), list(value)]
            for r, terms in enumerate(entries, OFFSET)
            for (parity, factors), value in sorted(terms.items())]


def decode_entries(records):
    return {(r, parity, tuple(factors)): tuple(Q(v) for v in value)
            for r, parity, factors, value in records}


def controls():
    # A single non-symmetric ADD affects opposite coordinate lists on a forward
    # column and a pullback row. A transpose mistake must fail these fixtures.
    event = ["B", "ADD", ROLE, 36, "-3/2"]
    col = unit(36)
    row = unit(ROLE)
    propagate(col, event, 1)
    propagate(row, event, 1, pullback=True)
    assert col[ROLE - OFFSET] == row[36 - OFFSET] == {(0, ()): (Q(-3, 2), Q(0))}
    assert not literal_action([event], 1)[36 - OFFSET]
    wrong = unit(ROLE)
    propagate(wrong, event, 1, pullback=False)
    assert wrong != row
    for sector in (1, -1):
        x = unit(ROLE, 1)
        propagate(x, ["B", "IDLE_ODD", ROLE, [7], 1], sector)
        assert x == unit(ROLE, 0, (7,), (Q(sector), Q(0)))
    return {"transpose_mutant_rejected": True, "odd_phase_changes_by_sector": True}


def verify_sector(tape, lead, sector):
    expected_prefix = unit(ROLE, 0, (7,))
    row = literal_action(tape[:CUT], sector, pullback=True)
    col = literal_action(tape[:CUT], sector)
    row_terms, col_terms = encoded(row), encoded(col)
    row_off = [record for record in row_terms if record[0] != ROLE]
    col_off = [record for record in col_terms if record[0] != ROLE]
    own = [record for record in row_terms if record[0] == ROLE]
    assert [record for record in col_terms if record[0] == ROLE] == own
    assert decode_entries(row_off) == decode_entries(lead["row_contamination"])
    assert decode_entries(col_off) == decode_entries(lead["column_contamination"])
    assert decode_entries(own) == decode_entries([[ROLE, *r] for r in lead["own_terms"]])
    isolated = row == col == expected_prefix
    assert isolated == lead["exact_rank8_primitive"]
    expected_full = unit(ROLE, 1, (7, 8), (Q(sector), Q(0)))
    full_column = literal_action(tape, sector)
    full_row = literal_action(tape, sector, pullback=True)
    assert full_column == full_row == expected_full
    result = {
        "prefix_row": row_terms, "prefix_column": col_terms,
        "row_contaminants": len(row_off), "column_contaminants": len(col_off),
        "isolated_rank8": isolated, "old_full_row_and_column": encoded(expected_full),
    }
    if isolated:
        # The suffix acts on a freshly supplied formal field, before any
        # physical admission or liveness assumption is granted.
        expected_suffix = unit(ROLE, 1, (8,), (Q(sector), Q(0)))
        forward_suffix = literal_action(tape[CUT:], sector)
        reverse_suffix = literal_action(tape[CUT:], sector, pullback=True)
        result["suffix_row"] = encoded(reverse_suffix)
        result["suffix_column"] = encoded(forward_suffix)
        result["isolated_rank9_suffix"] = forward_suffix == reverse_suffix == expected_suffix
        # Altering the expected even stage-7 return to odd must fail.
        assert row != unit(ROLE, 1, (7,))
    else:
        result["first_row_contaminant"] = row_off[0] if row_off else None
        result["first_column_contaminant"] = col_off[0] if col_off else None
    return result


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()
    checked = []

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", role=ROLE, cut=CUT, cap_seconds=CAP,
             checked_sectors=checked, seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP)
    raw = {p: (args.root / p).read_bytes() for p in PINS}
    assert {p: sha256(data).hexdigest() for p, data in raw.items()} == PINS
    app = loads(raw["inputs/7481-APPLICATION.json"], object_pairs_hook=unique_pairs)
    caller = loads(raw["inputs/7113-CALLER.json"], object_pairs_hook=unique_pairs)
    assert app["caller_head"] == CALLER and app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    assert app["claim_decimal"] == "0.003647081039689"
    tape = caller["events"]
    assert caller["roles"] == 72 and len(tape) == 4783 and caller["stages"] == 17
    kind = caller["types"]["B"]
    assert kind["offset"] == OFFSET and kind["roles"] == COUNT and len(kind["ports"]) == 8
    body78 = [-1, 0] + [int(j in (7, 8)) for j in range(1, 18)]
    assert kind["diagonal"][14:16] == [body78, body78]
    assert tape[967] == tape[1030] == ["B", "IDLE_ONE", 36, [7]]
    assert tape[1138] == ["J", 7, [7, 0, 18, 25], [36, 37, "-1", "1/2"]]
    assert tape[1214] == ["B", "ADD", 37, 36, "-1"]
    assert tape[CUT] == ["B", "ADD", 37, 36, "41/15"]
    assert tape[1228] == ["B", "ADD", ROLE, 36, "7/30"]
    assert tape[1244] == ["B", "ADD", 36, ROLE, "-982"]
    lead_raw = args.lead_receipt.read_bytes()
    assert sha256(lead_raw).hexdigest() == args.lead_sha256
    start, lead = (loads(line, object_pairs_hook=unique_pairs) for line in lead_raw.splitlines())
    assert start["status"] == "START" and start["comparator"] == HEAD and start["caller"] == CALLER
    assert start["role"] == ROLE and start["cut"] == CUT
    assert lead["status"] in ("EXCLUDED_LITERAL_SEAM", "ISOLATED_STAGE7_SURVIVOR", "EXCLUDED_FIXED_SUFFIX")
    checks = controls()
    results = {}
    for sector in (1, -1):
        results[sector] = verify_sector(tape, lead["sectors"][str(sector)], sector)
        checked.append(sector)
    if all(r["isolated_rank8"] for r in results.values()):
        suffix = all(r["isolated_rank9_suffix"] for r in results.values())
        assert suffix == lead["suffix_match"] == (lead["status"] == "ISOLATED_STAGE7_SURVIVOR")
        status = "PASS_INDEPENDENT_FORMAL_SEAM_AND_SUFFIX" if suffix else "PASS_INDEPENDENT_SUFFIX_EXCLUSION"
        unresolved = ["physical exposure and fresh input admission", "signed physical and complete price"] if suffix else []
    else:
        assert lead["status"] == "EXCLUDED_LITERAL_SEAM"
        status, unresolved = "PASS_INDEPENDENT_LITERAL_SEAM_EXCLUSION", []
    emit(status=status, role=ROLE, cut=CUT, comparator=HEAD, caller=CALLER,
         sectors=results, controls=checks, tested=1, unresolved=unresolved, input_pins=PINS,
         lead_sha256=args.lead_sha256, cap_seconds=CAP, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
