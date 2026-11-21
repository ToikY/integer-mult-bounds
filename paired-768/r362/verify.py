"""Verify component completeness, real chart-contact controls and the exact prior coverage mapping."""
from pathlib import Path
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
import gzip,json,runpy,sys,subprocess,time
def need(x,msg):
    if not x:raise ValueError(msg)
def dig(p):return sha256(p.read_bytes()).hexdigest()
def check(a):
    source=Path(__file__).with_name('check.py');builder=runpy.run_path(str(source));r=json.loads(a.result.read_bytes())
    need(dig(a.word)=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326','archived literal')
    w=json.loads(gzip.decompress(a.word.read_bytes()));cc,m,t,refs,arcs,start,final=builder['graph'](w)
    labels=[t[k] for k in m];need(len(set(labels))==len(labels)==636 and set(labels)==set(map(int,w['frames'])),'one-to-one onto full catalog')
    protected={cc[i] for i in start[:222]+final[:222]};neighbors=Counter((t[u],t[v]) for u,v,_ in arcs)
    eligible=[(L,B) for k,L in zip(m,labels) if k not in protected for B in sorted(labels) if B!=L]
    prior=Counter()
    pairs=set()
    for A,B in eligible:
        if neighbors[A,B]+neighbors[B,A]:pairs.add((A,B))
        prior['R361 paid-neighbor contractions' if (A,B) in pairs else 'R360 no identity contractions']+=1
    need(len(eligible)==sum(r['classification'].values()) and len(pairs)==3010 and len(protected)==r['main_anchored'],'correspondence')
    need(dig(a.r361)=='40f9e71f6485b0296bd1bb403964cfde6ba4722f7d1be11e94dcf403b474ec48','R361 exact original ordered exclusions')
    all361=json.loads(a.r361.read_bytes());need(set((a,b) for a,b,_ in all361)==pairs,'complete neighbor equality')
    # The ordinary ledger has fixed roles/banks/caller; each removed opcode cuts exactly one
    # native instruction in 36 calls, 36 paid jobs, and hence 4*36 route groups.
    charge=json.loads((a.word.parent/'APPLICATION.json').read_bytes())['binary_native']['ordinary']
    by_deletion=Counter(neighbors[x,y]+neighbors[y,x] for x,y,gate in all361 if gate=='raw ceiling')
    need(sum(by_deletion.values())==454,'R361 full charge count')
    ordinary={str(k):dict(cases=n,owned_backing=charge['owned_backing'],ordinary_records=charge['ordinary_records']-36*k*(16*charge['native_banks_and_scratch']+4*80*(134**2+134))) for k,n in by_deletion.items()}
    idx=next(i for i,v in enumerate(w['program']) if v[0]=='ADD')
    stream=w['program'].copy();stream[idx]=[*stream[idx][:-1],(stream[idx][-1]+1)%636]
    try:builder['graph'](dict(w,program=stream))
    except ValueError as e:need(str(e)=='ADD tag','exact rejected control')
    else:raise ValueError('modified ADD passed')
    toy={'public':2,'owned_fields':1,'start':[0,1],'final':[1,0],'program':[['INIT',2,1],['SWAP',0,1],['ADD',0,2,1],['CLEAR',2,1]]}
    sc,_,_,_,_,st,en=builder['graph'](toy);need(sc[st[1]]==sc[en[0]]==sc[2] and sc[st[0]]!=sc[en[0]],'swapped ownership')
    try:builder['graph'](dict(toy,program=[toy['program'][0],*toy['program'][2:]]))
    except ValueError as e:need(str(e)=='ADD tag','omitted physical swap control')
    else:raise ValueError('omitted SWAP passed')
    value=dict(primary_result=dig(a.result),source=dig(source),actual_one_to_one_components=636,graph_controls=dict(changed_add_clock=idx,changed_chart_rejected=True,swapped_owner_contact=True,omitted_swap_rejected=True),exhaustive_price_coverage=dict(prior),R361_complete_dim_valid_ordinary=ordinary,unresolved=0)
    a.out.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':
    p=ArgumentParser()
    for n in ('word','result','out','r361'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:check(a)
    else:
        begin=time.monotonic();z=subprocess.run([sys.executable,'-IB',__file__,'--child',*sys.argv[1:]],timeout=15);print('exit',z.returncode,'seconds',time.monotonic()-begin);raise SystemExit(z.returncode)
