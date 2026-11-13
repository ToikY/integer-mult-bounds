"""Exact fixed-deadline gates for the staggered owned1547 variant."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
import sys

HELPER_PIN = 'aa98dca3f4dc9706c094e2a9fcc2f708c0eea6a8a7709b9522e0f15040a1c1ec'
LATE = (41950, 761, 402, (569,))
CLEAR = (39897, 470, 1547, (402, 727, 1164, 1536))


def emit(**result):
    print(json.dumps(result, default=str, sort_keys=True), flush=True)


def evaluate(row, probe):
    return sum((q*probe.get(i,0) for i,q in row.items()), Q(0))


def difference(a, b):
    return {i:a.get(i,0)-b.get(i,0) for i in a.keys()|b.keys()
            if a.get(i,0)!=b.get(i,0)}


def solve(old, new, donors, basis, representation):
    donor_basis = basis(donors)
    target_remainder, target_terms = representation(donor_basis, old)
    self_remainder, self_terms = representation(donor_basis, new)
    if self_remainder and not target_remainder:
        return {'status':'ZERO_SELF_REQUIRED', 'self_probe':separator(donor_basis, self_remainder)}
    combined = basis([new,*donors])
    residual, terms = representation(combined, old)
    if residual:
        probe = separator(combined, residual)
        assert evaluate(old,probe)==1 and evaluate(new,probe)==0
        assert all(evaluate(row,probe)==0 for row in donors)
        return {'status':'EXACT_COLLISION', 'probe':probe, 'old':1, 'edited':0,
                'donor_values':[0]*len(donors)}
    if self_remainder:
        assert terms[0]
        return {'status':'SUPPORT_SURVIVES', 'self':terms.pop(0),
                'donors':{i-1:v for i,v in terms.items()}}
    assert not target_remainder
    terms = {i:target_terms.get(i,0)-self_terms.get(i,0)
             for i in target_terms.keys()|self_terms.keys()}
    return {'status':'SUPPORT_SURVIVES','self':1,'donors':{i:v for i,v in terms.items() if v}}


def separator(pivots, residual):
    free = min(residual)
    assert free not in pivots
    probe = {free:1/residual[free]}
    for i,(row,_) in sorted(pivots.items(),reverse=True):
        v = evaluate(row,probe)
        if v:
            probe[i] = -v
    return probe


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    stages=[]
    def cap(_sig,_frame):
        emit(status='UNRESOLVED_CAP', completed=stages, seconds_cap=30)
        raise SystemExit(124)
    signal(SIGALRM,cap)
    alarm(30)
    root=Path(sys.argv[1])
    helper=Path(__file__).resolve().with_name('check_fusion.py')
    assert sha256(helper.read_bytes()).hexdigest()==HELPER_PIN
    prior=run_path(str(helper))
    raw={p:(root/p).read_bytes() for p in prior['PINS']}
    assert {p:sha256(b).hexdigest() for p,b in raw.items()}==prior['PINS']
    payload=decompress(raw['7481-WORD.json.gz'])
    app=json.loads(raw['7481-APPLICATION.json'])
    assert sha256(payload).hexdigest()==app['candidate_canonical_sha256']
    word=json.loads(payload); tape=word['program']; n=word['public']
    assert len(tape)==76475 and n==1501
    assert tape[30581]==['MOVE',1547,601,470,True]
    assert tape[39897]==['CLEAR',1547,470]
    assert tape[41950]==['ADD',569,402,'1',761]
    assert tape[41948]==['MOVE',569,594,761,False]
    assert tape[41949]==['MOVE',402,470,761,False]
    assert tape[41951]==['MOVE',1164,470,761,False]
    gate=run_path(str(root/'gate.py')); reverse=gate['exact_cut_rows']
    u,=reverse(tape[:30531],[1510],n)
    edits=prior['EDIT']; drop=prior['DROP']
    active=dict(enumerate(word['initial']))
    edited=[]; cuts={}
    def step(event):
        op,d,*a=event
        if op=='INIT':
            assert d>=n and d not in active
            active[d]=a[0]
        elif op=='CLEAR':
            assert d>=n and active.pop(d)==a[0]
        elif op=='MOVE':
            assert active[d]==a[0] and a[2]==(d>=n)
            active[d]=a[1]
        elif op in ('ADD','COPY'):
            assert active[d]==active[a[0]]==a[-1]
        else:
            assert op=='SCALE' and active[d]==a[-1]
        edited.append(event)
    for clock,event in enumerate(tape[:41951]):
        if clock in (30590,39897,41950):
            cuts[clock]=(len(edited), dict(active))
        if clock==30581:
            step(['ADD',1547,1521,'4',601])
        if clock not in drop:
            step(edits.get(clock,event))
    early,_=cuts[30590]
    assert reverse(tape[:30590],[1536],n)==reverse(edited[:early],[1536],n)
    stages.append('early1536 restored')
    def deadline(case):
        clock,chart,recipient,donors=case
        stop,state=cuts[clock]
        assert {i for i,c in state.items() if c==chart}=={recipient,*donors}
        old,*old_donors=reverse(tape[:clock],[recipient,*donors],n)
        new,*rows=reverse(edited[:stop],[recipient,*donors],n)
        assert difference(old,new)==u
        if clock==41950:
            assert rows==old_donors
        outcome=solve(old,new,rows,gate['basis'],gate['representation'])
        return dict(clock=clock,chart=chart,recipient=recipient,donor_roles=donors,**outcome)
    late=deadline(LATE); stages.append('late402 resolved')
    clear=deadline(CLEAR) if late['status']=='SUPPORT_SURVIVES' else None
    lo,hi=map(Q,app['directed_crossing_bracket'])
    h=run_path(str(root/'pricing.py'))['power_bounds']
    gross=[17*(1+h(2,hi)[0]-h(3,lo)[1]),17*(1+h(2,lo)[1]-h(3,hi)[0])]
    alarm(0)
    emit(status='LATE_FIXED_REPAIR_EXCLUDED' if clear is None else 'LATE_SUPPORT_SURVIVES',
         mandatory=late, conservative_clear=clear, gross=gross, pins=prior['PINS'],
         helper_sha256=HELPER_PIN, early1536_restored=True, seconds_cap=30)


if __name__=='__main__':
    main()
