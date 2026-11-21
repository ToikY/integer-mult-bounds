"""Fixed-word one-label atlas substitution with a dimension-first whole-invoice screen."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from math import comb
from pathlib import Path
import gzip,json,runpy,subprocess,sys,tarfile,tempfile,time,os

PINS={'BINARY-CANDIDATE.json.gz':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326',
      'APPLICATION-SOURCES.tar.gz':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
      'APPLICATION.json':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f'}
LITERAL='4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c'
CALLER='757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
ACCEPT='0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377'
WORD='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'
OLD=F('.00389011527141'); UPPER=F('.00389848144655'); C=F('.003890115277594')
SCALE=10**32; H=299610000000000; h=1024; v=768; p=40
G=set(range(1,9))|{7,14,21,28,35,42,49,56,15,22,29,36,43,50,57,64,127}
def certify(x,why):
    if not x:raise ValueError(why)
def save(p,data):
    tmp=p.with_suffix(p.suffix+'.part');tmp.write_text(json.dumps(data,sort_keys=True,separators=(',',':'))+'\n');tmp.replace(p)
def dig(b):return sha256(b).hexdigest()
def hist(x):return Counter({int(k):n for k,n in x.items() if n})
@lru_cache(None)
def logint(r):
    if r==1:return (D(0),D(0))
    with localcontext() as c:
        c.prec=65;x=D(r).ln();return x.next_minus(),x.next_plus()
@lru_cache(None)
def power(r,e,logfactor=False):
    if r==1:return (0,0) if logfactor else (SCALE,SCALE)
    with localcontext() as c:
        c.prec=62
        lo,hi=logint(r);a=D(e.numerator)/D(e.denominator)
        l=(a.next_minus()*lo).next_minus().exp().next_minus()
        u=(a.next_plus()*hi).next_plus().exp().next_plus()
        if logfactor:l=(l*lo).next_minus();u=(u*hi).next_plus()
        return int((l*SCALE).next_minus()),int((u*SCALE).next_plus())+1
@lru_cache(None)
def basis(e,logfactor=False):return {r:power(r,e,logfactor) for r in G}
def moment(s,e,logfactor=False):
    b=basis(e,logfactor)
    return (sum(n*b[r][n<0] for r,n in s.items()),sum(n*b[r][n>=0] for r,n in s.items()))
def upper_bound(s):
    # On the whole bracket: -S'(k)=sum s_r r^(1-k) log(r).
    lower=sum(n*power(r,1-(UPPER if n>0 else OLD),True)[n<0] for r,n in s.items())
    if lower<=0:return UPPER
    if moment(s,1-OLD)[1]<0:return OLD
    if moment(s,1-UPPER)[0]>0:return UPPER
    a,b=OLD,UPPER
    for _ in range(20):
        m=(a+b)/2;lo,hi=moment(s,1-m)
        if lo>0:a=m
        elif hi<0:b=m
        else:break
    return b
def static_guards():
    L=(((H+h)**p)//h**p).bit_length()
    certify(L==1524 and (h+H)*L>2*H*p,'terminal/tail')
    below=F(3,2*v)**p*F(sum(comb(v,k)*67**k*83**(v-k)*k**p for k in range(v+1)),150**v)
    z=F(7,10); tail=2*F(9,10)**v
    certify(below+tail<z**p,'full split and moment')
    t=1-C
    with localcontext() as c:
        c.prec=60
        dc=D(C.numerator)/D(C.denominator)
        x=-(D(v)*dc.next_plus()*logint(134)[1]).next_plus()
        eta=t*F(x.exp().next_minus())
    certify(max(((F(7,20)+z)/F(21,10))**p,(z/F(51,50))**p)<eta,'all-height proof')
    certify(2**(20*h)<=15**(7*v) and (2**h*134**v)**10>=15**(21*v) and 16**50>=15**51 and 8*v*C<p and 7*v>h,'geometry/base')
    covered=C-F(L,H)-F(1,H*2**38); previous=F('.00385248'); stages=[]
    for i in range(4):
        e=(249*covered+previous)/250; b=F((e*10**15)//1-1,10**15)
        g=min(e-b,F(1,250)-b,F(249,250)-b)
        certify(previous<b and g>0,'ordinary');stages.append(list(map(str,(previous,e,b,g))));previous=b
    k=F((previous*10**14)//1-8,10**14)
    certify(k>OLD and k+F(7,10**14)<previous,'signed grid')
    return k,dict(cap=str(previous),claim=str(k),stages=stages,tested=str(k+F(7,10**14)),uniform_L=L,
                  trial=str(C),covered=str(covered),binomial_moment_upper=str(below),eta_lower=str(eta))
def price_gates(T,P):
    t=1-C
    if max(P)>56 or not T[64] or not T[8] or max(T)!=127:return 'support'
    plo,phi=moment(P,t);tlo,thi=moment(T,t)
    # Compare ceil(P/T), gamma<=.9, lambda<=.96 and complete finite gap without large powers per case.
    if phi>=tlo:return 'alpha'
    u=F(1,5); c15=power(15,u)[0]; f16=power(16,u)[1]
    if 10*moment(P,t+u)[1]*SCALE>9*c15*plo:return 'split slope'
    if 25*f16*moment(T,t-u)[1]>24*tlo*SCALE:return 'productive loss'
    # gamma=alpha*slope <.9. Certified 2*.9^768+.96^768 < 10^-12.
    if phi*10**14 > (10**14-1)*tlo:return 'finite strict gap'
    # 1/(1+768*10^-14)+10^-12<1.
    loglo=F(logint(15)[0])
    if 100*moment(P,t,True)[1] > 67*plo*loglo:return 'source mean'
    return 'PASS'
def run(a):
    certify(sys.version_info[:2]==(3,12) and __debug__,'3.12')
    work=a.out;work.mkdir(exist_ok=True)
    def note(stage,**kw):save(work/'progress.json',dict(stage=stage,**kw))
    note('input authentication')
    for n,pin in PINS.items():certify(dig((a.peer/n).read_bytes())==pin,n)
    certify(dig(a.accept.read_bytes())==ACCEPT,'baseline')
    app=json.loads((a.peer/'APPLICATION.json').read_bytes())
    word=json.loads(gzip.decompress((a.peer/'BINARY-CANDIDATE.json.gz').read_bytes()))
    with tarfile.open(a.peer/'APPLICATION-SOURCES.tar.gz') as ar:
        src=ar.extractfile('parent/binary/independent/literal.py').read()
        cp=ar.extractfile('source/research/paired-query-only-bit/EFREE-CALLER.json.gz').read()
    certify(dig(src)==LITERAL and dig(cp)==CALLER,'original readers')
    caller=json.loads(gzip.decompress(cp))
    with tempfile.TemporaryDirectory() as td:
        f=Path(td)/'literal.py';f.write_bytes(src);lit=runpy.run_path(str(f))
    certify(lit['canonical'](word)==WORD and F(json.loads(a.accept.read_bytes())['claim'])==OLD,'control pins')
    charts=lit['Charts'](word['frames']);dims=charts.rank
    moves=Counter((op[2],op[3]) for op in word['program'] if op[0]=='MOVE')
    helpers=Counter(zip(word['start'][222:],word['final'][222:]))
    events=Counter(e[0] for e in caller['events'])
    def census(edges):return Counter({}) if not edges else sum_counts((charts.leg(x,y),n) for (x,y),n in edges.items())
    def sum_counts(items):
        c=Counter()
        for k,n in items:c[k]+=n
        return c
    p0,t0=census(moves),census(helpers)
    P,T=lit['paired_invoice'](caller,p0,t0,events)
    certify(P==hist(app['binary_native']['paid_all']) and T==hist(app['binary_native']['productive_all']) and
            len(word['frames'])==636 and sum(moves.values())==2803 and sum(helpers.values())==408 and events['LOCAL']==36,'whole paired census')
    ordinary=lit['ordinary'](word,caller,events,P,T);certify(ordinary==app['binary_native']['ordinary'],'whole ordinary control')
    fixed=set(word['start'][:222]+word['final'][:222])
    incident=defaultdict(list)
    for kind,rows in (('P',moves),('T',helpers)):
        for (x,y),n in rows.items():
            for z in set((x,y)):incident[z].append((kind,x,y,n))
    dimension_groups=defaultdict(list)
    for z,d in sorted(dims.items()):dimension_groups[d].append(z)
    labels=sorted(set(incident)-fixed)
    k,proof=static_guards()
    certify(2*F(9,10)**768+F(24,25)**768<F(1,10**12) and F(1,1+768*F(1,10**14))+F(1,10**12)<1,'uniform finite constants')
    types=Counter(); candidates=[]; profiles={}; buckets=[]; old_upper=F(app['binary_raw'][1])
    for A in labels:
        for d,bs in dimension_groups.items():
            if d==dims[A]:types['unchanged dimension']+=len(bs)-(A in bs);continue
            paid,target=P.copy(),T.copy()
            bad=None
            for kind,x,y,n in incident[A]:
                oldg=abs(dims[y]-dims[x]); delta=(d if y==A else dims[y])-(d if x==A else dims[x])
                g=abs(delta) if kind=='P' else delta
                if g<=0:bad='nonpositive gap';break
                hst=paid if kind=='P' else target;hst[oldg]-=36*n;hst[g]+=36*n
            if bad:types[bad]+=len(bs);continue
            paid=+paid;target=+target
            key=(tuple(sorted(paid.items())),tuple(sorted(target.items())))
            if key not in profiles:
                s=target.copy();s.subtract(paid)
                upper=upper_bound(s)
                state='no relaxed improvement' if upper<=OLD else price_gates(target,paid)
                if state=='PASS' and moment(s,1-old_upper)[0]<=0:state='raw separation unresolved'
                profiles[key]=(upper,state)
            upper,state=profiles[key]; types[state]+=len(bs)
            buckets.append([A,d,str(upper),state])
            if state=='PASS':
                candidates.extend((upper,A,B) for B in bs)
        if A%16==0:note('pricing',A=A,buckets=len(buckets),eligible_pairs=len(candidates))
    candidates.sort(key=lambda x:(-x[0],x[1],x[2]))
    ranked=[[A,B] for _,A,B in candidates]
    save(work/'ranked.json',ranked);save(work/'buckets.json',buckets)
    cert={'comparator':str(OLD),'word':WORD,'source':PINS,'baseline_accept':ACCEPT,'source_proof':proof,'counts':dict(types),
          'dimension_incidence_sources':len(labels),'nonzero_dimension_buckets':len(buckets),'unique_profiles':len(profiles),
          'ranked_pairs':len(ranked),'ranked_sha256':dig((work/'ranked.json').read_bytes()),
          'upper_root_bisections':20,'lower_trial':str(C),'tested':[]}
    note('concrete',next_rank=a.start)
    def compare_edges(A,B):
        for kind,x,y,n in incident[A]:
            i=B if x==A else x;j=B if y==A else y
            try:charts.leg(i,j)
            except (ValueError,AssertionError,RuntimeError):return [kind,x,y,i,j]
        return None
    for i in range(a.start,min(a.start+64,len(candidates))):
        ub,A,B=candidates[i]; bad=compare_edges(A,B)
        cert['tested'].append([i,A,B,bad])
        if bad is None:
            m=lambda x:B if x==A else x
            ops=[]
            for op in word['program']:
                k0=op[0]
                if k0 in ('INIT','CLEAR'):o=[k0,op[1],m(op[2])]
                elif k0=='ADD':o=[*op[:3],m(op[3])]
                elif k0=='MOVE':o=[*op[:2],m(op[2]),m(op[3])]
                else:o=op
                ops.append(o)
            changed=dict(word,start=list(map(m,word['start'])),final=list(map(m,word['final'])),program=ops)
            certify(charts.main_contacts(changed['start'],changed['final'])==111,'main')
            outs,fwd,_=lit['tape'](changed,charts);outs2,adj,_=lit['tape'](changed,charts,adjoint=True)
            certify(outs==lit['expected_rows'](630,False) and outs2==lit['expected_rows'](630,True) and fwd['paid']==adj['paid'],'both endpoints')
            nativeT=Counter(charts.leg(x,y) for x,y in zip(changed['start'][222:],changed['final'][222:]))
            pay,tar=lit['paired_invoice'](caller,fwd['paid'],nativeT,events)
            cert['candidate']=dict(A=A,B=B,word=lit['canonical'](changed),paid=dict(pay),targets=dict(tar),
                                   native_paid=dict(fwd['paid']),native_targets=dict(nativeT),ordinary=lit['ordinary'](changed,caller,events,pay,tar))
            certify(price_gates(tar,pay)=='PASS','full reprice');cert['decision']='ONE_LITERAL_NATIVE_CANDIDATE_PENDING_INDEPENDENT_AND_OUTER'
            save(work/'candidate.json',changed);break
        note('concrete',next_rank=i+1)
    else:cert['decision']='NO_GAIN_WITHIN_FROZEN_PRICE_AND_CONCRETE_SCOPE'
    cert['next_rank']=a.start+len(cert['tested']);cert['unresolved_ranked_pairs']=len(ranked)-cert['next_rank']
    save(work/'result.json',cert);print(cert['decision'],cert['counts'],len(cert['tested']),cert.get('candidate',{}).get('word'),flush=True)
def main():
    c=ArgumentParser()
    for n in ('peer','accept','out'):c.add_argument('--'+n,type=Path,required=True)
    c.add_argument('--start',type=int,default=0);c.add_argument('--child',action='store_true')
    a=c.parse_args()
    if a.child:run(a);return
    certify(not a.out.exists(),'fresh output');a.out.mkdir(parents=True)
    t=time.monotonic()
    try:ret=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=45).returncode
    except subprocess.TimeoutExpired:ret=124
    save(a.out/'time.json',dict(exit=ret,seconds=time.monotonic()-t,cap=45,reserve=15))
    raise SystemExit(ret)
if __name__=='__main__':main()
