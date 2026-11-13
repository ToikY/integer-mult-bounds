"""Check one literal Type B productive rail at the completed B7 seam."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

HERE = Path(__file__).resolve().parent
ROLE, CUT, CAP = 50, 1215, 30
HEAD = "89eaa9d8cae37c1540de98f2d29a3abaabb96a2b"
SOURCE_PREDECESSOR = "58a9d052143f5d85295ed2d0163591c47f89a331"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "check_type_b_root.py": "4734ba6500c4934b3f8616f4c39a62e458909685c9e6f306130ddb101127eba9",
    "type_a_laurent.py": "1043c6cb86af5c3fe348e62e5e7f89c2148e1273f1456382907a1a77a739b0df",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
ZERO, ONE = (Q(0), Q(0)), (Q(1), Q(0))


def emit(**fields):
    print(json.dumps(fields, default=str, sort_keys=True), flush=True)


def read_checked(path, sha):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == sha, path
    return raw


def unique_object(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs)
    return result


def unit(role):
    rows = [{} for _ in range(36)]
    rows[role - 36][0, ()] = ONE
    return rows


def serialize(rows):
    return [[role, phase, mask, value] for role, row in enumerate(rows, 36)
            for (phase, mask), value in sorted(row.items())]


def sector_coefficients(row, sector):
    table = {}
    for (phase, body), coefficient in row.items():
        key = (phase % 2, body)
        value = tuple(a + sector ** (phase // 2) * b
                      for a, b in zip(table.get(key, ZERO), coefficient, strict=True))
        if any(value):
            table[key] = value
        else:
            table.pop(key, None)
    return table


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    root = Path(sys.argv[1]).resolve()
    checked, last_column = [], None

    def timeout(_signum, _frame):
        emit(status="UNRESOLVED_CAP", cap_seconds=CAP, role=ROLE, cut=CUT,
             completed_sectors=checked, last_checked_input_column=last_column)
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(CAP)
    inputs = {name: read_checked((HERE if name in ("check_type_b_root.py", "type_a_laurent.py")
                                else root) / name, pin) for name, pin in PINS.items()}
    caller = json.loads(inputs["7113-CALLER.json"], object_pairs_hook=unique_object)
    app = json.loads(inputs["7481-APPLICATION.json"], object_pairs_hook=unique_object)
    assert app["source_head"] == SOURCE_PREDECESSOR
    assert app["caller_head"] == CALLER
    assert app["caller_sha256"] == PINS["7113-CALLER.json"]
    assert app["claim_decimal"] == "0.003647081039689"
    tape, typ = caller["events"], caller["types"]["B"]
    assert len(tape) == 4783 and caller["stages"] == 17
    assert typ["offset"] == 36 and typ["roles"] == 36 and len(typ["ports"]) == 8
    body78 = [-1, 0] + [int(i in (7, 8)) for i in range(1, 18)]
    assert typ["diagonal"][14:16] == [body78, body78]
    assert tape[967] == tape[1030] == ["B", "IDLE_ONE", 36, [7]]
    assert tape[1138] == ["J", 7, [7, 0, 18, 25], [36, 37, "-1", "1/2"]]
    assert tape[1214:1216] == [["B", "ADD", 37, 36, "-1"], ["B", "ADD", 37, 36, "41/15"]]
    assert tape[1228] == ["B", "ADD", ROLE, 36, "7/30"]
    assert tape[1244] == ["B", "ADD", 36, ROLE, "-982"]
    engine = run_path(str(HERE / "type_a_laurent.py"))
    propagate = run_path(str(HERE / "check_type_b_root.py"))["propagate"]
    add, scale = engine["add_scaled"], engine["scaled"]
    lo, hi = map(Q, app["directed_crossing_bracket"])
    power = run_path(str(root / "pricing.py"))["power_bounds"]
    gross = [8 * (power(8, hi)[0] + power(9, hi)[0] - power(17, lo)[1]),
             8 * (power(8, lo)[1] + power(9, lo)[1] - power(17, hi)[0])]
    assert Q("0.33985048763130562") <= gross[0] <= gross[1] <= Q("0.33985048763130563")

    emit(status="START", comparator=HEAD, application_source_predecessor=SOURCE_PREDECESSOR,
         caller=CALLER, pins=PINS, role=ROLE, cut=CUT,
         cap_seconds=CAP, first_changed_state_deadline=1228, first_outward_read=1244,
         paid_delta={}, projected_productive_delta={8: 8, 9: 8, 17: -8}, gross_raw=gross)

    # The queried input has no contact before ADD949. Replay every earlier
    # event because the selected output row may depend on other inputs.
    prefix_row, prefix_column = {}, None
    for source in range(36, 72):
        rows = unit(source)
        for event in tape[:CUT]:
            propagate(rows, event, add, scale)
        prefix_row[source] = rows[ROLE - 36]
        if source == ROLE:
            prefix_column = rows
        last_column = source
    assert prefix_column is not None
    assert sector_coefficients({(0, ()): ONE, (2, ()): ONE}, -1) == {}
    assert sector_coefficients({(0, (7,)): ONE}, 1) == {(0, (7,)): ONE}
    results = {}
    for sector in (1, -1):
        row_fail = [[source, phase, mask, value]
                    for source, terms in prefix_row.items() if source != ROLE
                    for (phase, mask), value in sector_coefficients(terms, sector).items()]
        column_fail = [[dest, phase, mask, value]
                       for dest, terms in enumerate(prefix_column, 36) if dest != ROLE
                       for (phase, mask), value in sector_coefficients(terms, sector).items()]
        own = sector_coefficients(prefix_row[ROLE], sector)
        results[sector] = dict(row_contamination=row_fail, column_contamination=column_fail,
                               own_terms=[[phase, mask, value] for (phase, mask), value in own.items()],
                               exact_rank8_primitive=own == {(0, (7,)): ONE} and
                                                     not row_fail and not column_fail)
        checked.append(sector)
    if not all(result["exact_rank8_primitive"] for result in results.values()):
        emit(status="EXCLUDED_LITERAL_SEAM", sectors=results, unresolved=[],
             scope="literal coordinate e50 and no changed paid clocks")
        signal.alarm(0)
        return

    # Check the literal suffix on a fresh formal cut coordinate. The physical
    # fresh-input and adjoint checks are separate gates.
    suffix = unit(ROLE)
    for event in tape[CUT:]:
        propagate(suffix, event, add, scale)
    expected = unit(ROLE)
    expected[ROLE - 36] = {(3, (8,)): ONE}
    suffix_match = all(sector_coefficients(x, sign) == sector_coefficients(y, sign)
                       for x, y in zip(suffix, expected, strict=True) for sign in (1, -1))
    emit(status="ISOLATED_STAGE7_SURVIVOR" if suffix_match else "EXCLUDED_FIXED_SUFFIX",
         sectors=results, suffix_terms=serialize(suffix), suffix_match=suffix_match,
         unresolved=["physical exposure, fresh admission, adjoint, complete signed price"]
         if suffix_match else [])
    signal.alarm(0)


if __name__ == "__main__":
    main()
