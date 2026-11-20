"""Find fixed-order paid withdrawals after projecting one independent helper."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time

def rem(value,basis):
    result=0
    while value:
        k=value.bit_length()-1
        if k in basis:
            value^=basis[k]
        else:
            result|=1<<k
            value^=1<<k
    return result

def directions(word,edge,reverse):
    s,f,m,rows,clocks=edge["extract"](word)
    order=sorted(m,key=clocks.get)
    columns=edge["basis"](s,m,rows,order)
    if reverse:
        stock=columns
        s,f=f,s
        m={k:(b,a) for k,(a,b) in m.items()}
        order.reverse()
    else:
        stock={i:1<<i for i in s}
        for k in order:
            stock[k]=edge["combine"](rows[k],stock)
    return s,f,m,clocks,stock,order

def main():
    p=argparse.ArgumentParser()
    for x in ('root','out'):
        p.add_argument(x,type=Path)
    a=p.parse_args()
    t=time.monotonic()
    source=a.root/'inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py'
    assert hashlib.sha256(source.read_bytes()).hexdigest()=='4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e'
    edge=runpy.run_path(str(source))
    word=json.loads(gzip.decompress((a.root/'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz').read_bytes()))
    assert edge['digest'](word)=='d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d'
    independent=a.root/'inputs/cache/parent/binary/independent'
    sys.path.insert(0,str(independent.resolve()))
    assert hashlib.sha256((independent/'price.py').read_bytes()).hexdigest()=='d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b'
    import price
    kappa=Fraction('0.003879928046155')
    cases=[]
    completed=[]
    def grade(x,y):
        return abs(word['frames'][str(x)]['dim']-word['frames'][str(y)]['dim'])
    for rev in (False,True):
        s,f,m,clocks,V,order=directions(word,edge,rev)
        bases=defaultdict(dict)
        for h,c in s.items():
            bases[c][h]=1<<h
        withdraw=defaultdict(list)
        for idx,k in enumerate(order):
            if time.monotonic()-t>=60:
                a.out.write_text(json.dumps({'status':'capped','orientation':rev,'next_packet':k,'completed':completed,'cases':cases})+'\n')
                return
            src,dst=m[k]
            B=bases[dst]
            residual=rem(V[k],B)
            if residual:
                # For any nonpivot coordinate the unit reduces to itself.
                hs=[h for h in B if h>=222 and rem(1<<h,B)==residual]
                if residual.bit_count()==1:
                    h=residual.bit_length()-1
                    if 222<=h<len(s) and h not in B:
                        hs.append(h)
                B[residual.bit_length()-1]=residual
            else:
                hs=range(222,len(s))
            for h in hs:
                withdraw[h].append(k)
        completed.append([rev,len(order),len(s)-222])
        for h in range(222,len(s)):
            minus=withdraw[h]
            hist=Counter(grade(*m[k]) for k in minus)
            bridge=grade(s[h],f[h])
            hist[bridge]-=1
            margin=price.moment({r:36*n for r,n in hist.items()},kappa)
            cases.append(dict(reverse=rev,helper=h,bridge_grade=bridge,packets=minus,
                              clocks=[clocks[k] for k in minus],signed_price=price.decimal_interval(margin,20),
                              delta_paid={r:-36*n for r,n in hist.items() if n},positive=margin[0]>0))
    ranked=sorted((v for v in cases if v['positive']),key=lambda c:Fraction(c['signed_price'][0]),reverse=True)
    out=dict(status='exhausted',completed=completed,cases=cases,positive=len(ranked),best=ranked[:1],seconds=time.monotonic()-t)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],len(cases),'positive',len(ranked),'best',ranked[:1],out['seconds'])

if __name__=='__main__':
    main()
