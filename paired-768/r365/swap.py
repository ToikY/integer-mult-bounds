"""Independently test exchanging two incident unequal-dimensional existing chart labels."""
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
    need(hashfile(a.accept)==H['ACCEPT'],'baselines')
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
    for rev in (True,False):
        rows,baseline,_=lit['tape'](w,charts,adjoint=rev)
        need(rows==lit['expected_rows'](w['public'],rev) and baseline['paid']==native[0],'signed native baseline')
    seeds=defaultdict(set)
    for prod,edge in ((True,helpers),(False,moves)):
        for i,(x,y) in edge.items():
            if x in fixed or y in fixed or d[x]==d[y]:continue
            key=tuple(sorted((x,y)));seeds[key].add('helper' if prod else 'paid')
    counts=Counter();cases=[];formats=Counter();profiles={};ranked=[];tested=[];best=None;H['static_guards']()
    oldordinary=lit['ordinary'](w,caller,ev,P,T)
    for pair in sorted(seeds):
        A,B=pair;change={A:B,B:A};delta=[Counter(),Counter()];mutual=[0,0];issues=[[],[]];boundary=[]
        for prod,i in sorted(incident[A]|incident[B]):
            x,y=(helpers if prod else moves)[i];u,v=change.get(x,x),change.get(y,y)
            related=(u==y and v==x);mutual[prod]+=int(related)
            need(u!=v,'injective relabel cannot elide an opcode')
            grade=d[v]-d[u] if prod else abs(d[v]-d[u]);g=abs(d[y]-d[x])
            if grade<=0:issues[prod].append([i,x,y,u,v,grade])
            else:
                if related:need(g==grade and not prod,'mutual MOVE grade')
                delta[prod][g]-=36;delta[prod][grade]+=36
                boundary.append((prod,i,x,y,u,v))
        formats['+'.join(sorted(seeds[pair]))]+=1
        need(any(mutual) and (not mutual[1] or issues[1]),'seed membership and reversed productive')
        if any(issues):
            reason='both' if all(issues) else 'paid equal-dimension' if issues[0] else 'productive nonpositive'
            cases.append([pair,reason,mutual,[e[0] if e else None for e in issues]]);counts[reason]+=1;continue
        p=P.copy();t=T.copy();p.update(delta[0]);t.update(delta[1]);p=+p;t=+t
        need(sum(p.values())==sum(P.values()) and sum(t.values())==sum(T.values()),'nondeletion invoice')
        need(lit['ordinary'](w,caller,ev,p,t)==oldordinary,'whole ordinary and backing')
        sig=(tuple(sorted(p.items())),tuple(sorted(t.items())))
        if sig not in profiles:
            s=t.copy();s.subtract(p);cap=H['upper_bound'](s)
            margin=F(H['moment'](s,1-old)[1],H['SCALE'])
            slope=-F(sum(n*H['power'](k,1-(H['UPPER'] if n>0 else old),True)[n<0] for k,n in s.items()),H['SCALE'])
            state='same signed invoice' if p==P and t==T else 'below comparator' if cap<=old else H['price_gates'](t,p)
            if state=='PASS' and H['moment'](s,1-rb)[0]<=0:state='unresolved raw separation'
            profiles[sig]=(state,cap,margin,slope)
        state,cap,margin,slope=profiles[sig]
        counts[state]+=1;cases.append([pair,state,mutual,list(map(str,(cap,margin,slope)))])
        if state=='PASS':ranked.append((cap,A,B,boundary,p,t))
    ranked.sort(key=lambda q:(-q[0],q[1],q[2]));put(a.out/'cases.json',cases)
    put(a.out/'ranked.json',[[a0,b0] for _,a0,b0,*rest in ranked])
    for cap,A,B,boundary,p,t in ranked[:128]:
        bad=None
        for prod,i,x,y,u,v in boundary:
            try:charts.leg(u,v)
            except ValueError:
                l,h=sorted((u,v),key=d.get)
                cert=next((j,k,str(z)) for j,r in enumerate(charts.frames[l][0]) for k,s in enumerate(charts.frames[h][1]) if (z:=sum(x*y for x,y in zip(r,s))))
                bad=[prod,i,l,h,cert];break
        tested.append([A,B,bad])
        if bad:continue
        m=lambda z:B if z==A else A if z==B else z
        ops=[]
        for r in w['program']:
            if r[0]=='SWAP':ops.append(r)
            elif r[0]=='MOVE':ops.append([*r[:2],m(r[2]),m(r[3])])
            else:ops.append([*r[:-1],m(r[-1])])
        word=dict(w,start=list(map(m,w['start'])),final=list(map(m,w['final'])),program=ops)
        need(word['start'][:222]==w['start'][:222] and word['final'][:222]==w['final'][:222],'all main')
        for rev in (False,True):
            rows,rec,_=lit['tape'](word,charts,adjoint=rev);need(rows==lit['expected_rows'](w['public'],rev),'arbitrary input action')
        n=Counter(charts.leg(x,y) for x,y in zip(word['start'][222:],word['final'][222:]))
        pi,ti=lit['paired_invoice'](caller,rec['paid'],n,ev);need(p==pi and t==ti and lit['ordinary'](word,caller,ev,pi,ti)==oldordinary,'literal invoice')
        best=dict(pair=[A,B],sha256=lit['canonical'](word),ordinary=oldordinary,paid=dict(p),productive=dict(t));put(a.out/'candidate.json',word);break
    result=dict(source=H['PINS'],word=H['WORD'],comparator=str(old),r352=H['ACCEPT'],source_helper=hashfile(a.helper),native_paid=len(moves),native_productive=len(helpers),num_signed_local=ev['LOCAL'],external=dict(ev),anchored_labels=len(fixed),scope=len(seeds),seeds_by_type=dict(formats),decisions=dict(counts),signed_profiles=len(profiles),profiles=[dict(state=st,upper=str(cap),absolute_margin_upper=str(ma),margin_derivative_upper=str(sl),paid=dict(p),productive=dict(t)) for (p,t),(st,cap,ma,sl) in profiles.items()],num_ranked=len(ranked),tested=tested,unvisited=len(ranked)-len(tested),one_candidate=best,complete_ordinary=oldordinary,ledger=hashfile(a.out/'cases.json'),ranking=hashfile(a.out/'ranked.json'))
    put(a.out/'result.json',result);print(result['scope'],result['seeds_by_type'],result['decisions'],len(profiles),len(ranked),len(tested),best and best['pair'])
if __name__=='__main__':
    p=ArgumentParser()
    for n in ('peer','accept','helper','out'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:go(a)
    else:
        a.out.mkdir();t=time.monotonic()
        try:rc=subprocess.run([sys.executable,'-IB',__file__,'--child',*sys.argv[1:]],timeout=45).returncode
        except subprocess.TimeoutExpired:rc=124
        put(a.out/'time.json',dict(exit=rc,cap=45,reserve=15,elapsed=time.monotonic()-t));raise SystemExit(rc)
