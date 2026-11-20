"""Test each frozen pair of idle masks at either original event clock."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import time

OPERATOR_SHA = "36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349"

def pinned(path,sha):
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=sha:
        raise ValueError(path)
    return data

def difference(actual,expected,reverse):
    for i,(left,right) in enumerate(zip(actual,expected,strict=True)):
        for monomial in sorted(left.keys()|right.keys()):
            delta=left.get(monomial,0)^right.get(monomial,0)
            if delta:
                j=(delta & -delta).bit_length()-1
                return dict(reverse=reverse,output=i,input=j,monomial=monomial,
                            actual=(left.get(monomial,0)>>j)&1,expected=(right.get(monomial,0)>>j)&1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("caller",type=Path)
    p.add_argument("operator",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    clock=time.monotonic()
    caller=json.loads(gzip.decompress(pinned(a.caller,"757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b")))
    pinned(a.operator,OPERATOR_SHA)
    m=runpy.run_path(str(a.operator))
    wanted=[{m["caller_monomial"](e["stages"],True):1<<i} for i,e in enumerate(caller["diagonal"])]
    assert all(m["caller_operator"](caller,rev)==wanted for rev in (False,True))
    by_role=defaultdict(list)
    for i,e in enumerate(caller["events"]):
        if e[0]=="IDLE_ONE":
            by_role[e[1]].append((i,e[2]))
    pool=[]
    for role,events in sorted(by_role.items()):
        (i,x),(j,y)=events
        assert set(x).isdisjoint(y)
        for retained in (i,j):
            pool.append(dict(role=role,clocks=[i,j],retained=retained,masks=[x,y],union=sorted(x+y)))
    assert len(pool)==32
    cases=[]
    for case in pool:
        if time.monotonic()-clock>=30:
            break
        lo,hi=case["clocks"]
        edit=[]
        for i,e in enumerate(caller["events"]):
            if i==case["retained"]:
                edit.append(["IDLE_ONE",case["role"],case["union"]])
            elif i not in (lo,hi):
                edit.append(e)
        test=dict(caller,events=edit)
        errs=[difference(m["caller_operator"](test,rev),wanted,rev) for rev in (False,True)]
        cases.append(dict(**case,first_differences=errs))
        if errs==[None,None]:
            break
    a.output.write_text(json.dumps(dict(cases=cases,unvisited=pool[len(cases):],elapsed_s=time.monotonic()-clock),indent=2)+"\n")
    print(len(cases),"tested",sum(c["first_differences"]==[None,None] for c in cases),"survivors")

if __name__=="__main__":
    main()
