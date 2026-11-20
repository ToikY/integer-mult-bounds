"""Check the complete frame screen from the literal tape and primal frame bases."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from functools import cache
from math import gcd,lcm
from pathlib import Path
import argparse,gzip,hashlib,json,time

ap=argparse.ArgumentParser();ap.add_argument('word',type=Path);ap.add_argument('receipt',type=Path)
ap.add_argument('out',type=Path);args=ap.parse_args()
t=time.monotonic()
r=json.loads(args.receipt.read_bytes()); raw=args.word.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9'
word=json.loads(gzip.decompress(raw))
def primitive(vec):
    common=lcm(*(x.denominator for x in vec)); out=[int(common*x) for x in vec]
    divisor=gcd(*out)
    return [x//divisor for x in out] if divisor else out
def triangular(rows):
    table={}
    for row in rows:
        v=list(row)
        for j in range(7,-1,-1):
            if not v[j]:continue
            if j not in table:table[j]=v;break
            b=table[j];x=v[j]
            v=primitive([b[j]*a-x*y for a,y in zip(v,b)])
    return table
def annihilator(rows):
    piv=triangular(rows); out=[]
    for j in sorted(set(range(8))-piv.keys()):
        v=[Q(0)]*8;v[j]=Q(1)
        for i,b in sorted(piv.items()):
            v[i]=-sum((b[a]*v[a] for a in range(i)),Q(0))/b[i]
        out.append(primitive(v))
    return out
frames={int(c):[primitive(list(map(Q,row))) for row in fr['B']] for c,fr in word['frames'].items()}
dim={i:len(triangular(rows)) for i,rows in frames.items()}
dual={i:annihilator(rows) for i,rows in frames.items()}
@cache
def rank(ids,perp):
    src=dual if perp else frames
    return len(triangular(row for i in ids for row in src[i]))
@cache
def incident(a,b):
    return all(sum(x*y for x,y in zip(v,w))==0 for v in frames[a] for w in dual[b])
charges=defaultdict(Counter)
for op in word['program']:
    if op[0]=='MOVE':
        x,y=op[2:];charges[x][y]+=1;charges[y][x]+=1
charts=sorted(frames.keys()-set(word['start']+word['final']))
classes=Counter();histograms=Counter();cases=[]
assert 20**100>8*19**100
for c in charts:
    for d in range(9):
        if time.monotonic()-t>15:raise TimeoutError((c,d))
        lower=tuple(sorted(n for n in charges[c] if dim[n]<=d))
        upper=tuple(sorted(n for n in charges[c] if dim[n]>=d))
        if not (all(incident(a,b) for a in lower for b in upper) and rank(lower,False)<=d<=8-rank(upper,True)):
            cases.append([c,d,'infeasible']);classes['infeasible']+=1;continue
        hist=Counter()
        for n,edges in charges[c].items():
            hist[abs(dim[c]-dim[n])]+=edges
            if dim[n]!=d:hist[abs(d-dim[n])]-=edges
        nonzero=tuple(sorted((rank,num) for rank,num in hist.items() if num))
        label='neutral'
        if nonzero:
            # For 0<=k<=1/100, (19/20)*r <= r^(1-k) <= r.
            assert 20*sum(r*n for r,n in nonzero if n>0)<19*sum(-r*n for r,n in nonzero if n<0)
            label='negative'
        else:assert d==dim[c]
        histograms[nonzero]+=1
        cases.append([c,d,label,[list(item) for item in nonzero]])
        classes[label]+=1
assert cases==r['cases']
out=dict(check='literal-edges/primal-nullspaces/integer-sign-bounds',cases=len(cases),
         counts=dict(classes),charged_histograms=[[h,n] for h,n in sorted(histograms.items())],
         valid_kappa=['0','1/100'],seconds=time.monotonic()-t)
args.out.write_text(json.dumps(out,indent=2)+'\n')
print(out['counts'],out['seconds'])
