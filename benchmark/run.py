"""Replay the exact #7973 closure and compare all seven controls and outer application."""
import sys,json,hashlib,time,subprocess,shutil,os
from pathlib import Path
p=Path(__file__).resolve().parent;r=p/'extract'
H=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert H(p/'replay.tar.gz')=='bffb02e833d8253c693ea3e679fdc1a737a5a45f81089255848d9ee9a7d3487d'
expected={}
for line in (r/'SHA256SUMS').read_text().splitlines():
 h,n=line.split(maxsplit=1);assert n not in expected and H(r/n)==h;expected[n]=h
assert len(expected)==253
runroot=p/'fresh-consumer'
shutil.copytree(r/'451-consumer',runroot,ignore=shutil.ignore_patterns('clean-replay-output'))
result={'python':sys.version,'archive_sha256':H(p/'replay.tar.gz'),'files':len(expected),'runs':[]}
def run(cwd,command,match=None):
 start=time.monotonic(); proc=subprocess.run([sys.executable,'-IB',command],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 fn=Path(command).stem
 (p/(fn+'.stdout')).write_bytes(proc.stdout);(p/(fn+'.stderr')).write_bytes(proc.stderr)
 exact=True if match is None else proc.stdout==(cwd/match).read_bytes()
 result['runs'].append({'command':['python3.12','-IB',command],'cwd':cwd.relative_to(p).as_posix(),'exit':proc.returncode,'seconds':time.monotonic()-start,'expected_file':match,'byte_equal':exact})
 (p/'fresh-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
 assert proc.returncode==0 and exact,(command,proc.stderr.decode()[-500:],exact)
run(runroot,'clean_replay.py')
for fn in ('APPLICATION.json','AUDIT.json','INDEPENDENT.json'):
 assert (runroot/'clean-replay-output'/fn).read_bytes()==(r/'451-consumer/clean-replay-output'/fn).read_bytes()
for cmd,match in [('funded_replay.py','funded-replay-result.json'),('pulse_case_replay.py','pulse-case-result.json'),('all_pulse_replay.py','all-pulse-result.json'),('structural_r4.py','structural-r4-result.json'),('independent_witness.py','independent-witness-result.json'),('qzero-review/independent_certificates.py','qzero-review/independent-certificates-result.json'),('finite-451/replay_451.py','finite-451/FRESH.json')]:
 run(r,cmd,match)
print('PASS',len(result['runs']))
