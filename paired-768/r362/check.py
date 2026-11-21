"""Build a tag-only undirected equality graph, independently of the primary interval partition."""
from collections import Counter, defaultdict
from argparse import ArgumentParser
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from functools import lru_cache
import gzip,json,subprocess,sys,tarfile,tempfile,time,runpy
def need(z,m):
    if not z:raise ValueError(m)
def put(p,obj):p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
def graph(w):
    start=list(range(w['public']));nextid=len(start)
    live=start+[None]*w['owned_fields'];tag=list(w['start']);adj=[set() for _ in tag]
    refs=[];arcs=[]
    def fresh(t):
        idx=len(tag);tag.append(t);adj.append(set());return idx
    for i,(op,r,*v) in enumerate(w['program']):
        z=live[r]
        if op=='ADD':
            u,t=v;s=live[u];need(z is not None and s is not None and tag[z]==tag[s]==t,'ADD tag')
            adj[z].add(s);adj[s].add(z);refs.append((z,))
        elif op=='SWAP':
            other=v[0];need(z is not None and live[other] is not None,'swap dead')
            live[r],live[other]=live[other],z;refs.append(())
        elif op=='INIT':
            need(z is None,'init live');live[r]=fresh(v[0]);refs.append((live[r],))
        elif op=='CLEAR':
            need(z is not None and tag[z]==v[0],'clear tag');live[r]=None;refs.append((z,))
        else:
            x,y=v;need(op=='MOVE' and z is not None and tag[z]==x,'move tag')
            live[r]=fresh(y);refs.append((z,live[r]));arcs.append((z,live[r],i))
    need(all(z is None for z in live[w['public']:]) and [tag[z] for z in live[:w['public']]]==w['final'],'all endpoints')
    final=live[:w['public']]
    cc=[None]*len(tag);members={}
    for root in range(len(tag)):
        if cc[root] is not None:continue
        todo=[root];cc[root]=root;members[root]=0
        while todo:
            c=todo.pop();members[root]+=1;need(tag[c]==tag[root],'component homogeneous')
            for j in adj[c]:
                if cc[j] is None:cc[j]=root;todo.append(j)
    return cc,members,tag,refs,arcs,start,final
