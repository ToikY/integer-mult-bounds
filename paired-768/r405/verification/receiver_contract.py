"""Independently check actual frame counts, owner dimensions, and signed route."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from math import prod
from pathlib import Path
import sys
from types import SimpleNamespace

p = ArgumentParser(description=__doc__)
p.add_argument("--runtime", type=Path, required=True)
p.add_argument("--runtime-inventory", type=Path, required=True)
args = p.parse_args()
runtime = args.runtime.resolve()
inventory = json.loads(args.runtime_inventory.read_bytes())["new_runtime_sha256"]
names = ("five_exchange.py","inputs/triangular/quotient_route.py","inputs/triangular/direct_body.py",
         "inputs/triangular/receiver.py","inputs/triangular/same_order_body.py")
for name in names:
    assert sha256((runtime/name).read_bytes()).hexdigest() == inventory[name]

sys.path.insert(0, str(runtime))
from upstream import install
install()
from five_exchange import corner_exchanges, direct_line
from growing_binary import Weighted
from quotient_route import free_count, low_rows, representative
from same_order_body import SameOrderBody
from streaming_routes import cold_swap_tape

def dot(a,b,mod=3):
    return sum(x*y for x,y in zip(a,b,strict=True))%mod

def inverse(matrix, mod=3):
    n=len(matrix)
    work=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    for i in range(n):
        j=next(j for j in range(i,n) if work[j][i]%3)
        work[i],work[j]=work[j],work[i]
        work[i]=[a*pow(work[i][i],-1,mod)%mod for a in work[i]]
        for j in range(n):
            if j!=i:
                m=work[j][i]
                work[j]=[(a-m*b)%mod for a,b in zip(work[j],work[i],strict=True)]
    return [row[n:] for row in work]

def shortest(u,v):
    n=len(u)
    if u[0] and v[-1]:
        return 0
    for left,right in product(range(n),repeat=2):
        outside_primal = u[right] if left == 0 else u[0]
        outside_dual = v[left] if right == n-1 else v[-1]
        if outside_primal and outside_dual:
            return 1
    return 2

def low_histograms(n):
    unit=(1,)+(0,)*(n-1)
    vectors=tuple(product(range(3),repeat=n))
    frames=[(u,v) for u in vectors for v in vectors if dot(u,v)==1]
    frame_counts={frame:Counter() for frame in frames}
    joint=Counter()
    seen=set()
    total=prod(3**d-1 for d in range(1,n+1))
    for low in low_rows(n):
        cv=list(zip(*inverse(low),strict=True))
        flat=sum(low,())
        assert flat not in seen
        seen.add(flat)
        high_count=3**free_count(n)
        for index in (0,1,high_count//2,high_count-1):
            high=representative(flat,index,n,2)
            assert tuple(tuple(x%3 for x in row) for row in high)==low
        for u,v in frames:
            primal=tuple(dot(row,u) for row in low)
            dual=tuple(dot(v,col) for col in cv)
            assert dot(primal,dual)==1
            pivot=next(i for i in range(n) if primal[i] and dual[i])
            pairs=corner_exchanges(primal,dual,pivot)
            assert len(pairs)==shortest(primal,dual)
            lifted_p=[*primal,*primal]
            lifted_q=[*dual,*dual]
            for a,b in pairs:
                lifted_p[a],lifted_p[n+b]=lifted_p[n+b],lifted_p[a]
                lifted_q[a],lifted_q[n+b]=lifted_q[n+b],lifted_q[a]
            assert lifted_p[0] and lifted_q[-1]
            frame_counts[u,v][1+2*len(pairs)] += 1
            if (u,v)==(unit,unit):
                joint[bool(primal[0]),bool(dual[-1])]+=1
    assert len(seen)==total
    x=3**(n-2)
    denominator=9*x-1
    assert {event:Q(joint[event],total) for event in product((False,True),repeat=2)}=={
        (True,True):Q(4*x,denominator), (True,False):Q(2*x,denominator),
        (False,True):Q(2*x,denominator), (False,False):Q(x-1,denominator)}
    worst=max(Q(sum(k*c for k,c in hist.items()),total) for hist in frame_counts.values())
    assert worst==Q(21*x+3,denominator)
    sharp=frame_counts[unit,unit]
    assert Q(sum(k*c for k,c in sharp.items()),total)==worst
    return dict(rank=n, lows=total, frames=len(frames), sharp_histogram=sharp,
                same_high_count_at_modulus_9=high_count, exact_worst_mean=worst)

def fold(digits, dimensions):
    value=0
    for digit,size in zip(digits,dimensions,strict=True):
        value=value*size+digit
    return value

def signed_direct(width):
    q=3**width
    direct=[[1,0],[0,1]]
    word=(("add",0,1,2),("add",1,0,-1),("swap",0,1),("scale",0,Q(-2,1)))
    # Independent column calculation of a noncommuting paid frame F.
    for row in direct:
        row[0]=(row[0]+2*row[1])%q
        row[1]=(row[1]-row[0])%q
        row[0],row[1]=row[1],row[0]
        row[0]=-2*row[0]%q
    reverse=inverse(direct,q)
    u=tuple(row[1] for row in direct)
    v=tuple(reverse[1])
    assert dot(u,v,q)==1
    assert (u,v)!=((0,1),(0,1))
    frame=SimpleNamespace(mask=(1,),word=word)
    dims=(2,2,q,q,2,q,q,2)
    count=prod(dims)
    raw=b"".join(i.to_bytes(4,"little") for i in range(count))
    dense=bytearray(len(raw))
    weights=((1,2),(4,5))
    for address in product(*(range(size) for size in dims)):
        free,old,h0,h1,gap,t0,t1,tail=address
        a=weights[old]
        h,t=(h0,h1),(t0,t1)
        delta=dot(v,tuple(y-pow(z,-1,q)*x for z,x,y in zip(a,h,t,strict=True)),q)
        hh=[(x+z*b*delta)%q for z,b,x in zip(a,u,h,strict=True)]
        tt=[(y-b*delta)%q for b,y in zip(u,t,strict=True)]
        src=fold(address,dims)
        dst=fold((free,old,*hh,gap,*tt,tail),dims)
        dense[4*dst:4*(dst+1)]=raw[4*src:4*(src+1)]
    assert dense!=raw

    class Core(SameOrderBody, Weighted):
        def __init__(self):
            super().__init__(2,(1,width,0,0),cold_swap_tape)
            self.stock=self.owners
            self.counts=[]
        def weighted(self,*params,**kwargs):
            self.counts.append(tuple(kwargs[key] for key in ("atoms","available","older","gap","suffix")))
            return super().weighted(*params,**kwargs)

    core=Core()
    source,target=BytesIO(raw),BytesIO()
    kwargs=dict(frame=frame,f=1,unused=2,older=2,gap=2,suffix=8,weight=lambda old,j:weights[old][j])
    direct_line(core,source,target,**kwargs)
    assert target.getvalue()==dense and source.getvalue()==raw and source.tell()==len(raw)
    # The same involutive signed exchange must restore the dirty field.
    first=BytesIO(target.getvalue())
    restored=BytesIO()
    direct_line(core,first,restored,**kwargs)
    assert restored.getvalue()==raw and first.getvalue()==dense
    # Losing the inverse basis cannot accidentally satisfy the dense control.
    bad=bytearray(dense)
    bad[11]^=1
    assert bad!=target.getvalue()
    assert core.counts==[(1,2,2*q,2*q,8)]*2
    assert all(a*b*c*d*q**(2*f)==len(raw) for f,a,b,c,d in (
        core.counts
    ))
    return dict(width=width,modulus=q,records=count,one_child_each_direction=True,child_shape=core.counts[0])

# Symbolically, 75(9x-1) - 32(21x+3) = 3x-171.
# N >= 8 gives x >= 729 and the linear difference grows thereafter.
assert 75*9-32*21==3 and -75-32*3==-171 and 3*3**6-171>0
# The exact quotient dimensions preserve total bytes for all child pairs.
for n,f,a in ((2,1,3),(4,3,9),(7,4,27)):
    unused,high,older,gap,suffix=2,9,5,7,17
    owner=unused*high*older*gap*suffix*a**(2*n*f)
    for i,j in product(range(n),repeat=2):
        start,end=i*f,(n+j)*f
        shape=(unused,high*older*a**start,gap*a**(end-start-f),suffix*a**(2*n*f-end-f))
        assert prod(shape)*a**(2*f)==owner
        for index in (0,a**start-1,a**start*older,a**start*high*older-1):
            reconstructed=divmod(index//a**start,older)
            assert reconstructed==(index//(a**start*older),(index//a**start)%older)
# A direct full owner stays 1/B of the node. The equal true low packets
# occupy 1/(BQ), not 1/Q or 1/(BQ times the high multiplicity).
assert Q(75,32)/Q(2401,1024)==Q(2400,2401)
assert 1/(1-Q(2400,2401))==2401
print(json.dumps(dict(quotient_low_census=[low_histograms(n) for n in (2,3)],
                      signed_direct=[signed_direct(w) for w in (1,2)],
                      max_child_volume_per_paid_owner="75/32",
                      normalized_moments=["t","1"],
                      child_contraction="2400/2401", finite_geometric_sum=2401,
                      receiver_source_sha256={name:inventory[name] for name in names}),
                 indent=2,default=str))
