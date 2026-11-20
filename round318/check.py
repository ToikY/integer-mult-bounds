"""Independent literal-stock, quotient-signature cross-check for calibrated GF(2) births."""
from collections import defaultdict
from hashlib import sha256
import json,runpy
from pathlib import Path
from time import monotonic
import sys

def extend(base,x):
    while x:
        p=x&-x
        if p not in base:
            base[p]=x
            break
        x^=base[p]

def coefficients(rows):
    base={}
    for v in rows:
        extend(base,v)
    def remainder(x):
        answer=0
        while x:
            p=x&-x
            if p in base:
                x^=base[p]
            else:
                answer|=p
                x^=p
        return answer
    return remainder

def ker(group,remainder):
    piv={}
    answer=[]
    for h in group:
        y=remainder(1<<h)
        order=1<<h
        while y:
            p=y&-y
            if p not in piv:
                piv[p]=y,order
                break
            a,b=piv[p]
            y^=a
            order^=b
        else:
            answer.append(order)
    return answer

def paired(q,s):
    return any((a&b).bit_count()%2 for a in q for b in s)

def main():
    root,result,receipt=map(Path,sys.argv[1:])
    t=monotonic()
    engine=root/'upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py'
    assert sha256(engine.read_bytes()).hexdigest()=='36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349'
    m=runpy.run_path(str(engine))
    w=m['load_json'](root/'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz',m['WORD_GZIP'],True)
    atlas=m['Atlas'](w['frames'])
    tapes=[m['run_tape'](w,atlas,rev) for rev in (False,True)]
    assert all(h.output==m['expected_operator'](bool(i)) and h.dirty==3554 for i,h in enumerate(tapes))
    data=json.loads(result.read_bytes())
    assert data['status']=='exhausted' and data['all_time_positive']==0 and data['witness'] is None
    groups=defaultdict(list)
    for h in range(222,w['public']):
        groups[w['start'][h],w['final'][h]].append(h)
    assert data['cohorts']=={f'{a}/{b}':hex(sum(1<<h for h in ids)) for (a,b),ids in groups.items()}
    assert len(data['charts'])==2*len(atlas.body)
    stats=defaultdict(int)
    for c in sorted(atlas.body):
        lhs,rhs=[coefficients(obs.row for obs in tape.stock[c]) for tape in tapes]
        want=[]
        for (a,b),group in sorted(groups.items()):
            x,y=atlas.grade(a,c),atlas.grade(c,b)
            if min(x,y)<=0 or x+y!=atlas.grade(a,b):
                continue
            q=ker(group,lhs)
            d=ker(group,rhs)
            assert not paired(q,d)
            stats['left_positive']+=bool(q)
            stats['right_positive']+=bool(d)
            stats['both_nonempty']+=bool(q and d)
            stats['nested_per_orientation']+=1
            want.append([a,b,0])
        for j in range(2):
            assert data['charts'][f'{j}/{c}']==want
    # Non-identical pair with odd overlap; a pair with two overlapping bits is orthogonal.
    assert paired(ker([0,1,2],coefficients([3,8])),ker([0,1,2],coefficients([6,16])))
    assert not paired(ker([0,1,2],coefficients([3,8])),ker([0,1,2],coefficients([3,16])))
    out=dict(status='exhausted',chart_cohort_orientations=len(atlas.body)*len(groups)*2,forward=dict(stats),
             dirty_retires=[h.dirty for h in tapes],seconds=monotonic()-t)
    receipt.write_text(json.dumps(out,indent=2)+'\n')
    print(out)
if __name__=='__main__':
    main()
