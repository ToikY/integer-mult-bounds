"""Rebuild independent 451-factor and producer receipts from exact sources."""
from pathlib import Path
import shutil,sys,subprocess,time,json,hashlib
p=Path(__file__).resolve().parent
c=p/'producer'
shutil.copytree(p/'extract/451-consumer',c,ignore=shutil.ignore_patterns('replay','clean-replay-output'))
result=[]
for name,target,out in [('replay_451.py','BIT-451.json','BIT-451.json'),('carrier_independent.py','CARRIER-INDEPENDENT.json','CARRIER-INDEPENDENT.json'),('carrier_labels.py','CARRIER-LABELS.json','CARRIER-LABELS.json'),('consumer_review.py','CONSUMER-REVIEW.json','CONSUMER-REVIEW.json'),('prime_scope_check.py','independent-review/prime-receipt.json',None)]:
 t=time.monotonic();proc=subprocess.run([sys.executable,'-IB',name],cwd=c,capture_output=True)
 (p/('producer-'+name+'.log')).write_bytes(proc.stdout+proc.stderr)
 got=(c/'replay'/out).read_bytes() if out is not None and (c/'replay'/out).exists() else proc.stdout
 same=(c/target).read_bytes()==got
 result.append(dict(command=['python3.12','-IB',name],target=target,exit=proc.returncode,byte_equal=same,sha256=hashlib.sha256(got).hexdigest(),seconds=time.monotonic()-t))
 (p/'producer-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
 assert same and not proc.returncode,(name,proc.stderr.decode()[-400:],same)
print('PASS',len(result))
