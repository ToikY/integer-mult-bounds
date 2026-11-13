"""Independently replay the fixed nested Type B idle and its exact rank gate."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

HERE = Path(__file__).resolve().parent
ENGINE = "875041e1b30cf053ece208a00d56567b4008877753db5a04e46a59fa2947d1bb"
START, STOP, OFFSET, CAP = 2324, 2356, 36, 30
ROLES = list(range(OFFSET,72))
ACTIVE, RETAINED, REMOVED = (2324,2337,2355), 2337, (2324,2355)


def emit(**record):
    print(dumps(record,sort_keys=True,default=str),flush=True)


def determinant(rows):
    if not rows:
        return Q(1)
    return sum((-1)**j * v * determinant([r[:j]+r[j+1:] for r in rows[1:]])
               for j,v in enumerate(rows[0]) if v)


def rank_and_minor(matrix):
    # Select active columns first by exact elimination of transposed rows,
    # then reconstruct and independently evaluate the selected original minor.
    width = len(matrix[0])
    cols = [list(col) for col in zip(*matrix,strict=True)]
    reduced = {}
    chosen = []
    for j,col in enumerate(cols):
        current = col.copy()
        for i,pivot in reduced.items():
            factor = current[i]
            if factor:
                current = [a-factor*b for a,b in zip(current,pivot,strict=True)]
        i = next((i for i,value in enumerate(current) if value),None)
        if i is not None:
            weight = current[i]
            reduced[i] = [v/weight for v in current]
            chosen.append(j)
    assert len(cols) == width and len(reduced) == len(chosen)
    rows = list(reduced)
    minor = [[matrix[i][j] for j in chosen] for i in rows]
    det = determinant(minor)
    assert det
    return {"rank":len(rows),"rows":[i+OFFSET for i in rows],"cols":[j+OFFSET for j in chosen],
            "minor":minor,"determinant":det}


def displacement(a,b):
    return [[x-y for x,y in zip(r,s,strict=True)] for r,s in zip(a,b,strict=True)]


def check_primary(blocks, ranks, mismatch, args, kit):
    raw = args.lead_receipt.read_bytes()
    assert sha256(raw).hexdigest() == args.lead_sha256
    start, lead = [loads(line,object_pairs_hook=kit["unique"]) for line in raw.splitlines()]
    assert start["window"] == [START,STOP] and start["old_sign_clocks"] == list(ACTIVE)
    assert start["new_sign_clocks"] == [RETAINED] and start["tested_width"] == start["q"] == 1
    assert start["b9"] == -1 and lead["tested_columns"] == ROLES
    assert lead["status"] == ("EXCLUDED_SECTOR_INDEPENDENT_WRAPPERS" if ranks["old"]["rank"] > 1
                              else "EXCLUDED_FIXED_WRAPPERS" if mismatch else "B9_SIGN_SURVIVOR")
    for label, ours in ranks.items():
        theirs = lead["difference_ranks"][label]
        assert ours["rank"] == theirs["rank"]
        m = [[blocks[label][i-OFFSET][j-OFFSET] for j in theirs["cols"]] for i in theirs["rows"]]
        assert m == [[Q(v) for v in row] for row in theirs["minor"]]
        assert determinant(m) == Q(theirs["determinant"])
    if mismatch:
        exact = {k:v for k,v in mismatch.items() if k not in ("old_entry","edited_entry")}
        assert loads(dumps(exact,default=str)) == lead["exact_difference_witnesses"][0]


def main():
    assert __debug__ and version_info[:2] == (3,12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", nargs="?", type=Path)
    parser.add_argument("lead_sha256", nargs="?")
    args = parser.parse_args()
    started = perf_counter()
    visited = []

    def cap(_signal,_frame):
        emit(status="INDEPENDENT_CAP", completed_rows=visited, unvisited_rows=[r for r in ROLES if r not in visited],
             cap_seconds=CAP,seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    engine = HERE/"check_body2_pullback.py"
    assert sha256(engine.read_bytes()).hexdigest() == ENGINE
    kit = run_path(str(engine))
    pins=kit["PINS"]
    raw={p:(args.root/p).read_bytes() for p in pins}
    assert {p:sha256(data).hexdigest() for p,data in raw.items()} == pins
    caller=loads(raw["inputs/7113-CALLER.json"],object_pairs_hook=kit["unique"])
    app=loads(raw["inputs/7481-APPLICATION.json"],object_pairs_hook=kit["unique"])
    assert app["caller_head"]==kit["CALLER"] and app["caller_sha256"]==pins["inputs/7113-CALLER.json"]
    tape=caller["events"]
    assert len(tape)==4783 and caller["stages"]==17 and caller["ambient_rank"]==145
    kind=caller["types"]["B"]
    assert kind["offset"]==kind["roles"]==36 and kind["ports"]==[15,17,27,34,35,42,47,55]
    assert tape[2323]==["B","ADD",36,53,"6"] and tape[2328]==["B","ADD",53,36,"-9/32"]
    assert tape[2356]==["B","ADD",36,55,"-76"]
    wide=list(range(16,8,-1))
    narrow=list(range(15,8,-1))
    assert tape[2324]==["B","IDLE_ONE",36,wide] and tape[2337]==["B","IDLE_ONE",37,wide]
    assert tape[2355]==["B","IDLE_ONE",36,narrow]
    block=tape[START:STOP]
    assert all(e[0]=="B" for e in block)
    assert Counter(e[1] for e in block)=={"ADD":25,"SCALE":4,"IDLE_ONE":3}
    new=[["B","IDLE_ONE",36,[16]] if i==2324 else e for i,e in enumerate(block,START) if i!=2355]
    omit=[e for i,e in enumerate(block,START) if i!=2337]
    axes=tuple(range(9+8*(9-1),9+8*9))
    assert axes==tuple(range(73,81))
    state=sum(1<<i for i in axes[:2])
    eigen=kit["conjugate_walsh_eigenvalue"]
    groups=[sum(1<<i for i in range(9+8*j,17+8*j)) for j in range(17)]
    signatures=[eigen(group,state) for group in groups]
    signs=[v[0] for v in signatures]
    assert signs==[1]*8+[-1]+[1]*8 and all(v[1]==0 for v in signatures)
    assert all(eigen(group,state)[0]**2==eigen(group,0)[0]**2==1 for group in groups[8:15])
    assert eigen(groups[15],state)==eigen(groups[15],0)==(1,0) and not state&511
    assert [i for i,e in enumerate(block,START) if e[1]=="IDLE_ONE" and 9 in e[3]]==list(ACTIVE)
    unit=[1]*17
    pull=kit["pulled_row"]
    matrices={"unit":[],"old":[],"proposed":[],"omitted_control":[]}
    for r in ROLES:
        baseline=pull(block,r,unit)
        assert pull(new,r,unit)==pull(omit,r,unit)==baseline
        matrices["unit"].append(baseline)
        for label,t in (("old",block),("proposed",new),("omitted_control",omit)):
            matrices[label].append(pull(t,r,signs))
        visited.append(r)
    diffs={k:displacement(m,matrices["unit"]) for k,m in matrices.items() if k!="unit"}
    ranks={k:rank_and_minor(m) for k,m in diffs.items()}
    assert ranks["old"]["rank"]<=3 and ranks["proposed"]["rank"]==1
    assert ranks["omitted_control"]["rank"]<=2 and diffs["omitted_control"]!=diffs["old"]
    mismatch=kit["first_difference"](matrices["old"],matrices["proposed"])
    assert (args.lead_receipt is None)==(args.lead_sha256 is None)
    if args.lead_receipt:
        check_primary(diffs,ranks,mismatch,args,kit)
    emit(status="PASS_INDEPENDENT_NESTED_IDLE_OBSTRUCTION" if ranks["old"]["rank"]>1 else "INDEPENDENT_FIXED_WRAPPER_CHECK",
         window=[START,STOP],completed_rows=visited,unvisited_rows=[],first_mismatch=mismatch,
         difference_ranks=ranks,unit_body_full_matrix_equal=True,square_translation_same_eigenvalue=True,
         specialization={"width":1,"q":1,"B9":-1,"other_bodies":1,"body9_axes":list(axes),"minus_X_axes":list(axes[:2])},
         wrapper_scope="same induced ordinary wrappers and additive bypass on both fixed fibres, one varying rank-one role action",
         caller_head=kit["CALLER"],input_pins=pins|{"independent/check_body2_pullback.py":ENGINE},
         lead_sha256=args.lead_sha256,cap_seconds=CAP,seconds=perf_counter()-started)
    alarm(0)


if __name__=="__main__":
    main()
