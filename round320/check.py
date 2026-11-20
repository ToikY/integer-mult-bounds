"""Independently delete both payloads on the literal tape and measure the public defect."""
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations
import json,runpy,sys
from pathlib import Path
from time import monotonic

def defect_rank(program,addresses,n,initial,reference,first,second):
    rows=initial.copy()
    for op,a,b in program:
        if op==0:
            rows[a]^=rows[b]
        elif op==1:
            rows[a],rows[b]=rows[b],rows[a]
        elif op==2:
            rows[a]=0
        elif b==first or b==second:
            rows[a]=0
    basis={}
    for x,y in zip(rows[:n],reference,strict=True):
        z=x^y
        while z:
            pivot=z&-z
            if pivot not in basis:
                basis[pivot]=z
                break
            z^=basis[pivot]
    return len(basis)

def main():
    t=monotonic()
    root,result,receipt=map(Path,sys.argv[1:])
    f=root/'upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py'
    assert sha256(f.read_bytes()).hexdigest()=='36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349'
    m=runpy.run_path(str(f))
    w=m['load_json'](root/'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz',m['WORD_GZIP'],True)
    atlas=m['Atlas'](w['frames'])
    fwd,rev=[m['run_tape'](w,atlas,j) for j in (False,True)]
    assert all(x.output==m['expected_operator'](i) and x.dirty==3554 for i,x in enumerate([fwd,rev]))
    out=json.loads(result.read_bytes())
    assert out['survivors']==[] and out['status']=='exhausted'
    groups=defaultdict(list)
    for k,p in sorted(fwd.packets.items(),key=lambda it:it[1].clock):
        groups[p.source,p.receiver].append(k)
    n=w['public']
    addresses=n+w['owned_fields']
    initial=[1<<i for i in range(n)]+[0]*w['owned_fields']
    program=[]
    for idx,(op,a,*rest) in enumerate(w['program']):
        if op=='ADD': program.append((0,a,rest[0]))
        elif op=='SWAP': program.append((1,a,rest[0]))
        elif op in ('INIT','CLEAR'): program.append((2,a,0))
        elif op=='MOVE': program.append((3,a,idx))
        else: raise ValueError(op)
    def rank(i,j):
        return defect_rank(program,addresses,n,initial,fwd.output,i,j)
    assert rank(-1,-2)==0
    hist=Counter()
    routes=0
    for (a,b),labels in sorted(groups.items()):
        if len(labels)<2:
            continue
        row=out['routes'][f'{a}/{b}']
        digest=sha256()
        tested=0
        for i,j in combinations(labels,2):
            if monotonic()-t>=20:
                receipt.write_text(json.dumps(dict(status='capped',rank_counts=hist,restart=[a,b,i,j],seconds=monotonic()-t)))
                print('independent cap',i,j)
                return
            x,y=fwd.packets[i].arrival.row,fwd.packets[j].arrival.row
            p,q=rev.packets[i].arrival.row,rev.packets[j].arrival.row
            h=rank(fwd.packets[i].clock,fwd.packets[j].clock)
            hist[h]+=1
            digest.update(f'{i},{j},{int(bool(x and y and x!=y))},{int(bool(p and q and p!=q))}\n'.encode())
            assert h==2 and x and y and x!=y and p and q and p!=q
            tested+=1
        assert labels==row['labels'] and tested==row['tested'] and digest.hexdigest()==row['sha256']
        routes+=1
    assert routes==len(out['routes']) and hist[2]==out['rank_two']==out['all_pairs']
    first=fwd.packets[next(iter(fwd.packets))].clock
    assert rank(first,first)==1
    d=dict(status='exhausted',paired_routes=routes,full_public_defect_ranks=hist,baseline_control=0,
           one_packet_control=1,public=n,dirty_retires=[fwd.dirty,rev.dirty],seconds=monotonic()-t)
    receipt.write_text(json.dumps(d,indent=2)+'\n')
    print(d)
if __name__=='__main__': main()