def check(a):
    need(sys.version_info[:2]==(3,12) and __debug__,'python3.12')
    need(sha256(a.helper.read_bytes()).hexdigest()=='798589c4bcdd19413bb270367b08862482d827191b66344810d1c05c7186be41','sealed arithmetic')
    h=runpy.run_path(str(a.helper));dig=h['dig']
    for name,code in h['PINS'].items():need(dig((a.peer/name).read_bytes())==code,name)
    need(dig(a.accept.read_bytes())==h['ACCEPT'],'prior')
    w=json.loads(gzip.decompress((a.peer/'BINARY-CANDIDATE.json.gz').read_bytes()))
    app=json.loads((a.peer/'APPLICATION.json').read_bytes());old=h['OLD'];ub0=Q(app['binary_raw'][1])
    with tarfile.open(a.peer/'APPLICATION-SOURCES.tar.gz') as ar:
        c=ar.extractfile('source/research/paired-query-only-bit/EFREE-CALLER.json.gz').read()
        s=ar.extractfile('parent/binary/independent/literal.py').read()
    need(dig(s)==h['LITERAL'] and dig(c)==h['CALLER'],'support')
    with tempfile.TemporaryDirectory() as td:
        f=Path(td)/'literal.py';f.write_bytes(s);lit=runpy.run_path(str(f))
    caller=json.loads(gzip.decompress(c));event=Counter(e[0] for e in caller['events'])
    need(lit['canonical'](w)==h['WORD'],'native word');ch=lit['Charts'](w['frames']);dim=ch.rank
    cc,members,tag,refs,arcs,start,final=graph(w)
    anchored={cc[j] for j in start[:222]+final[:222]}
    def log(**kw):put(a.out/'progress.json',kw)
    edges=defaultdict(list);p0=Counter();t0=Counter()
    for prod,ar in ((False,arcs),(True,[(z,k,i) for i,(z,k) in enumerate(zip(start,final)) if i>=222])):
        for u,v,i in ar:
            u,v=cc[u],cc[v];need(u!=v,'original positive');r=ch.leg(tag[u],tag[v])
            need(not prod or dim[tag[u]]<dim[tag[v]],'directed')
            edges[u].append((prod,1,tag[v],r));edges[v].append((prod,-1,tag[u],r));(t0 if prod else p0)[r]+=1
    P,T=lit['paired_invoice'](caller,p0,t0,event);ordinary=lit['ordinary'](w,caller,event,P,T)
    need(P==h['hist'](app['binary_native']['paid_all']) and T==h['hist'](app['binary_native']['productive_all']) and ordinary==app['binary_native']['ordinary'],'all legacy signed prices')
    for rev in (True,False):
        observed,rec,_=lit['tape'](w,ch,adjoint=rev);need(observed==lit['expected_rows'](len(start),rev) and rec['paid']==p0,'control signed')
    static=h['static_guards']();charts=defaultdict(list)
    for b in sorted(dim):charts[dim[b]].append(b)
    components=sorted(k for k in members if k not in anchored and edges[k])
    total=Counter();binrows=[];ranked=[];profiles={};at=0
    for k in components:
        A=tag[k]
        for d,labels in sorted(charts.items()):
            delta=[Counter(),Counter()];forced=set();bad=None;dropped=0
            for prod,orient,neighbor,rank in edges[k]:
                diff=(dim[neighbor]-d)*orient
                if prod and diff<=0:bad='nonpositive_productive';break
                if diff==0:forced.add(neighbor);dropped+=1
                else:delta[prod][diff if prod else abs(diff)]+=36
                delta[prod][rank]-=36
            scope=len(labels)-int(A in labels)
            if bad or len(forced)>1:
                state=bad or 'different_equal_dimension_neighbors';total[state]+=scope;binrows.append([k,d,state,scope]);continue
            options=[x for x in labels if x!=A and (not forced or x in forced)]
            total['different_equal_dimension_neighbors']+=scope-len(options)
            if not options:continue
            key=tuple((tuple(sorted((i,n) for i,n in g.items() if n))) for g in delta)
            if key not in profiles:
                pay=P.copy();tar=T.copy();pay.update(delta[0]);tar.update(delta[1]);pay=+pay;tar=+tar
                v=tar.copy();v.subtract(pay)
                root=h['upper_bound'](v);mar=Q(h['moment'](v,1-old)[1],h['SCALE'])
                state='same_histograms' if not any(key) else 'below_comparator' if root<=old else h['price_gates'](tar,pay)
                if state=='PASS' and h['moment'](v,1-ub0)[0]<=0:state='unresolved_raw_separation'
                ord1=lit['ordinary'](dict(w,program=range(len(w['program'])-dropped)),caller,event,pay,tar)
                need(ord1['owned_backing']==ordinary['owned_backing'] and sum(pay.values())==sum(P.values())-36*dropped,'ordinary changes')
                profiles[key]=(state,root,mar,pay,tar,ord1)
            state,root,mar,pay,tar,ords=profiles[key]
            total[state]+=len(options);binrows.append([k,d,state,len(options),str(mar),str(root),dropped,ords['ordinary_records']])
            if state=='PASS':
                vv=tar.copy();vv.subtract(pay);raw_at_c=h['moment'](vv,1-h['C'])[1]
                ranked.append((raw_at_c,k,d,options,key))
        at+=1
        if at%100==0:log(stage='price',index=at,total=len(components))
    need(sum(total.values())==len(components)*(len(dim)-1),'scoped exhaustive')
    ordered=sorted((-m,k,b,d,key) for m,k,d,bs,key in ranked for b in bs)
    todo=[(k,d,b,key) for _,k,b,d,key in ordered]
    put(a.out/'bins.json',binrows);put(a.out/'ranked.json',[[k,d,b] for k,d,b,_ in todo]);log(stage='geometry',cases=len(todo))
    reject=[];best=None
    for k,d,B,key in todo[:128]:
        obstacle=None
        for prod,orient,other,g in edges[k]:
            if not prod and other==B:continue
            try:ch.leg(B,other)
            except ValueError:
                lo,hi=sorted((other,B),key=dim.get)
                witness=next((i,j,str(dot)) for i,x in enumerate(ch.frames[lo][0]) for j,y in enumerate(ch.frames[hi][1]) if (dot:=sum(v*w for v,w in zip(x,y))))
                obstacle=[B,other,prod,orient,witness];break
        if obstacle:reject.append([k,d,B,obstacle]);continue
        def rel(n):return B if cc[n]==k else tag[n]
        nw=[];removed=[]
        for i,(row,nodes) in enumerate(zip(w['program'],refs)):
            op=row[0]
            if op=='SWAP':nw.append(row)
            elif op=='MOVE':
                v,u=map(rel,nodes)
                if v==u:removed.append(i)
                else:nw.append([op,row[1],v,u])
            else:nw.append([*row[:-1],rel(nodes[0])])
        word=dict(w,program=nw,start=list(map(rel,start)),final=list(map(rel,final)))
        need(word['start'][:222]==w['start'][:222] and word['final'][:222]==w['final'][:222],'main anchors')
        for rev in (False,True):
            obs,rec,_=lit['tape'](word,ch,adjoint=rev);need(obs==lit['expected_rows'](len(start),rev),'native signed')
        nt=Counter(ch.leg(x,y) for x,y in zip(word['start'][222:],word['final'][222:]))
        pay,tar=lit['paired_invoice'](caller,rec['paid'],nt,event)
        state,upper,mar,p,t,ord1=profiles[key]
        need(p==pay and t==tar and ord1==lit['ordinary'](word,caller,event,pay,tar),'all literal work')
        best=dict(component=k,old_chart=tag[k],chart=B,deleted=removed,canonical=lit['canonical'](word),ordinary=ord1,paid=dict(pay),productive=dict(tar))
        put(a.out/'candidate.json',word);break
    labels=Counter(tag[k] for k in members)
    result=dict(source=h['PINS'],word=h['WORD'],comparator=str(old),price_trial=str(h['C']),raw_upper=str(ub0),segments=len(cc),components=len(members),main_anchored=len(anchored),eligible=len(components),eligible_components_split_from_label=sum(labels[tag[k]]>1 for k in components),no_cost_and_unanchored=len(members)-len(anchored)-len(components),typed_instructions=len(refs),moves=len(arcs),helper_endpoints=sum(t0.values()),classification=dict(total),signed_profiles=len(profiles),price_positive=len(todo),geometry_rejects=reject,built=best,restart_index=len(reject)+int(bool(best)),unvisited=len(todo)-len(reject)-int(bool(best)),bins_sha256=dig((a.out/'bins.json').read_bytes()),rank_sha256=dig((a.out/'ranked.json').read_bytes()))
    put(a.out/'result.json',result);print({k:v for k,v in result.items() if k not in ('geometry_rejects','built','source')},'candidate',best and (best['component'],best['chart']),flush=True)
if __name__=='__main__':
    p=ArgumentParser()
    for n in ('peer','accept','helper','out'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--child',action='store_true');a=p.parse_args()
    if a.child:check(a)
    else:
        a.out.mkdir();t=time.monotonic()
        try:code=subprocess.run([sys.executable,'-IB',__file__,'--child',*sys.argv[1:]],timeout=45).returncode
        except subprocess.TimeoutExpired:code=124
        put(a.out/'time.json',dict(exit=code,cap=45,verification_reserve=15,wall=time.monotonic()-t));raise SystemExit(code)
