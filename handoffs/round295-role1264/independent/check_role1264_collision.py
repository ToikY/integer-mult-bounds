"""Find and replay a minimum-support collision on the fixed chart515 bank."""
import argparse
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import gcd
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "ROLE902-WORD.json.gz":"6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "ROLE902-APPLICATION.json":"a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "7113-CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
ROLE, CUT, CHART, CAP = 1264, 38880, 515, 30
BANK = [446, 1203, ROLE]
UNIT = 1125*2**25


def emit(**record):
    print(dumps(record,sort_keys=True,default=str),flush=True)


def unique(pairs):
    obj=dict(pairs)
    assert len(obj)==len(pairs),"duplicate JSON key"
    return obj


def canonical(x):
    return dumps(x,sort_keys=True,separators=(",",":")).encode()


def span(basis):
    v={0}
    for a in basis:
        assert a not in v and 0<a<512
        v.update(a^x for x in tuple(v))
    return v


@cache
def exact(value):
    x=Fraction(value)
    assert x
    return x.numerator,x.denominator


class State:
    def __init__(self,word,spaces,rows):
        self.public=word["public"]
        self.chart=word["initial"]+[None]*word["owned_fields"]
        self.rows=rows+[{} for _ in range(word["owned_fields"])]
        self.owners={}
        self.spaces=spaces

    def apply(self,i,event):
        op,role,*tokens=event
        if op=="INIT":
            assert role>=self.public and not self.rows[role] and self.chart[role] is None and role not in self.owners
            self.chart[role]=tokens[0]
            self.owners[role]=i
        elif op=="CLEAR":
            assert self.chart[role]==tokens[0] and role in self.owners
            self.chart[role]=None
            self.rows[role]={}
            del self.owners[role]
        elif op=="MOVE":
            a,b,owned=tokens
            assert self.chart[role]==a and owned==(role>=self.public)==(role in self.owners)
            assert self.spaces[a]<self.spaces[b] or owned and self.spaces[b]<self.spaces[a]
            self.chart[role]=b
        else:
            assert op in ("ADD","COPY","SCALE")
            source=role if op=="SCALE" else tokens[0]
            assert self.chart[role]==self.chart[source]==tokens[-1] and ((role==source)==(op=="SCALE"))
            p,q=exact(tokens[-2])
            read=self.rows[source]
            changed={}
            for j,value in read.items():
                scaled,rem=divmod(value*p,q)
                assert not rem
                if scaled:
                    changed[j]=scaled
            if op=="ADD":
                write=self.rows[role]
                for j,value in changed.items():
                    total=write.get(j,0)+value
                    if total:
                        write[j]=total
                    else:
                        write.pop(j,None)
            else:
                if op=="COPY":
                    assert not self.rows[role] and role in self.owners
                self.rows[role]=changed


def run_to_cut(word, spaces, rows, progress):
    state = State(word, spaces, rows)
    for i, event in enumerate(word["program"][:CUT]):
        progress["clock"] = i
        state.apply(i, event)
    assert [j for j, k in enumerate(state.chart) if k == CHART] == BANK
    return state


