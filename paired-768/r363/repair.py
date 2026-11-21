"""Independently recover every named A-D shared obstruction on the original physical tape."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip,json,runpy,subprocess,sys,tarfile,tempfile,time
def need(x,m):
    if not x:raise ValueError(m)
def put(p,obj):p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
def go(a):
    need(sys.version_info[:2]==(3,12) and __debug__,'CPython3.12')
    hashfile=lambda p:sha256(p.read_bytes()).hexdigest()
    need(hashfile(a.helper)=='798589c4bcdd19413bb270367b08862482d827191b66344810d1c05c7186be41','directed price checker')
    H=runpy.run_path(str(a.helper));digest=H['dig']
    for n,s in H['PINS'].items():need(hashfile(a.peer/n)==s,n)
    need(hashfile(a.accept)==H['ACCEPT'] and hashfile(a.r361)=='40f9e71f6485b0296bd1bb403964cfde6ba4722f7d1be11e94dcf403b474ec48','baselines')
    w=json.loads(gzip.decompress((a.peer/'BINARY-CANDIDATE.json.gz').read_bytes()))
    app=json.loads((a.peer/'APPLICATION.json').read_bytes());rb=F(app['binary_raw'][1]);old=H['OLD']
    with tarfile.open(a.peer/'APPLICATION-SOURCES.tar.gz') as ar:
        src=ar.extractfile('parent/binary/independent/literal.py').read();cl=ar.extractfile('source/research/paired-query-only-bit/EFREE-CALLER.json.gz').read()
    need(digest(src)==H['LITERAL'] and digest(cl)==H['CALLER'],'original tape and caller')
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'literal.py';path.write_bytes(src);lit=runpy.run_path(str(path))
    caller=json.loads(gzip.decompress(cl));ev=Counter(i[0] for i in caller['events'])
    charts=lit['Charts'](w['frames']);d=charts.rank
    need(lit['canonical'](w)==H['WORD'] and charts.main_contacts(w['start'],w['final'])==111,'word and fixed anchors')
    fixed=set(w['start'][:222]+w['final'][:222]);moves={i:(r[2],r[3]) for i,r in enumerate(w['program']) if r[0]=='MOVE'}
    helpers={i:(w['start'][i],w['final'][i]) for i in range(222,w['public'])}
    incident=defaultdict(set);opp=defaultdict(set)
    def snapshot(edges,prod):
        hist=Counter()
        for i,(x,y) in edges.items():
            v=charts.leg(x,y);need(not prod or d[y]>d[x],'original productive')
            hist[v]+=1
            for z in (x,y):incident[z].add((prod,i))
            if not prod:opp[x].add(y);opp[y].add(x)
        return hist
    native=(snapshot(moves,False),snapshot(helpers,True))
    P,T=lit['paired_invoice'](caller,*native,ev)
    need(P==H['hist'](app['binary_native']['paid_all']) and T==H['hist'](app['binary_native']['productive_all']) and lit['ordinary'](w,caller,ev,P,T)==app['binary_native']['ordinary'],'signed control')
    prior={(i,j):reason for i,j,reason in json.loads(a.r361.read_text())}
    pairs=sorted((x,y) for x in opp if x not in fixed for y in opp[x])
    need(len(pairs)==3010 and set(pairs)==set(prior),'all prior pair keys')
    triggers=[];counts=Counter();canonical=defaultdict(list)
    for A,B in pairs:
        bad=sorted(x for x in opp[A] if d[x]==d[B] and x!=B)
        need(bool(bad)==(prior[A,B]=='zero distinct paid grade'),'all immediate paid failures')
        if not bad:state='no paid obstruction'
        elif len(bad)>1:state='multiple distinct blockers'
        elif bad[0] in fixed:state='single protected blocker'
        else:
            D=bad[0];state='eligible singleton'
            canonical[min(A,D),max(A,D),B].append([A,B,D])
        counts[state]+=1;triggers.append([A,B,bad,state])
    put(a.out/'triggers.json',triggers)
    costing={};states=Counter();positive=[];proofs=[];maxgross=F(0);separators=[]
    H['static_guards']()
    for triple,witness in sorted(canonical.items()):
        A,D,B=triple;replace={A:B,D:B};affected=sorted(incident[A]|incident[D]);delta=[Counter(),Counter()];delclocks=[];price=F(0);errors=[];edges=[]
        for prod,i in affected:
            x,y=(helpers if prod else moves)[i];g=abs(d[y]-d[x]);u,v=replace.get(x,x),replace.get(y,y)
            need(u==B or v==B,'exact incidence')
            delta[prod][g]-=36
            if not prod and u==v:
                delclocks.append(i);price+=36*F(H['power'](g,1-old)[1],H['SCALE']);continue
            new=d[v]-d[u] if prod else abs(d[v]-d[u])
            if new<=0:errors.append([prod,i,x,y,u,v]);continue
            delta[prod][new]+=36;edges.append((prod,i,x,y,u,v))
        maxgross=max(maxgross,price)
        if errors:
            states['grade-invalid joint edit']+=1;proofs.append([triple,delclocks,str(price),errors]);continue
        p=P.copy();t=T.copy();p.update(delta[0]);t.update(delta[1]);p=+p;t=+t
        need(sum(p.values())+36*len(delclocks)==sum(P.values()) and sum(t.values())==sum(T.values()),'joint net census')
        sig=tuple(sorted(p.items())),tuple(sorted(t.items()))
        if sig not in costing:
            s=t.copy();s.subtract(p);cap=H['upper_bound'](s)
            upper=F(H['moment'](s,1-old)[1],H['SCALE'])
            slope=-F(sum(n*H['power'](r,1-(H['UPPER'] if n>0 else old),True)[n<0] for r,n in s.items()),H['SCALE'])
            state='below comparator' if cap<=old else H['price_gates'](t,p)
            if state=='PASS' and H['moment'](s,1-rb)[0]<=0:state='old raw crossing unresolved'
            costing[sig]=(state,cap,upper,slope)
        state,cap,upper,slope=costing[sig];states[state]+=1
        ordinary=lit['ordinary'](dict(w,program=range(len(w['program'])-len(delclocks))),caller,ev,p,t)
        proofs.append([triple,delclocks,str(price),state,str(cap),str(upper),str(slope),ordinary])
        if state=='PASS':positive.append((cap,triple,p,t,edges,delclocks,ordinary))
    put(a.out/'profiles.json',proofs);positive.sort(key=lambda z:(-z[0],z[1]))
    best=None
    for cap,triple,p,t,edges,delclocks,ord1 in positive[a.start:a.start+128]:
        fail=None
        for prod,i,x,y,u,v in edges:
            try:charts.leg(u,v)
            except ValueError:
                l,h=sorted((u,v),key=d.get)
                cert=next((j,k,str(z)) for j,r in enumerate(charts.frames[l][0]) for k,s in enumerate(charts.frames[h][1]) if (z:=sum(x*y for x,y in zip(r,s))))
                fail=[prod,i,l,h,cert];break
        if fail:separators.append([triple,fail]);continue
        A,D,B=triple;newtag=lambda j:B if j in (A,D) else j
        program=[]
        for j,rec in enumerate(w['program']):
            op=rec[0]
            if op=='SWAP':program.append(rec)
            elif op=='MOVE':
                l,h=map(newtag,rec[2:]);need((l==h)==(j in delclocks),'exact dropped instruction')
                if l!=h:program.append([*rec[:2],l,h])
            else:program.append([*rec[:-1],newtag(rec[-1])])
        word=dict(w,start=list(map(newtag,w['start'])),final=list(map(newtag,w['final'])),program=program)
        for rev in (False,True):
            out,rec,_=lit['tape'](word,charts,adjoint=rev)
            need(out==lit['expected_rows'](w['public'],rev),'arbitrary signed values')
        pr=Counter(charts.leg(x,y) for x,y in zip(word['start'][222:],word['final'][222:]))
        px,tx=lit['paired_invoice'](caller,rec['paid'],pr,ev);need(px==p and tx==t and lit['ordinary'](word,caller,ev,px,tx)==ord1,'full rebuilt literal')
        best=dict(triple=triple,word=lit['canonical'](word),deleted=delclocks,paid=dict(p),productive=dict(t),ordinary=ord1)
        put(a.out/'candidate.json',word);break
    tryct=len(separators)+int(best is not None)
    result=dict(scope=len(pairs),classifications=dict(counts),canonical_triples=len(canonical),source=H['PINS'],accept=H['ACCEPT'],word=H['WORD'],old=str(old),signed_local_calls=ev['LOCAL'],native_moves=len(moves),native_productive=len(helpers),full_prices=dict(states),max_deleted_charge_upper=str(maxgross),price_profile_count=len(costing),max_valid_margin_upper=str(max(z[2] for z in costing.values())) if costing else None,largest_margin_derivative_upper=str(max(z[3] for z in costing.values())) if costing else None,ranked=[z[1] for z in positive],tested=tryct,unresolved_ranked=len(positive)-a.start-tryct,geometry_obstructions=separators,one_candidate=best,triggers_sha256=hashfile(a.out/'triggers.json'),profiles_sha256=hashfile(a.out/'profiles.json'))
    put(a.out/'result.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source','geometry_obstructions','ranked','one_candidate')},sort_keys=True))
if __name__=='__main__':
    p=ArgumentParser()
    for n in ('peer','accept','helper','r361','out'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--start',type=int,choices=(0,128),default=0);p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:go(a)
    else:
        a.out.mkdir();begin=time.monotonic()
        try:rc=subprocess.run([sys.executable,'-IB',__file__,'--child',*sys.argv[1:]],timeout=45).returncode
        except subprocess.TimeoutExpired:rc=124
        put(a.out/'time.json',dict(exit=rc,cap=45,reserve=15,elapsed=time.monotonic()-begin));raise SystemExit(rc)
