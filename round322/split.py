"""Search for free calibrated midpoint births under separate source and return supports."""
import argparse
from collections import defaultdict, Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import product
from math import lcm
import gzip,json,runpy
from pathlib import Path
from time import monotonic

WORD="inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz"
ENGINE="inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py"
PINS={WORD:"d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",ENGINE:"4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e"}
def action(v,reverse):
    main=(1<<111)-1
    return v^((v>>111)&main if reverse else (v&main)<<111)

def part(rows,mask):
    outside={}
    inside={}
    for v,l in rows:
        while v:
            bad=v&~mask
            basis=outside if bad else inside
            pivot=(bad or v).bit_length()-1
            if pivot not in basis:
                basis[pivot]=(v,l)
                break
            x,y=basis[pivot]
            v^=x;l^=y
    return list(inside.values())

def pulse(read,send,A,B,H,rev):
    # Restrict preimage and image of the pulse, without discarding labelled provenance.
    vstock=part([(v,1<<tag) for clk,tag,v in send],B)
    dirs=part([(action(v,rev),tag) for v,tag in vstock],A)
    dirs=[(d,action(d,rev),tag) for d,tag in dirs]
    if not dirs:return 'no_pulse',None
    qstock=part([(v,1<<tag) for clk,tag,v in read],A)
    if not qstock:return 'no_read',None
    ustock=part([(action(v,not rev),1<<tag) for clk,tag,v in read],B)
    if not ustock:return 'no_calibration',None
    for (q,qr),(u,ur) in product(qstock,ustock):
        qflag=[(q&d).bit_count()%2 for d,v,l in dirs]
        kflag=[(u&v).bit_count()%2 for d,v,l in dirs]
        if not any(qflag) or not any(kflag):continue
        hs=H
        while hs:
            z=hs&-hs;hs^=z
            basis={0:(0,0)}
            for idx,(d,v,tag) in enumerate(dirs):
                flags=qflag[idx]|kflag[idx]<<1|bool(v&z)<<2
                for s,(dd,tt) in list(basis.items()):
                    if s^flags not in basis:basis[s^flags]=(d^dd,tag^tt)
                if 7 in basis:
                    direction,pulse_tag=basis[7]
                    v=action(direction,rev)
                    k=action(u,not rev)
                    assert v&z and (q&direction).bit_count()%2 and (k&direction).bit_count()%2
                    return 'hit',dict(h=z.bit_length()-1,q=hex(q),k=hex(k),d=hex(direction),v=hex(v),send=hex(pulse_tag),read=hex(qr),calibrate=hex(ur))
    return 'orthogonal',None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
    t=monotonic()
    for p,h in PINS.items():assert sha256((a.root/p).read_bytes()).hexdigest()==h
    w=json.loads(gzip.decompress((a.root/WORD).read_bytes()));e=runpy.run_path(str(a.root/ENGINE))
    S,F,M,R,T=e['extract'](w);order=sorted(M,key=T.get);adj=e['basis'](S,M,R,order);val={h:1<<h for h in S}
    for h in S:assert adj[h]==action(1<<h,False)
    for k in order:val[k]=e['combine'](R[k],val)
    def integer(v):
        row=list(map(Fraction,v));den=lcm(*(a.denominator for a in row))
        return {i:int(n*den) for i,n in enumerate(row) if n}
    B={int(c):[integer(r) for r in f['B']] for c,f in w['frames'].items()}
    ann={int(c):[integer(r) for r in f['A']] for c,f in w['frames'].items()}
    @cache
    def lt(i,j):
        return len(B[i])<len(B[j]) and all(not sum(n*u.get(k,0) for k,n in v.items()) for v in B[i] for u in ann[j])
    records=[];survivors=[];chrono=[];witness=None;status='exhausted';cursor=None;counts=Counter();cache_data={}
    for rev in (False,True):
        st,fn=(F,S) if rev else (S,F)
        sp,fp,groups=defaultdict(int),defaultdict(int),defaultdict(int)
        rd,sd=defaultdict(list),defaultdict(list)
        for h in st:
            sp[st[h]]|=1<<h;fp[fn[h]]|=1<<h
            if h>=222:groups[st[h],fn[h]]|=1<<h
            rd[st[h]].append((-1,h,1<<h));sd[fn[h]].append((len(M),h,1<<h))
        for pos,k in enumerate(reversed(order) if rev else order):
            x,y=M[k][::-1] if rev else M[k]
            rd[y].append((pos,k,adj[k] if rev else val[k]))
            sd[x].append((pos,k,val[k] if rev else adj[k]))
        cache_data[rev]=(rd,sd,sp,fp,groups)
        for c in sorted(B):
            for (x,y),group in sorted(groups.items()):
                if monotonic()-t>=60:status='capped';cursor=['span',rev,c,x,y];break
                lo,hi=sorted((x,y),key=lambda q:len(B[q]))
                if not lt(lo,c) or not lt(c,hi):continue
                cls,sol=pulse(rd[c],sd[c],sp[x],fp[y],group,rev)
                records.append([rev,c,x,y,cls]);counts[cls]+=1
                if sol:survivors.append((rev,c,x,y))
            if cursor:break
        if cursor:break
    for rev,c,x,y in survivors:
        if cursor:break
        rd,sd,sp,fp,groups=cache_data[rev]
        for cut in sorted({p for p,k,v in rd[c]}):
            if monotonic()-t>=60:status='capped';cursor=['cut',rev,c,x,y,cut];break
            cls,sol=pulse([z for z in rd[c] if z[0]<=cut],[z for z in sd[c] if z[0]>cut],sp[x],fp[y],groups[x,y],rev)
            chrono.append([rev,c,x,y,cut,cls])
            if sol:
                witness=dict(reverse=rev,middle=c,source=x,terminal=y,cut=cut,**sol);status='hit';break
        if witness or cursor:break
    o=dict(pins=PINS,status=status,all_time=records,counts=counts,survivors=survivors,chronology=chrono,witness=witness,cursor=cursor,seconds=monotonic()-t)
    a.out.write_text(json.dumps(o,indent=2)+'\n')
    print(status,counts,len(survivors),len(chrono),witness,o['seconds'])
if __name__=='__main__':main()
