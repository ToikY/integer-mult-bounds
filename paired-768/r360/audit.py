"""Independent chart-substitution audit on #8027. CPython 3.12, standard library only."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from decimal import Decimal,localcontext
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from pathlib import Path
import gzip,json,math,runpy,subprocess,sys,tarfile,time,tempfile

PINS={'APPLICATION.json':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f','APPLICATION-SOURCES.tar.gz':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968','BINARY-CANDIDATE.json.gz':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'}
C=Q('.003890115277594'); ceiling=Q('.00389848144655');old=Q('.00389011527141');v=768;H=299610000000000
def must(ok,msg):
    if not ok:raise ValueError(msg)
def save(f,o):
    with f.open('x') as s:json.dump(o,s,indent=2,sort_keys=True);s.write('\n')
def digest(p):return sha256(p.read_bytes()).hexdigest()
@cache
def ev(r,x):
    if r==1:return Q(1),Q(1)
    with localcontext() as c:
        c.prec=58
        a=Decimal(r).ln();b=Decimal(x.numerator)/Decimal(x.denominator)
        lo=(a.next_minus()*b.next_minus()).next_minus();hi=(a.next_plus()*b.next_plus()).next_plus()
        return Q(lo.exp().next_minus()),Q(hi.exp().next_plus())
@cache
def log(r):
    if r==1:return Q(0),Q(0)
    with localcontext() as c:
        c.prec=58;y=Decimal(r).ln();return Q(y.next_minus()),Q(y.next_plus())
def sumterm(hist,x,idx):return sum(n*ev(r,x)[idx] for r,n in hist.items() if n)
def floor_grid(f,g):return Q(int(f*g),g)
def ceil_grid(f):return Q(math.ceil(f*10**22),10**22)
def pwrupper(f,p):
    # Keep subsequent exact rational checks small. Ceiling after exponentiation.
    return ceil_grid(ceil_grid(f)**p)
def clean(hist):return {int(r):int(n) for r,n in hist.items() if n}
def rank(rows):
    piv={}
    for vec in rows:
        w=list(map(Q,vec))
        for i in sorted(piv):
            if w[i]:w=[x-w[i]*y for x,y in zip(w,piv[i])]
        k=next((i for i,x in enumerate(w) if x),None)
        if k is not None:piv[k]=[z/w[k] for z in w]
    return len(piv)
def four():
    covered=C-Q(1524,H)-Q(1,H*2**38);prev=Q('.00385248');results=[]
    for _ in range(4):
        cap=Q(249,250)*covered+prev/250
        nxt=Q((cap*10**15).__floor__()-1,10**15);must(prev<nxt<cap<Q(1,250),'ordinary bootstrap')
        results.append(str(nxt));prev=nxt
    claim=floor_grid(prev,10**14)-Q(8,10**14)
    must(claim>old and claim+Q(7,10**14)<prev,'strict analytic price');return claim,results
def cert(p,t,raw_moment):
    x=1-C;off=Q(1,5);p0=sumterm(p,x,0);p1=sumterm(p,x,1);t0=sumterm(t,x,0)
    a=p1/t0;g=sumterm(p,x+off,1)/(t0*ev(15,off)[0]);l=ev(16,off)[1]*sumterm(t,x-off,1)/t0
    if max(a,g,l)>=1:return None
    # Use the same frozen conservative gates for candidate selection.
    split_ratio=sumterm(p,x+off,1)/(p0*ev(15,off)[0])
    if a>1-Q(1,10**14) or l>Q(96,100) or split_ratio>Q(9,10):return None
    bound=Q(1)/(1+768*(1-ceil_grid(a)))+2*pwrupper(g,v)+pwrupper(l,v)
    if bound>=1:return None
    mean=sum(n*ev(r,x)[1]*log(r)[1] for r,n in p.items())/(p0*log(15)[0])
    split=2*pwrupper(sumterm(p,x+off,1)/(p0*ev(15,off)[0]),v)
    eta=(1-C)/ev(134,C*v)[1]
    if (mean>Q(67,100) or raw_moment+split>=Q(7,10)**40 or
        max((Q(21,20)/Q(21,10))**40,(Q(7,10)/Q(51,50))**40)>=eta or
        p[56]<=0 or max(p)!=56 or max(t)>134 or not t[8] or not t[64]):return None
    return {'raw_at_C_lo':str(floor_grid(t0-p1,10**16)),'complete_separation_slack_lo':str(floor_grid(1-bound,10**22)),
            'norm_mean_up':str(ceil_grid(mean)),'split_upper':str(split),'eta_lower':str(floor_grid(eta,10**22))}
def run(args):
    for name,h in PINS.items():must(digest(args.peer/name)==h,name)
    must(digest(args.accept)=='0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377','R352 complete')
    word=json.loads(gzip.decompress((args.peer/'BINARY-CANDIDATE.json.gz').read_bytes()));app=json.loads((args.peer/'APPLICATION.json').read_bytes());nn=app['binary_native']
    with tarfile.open(args.peer/'APPLICATION-SOURCES.tar.gz') as arc:
        code=arc.extractfile('parent/binary/independent/literal.py').read();caller=json.loads(gzip.decompress(arc.extractfile('source/research/paired-query-only-bit/EFREE-CALLER.json.gz').read()))
    must(sha256(code).hexdigest()=='4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c','literal reader')
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'literal.py';path.write_bytes(code);native=runpy.run_path(str(path))
    charts=native['Charts'](word['frames']);dim=charts.rank;coords=charts.frames
    must(native['canonical'](word)==app['binary_word'] and len(coords)==636,'frames')
    e=Counter((a,b) for op,r,*arg in word['program'] if op=='MOVE' for a,b in [arg])
    tar=Counter(zip(word['start'][222:],word['final'][222:]));fixed=set(word['start'][:222]+word['final'][:222]);used={j for tup in e.keys()|tar.keys() for j in tup}-fixed
    inc=defaultdict(list);nr=Counter();nt=Counter()
    for is_target,pairs,acc in ((True,tar,nt),(False,e,nr)):
        for (s,t),n in pairs.items():
            g=dim[t]-dim[s] if is_target else abs(dim[s]-dim[t]);must(g>0,'old positive')
            acc[g]+=n
            for endpoint in (s,t):inc[endpoint].append((s,t,is_target,n,g))
    must(sum(nr.values())==2803 and sum(nt.values())==408 and nr==clean(nn['paid']) and nt==clean(nn['productive']),'native controls')
    callerops=Counter(t[0] for t in caller['events']);P,T=native['paired_invoice'](caller,nr,nt,callerops)
    must(callerops['LOCAL']==36 and P==clean(nn['paid_all']) and T==clean(nn['productive_all']) and
         native['ordinary'](word,caller,callerops,P,T)==nn['ordinary'],'paid caller all ordinary')
    for rev in (False,True):
        rows,lg,_=native['tape'](word,charts,adjoint=rev);must(rows==native['expected_rows'](630,rev) and lg['paid']==nr,'literal source control')
    # Source-independent admissible L40 upper for a binomial(768,67/150).
    k=40;S=[1]+[0]*k
    for _ in range(k):S=[0]+[i*S[i]+S[i-1] for i in range(1,k+1)]
    raw_moment=(Q(3,2*v))**k*sum(S[i]*math.perm(v,i)*Q(67,150)**i for i in range(k+1))
    must((1<<1523)*1024**40<=(H+1024)**40<(1<<1524)*1024**40 and H+1024<1024*2**39 and H*Q(1,H*2**38)/2==Q(64,2**45),'carrier, threshold and cover guards')
    common,stages=four()
    grouped={};fixed_results={};cells=[];first_legal=None
    order_ids=json.loads(args.ids.read_bytes()) if args.ids else None
    cache={}
    def grade(a,d):
        if (a,d) not in cache:
            pd=Counter();td=Counter()
            for s,t,is_tar,n,g in inc[a]:
                sd,tt=(d if s==a else dim[s]),(d if t==a else dim[t])
                gr=tt-sd if is_tar else abs(tt-sd)
                if gr<=0:cache[a,d]=None;return None
                out=td if is_tar else pd;out[g]-=36*n;out[gr]+=36*n
            p=P.copy();p.update(pd);t=T.copy();t.update(td);p=+p;t=+t
            x=1-ceiling
            raw_upper_sign=sumterm(t,x,0)-sumterm(p,x,1)
            raw_at_c=sumterm(t,1-C,0)-sumterm(p,1-C,1)
            lower=cert(p,t,raw_moment) if raw_at_c>0 else None
            cache[a,d]=(p,t,raw_upper_sign,lower)
        return cache[a,d]
    # The rational supplier upper caps every bucket. If at least 64 buckets/
    # assignments have positive certified margin there, no bisection can insert
    # a lower-ranked assignment ahead of them. For other raw uppers the exact
    # frozen producer IDs can be supplied explicitly and checked separately.
    inventory=None
    if order_ids is None:
        selected=[]
        for a in sorted(used):
            for b in sorted(dim):
                if b==a or dim[a]==dim[b]:continue
                state=grade(a,dim[b])
                if state and state[2]>0 and state[3]:
                    selected.append([a,b])
                    if len(selected)==64:break
            if len(selected)==64:break
        if len(selected)<64:
            profiles={};stats=Counter();records=[];worst=None;min_deriv=None
            cardinal=Counter(dim.values());positive_buckets=0
            for a in sorted(used):
                for d,m in sorted(cardinal.items()):
                    if d==dim[a]:
                        stats['same_dimension']+=m-1;continue
                    z=grade(a,d)
                    if not z:stats['nonpositive_grade']+=m;continue
                    pp,tt,_,_=z
                    ident=(tuple(sorted(pp.items())),tuple(sorted(tt.items())))
                    if ident not in profiles:
                        diff=tt.copy();diff.subtract(pp)
                        # The score decreases with kappa where sum(diff r^(1-k) log r)>0.
                        # Each signed summand is bounded at its worse endpoint.
                        # All arithmetic here is exact rational with each exp/log widened.
                        d_bound=sum(n*ev(r,1-(ceiling if n>0 else old))[n<0]*log(r)[n<0] for r,n in diff.items())
                        s_bound=sum(n*ev(r,1-old)[n>0] for r,n in diff.items())
                        profiles[ident]=(s_bound,d_bound)
                    s_bound,d_bound=profiles[ident]
                    must(s_bound<0<d_bound,'one unresolved crossing; retrieve frozen ranking')
                    worst=max(s_bound,worst) if worst is not None else s_bound
                    min_deriv=min(d_bound,min_deriv) if min_deriv is not None else d_bound
                    stats['negative_at_comparator_and_decreasing']+=m;positive_buckets+=1
                    records.append([a,d,m,str(ceil_grid(s_bound)),str(floor_grid(d_bound,10**22))])
            must(not selected and sum(stats.values())==len(used)*(len(dim)-1),'exhausted actual assignment space')
            inventory=dict(counts=dict(stats),changed_legal_dimension_buckets=positive_buckets,profiles=len(profiles),
                           max_absolute_margin_upper=str(ceil_grid(worst)),min_negative_derivative_magnitude=str(floor_grid(min_deriv,10**22)),buckets=records)
    else:selected=order_ids
    must(len(selected)<=64 and len(set(map(tuple,selected)))==len(selected),'frozen distinct cases')
    for a,b in selected:
        must(a in used and a!=b and dim[a]!=dim[b],'eligible ID');p,t,margin,case=grade(a,dim[b]);must(case,'fixed complete sufficient test')
        candidate=dict(A=a,B=b,dimension=dim[b],trial_price=case,raw_rational_ceiling_margin_lower=str(floor_grid(margin,10**16)))
        reject=None
        for s,u,is_target,count,_ in sorted(inc[a],key=lambda z:(z[0],z[1],z[2])):
            left=b if s==a else s;right=b if u==a else u;low,high=sorted((left,right),key=dim.get)
            primal,ann=coords[low];body,dual=coords[high]
            witness=next(((i,j,sum(m*n for m,n in zip(x,y))) for i,x in enumerate(primal) for j,y in enumerate(dual) if sum(m*n for m,n in zip(x,y))),None)
            if witness:
                i,j,value=witness
                reject={'old_edge':[s,u],'new_edge':[left,right],'type':'productive' if is_target else 'paid',
                        'low':low,'high':high,'primal_row':i,'upper_annihilator_row':j,'dot':str(value),
                        'primal_sum_rank':rank([*primal,*body]),'upper_rank':dim[high],'dual_sum_rank':rank([*ann,*dual]),'lower_annihilator_rank':8-dim[low]}
                must(reject['primal_sum_rank']>dim[high] and reject['dual_sum_rank']>8-dim[low],'both chart inclusions reject');break
            must(rank([*primal,*body])==dim[high] and rank([*ann,*dual])==8-dim[low],'both exact inclusions')
        candidate['geometry_failure']=reject;cells.append(candidate)
        if reject is None:
            first_legal=[a,b];break
    literal_survivor=None
    if first_legal is not None:
        a,b=first_legal
        def subst(chart):return b if chart==a else chart
        newops=[]
        for op,r,*vargs in word['program']:
            if op in ('INIT','CLEAR'):item=[op,r,subst(vargs[0])]
            elif op=='ADD':item=[op,r,vargs[0],subst(vargs[1])]
            elif op=='SWAP':item=[op,r,vargs[0]]
            else:
                must(op=='MOVE','typed opcode')
                item=[op,r,*map(subst,vargs)]
            newops.append(item)
        w=dict(word,start=list(map(subst,word['start'])),final=list(map(subst,word['final'])),program=newops)
        must(w['start'][:222]==word['start'][:222] and w['final'][:222]==word['final'][:222] and charts.main_contacts(w['start'],w['final'])==111,'main physical attachments')
        for rev in (False,True):
            rows,ledger,_=native['tape'](w,charts,adjoint=rev)
            must(rows==native['expected_rows'](630,rev),'all signed changed scalar contacts')
        omit=next(i for i,z in enumerate(newops) if z[0]=='CLEAR')
        try:native['tape'](w,charts,omit=omit)
        except ValueError:pass
        else:raise ValueError('omitted CLEAR accepted')
        encoded_target=Counter(charts.leg(s,t) for s,t in zip(w['start'][222:],w['final'][222:]))
        cp,ct=native['paired_invoice'](caller,ledger['paid'],encoded_target,callerops)
        predicted=grade(a,dim[b])
        must(cp==predicted[0] and ct==predicted[1],'matched whole signed invoice')
        charged=native['ordinary'](w,caller,callerops,cp,ct)
        must(charged==nn['ordinary'],'frozen total operations, owners, route-group cardinality')
        literal_survivor=dict(word_sha=native['canonical'](w),full_signed_paid=clean(cp),full_signed_target=clean(ct),ordinary=charged,omitted_clear=omit,owned_endpoints_restored=True,
                              pending='all-size physical gauge proof, candidate exact finite and rational signed consumer')
    control={'native_paid':clean(nr),'native_productive':clean(nt),'caller_cost':nn['ordinary'],'caller_LOCALs':callerops['LOCAL'],'paired_rows':630**2,
             'fixed_main_charts':sorted(fixed),'public_helpers':sum(nt.values()),'initial_live_catalog':len(dim)}
    save(args.out,dict(status='NESTED_SUBSTITUTION_ADMITTED_INTERFACE_PENDING' if first_legal else 'WHOLE_RELAXED_PRICE_EXCLUDED' if inventory else 'ALL_VISITED_SUBSTITUTIONS_FAIL',
        comparator=str(old),C=str(C),sources=PINS,control=control,inventory=inventory,selection=selected,rank_source='all price buckets eliminated independently' if inventory else 'upper-cap tie independent with certified admission' if not args.ids else 'explicit frozen cases independently priced',
        visited=cells,first_legal=first_legal,literal_survivor=literal_survivor,remaining_selected=len(selected)-len(cells),price_final_claim=str(common),bootstrap=stages))
    print('selection',selected[:3],(selected[-1] if selected else None),'visited',len(cells),'positive',first_legal)
def main():
    ap=ArgumentParser()
    for n in ('peer','out','accept'):ap.add_argument('--'+n,type=Path,required=True)
    ap.add_argument('--ids',type=Path);ap.add_argument('--child',action='store_true');a=ap.parse_args()
    must(sys.version_info[:2]==(3,12) and __debug__,'CPython3.12')
    if a.child:run(a);return
    start=time.monotonic();must(not a.out.exists() and not a.out.with_suffix('.timing.json').exists(),'fresh outputs')
    try:rc=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=44.09).returncode
    except subprocess.TimeoutExpired:rc=124
    save(a.out.with_suffix('.timing.json'),dict(cap=44.09,total_authorized=45,reserve=15,exit=rc,wall_seconds=round(time.monotonic()-start,6)));raise SystemExit(rc)
if __name__=='__main__':main()
