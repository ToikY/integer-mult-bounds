"""Independently validate the frozen BIT singleton midpoint decision on literal tapes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import runpy
import time

def in_span(rows):
    pivots = {}
    for v in rows:
        while v:
            p = v & -v
            if p not in pivots:
                pivots[p] = v
                break
            v ^= pivots[p]
    def contains(v):
        while v:
            p = v & -v
            if p not in pivots:
                return False
            v ^= pivots[p]
        return True
    return contains

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root',type=Path)
    p.add_argument('result',type=Path)
    p.add_argument('receipt',type=Path)
    a=p.parse_args()
    t=time.monotonic()
    path=a.root/'upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py'
    assert sha256(path.read_bytes()).hexdigest()=='36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349'
    m=runpy.run_path(str(path))
    word=m['load_json'](a.root/'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz',m['WORD_GZIP'],True)
    atlas=m['Atlas'](word['frames'])
    tapes=[m['run_tape'](word,atlas,rev) for rev in (False,True)]
    assert all(h.output==m['expected_operator'](bool(i)) and h.dirty==3554 for i,h in enumerate(tapes))
    result=json.loads(a.result.read_bytes())
    assert result['status']=='exhausted' and result['witness'] is None
    count=dimension_ok=two_sided=nested=0
    assert len(result['charts'])==2*len(atlas.body)==1272
    for ch in atlas.body:
        left,right=[in_span([obs.row for obs in h.stock[ch]]) for h in tapes]
        valid=[]
        nonzero=[]
        for owner in range(222,word['public']):
            x,y=word['start'][owner],word['final'][owner]
            dx=len(atlas.body[x]); dy=len(atlas.body[y]); dc=len(atlas.body[ch])
            count+=2
            if min(dx,dy)<dc<max(dx,dy):
                valid.append(owner)
                dimension_ok+=2
                if left(1<<owner) and right(1<<owner):
                    two_sided+=2
                    g,k=atlas.grade(x,ch),atlas.grade(ch,y)
                    if g and k and g+k==abs(dx-dy):
                        nested+=2
                        nonzero.append(owner)
        for rev in range(2):
            row=result['charts'][f'{rev}/{ch}']
            assert int(row['dimension_eligible'],16)==sum(1<<i for i in valid)
            assert row['all_time']==nonzero==[] and row['causal_rejected']==[]
    assert count==result['all'] and in_span([3,2])(1) and not in_span([3])(1)
    receipt=dict(chart_helper_orientations=count,dimension_eligible=dimension_ok,joint_before_geometry=two_sided,
                 joint_after_geometry=nested,verified_source='literal full forward and adjoint',
                 source_dirty_retires=[h.dirty for h in tapes],scientific_elapsed_s=time.monotonic()-t)
    a.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt)

if __name__=='__main__':
    main()
