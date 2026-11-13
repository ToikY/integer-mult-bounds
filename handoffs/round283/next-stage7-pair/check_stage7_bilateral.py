"""Necessary bilateral support gate for a two-rail Type B stage-7 return."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

HERE = Path(__file__).resolve().parent
HELPER_HASH = "7deae3576918f81c11804ef91883f5ad350765f62fec3807a1fe47fee0f70da4"
ROLES, CUT, CAP = (50, 51), 1215, 30
CLASSES = ((0, (7,)), (1, (7,)))
ZERO, ONE = (Q(0), Q(0)), (Q(1), Q(0))
completed = {}


def emit(**result):
    print(json.dumps(result, default=str, sort_keys=True), flush=True)


def verify(path, pin):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == pin, path
    return raw


def minus(value):
    return -value[0], -value[1]


def dot(left, right, mul):
    first, second = (mul(a, b) for a, b in zip(left, right, strict=True))
    return first[0] + second[0], first[1] + second[1]


def kernel(rows, minor):
    witness = minor(rows)
    if witness["rank"] == 2:
        return [], witness
    if not witness["rank"]:
        return [(ONE, ZERO), (ZERO, ONE)], witness
    a, b = witness["first_nonzero"][1]
    return [(b, minus(a))], witness


def coefficients(terms, selector):
    first, second = terms
    return [(key, (first.get(key, ZERO), second.get(key, ZERO)))
            for key in sorted(first.keys() | second.keys()) if selector(key)]


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    root = Path(sys.argv[1]).resolve()

    def timeout(_signum, _frame):
        emit(status="UNRESOLVED_CAP", cut=CUT, cap_seconds=CAP, completed=completed)
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(CAP)
    helper_path = HERE / "check_stage7_isolation.py"
    verify(helper_path, HELPER_HASH)
    helper = run_path(str(helper_path))
    pins = {**helper["PINS"], helper_path.name: HELPER_HASH}
    local = {"check_type_b_root.py", "type_a_laurent.py", helper_path.name}
    raw = {name: verify((HERE if name in local else root) / name, pin)
           for name, pin in pins.items()}
    caller = json.loads(raw["7113-CALLER.json"], object_pairs_hook=helper["unique_object"])
    app = json.loads(raw["7481-APPLICATION.json"], object_pairs_hook=helper["unique_object"])
    assert app["source_head"] == helper["SOURCE_PREDECESSOR"]
    assert app["caller_head"] == helper["CALLER"] and app["caller_sha256"] == pins["7113-CALLER.json"]
    assert app["claim_decimal"] == "0.003647081039689"
    tape = caller["events"]
    assert tape[967] == tape[1030] == ["B", "IDLE_ONE", 36, [7]]
    assert tape[1138] == ["J", 7, [7, 0, 18, 25], [36, 37, "-1", "1/2"]]
    assert tape[1214:1216] == [["B", "ADD", 37, 36, "-1"], ["B", "ADD", 37, 36, "41/15"]]
    assert tape[1228] == ["B", "ADD", 50, 36, "7/30"]
    assert tape[1244] == ["B", "ADD", 36, 50, "-982"]
    assert caller["types"]["B"]["diagonal"][14:16] == [[-1, 0] +
            [int(j in (7, 8)) for j in range(1, 18)]] * 2
    assert len(caller["types"]["B"]["ports"]) == 8
    engine = run_path(str(HERE / "type_a_laurent.py"))
    forward = run_path(str(HERE / "check_type_b_root.py"))
    add, scale = engine["add_scaled"], engine["scaled"]
    minor, mul = forward["minor"], forward["multiply"]
    sectorize = helper["sector_coefficients"]
    lo, hi = map(Q, app["directed_crossing_bracket"])
    power = run_path(str(root / "pricing.py"))["power_bounds"]
    lower = 8 * (power(8, hi)[0] + power(9, hi)[0] - power(17, lo)[1])
    upper = 8 * (power(8, lo)[1] + power(9, lo)[1] - power(17, hi)[0])
    assert Q("0.33985048763130562") <= lower <= upper <= Q("0.33985048763130563")
    emit(status="START", cut=CUT, cap_seconds=CAP, pins=pins, comparator=helper["HEAD"],
         caller=helper["CALLER"], input_roles=ROLES, decoder_roles=ROLES,
         first_changed_deadline=1228, first_outward_read=1244, allowed_classes=CLASSES,
         gross_raw=[lower, upper], proposed_paid_delta={}, proposed_productive_delta={8:8, 9:8, 17:-8})

    def propagate_column(source):
        rows = helper["unit"](source)
        for event in tape[:CUT]:
            forward["propagate"](rows, event, add, scale)
        return rows

    def entries(rows, sector, selected):
        return {(role, phase, mask): coeff
                for role, row in enumerate(rows, 36) if role in selected
                for (phase, mask), coeff in sectorize(row, sector).items()}

    assert kernel([("one", (ONE, ONE))], minor)[0] == [(ONE, minus(ONE))]
    assert not kernel([("one", (ONE, ZERO)), ("two", (ZERO, ONE))], minor)[0]
    assert dot((ONE, ZERO), (ONE, ZERO), mul) == ONE
    assert dot((ONE, ZERO), (ZERO, ONE), mul) == ZERO

    columns = {source: propagate_column(source) for source in ROLES}
    all_results = {}
    for allowed in CLASSES:
        parity = allowed[0]
        completed[parity] = {}
        ingress = {}
        for sector in (1, -1):
            tables = [entries(columns[source], sector, range(36, 72)) for source in ROLES]
            forbidden = coefficients(tables, lambda key: key[1:] != allowed)
            vectors, witness = kernel(forbidden, minor)
            ingress[sector] = (vectors, tables)
            completed[parity][sector] = dict(forbidden_column_rank=witness, ingress_basis=vectors)
        if any(not vectors for vectors, _ in ingress.values()):
            all_results[parity] = "EXCLUDED_COLUMN_SUPPORT"
            continue

        columns.update({source: propagate_column(source) for source in range(36, 72) if source not in columns})
        paired = {}
        for sector in (1, -1):
            vectors, tables = ingress[sector]
            row_tables = [{(source, phase, mask): coeff for source, column in columns.items()
                           for (phase, mask), coeff in sectorize(column[role-36], sector).items()}
                          for role in ROLES]
            wrong = coefficients(row_tables, lambda key: key[0] not in ROLES or key[1:] != allowed)
            decoder, witness = kernel(wrong, minor)
            matches = []
            for vector in vectors:
                for weights in decoder:
                    left = tuple(dot(weights, tuple(t.get((source, *allowed), ZERO) for t in row_tables), mul)
                                 for source in ROLES)
                    right = tuple(dot(vector, tuple(t.get((role, *allowed), ZERO) for t in tables), mul)
                                  for role in ROLES)
                    pairing = dot(left, vector, mul)
                    assert pairing == dot(weights, right, mul)
                    if pairing != ZERO:
                        matches.append(dict(u=vector, w=weights, ell=left, v_on_decoder=right, pairing=pairing))
            paired[sector] = matches
            completed[parity][sector].update(decoder_forbidden_rank=witness, decoder_basis=decoder, matched=matches)
        all_results[parity] = ("BILATERAL_FORMAL_SURVIVOR" if all(paired.values())
                               else "EXCLUDED_FIXED_DECODER_PAIRING")

    survivors = [parity for parity, result in all_results.items() if result == "BILATERAL_FORMAL_SURVIVOR"]
    emit(status="BILATERAL_FORMAL_SURVIVOR" if survivors else "EXHAUSTED_FIXED_BILATERAL",
         cut=CUT, class_results=all_results, sectors=completed, survivor_parities=survivors,
         unresolved=["exact legal central-even bases and phase lowering", "physical stock and adjoint",
                     "independent fresh field, original output detachment and complete signed price"]
         if survivors else [])
    signal.alarm(0)


if __name__ == "__main__":
    main()
