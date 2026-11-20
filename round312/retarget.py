"""Search fixed-clock, strictly cheaper BIT sender charts on the pinned word."""
import argparse
from collections import defaultdict
from fractions import Fraction
from functools import cache
import gzip
import hashlib
import json
from math import lcm
from pathlib import Path
import runpy
import time

def integer_row(values):
    q=list(map(Fraction,values))
    n=lcm(*(v.denominator for v in q))
    return [(i,int(v*n)) for i,v in enumerate(q) if v]

class Stock:
    def __init__(self):
        self.rows={}
        self.union=0
    def add(self,value,labels):
        self.union|=value
        while value:
            k=value.bit_length()-1
            if k not in self.rows:
                self.rows[k]=(value,labels)
                return
            old,s=self.rows[k]
            value^=old
            labels^=s
    def solve(self,value):
        if value&~self.union:
            return None
        used=0
        while value:
            k=value.bit_length()-1
            if k not in self.rows:
                return None
            row,terms=self.rows[k]
            value^=row
            used^=terms
        return used

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument('root',type=Path)
    pa.add_argument('out',type=Path)
    pa.add_argument('--correction',action='store_true')
    args=pa.parse_args()
    start=time.monotonic()
    rr=args.root
    path=rr/'inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py'
    assert hashlib.sha256(path.read_bytes()).hexdigest()=='4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e'
    e=runpy.run_path(str(path))
    w=json.loads(gzip.decompress((rr/'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz').read_bytes()))
    assert e['digest'](w)=='d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d'
    f=w['frames']
    body={int(c):list(map(integer_row,v['B'])) for c,v in f.items()}
    dual={int(c):[dict(integer_row(row)) for row in v['A']] for c,v in f.items()}
    @cache
    def grade(a,b):
        if len(body[a])>len(body[b]):
            a,b=b,a
        d=len(body[b])-len(body[a])
        if d and all(sum(n*test.get(i,0) for i,n in row)==0 for row in body[a] for test in dual[b]):
            return d
        return 0
    S,F,M,R,clocks=e['extract'](w)
    order=sorted(M,key=clocks.get)
    adj=e['basis'](S,M,R,order)
    forward={i:1<<i for i in S}
    for k in order:
        forward[k]=e['combine'](R[k],forward)
    attempted=[]
    best=None
    nr=0
    cheaper_pairs=0
    for rev in (False,True):
        stock=defaultdict(Stock)
        for h,c in (F if rev else S).items():
            stock[c].add(1<<h,1<<h)
        for k in (reversed(order) if rev else order):
            if time.monotonic()-start>=90 or best:
                break
            a,b=M[k][::-1] if rev else M[k]
            row=(adj if rev else forward)[k]
            old=grade(a,b)
            assert old>0
            attempted.append([rev,k,clocks[k]])
            if old>1:
                dest=stock[b]
                for c,source in sorted(stock.items()):
                    if c in (a,b) or not source.rows:
                        continue
                    if row&~(source.union|(dest.union if args.correction else 0)):
                        continue
                    g=grade(c,b)
                    if not 0<g<old:
                        continue
                    cheaper_pairs+=1
                    val=source.solve(row)
                    if val is None and args.correction:
                        union=Stock()
                        for value,terms in dest.rows.values():
                            union.add(value,terms)
                        for value,terms in source.rows.values():
                            union.add(value,terms)
                        val=union.solve(row)
                    if val is not None:
                        best=dict(reverse=rev,packet=k,clock=clocks[k],old=[a,b,old],new=[c,b,g],
                                  labels=list(e['indices'](val)),row=hex(row))
                        break
            stock[b].add(row,1<<k)
            nr+=1
        if best:
            break
    d=dict(cases=nr,packets=attempted,cheaper_pairs=cheaper_pairs,hit=best,
           status='hit' if best else ('exhausted' if nr==2*len(order) else 'capped'),
           seconds=time.monotonic()-start)
    args.out.write_text(json.dumps(d,indent=2)+'\n')
    print(d['status'],nr,cheaper_pairs,best,d['seconds'])

if __name__=='__main__':
    main()
