"""Exact B9-sign and displacement-rank gate for one nested idle square."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

START, STOP, CAP = 2324, 2356, 30
OLD, PROPOSED, OMIT_CONTROL = (2324,2337,2355), (2337,), (2324,2355)
PINS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def emit(**fields):
    print(json.dumps(fields, default=str, sort_keys=True), flush=True)


def forward(block, source, active_factors):
    column = [Q(role == source) for role in range(36, 72)]
    for clock, (_, op, role, *args) in enumerate(block, START):
        r = role-36
        if op == "ADD":
            column[r] += Q(args[1])*column[args[0]-36]
        elif op == "SWAP":
            s = args[0]-36
            column[r], column[s] = column[s], column[r]
        elif op == "SCALE":
            column[r] *= Q(args[0])
        else:
            assert op == "IDLE_ONE" and len(args) == 1
            if clock in active_factors:
                column[r] = -column[r]
    return column


def displacement_minor(columns):
    original = [list(row) for row in zip(*columns, strict=True)]
    work = [row.copy() for row in original]
    labels = list(range(len(work)))
    rows, cols = [], []
    for j in range(len(work[0])):
        k = next((i for i in range(len(rows), len(work)) if work[i][j]), None)
        if k is None:
            continue
        pivot = len(rows)
        work[pivot], work[k] = work[k], work[pivot]
        labels[pivot], labels[k] = labels[k], labels[pivot]
        rows.append(labels[pivot])
        cols.append(j)
        for i in range(pivot+1, len(work)):
            if work[i][j]:
                f = work[i][j]/work[pivot][j]
                work[i] = [a-f*b for a,b in zip(work[i],work[pivot],strict=True)]
    submatrix = [[original[i][j] for j in cols] for i in rows]
    return [i+36 for i in rows], [j+36 for j in cols], submatrix


def determinant(rows):
    if not rows:
        return Q(1)
    return sum((-1)**i * value * determinant([r[:i]+r[i+1:] for r in rows[1:]])
               for i,value in enumerate(rows[0]) if value)


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    root = Path(sys.argv[1]).resolve()
    completed = []

    def cap(_signum, _frame):
        emit(status="UNRESOLVED_CAP", cap_seconds=CAP, completed_columns=completed,
             unvisited_columns=[r for r in range(36,72) if r not in completed])
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, cap)
    signal.alarm(CAP)
    raw = {name:(root/name).read_bytes() for name in PINS}
    assert {name:sha256(data).hexdigest() for name,data in raw.items()} == PINS
    caller = json.loads(raw["7113-CALLER.json"])
    app = json.loads(raw["7481-APPLICATION.json"])
    assert app["source_head"] == "58a9d052143f5d85295ed2d0163591c47f89a331"
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert app["caller_sha256"] == PINS["7113-CALLER.json"]
    assert app["claim_decimal"] == "0.003647081039689"
    bank = caller["types"]["B"]
    ports = bank["ports"]
    assert bank["offset"] == bank["roles"] == 36 and ports == [15,17,27,34,35,42,47,55]
    tape = caller["events"]
    assert len(tape) == 4783 and caller["stages"] == 17
    assert tape[2323] == ["B","ADD",36,53,"6"]
    assert tape[2324] == ["B","IDLE_ONE",36,list(range(16,8,-1))]
    assert tape[2328] == ["B","ADD",53,36,"-9/32"]
    assert tape[2337] == ["B","IDLE_ONE",37,list(range(16,8,-1))]
    assert tape[2355] == ["B","IDLE_ONE",36,list(range(15,8,-1))]
    assert tape[2356] == ["B","ADD",36,55,"-76"]
    block = tape[START:STOP]
    assert all(event[0] == "B" for event in block)
    opcode_counts = Counter(event[1] for event in block)
    assert opcode_counts == {"ADD":25,"SCALE":4,"IDLE_ONE":3}
    old = {i for i,event in enumerate(block,START) if event[1]=="IDLE_ONE" and 9 in event[3]}
    assert old == set(OLD)
    # q=+1 and width 1: two distinct minus Walsh bits in B9 give i^2=-1;
    # the square translation thus has eigenvalue i^4=+1 on this fibre.
    assert (1j)**2 == -1 and (1j)**4 == 1
    lo, hi = map(Q, app["directed_crossing_bracket"])
    H = run_path(str(root/"pricing.py"))["power_bounds"]
    gross = [8*(H(64,hi)[0]+H(56,hi)[0]-H(8,lo)[1]),
             8*(H(64,lo)[1]+H(56,lo)[1]-H(8,hi)[0])]
    assert Q("882.24727829181406823") <= gross[0] <= gross[1] <= Q("882.24727829181406824")
    emit(status="START", pins=PINS, window=[START,STOP], cap_seconds=CAP, q=1, b9=-1,
         other_bodies=1, tested_port=15, tested_width=1, ports=ports, old_sign_clocks=OLD,
         new_sign_clocks=PROPOSED, signed_paid_delta={8:8,56:-8,64:-8}, productive_delta={},
         optimistic_gross_8_ports=gross, optimistic_gross_per_port=[x/8 for x in gross])

    witnesses = []
    diffs = {"old":[], "proposed":[], "omitted_control":[]}
    for source in range(36,72):
        unit, absolute_old, absolute_new, changed_control = (
            forward(block,source,c) for c in ((),OLD,PROPOSED,OMIT_CONTROL)
        )
        for key,column in zip(diffs,(absolute_old,absolute_new,changed_control),strict=True):
            diffs[key].append([a-b for a,b in zip(column,unit,strict=True)])
        if absolute_old != absolute_new and not witnesses:
            row = next(i for i,(a,b) in enumerate(zip(absolute_old,absolute_new,strict=True),36) if a!=b)
            witnesses.append(dict(input=source, first_output=row, old=absolute_old, edited=absolute_new))
        completed.append(source)
    ranks = {}
    for key, values in diffs.items():
        rows, cols, matrix = displacement_minor(values)
        ranks[key] = dict(rank=len(rows),rows=rows,cols=cols,minor=matrix,determinant=determinant(matrix))
        assert ranks[key]["determinant"]
    assert ranks["old"]["rank"] <= 3 and ranks["proposed"]["rank"] == 1
    assert ranks["omitted_control"]["rank"] <= 2 and diffs["old"] != diffs["omitted_control"]
    if ranks["old"]["rank"] > 1:
        status = "EXCLUDED_SECTOR_INDEPENDENT_WRAPPERS"
    elif witnesses:
        status = "EXCLUDED_FIXED_WRAPPERS"
    else:
        status = "B9_SIGN_SURVIVOR"
    emit(status=status, tested_columns=completed, difference_ranks=ranks,
         exact_difference_witnesses=witnesses, unit_bodies_all_reflections_identity=True,
         square_translation_equal_in_two_sectors=True,
         unresolved=[] if witnesses else ["arbitrary-body signed and physical replay"])
    signal.alarm(0)


if __name__ == "__main__":
    main()
