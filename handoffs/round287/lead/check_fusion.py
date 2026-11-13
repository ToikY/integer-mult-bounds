"""Exact support gate for the fixed owned1521 descent."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
DROP = {30520,30532,30534,30537,30538,30541,30543,39947,45355,45357}
EDIT = {30545:["INIT",1521,1090],30547:["ADD",1521,1510,"-1/4",1090],
        30551:["MOVE",1521,1090,601,True]}
DONORS = (727,1164,1536,1546,1547)
CUT = 30588


def emit(**result):
    print(json.dumps(result, default=str, sort_keys=True), flush=True)


def spans(vectors):
    result = {0}
    for vector in vectors:
        result |= {vector ^ old for old in result}
    return result


def value(row, probe):
    return sum((coefficient*probe.get(j,0) for j,coefficient in row.items()), Q(0))


def main():
    stage = "source authentication"

    def capped(_signum, _frame):
        emit(status="UNRESOLVED_CAP", last_stage=stage, cut=CUT, seconds_cap=30)
        raise SystemExit(124)

    signal(SIGALRM,capped)
    alarm(30)
    root = Path("inputs")
    raw = {name:(root/name).read_bytes() for name in PINS}
    assert {name:sha256(data).hexdigest() for name,data in raw.items()} == PINS
    app = json.loads(raw["7481-APPLICATION.json"])
    payload = decompress(raw["7481-WORD.json.gz"])
    assert sha256(payload).hexdigest() == app["candidate_canonical_sha256"]
    word = json.loads(payload)
    tape = word["program"]
    assert word["public"] == 1501 and len(tape) == 76475
    assert tape[30537] == ["MOVE",1520,1090,470,True]
    assert tape[30551] == ["MOVE",1521,470,601,True]
    assert tape[30586][:4] == ["ADD",402,727,"-4"]
    assert tape[CUT][0:3] == ["ADD",1536,402]
    assert spans(word["frames"][601]) < spans(word["frames"][470]) < spans(word["frames"][1090])
    caller = json.loads(raw["7113-CALLER.json"])
    assert caller["stages"] == 17
    price = run_path(str(root/"pricing.py"))["power_bounds"]
    lo,hi = map(Q,app["directed_crossing_bracket"])
    gross = [17*(1+price(2,hi)[0]-price(3,lo)[1]),17*(1+price(2,lo)[1]-price(3,hi)[0])]
    assert 0 < gross[0] <= gross[1] < 1
    gate = run_path(str(root/"gate.py"))
    cut_rows = gate["exact_cut_rows"]
    edited = [EDIT.get(i,event) for i,event in enumerate(tape[:CUT]) if i not in DROP]
    active = dict(enumerate(word["initial"]))
    for op,dest,*args in edited:
        if op == "INIT":
            assert dest not in active
            active[dest] = args[0]
        elif op == "CLEAR":
            assert active.pop(dest) == args[0]
        elif op == "MOVE":
            assert active[dest] == args[0] and args[2] == (dest >= word["public"])
            active[dest] = args[1]
        elif op in ("ADD","COPY"):
            assert active[dest] == active[args[0]] == args[-1]
        else:
            assert op == "SCALE" and active[dest] == args[-1]
    assert sorted(j for j,ch in active.items() if ch==470) == [402,*DONORS]
    stage = "edited chronology authenticated"
    target, = cut_rows(tape[:30531],[1510],1501)
    old, = cut_rows(tape[:CUT],[402],1501)
    new,*rows = cut_rows(edited,[402,*DONORS],1501)
    assert {j:old.get(j,0)-new.get(j,0) for j in old.keys()|new.keys()
            if old.get(j,0)!=new.get(j,0)} == target
    assert not rows[3] and rows[2] == {j:-c/4 for j,c in rows[4].items()}
    stage = "exact rows reconstructed"
    pivots = gate["basis"](rows)
    residual,coeff = gate["representation"](pivots,target)
    probe = {}
    if residual:
        free = min(residual)
        assert free not in pivots
        probe[free] = 1/residual[free]
        for j,(row,_) in sorted(pivots.items(),reverse=True):
            correction = value(row,probe)
            if correction:
                probe[j] = -correction
        assert all(value(row,probe)==0 for row in rows) and value(target,probe)==1
    alarm(0)
    emit(status="FIXED_BANK_EXCLUDED" if residual else "SUPPORT_SURVIVES",
         cut=CUT, donors=DONORS, rank=len(pivots), gross=gross,
         probe=probe, donor_values=[value(row,probe) for row in rows],
         old402=value(old,probe), edited402=value(new,probe), source=value(target,probe),
         coefficients={DONORS[i]:c for i,c in coeff.items()} if not residual else {},
         pins=PINS, unresolved=[])


if __name__ == "__main__":
    main()
