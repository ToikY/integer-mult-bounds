"""Check zero-new-paid removal of frozen BIT packets at the first receiver read."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import time

PIN = "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"

def basis_for(stock):
    basis = {}
    for owner, row in stock:
        terms = 1 << owner
        while row:
            lead = row.bit_length() - 1
            if lead not in basis:
                basis[lead] = row, terms
                break
            other, used = basis[lead]
            row ^= other
            terms ^= used
    return basis

def support(stock, target):
    basis = basis_for(stock)
    missing, terms = target, 0
    for k in sorted(basis, reverse=True):
        if missing >> k & 1:
            missing ^= basis[k][0]
            terms ^= basis[k][1]
    if missing == 0:
        return {"span_rank": len(basis), "synthesis": [a for a, _ in stock if terms >> a & 1]}
    dual = 1 << (missing.bit_length() - 1)
    for k in sorted(basis):
        if (basis[k][0] & dual).bit_count() % 2:
            dual ^= 1 << k
    assert all((row & dual).bit_count() % 2 == 0 for _, row in stock)
    assert (target & dual).bit_count() % 2 == 1
    return {"span_rank":len(basis), "separating_input":hex(dual)}

def pool(word):
    touched = defaultdict(list)
    moves = []
    for clock, event in enumerate(word["program"]):
        op, a, *args = event
        touched[a].append((clock, event))
        if op in ("ADD", "SWAP"):
            touched[args[0]].append((clock, event))
        if op == "MOVE":
            moves.append((clock, a, *args))
    frames = word["frames"]
    result = []
    for clock, a, src, dst in moves:
        uses = touched[a]
        if uses[0][1] != ["INIT", a, src] or uses[-1][1] != ["CLEAR", a, dst]:
            continue
        before = [(n,e) for n,e in uses[1:-1] if n < clock]
        after = [(n,e) for n,e in uses[1:-1] if n > clock]
        if not before or not after:
            continue
        if any(e[:2] != ["ADD", a] for _,e in before) or any(e[0] != "ADD" or e[2] != a for _,e in after):
            continue
        rank = abs(frames[str(src)]["dim"] - frames[str(dst)]["dim"])
        result.append(dict(clock=clock, owner=a, src=src, dst=dst, grade=rank,
                           first=after[0][0], reads=[n for n,_ in after], writes=[n for n,_ in before]))
    return sorted(result,key=lambda e:(-e["grade"],len(e["reads"]),e["clock"]))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("word",type=Path)
    parser.add_argument("out",type=Path)
    args=parser.parse_args()
    start=time.monotonic()
    raw=args.word.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    word=json.loads(gzip.decompress(raw))
    candidates=pool(word)
    scope=candidates[:32]
    by_first={e["first"]:e for e in scope}
    assert len(by_first)==len(scope)
    cells={i:(ch,1<<i) for i,ch in enumerate(word["start"])}
    by_clock={e["clock"]:e for e in scope}
    cases=[]
    for clock,event in enumerate(word["program"]):
        if time.monotonic()-start >= 30:
            break
        op,a,*args_op=event
        if clock in by_first:
            candidate=by_first[clock]
            owner,chart=candidate["owner"],candidate["dst"]
            assert cells[owner][0]==chart and owner==args_op[0]
            # Include even the destination of this ADD. A separating input
            # against this larger set also separates every legal source subset.
            stock=[(b,v) for b,(c,v) in cells.items() if b!=owner and c==chart]
            outcome=support(stock,cells[owner][1])
            cases.append(dict(**candidate,stock_count=len(stock),**outcome))
        if op=="INIT":
            cells[a]=(args_op[0],0)
        elif op=="CLEAR":
            del cells[a]
        elif op=="ADD":
            b,ch=args_op
            assert cells[a][0]==cells[b][0]==ch
            cells[a]=(ch,cells[a][1]^cells[b][1])
        elif op=="MOVE":
            old,new=args_op
            assert cells[a][0]==old
            if clock in by_clock:
                by_clock[clock]["sender_row"]=hex(cells[a][1])
            cells[a]=(new,cells[a][1])
        elif op=="SWAP":
            b,=args_op
            cells[a],cells[b]=cells[b],cells[a]
        else:
            raise ValueError(event)
        if len(cases)==len(scope):
            break
    ids={e["clock"] for e in cases}
    passed={e["clock"] for e in cases if "synthesis" in e}
    receipt=dict(word_gzip=PIN,pool=len(candidates),original_order=[e["clock"] for e in candidates],
                 frozen=[e["clock"] for e in scope],cases=cases,unvisited=[e["clock"] for e in candidates if e["clock"] not in ids],
                 screened_order=[e["clock"] for e in scope if e["clock"] in passed],
                 case_cap=32,wall_cap_s=30,elapsed_s=time.monotonic()-start)
    args.out.write_text(json.dumps(receipt,indent=2)+"\n")
    print(f"Pool {len(candidates)}, tested {len(cases)}, survivors {len(passed)}, open {len(receipt['unvisited'])}")

if __name__=="__main__":
    main()
