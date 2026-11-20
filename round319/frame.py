"""Price arbitrary rational frame replacements of one internal #7830 BIT chart."""
from collections import Counter,defaultdict
from fractions import Fraction
from functools import cache
from pathlib import Path
import argparse,gzip,hashlib,json,runpy,sys,time

ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('output',type=Path)
arg=ap.parse_args();start=time.monotonic()
deps={
    'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz':'d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9',
    'inputs/cache/parent/binary/independent/price.py':'d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b',
    'inputs/cache/parent/binary/independent/literal.py':'4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c'}
files=[arg.root/x for x in deps]
for p,sha in zip(files,deps.values()):assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
w=json.loads(gzip.decompress(files[0].read_bytes()));sys.path.insert(0,str(files[1].parent.resolve()))
price=runpy.run_path(str(files[1])); k=Fraction('0.003879928046155')
D={int(c):f['dim'] for c,f in w['frames'].items()}
B={int(c):[list(map(Fraction,row)) for row in f['B']] for c,f in w['frames'].items()}
A={int(c):[list(map(Fraction,row)) for row in f['A']] for c,f in w['frames'].items()}
def rref(rows):
    piv={}
    for vec in rows:
        v=list(vec)
        for i in sorted(piv):
            if v[i]:
                x=v[i];v=[a-x*b for a,b in zip(v,piv[i])]
        i=next((j for j,x in enumerate(v) if x),None)
        if i is not None:piv[i]=[x/v[i] for x in v]
    for i in reversed(sorted(piv)):
        for j in range(i):
            if j in piv and piv[j][i]:
                x=piv[j][i];piv[j]=[a-x*b for a,b in zip(piv[j],piv[i])]
    return [piv[i] for i in sorted(piv)]
@cache
def aggregates(ids,ann):
    source=A if ann else B
    return rref(v for i in ids for v in source[i])
@cache
def feasible(lower,upper,d):
    L=aggregates(lower,False);T=aggregates(upper,True)
    if len(L)>d or 8-len(T)<d:return False
    return all(sum(x*y for x,y in zip(b,a))==0 for b in L for a in T)
for c in D:
    assert len(rref(B[c]))==D[c] and len(rref(A[c]))==8-D[c]
    assert all(sum(x*y for x,y in zip(b,a))==0 for b in B[c] for a in A[c])
inc=defaultdict(Counter)
for op,*items in w['program']:
    if op=='MOVE':
        x,y=items[-2:];inc[x][y]+=1;inc[y][x]+=1
ends=set(w['start'])|set(w['final']); charts=sorted(D.keys()-ends)
checked=[];hit=next_case=None
for c in charts:
    costs=inc[c];neighbors=sorted(costs);old=Counter()
    for n,count in costs.items():old[abs(D[c]-D[n])]+=count
    for d in range(9):
        if time.monotonic()-start>=60:next_case=[c,d];break
        lower=tuple(n for n in neighbors if D[n]<=d)
        upper=tuple(n for n in neighbors if D[n]>=d)
        # Equal-dimension neighbors occur in both, forcing exact equality.
        if not feasible(lower,upper,d):
            checked.append([c,d,'infeasible']);continue
        diff=old.copy()
        for n,count in costs.items():
            if D[n]!=d:diff[abs(d-D[n])]-=count
        h=tuple(sorted((r,n) for r,n in diff.items() if n))
        interval=price['moment']({r:36*n for r,n in h},k)
        checked.append([c,d,'positive' if interval[0]>0 else ('neutral' if not h else 'negative'),h])
        if interval[0]>0:
            hit=dict(c=c,d=d,incident=costs,L=[[str(v) for v in row] for row in aggregates(lower,False)],
                     U_ann=[[str(v) for v in row] for row in aggregates(upper,True)],hist=h,
                     interval=price['decimal_interval'](interval,24))
            break
        assert not h or interval[1]<0
    if hit or next_case:break
out=dict(pins=deps,scope=[len(charts),9],counts=Counter(c[2] for c in checked),
         cases=checked,hit=hit,next_case=next_case,seconds=time.monotonic()-start)
arg.output.write_text(json.dumps(out,separators=(',',':'))+'\n')
print({key:val for key,val in out.items() if key not in ('pins','cases')})
