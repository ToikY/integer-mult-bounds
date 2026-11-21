"""Replay every R365 decision from the literal tape, recomputing every grade on eligibility."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip,json,runpy,sys,subprocess,time
def need(x,m):
    if not x:raise ValueError(m)
def dig(p):return sha256(p.read_bytes()).hexdigest()
def check(a):
    need(dig(a.helper)=='798589c4bcdd19413bb270367b08862482d827191b66344810d1c05c7186be41','directed bound')
    h=runpy.run_path(str(a.helper));r=json.loads((a.run/'result.json').read_bytes());ledger=json.loads((a.run/'cases.json').read_bytes())
    for n,sha in h['PINS'].items():need(dig(a.peer/n)==sha,n)
    w=json.loads(gzip.decompress((a.peer/'BINARY-CANDIDATE.json.gz').read_bytes()));base=json.loads((a.peer/'APPLICATION.json').read_bytes())['binary_native'];pub=w['public']
    edges=[(i,x,y) for i,row in enumerate(w['program']) if row[0]=='MOVE' for x,y in [row[2:]]]
    prod=[(i,w['start'][i],w['final'][i]) for i in range(222,pub)];dim={int(j):v['dim'] for j,v in w['frames'].items()}
    main=set(w['start'][:222]+w['final'][:222]);allowed={tuple(sorted((x,y))) for _,x,y in edges+prod if x not in main and y not in main and dim[x]!=dim[y]}
    need(allowed=={tuple(z[0]) for z in ledger} and len(ledger)==len(allowed)==969,'full exact scope')
    nohelper=sum(not({x,y}&main) for _,x,y in prod);need(nohelper==0,'protected helper seed endpoint')
    old=(Counter(abs(dim[x]-dim[y]) for _,x,y in edges),Counter(dim[y]-dim[x] for _,x,y in prod))
    axes=[h['hist'](base[name]) for name in ('paid_all','productive_all')]
    need(dig(a.run/'cases.json')==r['ledger'],'ledger')
    actual=Counter();oldpaidclocks={i:(x,y) for i,x,y in edges}
    for pair,state,mutual,wit in ledger:
        A,B=pair;flip={A:B,B:A}
        if state=='paid equal-dimension':
            i,x,y,u,v,grade=wit[0]
            need(oldpaidclocks[i]==(x,y) and (flip.get(x,x),flip.get(y,y))==(u,v) and u!=v and dim[u]==dim[v] and grade==0,'concrete paid failure')
        else:
            fresh=[]
            for exchange,prod0 in ((edges,False),(prod,True)):
                g=Counter()
                for _,x,y in exchange:
                    u,v=flip.get(x,x),flip.get(y,y)
                    rank=dim[v]-dim[u] if prod0 else abs(dim[v]-dim[u])
                    need(u!=v and rank>0,'every original typed edge remains strictly positive');g[rank]+=1
                fresh.append(g)
            for n,(c,b,f,pkey) in enumerate(zip(axes,old,fresh,['paid','productive'])):
                rebuilt=Counter({i:c[i]+36*(f[i]-b[i]) for i in c.keys()|b.keys()|f.keys()});need(+rebuilt==h['hist'](r['profiles'][0][pkey]),'all complete grades')
            need(state=='below comparator' and wit[1:]==[r['profiles'][0]['absolute_margin_upper'],r['profiles'][0]['margin_derivative_upper']],'directed profile match')
        actual[state]+=1
    pr=r['profiles'][0]
    # Repeat endpoints directly using signed interval dot products and the original immutable comparator.
    ds=h['hist'](pr['productive']);ds.subtract(h['hist'](pr['paid']));oldk=h['OLD'];scale=h['SCALE']
    price=sum(n*h['power'](k,1-oldk)[n>=0] for k,n in ds.items())
    di=-sum(n*h['power'](k,1-(h['UPPER'] if n>0 else oldk),True)[n<0] for k,n in ds.items())
    need(F(price,scale)==F(pr['absolute_margin_upper'])<0 and F(di,scale)==F(pr['margin_derivative_upper'])<0,'global exclusion')
    baseline=axes[1].copy();baseline.subtract(axes[0]);need(h['moment'](baseline,1-oldk)[0]>0,'original baseline good')
    corrupt=ds.copy();corrupt[1]-=1
    need(h['moment'](corrupt,1-oldk)[1]==price-scale,'one extra paid rank-one exposed')
    check_forced=ledger[0][3][0];need(check_forced[3]!=check_forced[4],'deleting counterfeit identity must fail')
    result=dict(result=dig(a.run/'result.json'),ledger=dig(a.run/'cases.json'),explicit_paid_clock_exclusions=actual['paid equal-dimension'],valid_cases_full_word_reconstructed=actual['below comparator'],distinct_profiles=1,candidate_count=0,unresolved=0,uncorrupted_source_control=True,unequal_labels_cannot_be_deleted=check_forced,unit_cost_corruption_changes_signed_price_by='-1',sorted_ids=len(ledger),original_owned_backing=base['ordinary']['owned_backing'],original_ordinary_records=base['ordinary']['ordinary_records'])
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':
    p=ArgumentParser()
    for n in ('peer','helper','run','out'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:check(a)
    else:
        t=time.monotonic();rc=subprocess.run([sys.executable,'-IB',__file__,'--child',*sys.argv[1:]],timeout=15).returncode;print('exit',rc,'seconds',time.monotonic()-t);raise SystemExit(rc)
