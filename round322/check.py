"""Independently reconstruct separate bank-supported directions from the literal tape."""
from collections import Counter,defaultdict
from functools import cache
from hashlib import sha256
import json,runpy,sys
from pathlib import Path
from time import monotonic

def remainder(rows):
    piv={}
    for v in rows:
        while v:
            bit=v&-v
            if bit not in piv:
                piv[bit]=v;break
            v^=piv[bit]
    def reduce(v):
        out=0
        while v:
            bit=v&-v
            if bit in piv:v^=piv[bit]
            else:out|=bit;v^=bit
        return out
    return reduce

def ker(pairs):
    piv={};basis=[]
    for i,res in pairs:
        tag=1<<i
        while res:
            bit=res&-res
            if bit not in piv:
                piv[bit]=(res,tag);break
            v,w=piv[bit];res^=v;tag^=w
        else:basis.append(tag)
    return basis

def apply(field,images):
    row=0
    while field:
        b=field&-field;field^=b;row^=images[b.bit_length()-1]
    return row

def classify(pulse,read,calib,helpers,inv):
    if not pulse:return 'no_pulse'
    if not read:return 'no_read'
    if not calib:return 'no_calibration'
    def sig(row,cols): return sum(((row&v).bit_count()%2)<<i for i,v in enumerate(cols))
    pre=[apply(v,inv) for v in pulse]
    q={sig(form,pre) for form in read}-{0}
    k={sig(form,pulse) for form in calib}-{0}
    h={sig(1<<i,pulse) for i in helpers}-{0}
    if any(a^b^c for a in q for b in k for c in h):return 'hit'
    return 'orthogonal'

def main():
    root,src,out=map(Path,sys.argv[1:]);t=monotonic()
    ref=root/'upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py'
    assert sha256(ref.read_bytes()).hexdigest()=='36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349'
    e=runpy.run_path(str(ref));w=e['load_json'](root/'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz',e['WORD_GZIP'],True)
    atlas=e['Atlas'](w['frames']);tapes=[e['run_tape'](w,atlas,rev) for rev in (False,True)]
    assert all(tape.output==e['expected_operator'](bool(i)) and tape.dirty==3554 for i,tape in enumerate(tapes))
    source=json.loads(src.read_bytes());assert source['status']=='exhausted' and not source['survivors'] and not source['chronology']
    actual=[];n=w['public'];ids=range(n)
    for rev in (False,True):
        start,end=(w['final'],w['start']) if rev else (w['start'],w['final'])
        A=defaultdict(list);B=defaultdict(list);groups=defaultdict(list)
        for h in ids:
            A[start[h]].append(h);B[end[h]].append(h)
            if h>=222:groups[start[h],end[h]].append(h)
        mats=tapes[rev].output;inv=tapes[not rev].output
        assert all(apply(inv[h],inv)==1<<h and apply(mats[h],mats)==1<<h for h in ids)
        for c in sorted(atlas.body):
            if monotonic()-t>=20:raise RuntimeError(('verification capped at',rev,c))
            lhs,rhs=[remainder(row.row for row in tapes[j].stock[c]) for j in (rev,not rev)]
            @cache
            def read(a):return ker((i,lhs(1<<i)) for i in A[a])
            @cache
            def calib(b):return ker((i,lhs(mats[i])) for i in B[b])
            for (a,b),hs in sorted(groups.items()):
                x,y=atlas.grade(a,c),atlas.grade(b,c)
                if min(x,y)<=0 or x+y!=atlas.grade(a,b):continue
                allowed=sum(1<<h for h in A[a])
                V=ker((i,rhs(1<<i) | ((inv[i]&~allowed)<<n)) for i in B[b])
                cls=classify(V,read(a),calib(b),hs,inv)
                actual.append([rev,c,a,b,cls])
    assert actual==source['all_time']
    # A nonzero triple of equal signatures is feasible; the zero-sum triple 01,10,11 is not.
    assert classify([1],[1],[1],[0],[1])=='hit'
    assert classify([3,5],[2],[4],[0],[1,2,4])=='orthogonal'
    d=dict(status='verified',counts=Counter(z[-1] for z in actual),nested_cases=len(actual),total=len(atlas.body)*len(groups)*2,public=n,dirty_retires=[z.dirty for z in tapes],seconds=monotonic()-t)
    out.write_text(json.dumps(d,indent=2)+'\n');print(d)
if __name__=='__main__': main()
