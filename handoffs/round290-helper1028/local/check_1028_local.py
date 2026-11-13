"""One exact chart23 repair gate before original MOVE36877."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

CAP, CUT = 30, 36877
BANK, ROLE = (25, 797, 1024, 1025), 797
WORD = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
PINS = {
    "COMPOSED-WORD.json.gz": "926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
    "COMPOSED-APPLICATION.json": "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
PREPEND = (36416, ["ADD", 1024, 1028, "1/2", 3])
DELETE = (36418, 36419)
REPLACE = (36421, ["MOVE", 1028, 3, 302, False])


def emit(**record):
    print(json.dumps(record, sort_keys=True, default=str), flush=True)


def add(row, index, amount):
    value = row.get(index, Q(0)) + amount
    if value:
        row[index] = value
    else:
        row.pop(index, None)


def pullback(program, role):
    covector = {role: Q(1)}
    for op, target, *args in reversed(program):
        coefficient = covector.get(target, 0)
        if not coefficient or op == "MOVE":
            continue
        if op == "SCALE":
            covector[target] *= Q(args[0])
        elif op in ("INIT", "CLEAR"):
            covector.pop(target)
        else:
            assert op in ("ADD", "COPY")
            if op == "COPY":
                covector.pop(target)
            add(covector, args[0], coefficient*Q(args[1]))
    assert all(role < 1501 for role in covector)
    return covector


def value(row, probe):
    return sum(coefficient*probe.get(role, 0) for role,coefficient in row.items())


def eliminate(offer):
    pivots = {}
    for name, row in offer.items():
        coefficients = {name: Q(1)}
        row = row.copy()
        for pivot,(previous, recipe) in sorted(pivots.items()):
            q = row.get(pivot, 0)
            if not q:
                continue
            for role,c in previous.items():
                add(row,role,-q*c)
            for role,c in recipe.items():
                add(coefficients,role,-q*c)
        if row:
            index = min(row)
            lead = row[index]
            pivots[index] = ({i:q/lead for i,q in row.items()},
                             {i:q/lead for i,q in coefficients.items()})
    return pivots


def express(pivots, target):
    residual = target.copy()
    recipe = {}
    for pivot,(row, step) in sorted(pivots.items()):
        q = residual.get(pivot, 0)
        if not q:
            continue
        for r,c in row.items():
            add(residual,r,-q*c)
        for r,c in step.items():
            add(recipe,r,q*c)
    return residual, recipe


def separator(pivots, residual):
    key = min(residual)
    assert key not in pivots
    probe = {key: 1/residual[key]}
    for role,(row,_) in sorted(pivots.items(),reverse=True):
        q = value(row,probe)
        if q:
            probe[role] = -q
    assert value(residual,probe) == 1
    return probe


def span(frame):
    space = {0}
    for q in frame:
        assert q not in space
        space |= {q ^ x for x in space}
    return space


def forward(program, initial, probe):
    chart = dict(enumerate(initial))
    rows = probe.copy()
    for op,r,*args in program:
        if op == "MOVE":
            assert chart[r] == args[0] and args[2] == (r>=1501)
            chart[r] = args[1]
        elif op == "INIT":
            assert r not in chart and r not in rows
            chart[r] = args[0]
        elif op == "CLEAR":
            assert chart.pop(r) == args[0]
            rows.pop(r,None)
        elif op == "SCALE":
            assert chart[r] == args[1]
            if r in rows:
                rows[r] *= Q(args[0])
        else:
            assert op in ("ADD","COPY") and chart[r] == chart[args[0]] == args[2]
            assert op != "COPY" or r not in rows
            add(rows,r,Q(args[1])*rows.get(args[0],0))
    return chart, rows


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    root = Path(sys.argv[1])
    stage = "authenticating"

    def timeout(_signum, _frame):
        emit(status="UNRESOLVED_CAP", last_stage=stage, cut=CUT, cap_seconds=CAP, unresolved=[CUT])
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(CAP)
    raw = {p:(root/p).read_bytes() for p in PINS}
    assert {p:sha256(v).hexdigest() for p,v in raw.items()} == PINS
    canonical = decompress(raw["COMPOSED-WORD.json.gz"])
    app = json.loads(raw["COMPOSED-APPLICATION.json"])
    assert sha256(canonical).hexdigest() == WORD == app["candidate_canonical_sha256"]
    assert app["status"] == "PASS_COMPOSED_7481_7542_FINAL_APPLICATION"
    assert app["claim_decimal"] == "0.003647969120276"
    assert json.loads(raw["7113-CALLER.json"])["stages"] == 17
    word = json.loads(canonical)
    tape = word["program"]
    assert len(tape) == 76491 and word["public"] == 1501
    assert tape[36415:36420] == [
        ["ADD",1338,1028,"2",3], ["MOVE",1024,3,23,False],
        ["ADD",797,1024,"-1",23], ["MOVE",1028,3,23,False],
        ["ADD",1024,1028,"1/2",23],
    ]
    assert tape[36421] == ["MOVE",1028,23,302,False]
    assert tape[36864:36866] == [["MOVE",1025,3,23,False], ["ADD",797,1025,"-1",23]]
    assert tape[CUT] == ["MOVE",797,23,292,False]
    spans = [span(word["frames"][c]) for c in (3,23,302)]
    assert spans[0] < spans[1] < spans[2]
    assert list(map(len,spans)) == [1,2,8]
    H = run_path(str(root/"pricing.py"))["power_bounds"]
    lo,hi = map(Q,app["raw_crossing"])
    gross = [17*(1+H(2,hi)[0]-H(3,lo)[1]),17*(1+H(2,lo)[1]-H(3,hi)[0])]
    assert Q("0.11812076067945571") <= gross[0] <= gross[1] <= Q("0.11812076067945572")

    prefix = tape[:CUT]
    edited = []
    for i,event in enumerate(prefix):
        if i == PREPEND[0]:
            edited.append(PREPEND[1])
        if i not in DELETE:
            edited.append(REPLACE[1] if i == REPLACE[0] else event)
    stage = "forming exact covectors"
    old = {r:pullback(prefix,r) for r in BANK}
    new = {r:pullback(edited,r) for r in BANK}
    assert all(old[r]==new[r] for r in BANK if r != ROLE)
    expected = {j:q/2 for j,q in pullback(tape[:36416],1028).items()}
    delta = old[ROLE].copy()
    for j,q in new[ROLE].items():
        add(delta,j,-q)
    assert delta == expected

    stage = "checking exact support and probe"
    full = eliminate(new)
    residue, recipe = express(full,old[ROLE])
    probe = {}
    if residue:
        probe = separator(full,residue)
        assert all(value(row,probe)==0 for row in new.values()) and value(old[ROLE],probe)==1
        status = "EXCLUDED_FIXED_CHART23_BANK"
        recipe = {}
    else:
        donors = eliminate({r:row for r,row in new.items() if r != ROLE})
        new_mod,_ = express(donors,new[ROLE])
        if not new_mod:
            remainder, recipe = express(donors,delta)
            assert not remainder
            recipe[ROLE] = Q(1)
        status = "FIXED_BANK_SURVIVOR" if recipe.get(ROLE) else "EXCLUDED_REQUIRED_NONZERO_SELF"
    old_chart, old_values = forward(prefix,word["initial"],probe)
    new_chart, new_values = forward(edited,word["initial"],probe)
    assert all(tuple(sorted(r for r,ch in c.items() if ch==23)) == BANK for c in (old_chart,new_chart))
    assert all(old_values.get(r,0) == value(old[r],probe) and new_values.get(r,0) == value(new[r],probe)
               for r in BANK)
    emit(status=status, source_word=WORD, pins=PINS, cut=CUT, chart=23, bank=BANK,
         one_case_completed=True, elapsed_cap=CAP, rank=len(full), gross_raw=gross, separator=probe,
         old_values={r:old_values.get(r,0) for r in BANK}, edited_values={r:new_values.get(r,0) for r in BANK},
         normalized_required_delta=value(expected,probe), repair_coefficients=recipe,
         unresolved=[] if residue else ["signed physical direct move and complete admitted replay"] if recipe.get(ROLE) else [])
    signal.alarm(0)


if __name__ == "__main__":
    main()