def primitive(probe):
    scale = gcd(*probe.values())
    assert scale and all(probe.values())
    if probe[ROLE] < 0:
        scale = -scale
    return {j: n//scale for j, n in sorted(probe.items())}


def collision(rows, public):
    # Every separating difference contains x1264. Its column is UNIT*e1264.
    assert [r.get(ROLE, 0) for r in rows] == [0, 0, UNIT]
    singles = []
    for j in range(public):
        if j != ROLE and not rows[0].get(j) and not rows[1].get(j) and rows[2].get(j):
            singles.append(j)
    if singles:
        j = singles[0]
        return primitive({j: UNIT, ROLE: -rows[2][j]}), singles, 0
    # Two donor vectors can cancel iff they are on the same nonzero line.
    # Zero lines cannot help because the complete singleton pass found none.
    line = {}
    pairs = []
    nonzero_columns = 0
    for j in range(public):
        if j == ROLE:
            continue
        a, b, h = (r.get(j, 0) for r in rows)
        pivot = a or b
        if not pivot:
            continue
        nonzero_columns += 1
        direction = Fraction(a, pivot), Fraction(b, pivot)
        effective = Fraction(h, pivot)
        if direction in line:
            i, x, old = line[direction]
            if old != effective:
                w = rows[2].get(i, 0)*pivot - h*x
                assert w
                pairs.append((i, j, primitive({i: UNIT*pivot, j: -UNIT*x, ROLE: -w})))
        else:
            line[direction] = j, pivot, effective
    assert pairs, "no collision of cardinality three"
    return min(pairs, key=lambda t: t[:2])[2], singles, nonzero_columns


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    args = parser.parse_args()
    start = perf_counter()
    progress = {"stage": "authenticate", "clock": None}

    def cap(_sig, _frame):
        emit(status="INDEPENDENT_CAP", progress=progress, completed=0, cap_seconds=CAP, seconds=perf_counter()-start)
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(CAP)
    data = {p: (args.input_root/p).read_bytes() for p in PINS}
    assert {p: sha256(raw).hexdigest() for p, raw in data.items()} == PINS
    raw = decompress(data["ROLE902-WORD.json.gz"])
    assert sha256(raw).hexdigest() == WORD
    word = loads(raw, object_pairs_hook=unique)
    app = loads(data["ROLE902-APPLICATION.json"], object_pairs_hook=unique)
    caller = loads(data["7113-CALLER.json"], object_pairs_hook=unique)
    assert word["public"] == 1501 and len(word["program"]) == 76490 and caller["stages"] == 17
    assert app["status"].startswith("PASS_") and app["candidate_canonical_sha256"] == WORD
    assert app["caller_sha256"] == PINS["7113-CALLER.json"] and Fraction(app["claim"]) == Fraction("0.003648411294790")
    tape = word["program"]
    public = word["public"]
    assert ROLE not in set(word["live"]) | {r+112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert word["initial"][ROLE] == 3 and word["frames"][3] == []
    assert word["frames"][CHART] == [51, 146, 268]
    contacts = [(i,e) for i,e in enumerate(tape[:CUT]) if e[1] == ROLE or e[0] in ("ADD", "COPY") and e[2] == ROLE]
    assert contacts == [(29218,["ADD",ROLE,917,"1",3]), (32344,["ADD",ROLE,932,"1",3]),
                        (32479,["ADD",ROLE,899,"-1",3]), (38879,["MOVE",ROLE,3,CHART,False])]
    spaces = [span(v) for v in word["frames"]]
    assert len(spaces[CHART]) == 8
    progress["stage"] = "all exact public coefficients at cut"
    state = run_to_cut(word, spaces, [{j: UNIT} for j in range(public)], progress)
    assert [j for j, row in enumerate(state.rows) if row.get(ROLE)] == [ROLE]
    rows = [state.rows[r] for r in BANK]
    progress["stage"] = "minimum support search"
    probe, size_two_cases, nonzero_columns = collision(rows, public)
    assert len(probe) == (2 if size_two_cases else 3)
    assert all(not sum(row.get(j,0)*v for j,v in probe.items()) for row in rows)
    progress["stage"] = "independent scalar forwards of zero and collision"
    results = []
    for x in ({}, probe):
        y = run_to_cut(word, spaces, [{0: x[j]*UNIT} if j in x else {} for j in range(public)], progress)
        assert all(not y.rows[r] for r in BANK)
        results.append({"input":x,"chart515_bank":[0]*len(BANK),"required_original_x1264":x.get(ROLE,0)})
    assert results[0]["required_original_x1264"] != results[1]["required_original_x1264"]
    alarm(0)
    emit(status="PASS_INDEPENDENT_FIXED_1264_READOUT_COLLISION", cases_completed=1, unresolved_in_scope=[],
         cut=CUT, chart=CHART, role=ROLE, complete_bank=BANK, pure_x1264_direction={ROLE:1},
         probes=results, minimal_input_support=len(probe), support_two_candidates_checked=public-1,
         support_two_collisions=len(size_two_cases), collision_public_indices_with_x1264=size_two_cases,
         nonzero_donor_columns_examined_in_support_three_search=nonzero_columns,
         forward_rows_sha256=sha256(canonical(dict(zip(BANK,rows,strict=True)))).hexdigest(),
         word_canonical_sha256=WORD, caller_head=CALLER, input_pins=PINS, cap_seconds=CAP,
         seconds=perf_counter()-start)


if __name__ == "__main__":
    main()
