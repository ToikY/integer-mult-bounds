"""Matched R355 single-cut runner. One frozen case and two independent full endpoint replays."""
from argparse import Namespace
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter_ns
import json,runpy,subprocess,sys

def verify(path, expected):
    assert sha256(path.read_bytes()).hexdigest()==expected

def main(root):
    old=root/'r355'; solver=old/'solve.py'; audit=old/'audit.py'
    verify(solver,'ea670f0147465c3786bec516021d026767a8a4960676d65f26b1db110fa3a7a3')
    verify(audit,'97fc7367fcffaff5888a08974dfa762f609297f1144458cc59a9abfabf307ca0')
    verify(old/'receipt.json','e500abed99a9caf5d4633ef77b119d05bace82adb5b3c9d16cf0f2e30ec031fd')
    verify(old/'primary.json','099c3b5b333a91fe830c3addbd9225dc22ccaad1926c5f824a4638683996a61a')
    peer=root/'inputs'; accepted=root/'r352/accept.json'
    rows=[]; frozen=json.loads((old/'primary.json').read_bytes())
    with TemporaryDirectory() as d:
        for mode in ('current_exact','shared_singleton_first'):
            src=runpy.run_path(str(solver))
            run=src['run'];exact=src['solve']; measures={}
            def timed(donors,target):
                start=perf_counter_ns()
                if mode=='current_exact':
                    answer=exact(donors,target)
                else:
                    # All 630 singleton inputs, simultaneously; if none separates, use the exact default.
                    occupied=0
                    for _,r,_ in donors: occupied|=r
                    hits=target & ~occupied
                    if hits:
                        z=hits & -hits
                        rank=exact(donors,0)[0]
                        answer=rank,None,z
                    else: answer=exact(donors,target)
                rank,comb,z=answer
                assert rank==4 and comb is None and (target&z).bit_count()%2==1
                assert all((r&z).bit_count()%2==0 for _,r,_ in donors)
                measures['solver_and_local_verification_ns']=perf_counter_ns()-start
                return answer
            run.__globals__['solve']=timed
            claim=Path(d)/(mode+'.json');ind=Path(d)/(mode+'-audit.json')
            tic=perf_counter_ns()
            run(Namespace(peer=peer,probe=root/'r354/primary.json',accept=accepted,out=claim))
            loaded=json.loads(claim.read_bytes())
            for k in ('cut','target','legal_other_donors','legal_donor_rank','receiver_form','status','donor_values_on_separator','adjoint_output'):
                assert loaded[k]==frozen[k],k
            stop=perf_counter_ns()
            subprocess.run([sys.executable,'-IB',audit,'--peer',peer,'--accept',accepted,'--previous',root/'r354/receipt.json','--source',root/'r354/audit.py','--out',ind],check=True,stdout=subprocess.DEVNULL)
            verify(ind,'e500abed99a9caf5d4633ef77b119d05bace82adb5b3c9d16cf0f2e30ec031fd')
            done=perf_counter_ns()
            rows.append(dict(method=mode,solver_ns=measures['solver_and_local_verification_ns'],primary_ns=stop-tic,
                             independent_replay_ns=done-stop,total_to_checked_decision_ns=done-tic,separator=loaded['separating_input'],rank=loaded['legal_donor_rank'],resolved=1,open=0))
    return dict(case_id='8027:cut15264:read30338:chart585:3226->3604',case_cap=1,runner_cap_s=15,active_design_cap_s=90,results=rows)
if __name__=='__main__':
    assert sys.version_info[:2]==(3,12) and __debug__
    result=main(Path(sys.argv[1]).resolve())
    with Path(sys.argv[2]).open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
