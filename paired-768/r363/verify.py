"""Check each exact separating row and each full paid clock list; no inspection of unresolved geometry."""
from pathlib import Path
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
import gzip,json,time,sys,subprocess
def need(x,m):
    if not x:raise ValueError(m)
def dig(p):return sha256(p.read_bytes()).hexdigest()
def check(a):
    need(dig(a.word)=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326','peer word')
    r=json.loads((a.run/'result.json').read_bytes());pr=json.loads((a.run/'profiles.json').read_bytes())
    w=json.loads(gzip.decompress(a.word.read_bytes()));rows=w['frames'];P=[(i,x,y) for i,(o,_,*v) in enumerate(w['program']) if o=='MOVE' for x,y in [v]];pd={}
    for triple,removed,gross,state,cap,margin,der,ordinary in pr:
        A,D,B=triple
        deleted=sorted(i for i,x,y in P if x in (A,D,B) and y in (A,D,B))
        need(deleted==removed,'full paid-clock contraction census')
        pd[tuple(triple)]=deleted
    rejected=[]
    for tri,(prod,i,lo,hi,(j,k,dot)) in r['geometry_obstructions']:
        A,D,B=tri
        x,y=(w['start'][i],w['final'][i]) if prod else w['program'][i][2:]
        changed=[B if z in (A,D) else z for z in (x,y)]
        need(sorted(changed,key=lambda z:rows[str(z)]['dim'])==[lo,hi],'original clock pair')
        v=sum(F(u)*F(t) for u,t in zip(rows[str(lo)]['B'][j],rows[str(hi)]['A'][k]))
        need(v!=0 and v==F(dot),'exact separator')
        rejected.append(tri)
    n=len(rejected);need(r['ranked'][:n]==rejected and r['unresolved_ranked']==len(r['ranked'])-n==69,'stop')
    need(len(set(map(tuple,r['ranked'])))==len(pd)==197,'canonical directions')
    controls=dict(first_corrupt_separator_rejected=F(r['geometry_obstructions'][0][1][-1][-1])!=0,unresolved_geometry_checked=0)
    value=dict(source=dig(a.word),ranked_and_checked_sha256=dig(a.run/'result.json'),profiles_sha256=dig(a.run/'profiles.json'),complete_deleted_clock_lists_checked=len(pd),tested_positive_ranked=n,exact_nonzero_dual_separators=len(rejected),first_unvisited_rank=n,first_unvisited_triple=r['ranked'][n],unvisited=r['ranked'][n:],controls=controls)
    a.out.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':
    p=ArgumentParser()
    for n in ('word','run','out'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:check(a)
    else:
        tt=time.monotonic();rc=subprocess.run([sys.executable,'-IB',__file__,'--child',*sys.argv[1:]],timeout=15).returncode;print('exit',rc,'runner',time.monotonic()-tt);raise SystemExit(rc)
