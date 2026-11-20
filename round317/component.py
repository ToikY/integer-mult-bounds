"""Rank paid packet components on the pinned native BIT chart graph."""
import argparse
from collections import Counter,defaultdict
from fractions import Fraction
from functools import cache
from pathlib import Path
import gzip,hashlib,json,runpy,sys,time
from math import lcm

p=argparse.ArgumentParser()
p.add_argument('root',type=Path)
p.add_argument('out',type=Path)
a=p.parse_args()
t=time.monotonic()
pins={
'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz':'d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9',
'inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py':'4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e',
'inputs/cache/parent/binary/independent/price.py':'d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b',
'inputs/cache/parent/binary/independent/literal.py':'4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c'}
files=[a.root/d for d in pins]
for path,sha in zip(files,pins.values()):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
w=json.loads(gzip.decompress(files[0].read_bytes()))
e=runpy.run_path(str(files[1]))
sys.path.insert(0,str(files[2].parent.resolve()))
price=runpy.run_path(str(files[2]))
S,F,M,R,clocks=e['extract'](w)
e['basis'](S,M,R,sorted(M,key=clocks.get))
labels={**S,**{k:b for k,(a,b) in M.items()}}
expressions={**{~h:c for h,c in F.items()},**{k:a for k,(a,b) in M.items()}}
adj=defaultdict(set)
for side,table in ((0,labels),(1,expressions)):
    for k in table: adj[(side,k)]
for k,row in R.items():
    for i in e['indices'](row):
        assert labels[i]==expressions[k]
        adj[1,k].add((0,i)); adj[0,i].add((1,k))
bychart=defaultdict(list)
seen=set()
for v in sorted(adj):
    if v in seen: continue
    comp=[]; stack=[v]; seen.add(v)
    while stack:
        u=stack.pop(); comp.append(u)
        for nb in adj[u]:
            if nb not in seen: stack.append(nb); seen.add(nb)
    c=(labels if v[0]==0 else expressions)[v[1]]
    bychart[c].append(sorted(comp))
def ints(row):
    q=list(map(Fraction,row)); den=lcm(*(x.denominator for x in q))
    return {i:int(x*den) for i,x in enumerate(q) if x}
B={int(c):[ints(v) for v in f['B']] for c,f in w['frames'].items()}
A={int(c):[ints(v) for v in f['A']] for c,f in w['frames'].items()}
@cache
def grade(x,y):
    if x==y: return 0
    if len(B[x])>len(B[y]): return grade(y,x)
    d=len(B[y])-len(B[x])
    if d and all(sum(v*test.get(i,0) for i,v in row.items())==0 for row in B[x] for test in A[y]):
        return d
    return -1
pool=[]
whole=protected=0
for c,comps in sorted(bychart.items()):
    for comp in comps:
        if len(comps)<2: whole+=1;continue
        if any((side==0 and 0<=k<222) or (side==1 and -222<=k<0) for side,k in comp):
            protected+=1;continue
        paid=[]; helpers=[]
        for side,k in comp:
            if k in M:
                neighbor=M[k][side] # label/arrival: old origin; expression/departure: old destination
                paid.append((side,k,neighbor))
            else:
                h=k if side==0 else ~k
                neighbor=(F if side==0 else S)[h]
                helpers.append((side,h,neighbor))
        pool.append((c,comp,paid,helpers))
pool.sort(key=lambda row:(len(row[1]),row[0],row[1]))
kappa=Fraction('0.003879928046155')
@cache
def bill(hist):
    return price['moment']({i:36*n for i,n in enumerate(hist) if n},kappa)
out=dict(input_sha256=pins,charts=len(bychart),components=sum(map(len,bychart.values())),whole=whole,
         touches_main=protected,eligible=len(pool),tested=0,total=len(pool)*(len(B)-1),admitted=0,
         neutral=0,zero_productive=0,zero_productive_positive=0,hit=None,next_case=None,completed_components=0)
for ix,(c,comp,paid,helpers) in enumerate(pool):
    pcounts=Counter(n for s,k,n in paid); hcounts=Counter(n for s,k,n in helpers)
    neighbors=sorted(pcounts.keys()|hcounts.keys())
    old=[0]*9
    for n in neighbors:
        g=grade(c,n)
        assert g>0
        old[g]+=pcounts[n]-hcounts[n]
    for d in sorted(B.keys()-{c}):
        if time.monotonic()-t>=60:
            out['next_case']=[ix,c,d];break
        out['tested']+=1; delta=old.copy(); zero_t=False
        for n in neighbors:
            g=grade(d,n)
            if g<0: break
            if g==0 and hcounts[n]: zero_t=True
            if g: delta[g]-=pcounts[n]-hcounts[n]
        else:
            if zero_t:
                out['zero_productive']+=1
                out['zero_productive_positive']+=int(bill(tuple(delta))[0]>0)
                continue
            out['admitted']+=1
            if not any(delta):out['neutral']+=1
            elif bill(tuple(delta))[0]>0:
                out['hit']=dict(index=ix,chart=c,replacement=d,component=comp,paid=paid,
                    helpers=helpers,old=old,net_hist=delta,net_36=price['decimal_interval'](bill(tuple(delta)),24))
                break
    if out['hit'] or out['next_case']: break
    out['completed_components']+=1
out['seconds']=time.monotonic()-t
a.out.write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in out.items() if k!='input_sha256'})
