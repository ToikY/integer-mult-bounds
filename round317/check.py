"""Rebuild unary chart components directly from the literal MOVE registers."""
import argparse,gzip,hashlib,json,time
from collections import Counter,defaultdict
from fractions import Fraction
from functools import cache
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('word',type=Path)
ap.add_argument('screen',type=Path)
ap.add_argument('out',type=Path)
args=ap.parse_args(); start=time.monotonic()
raw=args.word.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9'
w=json.loads(gzip.decompress(raw)); screen=json.loads(args.screen.read_bytes())
n=w['public']; banks=[1<<i for i in range(n)]+[0]*w['owned_fields']
labels=dict(enumerate(w['start'])); expressions={}; origin={}
rank_by_chart={int(c):f['dim'] for c,f in w['frames'].items()}
def vectors(frame):
    pivots={}
    for v in frame:
        row=list(map(Fraction,v))
        for i in sorted(pivots):
            if row[i]:
                factor=row[i]
                row=[v-factor*u for v,u in zip(row,pivots[i])]
        first=next((i for i,v in enumerate(row) if v),None)
        if first is not None:
            pivots[first]=tuple(v/row[first] for v in row)
    return pivots
coords={int(c):vectors(f['B']) for c,f in w['frames'].items()}
@cache
def grade(x,y):
    if x==y: return 0
    if rank_by_chart[x]>rank_by_chart[y]:return grade(y,x)
    d=rank_by_chart[y]-rank_by_chart[x]
    if d==0:return -1
    Y=coords[y]
    for v in coords[x].values():
        row=list(v)
        for i in sorted(Y):
            if row[i]:
                factor=row[i]
                row=[v-factor*u for v,u in zip(row,Y[i])]
        if any(row):return -1
    return d

def var(i,side):return (i,side)
parent={}
def root(x):
    while parent[x]!=x:
        parent[x]=parent[parent[x]]; x=parent[x]
    return x
def record(k,c,bits):
    sink=var(k,1)
    parent[sink]=sink
    expressions[k]=c
    while bits:
        b=bits&-bits; src=var(b.bit_length()-1,0)
        assert labels[src[0]]==c
        parent[root(src)]=root(sink);bits^=b
for i in labels:parent[var(i,0)]=var(i,0)
k=n
for op,r,*args2 in w['program']:
    if op=='ADD': banks[r]^=banks[args2[0]]
    elif op in ('CLEAR','INIT'):banks[r]=0
    elif op=='SWAP':
        s=args2[0];banks[r],banks[s]=banks[s],banks[r]
    elif op=='MOVE':
        a,b=args2;record(k,a,banks[r]);labels[k]=b;origin[k]=a
        parent[var(k,0)]=var(k,0);banks[r]=1<<k;k+=1
    else:raise ValueError(op)
for i,c in enumerate(w['final']):record(~i,c,banks[i])
groups=defaultdict(list)
for x in parent:groups[root(x)].append(x)
count=Counter((labels if x[1]==0 else expressions)[x[0]] for x in groups)
worse=Counter(); totals=Counter()
for nodes in groups.values():
    if time.monotonic()-start>15:raise TimeoutError
    i,side=nodes[0]; c=(labels if side==0 else expressions)[i]
    if count[c]<=1:totals['whole']+=1;continue
    if any((side==0 and 0<=i<222) or (side==1 and -222<=i<0) for i,side in nodes):
        totals['touches_main']+=1;continue
    totals['eligible']+=1
    incident=[]
    members=set(nodes)
    for k,source in origin.items():
        if var(k,0) in members:incident.append((source,1))
        if var(k,1) in members:incident.append((labels[k],1))
    for h in range(222,n):
        if var(h,0) in members:incident.append((w['final'][h],-1))
        if var(~h,1) in members:incident.append((w['start'][h],-1))
    old=Counter()
    for neighbor,s in incident:old[grade(c,neighbor)]+=s
    for d in rank_by_chart:
        if d==c:continue
        totals['tested']+=1
        new=Counter();zerop=False
        for nb,sign in incident:
            g=grade(d,nb)
            if g<0:break
            if g:new[g]+=sign
            elif sign<0:zerop=True
        else:
            diff={r:old[r]-new[r] for r in old.keys()|new.keys() if old[r]!=new[r]}
            if zerop:totals['zero_productive']+=1
            else:
                totals['admitted']+=1
                if not diff:totals['neutral']+=1
            if diff:worse[zerop,tuple(sorted(diff.items()))]+=1
for k in ('whole','touches_main','eligible','tested','admitted','neutral','zero_productive'):
    assert totals[k]==screen[k],k
# For 0<=k<=1/100 and 1<=r<=8, (19/20)*r <= r^(1-k) <= r.
assert 20**100 > 8*19**100
for zerop, hist in worse:
    assert 20*sum(r*v for r,v in hist if v>0) < 19*sum(-r*v for r,v in hist if v<0)
result=dict(certified_interval=['0','1/100'],counts=dict(totals),histograms=[[z,h,number] for (z,h),number in sorted(worse.items())],seconds=time.monotonic()-start)
args.out.write_text(json.dumps(result,indent=2)+'\n')
print(result)
