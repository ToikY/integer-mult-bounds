"""Single-input formal polynomial replay of saved off-diagonal coefficients."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

caller_bytes=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(caller_bytes).hexdigest()=="757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"
caller=json.loads(gzip.decompress(caller_bytes))
results=json.loads(Path(sys.argv[2]).read_bytes())
assert len(results["cases"])==32 and results["unvisited"]==[]
actual_choices=set()
def scalar(events,i,rev):
    # Six bits per independent D exponent; the full frozen caller contains
    # fewer than 64 occurrences of any one D, even before cancellation.
    bound=[0]*18
    rows=[set() for _ in range(38)]
    rows[i]={0}
    for op,*args in (reversed(events) if rev else events):
        if op=="SWAP":
            a,b=args
            rows[a],rows[b]=rows[b],rows[a]
        elif op in ("ADD","QUERY"):
            a,b=args[::-1] if rev else args
            rows[a]^={v^(op=="QUERY") for v in rows[b]}
        elif op=="IDLE_ONE":
            a,stages=args
            shift=sum(1<<(1+6*(s-1)) for s in stages)
            for s in stages:
                bound[s-1]+=1
            rows[a]={v+shift for v in rows[a]}
        elif op=="LOCAL":
            s,a,b=args
            if rev:
                a,b=b,a
            shift=1<<(1+6*(s-1))
            bound[s-1]+=1
            rows[b]={v+shift for v in rows[b]^{v^1 for v in rows[a]}}
            rows[a]={v+shift for v in rows[a]}
        else:
            raise ValueError(op)
    assert max(bound)<64
    return rows

for trial in results["cases"]:
    a=trial["role"]
    matches=[i for i,e in enumerate(caller["events"]) if e[:2]==["IDLE_ONE",a]]
    assert matches==trial["clocks"] and trial["retained"] in matches
    union=sorted(set().union(*(caller["events"][k][2] for k in matches)))
    actual_choices.add((a,trial["retained"]))
    edits=[(["IDLE_ONE",a,union] if i==trial["retained"] else e)
           for i,e in enumerate(caller["events"]) if i not in set(matches)-{trial["retained"]}]
    assert len(edits)==797 and {w["reverse"] for w in trial["first_differences"]}=={False,True}
    for w in trial["first_differences"]:
        assert w["input"]!=w["output"] and w["actual"]==1 and w["expected"]==0
        mono=w["monomial"]
        witness=mono[0]+sum(k<<(1+6*j) for j,k in enumerate(mono[1:]))
        assert witness in scalar(edits,w["input"],w["reverse"])[w["output"]]
        assert not scalar(caller["events"],w["input"],w["reverse"])[w["output"]]
assert len(actual_choices)==32
print("PASS: 64 exact off-diagonal counterexamples; all 32 endpoint fusions fail in both orientations")
