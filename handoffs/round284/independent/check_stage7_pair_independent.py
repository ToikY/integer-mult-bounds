"""Check a two-rail Type B stage-7 mode using independently oriented sector matrices."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

HERE = Path(__file__).resolve().parent
ENGINE = "7a26ecf8262efa2d6c570a452e84c461b3af8f8f83429dc5388ef15b1a3afb8d"
ROLES, CUT, CAP, OFFSET = (50, 51), 1215, 30, 36
ONE, ZERO = (Q(1), Q(0)), (Q(0), Q(0))


def emit(**result):
    print(dumps(result, sort_keys=True, default=str), flush=True)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def conj(a):
    return a[0], -a[1]


def multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def dot(a, b):
    return add(multiply(a[0], b[0]), multiply(a[1], b[1]))


def fields(pair):
    return tuple(Q(v) for v in pair)


def flatten(rows):
    return {(r, p, m): value for r, terms in enumerate(rows, OFFSET)
            for (p, m), value in terms.items()}


def combine_tables(tables):
    a, b = tables
    return {key: (a.get(key, ZERO), b.get(key, ZERO)) for key in sorted(a.keys() | b.keys())}


def rank_and_kernel(entries):
    diag0, diag1, off = ZERO, ZERO, ZERO
    first = None
    for a, b in entries.values():
        diag0 = add(diag0, multiply(conj(a), a))
        diag1 = add(diag1, multiply(conj(b), b))
        off = add(off, multiply(conj(a), b))
        if first is None and (a != ZERO or b != ZERO):
            first = a, b
    real, imag = add(multiply(diag0, diag1), neg(multiply(conj(off), off)))
    assert imag == 0 and real >= 0
    if real:
        return 2, real, []
    if first is None:
        return 0, real, [(ONE, ZERO), (ZERO, ONE)]
    a, b = first
    kernel = b, neg(a)
    assert kernel != (ZERO, ZERO) and all(dot(row, kernel) == ZERO for row in entries.values())
    return 1, real, [kernel]


def verify_lead_witness(entries, record, rank):
    assert rank == record["rank"]
    if rank != 2:
        return None
    keys = [(r, p, tuple(m)) for r, p, m in record["keys"]]
    rows = tuple(entries[key] for key in keys)
    assert rows == tuple(tuple(fields(pair) for pair in row) for row in record["rows"])
    (a, b), (c, d) = rows
    det = add(multiply(a, d), neg(multiply(b, c)))
    assert det == fields(record["determinant"]) != ZERO
    return {"keys": keys, "rows": rows, "determinant": det}


def apply(rows, tape, sign, kit, pullback=False):
    result = list(rows)
    for event in reversed(tape) if pullback else tape:
        kit["propagate"](result, event, sign, pullback=pullback)
    return result


def check_old_endpoint(tape, sign, kit):
    for role in ROLES:
        expected = kit["unit"](role, 1, (7, 8), (Q(sign), Q(0)))
        original = kit["unit"](role)
        assert apply(original, tape, sign, kit) == expected
        assert apply(original, tape, sign, kit, pullback=True) == expected


def check_suffix(tape, sign, kit, parity, u, ell, v, w):
    def vectors(values, monomial, coefficient=ONE):
        out = [{} for _ in range(36)]
        for role, value in values.items():
            actual = multiply(value, coefficient)
            if actual != ZERO:
                out[role - OFFSET][monomial] = actual
        return out

    # d/p = q^(3-parity) B8, canonical modulo q²=sign.
    suffix_body = (1-parity, (8,))
    phase_scalar = Q(sign), Q(0)
    forward = apply(vectors(v, (0, ())), tape[CUT:], sign, kit)
    pulled = apply(vectors(dict(zip(ROLES, ell, strict=True)), (0, ())),
                   tape[CUT:], sign, kit, pullback=True)
    assert forward == vectors(dict(zip(ROLES, u, strict=True)), suffix_body, phase_scalar)
    assert pulled == vectors(dict(zip(ROLES, w, strict=True)), suffix_body, phase_scalar)


def pairing(tape, kit, parity, sign, column, input_kernels, lead):
    allowed = parity, (7,)
    row = combine_tables([flatten(apply(kit["unit"](r), tape[:CUT], sign, kit, pullback=True)) for r in ROLES])
    forbidden = {k: v for k, v in row.items() if k[0] not in ROLES or k[1:] != allowed}
    rank, determinant, decoder = rank_and_kernel(forbidden)
    witness = verify_lead_witness(forbidden, lead["decoder_forbidden_rank"], rank)
    matches = []
    for u in input_kernels:
        v = {key[0]: dot(values, u) for key, values in column.items() if key[1:] == allowed}
        for w in decoder:
            ell = tuple(dot(row.get((r, *allowed), (ZERO, ZERO)), w) for r in ROLES)
            value = dot(ell, u)
            assert value == dot(w, tuple(v.get(r, ZERO) for r in ROLES))
            if value != ZERO:
                check_suffix(tape, sign, kit, parity, u, ell, v, w)
                matches.append({"u": u, "v": v, "w": w, "ell": ell, "pairing": value,
                                "formal_suffix_forward_and_dual": True})
    assert bool(matches) == bool(lead["matched"])
    return {"decoder_rank": rank, "decoder_gram_determinant": determinant, "decoder_witness": witness,
            "matches": matches}


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()
    classes = {}

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", cut=CUT, cap_seconds=CAP, completed=classes,
             seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP)
    path = HERE / "check_stage7_independent.py"
    assert sha256(path.read_bytes()).hexdigest() == ENGINE
    kit = run_path(str(path))
    pins = kit["PINS"]
    raw = {p: (args.root / p).read_bytes() for p in pins}
    assert {p: sha256(b).hexdigest() for p, b in raw.items()} == pins
    unique = kit["unique_pairs"]
    caller = loads(raw["inputs/7113-CALLER.json"], object_pairs_hook=unique)
    app = loads(raw["inputs/7481-APPLICATION.json"], object_pairs_hook=unique)
    assert app["caller_head"] == kit["CALLER"] and app["caller_sha256"] == pins["inputs/7113-CALLER.json"]
    tape = caller["events"]
    assert len(tape) == 4783 and caller["roles"] == 72 and caller["stages"] == 17
    kind = caller["types"]["B"]
    assert kind["offset"] == OFFSET and kind["roles"] == 36 and len(kind["ports"]) == 8
    assert kind["diagonal"][14:16] == [[-1, 0] + [int(j in (7, 8)) for j in range(1, 18)]] * 2
    assert tape[967] == tape[1030] == ["B", "IDLE_ONE", 36, [7]]
    assert tape[1138] == ["J", 7, [7, 0, 18, 25], [36, 37, "-1", "1/2"]]
    assert tape[CUT - 1:CUT + 1] == [["B", "ADD", 37, 36, "-1"], ["B", "ADD", 37, 36, "41/15"]]
    for i, r in enumerate(ROLES):
        assert tape[1228 + i][:4] == ["B", "ADD", r, 36]
        assert tape[1244 + i][:4] == ["B", "ADD", 36, r]
    controls = kit["controls"]()
    assert rank_and_kernel({0: (ONE, ZERO), 1: (ZERO, ONE)})[:2] == (2, Q(1))
    assert rank_and_kernel({0: (ONE, ONE)})[:2] == (1, Q(0))
    lead_bytes = args.lead_receipt.read_bytes()
    assert sha256(lead_bytes).hexdigest() == args.lead_sha256
    start, lead = [loads(line, object_pairs_hook=unique) for line in lead_bytes.splitlines()]
    assert start["status"] == "START" and start["cut"] == lead["cut"] == CUT
    assert tuple(start["input_roles"]) == tuple(start["decoder_roles"]) == ROLES
    assert start["allowed_classes"] == [[0, [7]], [1, [7]]]

    tables = {}
    for sign in (1, -1):
        check_old_endpoint(tape, sign, kit)
        tables[sign] = combine_tables([flatten(apply(kit["unit"](r), tape[:CUT], sign, kit)) for r in ROLES])
    surviving = []
    for parity in (0, 1):
        sectors, kernels = {}, {}
        for sign, column in tables.items():
            allowed = parity, (7,)
            bad = {key: values for key, values in column.items() if key[1:] != allowed}
            rank, determinant, kernel = rank_and_kernel(bad)
            prior = lead["sectors"][str(parity)][str(sign)]
            witness = verify_lead_witness(bad, prior["forbidden_column_rank"], rank)
            assert bool(kernel) == bool(prior["ingress_basis"])
            kernels[sign] = kernel
            sectors[sign] = {"forbidden_rank": rank, "gram_determinant": determinant,
                             "forbidden_rows": len(bad), "lead_minor": witness}
        if all(kernels.values()):
            for sign, column in tables.items():
                prior = lead["sectors"][str(parity)][str(sign)]
                sectors[sign]["bilateral"] = pairing(tape, kit, parity, sign, column, kernels[sign], prior)
            if all(r["bilateral"]["matches"] for r in sectors.values()):
                surviving.append(parity)
                disposition = "BILATERAL_FORMAL_SURVIVOR"
            else:
                disposition = "EXCLUDED_FIXED_DECODER_PAIRING"
        else:
            disposition = "EXCLUDED_COLUMN_SUPPORT"
        assert disposition == lead["class_results"][str(parity)]
        classes[parity] = {"disposition": disposition, "sectors": sectors}
    assert surviving == lead["survivor_parities"]
    emit(status="PASS_INDEPENDENT_FIXED_BILATERAL_EXCLUSION" if not surviving else "INDEPENDENT_FORMAL_SURVIVOR",
         cut=CUT, roles=ROLES, classes=classes, survivor_parities=surviving,
         unresolved=lead["unresolved"], old_endpoint_rows_and_columns_both_sectors=True,
         controls=controls, lead_sha256=args.lead_sha256, cap_seconds=CAP,
         input_pins=pins | {"independent/check_stage7_independent.py": ENGINE},
         seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
