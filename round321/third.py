"""Find support for an existing independent direction across a two-packet deletion."""
from collections import defaultdict
import gzip, hashlib, json, runpy, sys, time
from pathlib import Path
from itertools import combinations
t=time.monotonic()
root=Path(sys.argv[1])
p=runpy.run_path(str(root.parent/'round320/pairs.py'))
for r,h in p['PINS'].items(): assert hashlib.sha256((root/r).read_bytes()).hexdigest()==h
w=json.loads(gzip.decompress((root/p['WORD']).read_bytes()));g=runpy.run_path(str(root/p['GRAPH']))
S,F,M,R,T=g['extract'](w); order=sorted(M,key=T.get);C=g['basis'](S,M,R,order);V={i:1<<i for i in S}
routes=defaultdict(list); dest=defaultdict(list); src=defaultdict(list)
for k in order:
 V[k]=g['combine'](R[k],V);a,b=M[k];routes[a,b].append(k);dest[b].append(k);src[a].append(k)
n=0;hits=[];example=None
for (a,b),ids in routes.items():
 for i,j in combinations(ids,2):
  for k in dest[b]:
   if T[k]>=T[i]: break
   n+=1
   if example is None and M[k][0]!=a:
    def first_read(m):
     bank=w['program'][T[m]][1]
     return next((idx,op) for idx,op in enumerate(w['program'][T[m]+1:],T[m]+1) if op[0]=='ADD' and op[2]==bank)
    example={'pair':[i,j],'extra':k,'routes':[M[x] for x in (i,j,k)],'clocks':[T[x] for x in (i,j,k)],'first_add_reads':[first_read(x) for x in (i,j,k)],'grade':[abs(w['frames'][str(M[x][0])]['dim']-w['frames'][str(M[x][1])]['dim']) for x in (i,j,k)],'sender_forms':[list(g['indices'](R[x])) for x in (i,j,k)]}
   cols=C[k] in (0,C[i],C[j],C[i]^C[j]);rows=V[k] in (0,V[i],V[j],V[i]^V[j])
   if cols or rows:
    hits.append(dict(pair=[i,j],carrier=k,charts=[a,b,M[k][0]],clocks=[T[i],T[j],T[k]],rows=rows,cols=cols))
out=dict(cases=n,hits=hits,example=example,seconds=time.monotonic()-t)
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(n,len(hits),hits[:5])
