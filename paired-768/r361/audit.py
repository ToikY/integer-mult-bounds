"""Check one catalogue-chart contraction along a literal paid edge on exact #8027."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
from functools import cache
import gzip,json,math,runpy,tarfile,time,tempfile,sys,subprocess

def need(ok,why):
    if not ok:raise ValueError(why)
def dig(p):return sha256(p.read_bytes()).hexdigest()
def put(p,data):
    with p.open('x') as s:json.dump(data,s,sort_keys=True,indent=2);s.write('\n')
def trace(args):
    need(dig(args.math)=='470790b310adad3508300666ff02ad4cab0cef60df460bd51a59e3433cf3828a','R360 directed arithmetic')
    need(dig(args.accept)=='0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377','R352 complete supplier')
    h=runpy.run_path(str(args.math));C,old,ceiling=h['C'],h['old'],h['ceiling'];ev,log=h['ev'],h['log']
    for n,sha in h['PINS'].items():need(dig(args.peer/n)==sha,n)
    app=json.loads((args.peer/'APPLICATION.json').read_bytes());N=app['binary_native']
    word=json.loads(gzip.decompress((args.peer/'BINARY-CANDIDATE.json.gz').read_bytes()))
    with tarfile.open(args.peer/'APPLICATION-SOURCES.tar.gz') as sa:
        bytecode=sa.extractfile('parent/binary/independent/literal.py').read()
        caller=json.loads(gzip.decompress(sa.extractfile('source/research/paired-query-only-bit/EFREE-CALLER.json.gz').read()))
    need(sha256(bytecode).hexdigest()=='4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c','source tape')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'literal.py';p.write_bytes(bytecode);lit=runpy.run_path(str(p))
    ch=lit['Charts'](word['frames']);D=ch.rank;rows=ch.frames;program=word['program']
    need(lit['canonical'](word)==app['binary_word'] and len(D)==636,'word')
    pub=word['public'];fixed=set(word['start'][:222]+word['final'][:222]);
    paid=Counter((op[2],op[3]) for op in program if op[0]=='MOVE')
    prod=Counter(zip(word['start'][222:],word['final'][222:]))
    pairs=sorted({(a,b) for x,y in paid for a,b in ((x,y),(y,x)) if a not in fixed})
    incidence={a:[] for a,_ in pairs}
    nativeP=Counter();nativeT=Counter()
    for prod_edge,edges,hh in ((False,paid,nativeP),(True,prod,nativeT)):
        for (x,y),m in edges.items():
            g=ch.leg(x,y);need(not prod_edge or D[x]<D[y],'directed original productive')
            hh[g]+=m
            for z in {x,y}&incidence.keys():incidence[z].append((prod_edge,x,y,m,g))
    call=Counter(op[0] for op in caller['events'])
    P,T=lit['paired_invoice'](caller,nativeP,nativeT,call)
    need(call['LOCAL']==36 and h['clean'](N['paid_all'])==P and h['clean'](N['productive_all'])==T and
         lit['ordinary'](word,caller,call,P,T)==N['ordinary'] and sum(nativeP.values())==2803 and sum(nativeT.values())==408,'complete old control')
    for reverse in (False,True):
        found,ledger,_=lit['tape'](word,ch,adjoint=reverse)
        need(found==lit['expected_rows'](pub,reverse) and ledger['paid']==nativeP,'old signed program')
    def writes(**msg):
        with args.out.with_suffix('.progress.jsonl').open('a') as s:s.write(json.dumps(msg)+'\n')
    writes(scope=len(pairs),stage='rank')
    @cache
    def powerlog(r,k):
        lo,hi=ev(r,1-k);return lo*log(r)[0],hi*log(r)[1]
    def bound(diff,k,side):
        return sum(n*ev(r,1-k)[(n>0)==side] for r,n in diff.items() if n)
    def upper_root(diff):
        derivative=sum(n*powerlog(r,ceiling if n>0 else old)[n<0] for r,n in diff.items() if n)
        if derivative<=0:return ceiling
        if bound(diff,old,True)<0:return old
        if bound(diff,ceiling,False)>0:return ceiling
        a,b=old,ceiling
        for _ in range(20):
            m=(a+b)/2
            if bound(diff,m,False)>0:a=m
            elif bound(diff,m,True)<0:b=m
            else:break
        return b
    targets=Counter();full=Counter();between=Counter();invalid=Counter();raw_rejected=Counter()
    profile_cache={};by_pair={};eligible=[];optim_gross=Q(0);best_net=None
    v,pow=768,40;st=[1]+[0]*pow
    for _ in range(pow):st=[0]+[i*st[i]+st[i-1] for i in range(1,pow+1)]
    raw_moment=Q(3,2*v)**pow*sum(st[i]*math.perm(v,i)*Q(67,150)**i for i in range(pow+1))
    oldsigned=T.copy();oldsigned.subtract(P)
    baseline_lo=bound(oldsigned,old,False);chosen_coverage=Counter()
    common,stages=h['four']();need(common>old,'grid price before concrete')
    for a,b in pairs:
        np=nativeP.copy();nt=nativeT.copy();dropped=0;err=None
        multiplicity=paid[a,b]+paid[b,a];between[multiplicity]+=1
        g_old=ch.leg(a,b);optim_gross=max(optim_gross,36*multiplicity*ev(g_old,1-old)[1])
        for is_prod,x,y,m,g in incidence[a]:
            s=b if x==a else x;t=b if y==a else y;dst=nt if is_prod else np;dst[g]-=m
            if not is_prod and s==t:dropped+=m;continue
            g1=D[t]-D[s] if is_prod else abs(D[t]-D[s])
            if g1<=0:err='nonpositive_productive' if is_prod else 'equal_dimension_distinct_labels';break
            dst[g1]+=m
        if err:invalid[err]+=1;by_pair[a,b]=(err,None);continue
        need(dropped==multiplicity,'only physical identities deleted');np=+np;nt=+nt
        p=P.copy();tt=T.copy()
        for g in nativeP.keys()|np.keys():p[g]+=36*(np[g]-nativeP[g])
        for g in nativeT.keys()|nt.keys():tt[g]+=36*(nt[g]-nativeT[g])
        p,tt=+p,+tt;ident=tuple(sorted(p.items())),tuple(sorted(tt.items()))
        if ident not in profile_cache:
            diff=tt.copy();diff.subtract(p);root=upper_root(diff)
            net=bound(diff,old,True)-baseline_lo
            state= ('below_comparator' if root<=old else
                    'old_raw_separation_unresolved' if bound(diff,Q(app['binary_raw'][1]),False)<=0 else
                    ('admitted' if h['cert'](p,tt,raw_moment) else 'frozen_price_unresolved'))
            profile_cache[ident]=(root,state,net)
        upper,state,net=profile_cache[ident];full[state]+=1;best_net=max(best_net,net) if best_net is not None else net
        by_pair[a,b]=(state,(p,tt,dropped,upper))
        if state=='admitted':eligible.append((-upper,a,b))
    eligible.sort()
    selected=eligible[:256];rejects=[];best=None
    writes(stage='geometry',ranked=len(eligible),selected=len(selected))
    for _,a,b in selected:
        witness=None
        for is_prod,x,y,m,g in sorted(incidence[a]):
            s=b if x==a else x;t=b if y==a else y
            if s==t and not is_prod:continue
            low,hi=sorted((s,t),key=D.get);pr,ann=rows[low];body,dual=rows[hi]
            clash=next(((i,j,u) for i,r in enumerate(pr) for j,d in enumerate(dual) if (u:=sum(x*y for x,y in zip(r,d)))),None)
            if clash:
                i,j,w=clash;rp=h['rank']([*pr,*body]);rd=h['rank']([*dual,*ann])
                need(rp>D[hi] and rd>8-D[low],'two independent subspace rank controls')
                witness=[is_prod,x,y,low,hi,i,j,str(w),rp,rd];break
            need(h['rank']([*pr,*body])==D[hi] and h['rank']([*ann,*dual])==8-D[low],'both nestings')
        if witness:
            rejects.append([a,b,witness]);continue
        p,t,count,upper=by_pair[a,b][1];best=[a,b]
        def chart(z):return b if z==a else z
        edits=[];deleted=[]
        for i,(o,r,*op) in enumerate(program):
            if o=='MOVE':
                x,y=map(chart,op)
                if x==y:deleted.append(i);continue
                edits.append([o,r,x,y])
            elif o in ('INIT','CLEAR'):edits.append([o,r,chart(op[0])])
            elif o=='ADD':edits.append([o,r,op[0],chart(op[1])])
            else:need(o=='SWAP','typed opcode');edits.append([o,r,op[0]])
        w=dict(word,start=list(map(chart,word['start'])),final=list(map(chart,word['final'])),program=edits)
        need(len(deleted)==count and w['start'][:222]==word['start'][:222] and w['final'][:222]==word['final'][:222] and ch.main_contacts(w['start'],w['final'])==111,'fixed attachments')
        for rev in (False,True):
            co,le,_=lit['tape'](w,ch,adjoint=rev);need(co==lit['expected_rows'](pub,rev),'all native coefficients')
        nt=Counter(ch.leg(x,y) for x,y in zip(w['start'][222:],w['final'][222:]))
        cp,ct=lit['paired_invoice'](caller,le['paid'],nt,call);need(p==cp and t==ct,'actual complete invoice')
        charge=lit['ordinary'](w,caller,call,cp,ct)
        exp=N['ordinary'];need(charge['owned_backing']==exp['owned_backing'] and
             charge['ordinary_records']==exp['ordinary_records']-36*count*(16*exp['native_banks_and_scratch']+4*80*(134**2+134)),'exact ordinary decrease')
        omit=next(i for i,z in enumerate(edits) if z[0]=='CLEAR')
        try:lit['tape'](w,ch,omit=omit)
        except ValueError:pass
        else:raise ValueError('wrong omitted-clear control')
        best=dict(A=a,B=b,deleted=deleted,canonical=lit['canonical'](w),native_paid=h['clean'](le['paid']),native_productive=h['clean'](nt),
                  complete_paid=h['clean'](p),complete_productive=h['clean'](t),ordinary=charge,signed_count=pub*pub,positive_trial=h['cert'](p,t,raw_moment),
                  remaining='full finite, all-size physical changed-gauge proof and rational caller')
        break
    writes(stage='complete',tests=len(rejects)+bool(best))
    put(args.out,dict(source=h['PINS'],comparator=str(old),C=str(C),control={'native_paid':h['clean'](nativeP),'native_productive':h['clean'](nativeT),
        'ordinary':N['ordinary'],'calls':36},scope=len(pairs),candidate_family='one attached pair only',multiplicity_histogram=dict(between),
        optimistic_max_old_charge_removed=str(h['ceil_grid'](optim_gross)),optimistic_max_full_margin_change_at_old=str(h['ceil_grid'](best_net)) if best_net is not None else None,
        invalid=dict(invalid),price_counts=dict(full),distinct_profiles=len(profile_cache),ranked=[[a,b] for _,a,b in eligible],eligible_count=len(eligible),
        selected=[[a,b] for _,a,b in selected],visited_bad=rejects,one_candidate=best,raw_eligible_unvisited=len(eligible)-len(rejects)-int(bool(best)),trial_stages=stages))
    print('total',len(pairs),'invalid',dict(invalid),'price',dict(full),'ranked',len(eligible),'visited',len(rejects)+int(bool(best)),'best',None if not best else (best['A'],best['B']))
def main():
    p=ArgumentParser()
    for n in ('peer','accept','math','out'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--child',action='store_true');args=p.parse_args();need(sys.version_info[:2]==(3,12) and __debug__,'CPython3.12')
    if args.child:trace(args);return
    need(not any(p.exists() for p in (args.out,args.out.with_suffix('.timing.json'),args.out.with_suffix('.progress.jsonl'))),'fresh output')
    ts=time.monotonic()
    try:rc=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=45).returncode
    except subprocess.TimeoutExpired:rc=124
    put(args.out.with_suffix('.timing.json'),dict(cap=45,reserve=15,exit=rc,wall_seconds=round(time.monotonic()-ts,6)));raise SystemExit(rc)
if __name__=='__main__':main()
