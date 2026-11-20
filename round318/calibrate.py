"""Scan paid cuts for a zero-paid calibrated birth in a joint endpoint cohort."""
import argparse
from collections import defaultdict
from fractions import Fraction
from functools import cache
from hashlib import sha256
from math import lcm
import gzip,json,runpy
from pathlib import Path
from time import monotonic

WORD="inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz"
ENGINE="inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py"
PINS={WORD:"d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",ENGINE:"4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e"}

def intersection(events,mask):
    """Eliminate outside coordinates first, retaining provenance for the kernel."""
    outside={}
    inside={}
    for _,k,v in events:
        label=1<<k
        while v:
            bad=v&~mask
            basis=outside if bad else inside
            pivot=(bad or v).bit_length()-1
            if pivot not in basis:
                basis[pivot]=(v,label)
                break
            vv,ll=basis[pivot]
            v^=vv
            label^=ll
    return inside.values()

def pair(read,send,mask):
    left=intersection(read,mask)
    right=intersection(send,mask)
    return next(((q,r,d,s) for q,r in left for d,s in right if (q&d).bit_count()%2),None)

def integer(v):
    row=list(map(Fraction,v))
    den=lcm(*(a.denominator for a in row))
    return {i:int(n*den) for i,n in enumerate(row) if n}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root',type=Path)
    ap.add_argument('result',type=Path)
    args=ap.parse_args()
    start=monotonic()
    for p,s in PINS.items():
        assert sha256((args.root/p).read_bytes()).hexdigest()==s
    w=json.loads(gzip.decompress((args.root/WORD).read_bytes()))
    e=runpy.run_path(str(args.root/ENGINE))
    S,F,M,R,clocks=e['extract'](w)
    order=sorted(M,key=clocks.get)
    adj=e['basis'](S,M,R,order)
    val={h:1<<h for h in S}
    for k in order:
        val[k]=e['combine'](R[k],val)
    frames={int(c):f for c,f in w['frames'].items()}
    B={c:[integer(row) for row in v['B']] for c,v in frames.items()}
    A={c:[integer(row) for row in v['A']] for c,v in frames.items()}
    @cache
    def lt(a,b):
        return len(B[a])<len(B[b]) and all(not sum(n*rhs.get(i,0) for i,n in row.items()) for row in B[a] for rhs in A[b])
    groups=defaultdict(int)
    for h in range(222,len(S)):
        groups[S[h],F[h]]|=1<<h
    result=dict(sources=PINS,cohorts={f'{x}/{y}':hex(v) for (x,y),v in groups.items()},charts={},witness=None,all_time_positive=0)
    def save(status,cursor):
        result.update(status=status,cursor=cursor,seconds=monotonic()-start)
        args.result.write_text(json.dumps(result,indent=2)+'\n')
        print(status,cursor,result['all_time_positive'],result['witness'],result['seconds'])
    for rev in (False,True):
        st,fn=(F,S) if rev else (S,F)
        read,write=defaultdict(list),defaultdict(list)
        for h in S:
            read[st[h]].append((-1,h,1<<h))
            write[fn[h]].append((len(M),h,1<<h))
        for p,k in enumerate(reversed(order) if rev else order):
            s,d=M[k][::-1] if rev else M[k]
            read[d].append((p,k,adj[k] if rev else val[k]))
            write[s].append((p,k,val[k] if rev else adj[k]))
        for c in sorted(frames):
            ids=[]
            result['charts'][f'{int(rev)}/{c}']=ids
            for (a,b),mask in sorted(groups.items()):
                if monotonic()-start>=60:
                    save('capped',[int(rev),c,a,b])
                    return
                lo,hi=(a,b) if len(B[a])<len(B[b]) else (b,a)
                if not (lt(lo,c) and lt(c,hi)):
                    continue
                ids.append([a,b,0])
                if not pair(read[c],write[c],mask):
                    continue
                result['all_time_positive']+=1
                ids[-1][-1]=1
                # Earliest prefix availability changes only on an arrival.
                for cut in sorted({p for p,k,v in read[c]}):
                    if monotonic()-start>=60:
                        save('capped',[int(rev),c,a,b,cut])
                        return
                    sol=pair([z for z in read[c] if z[0]<=cut],[z for z in write[c] if z[0]>cut],mask)
                    if sol:
                        q,r,d,s=sol
                        ids[-1][-1]=2
                        result['witness']=dict(reverse=rev,mid=c,endpoints=[a,b],cut=cut,h=(d&-d).bit_length()-1,
                            q=list(e['indices'](q)),d=list(e['indices'](d)),read=list(e['indices'](r)),send=list(e['indices'](s)))
                        save('witness',[int(rev),c,a,b,cut])
                        return
    save('exhausted',None)
if __name__=='__main__':
    main()
