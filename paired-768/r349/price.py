"""One bounded p128 weighted-exit test on the exact 768-factor conditional supplier."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import subprocess
import sys
import tarfile
import time

PINS = {'peer/APPLICATION.json':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f',
        'peer/APPLICATION-SOURCES.tar.gz':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
        'round347/BINARY.json':'f4aad2d07449c864479f26cc3b3ed4bbd8321f0ca14e1efc8676b28b54c27ed4',
        'round348/price.json':'523d6dc93a7cd34bf6183a66d03b624ab2f0dfcf18b7e95032b7d0ab695fa24f',
        'round348/REPLAY.json':'9b00a17913efb76995b01c7b75f5b00aab394a0531e26490ab02a5940adcac3c',
        'theorems/WEIGHTED-EXITS.md':'28e0308f315a583282291fa01998d53a874b4b7e3073cacc3ddbb38c5a7f66c7'}
MEMBERS = {'source/research/paired-query-only-bit/retained/inputs/credited_trim.py':'fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9',
           'parent/binary/PROOF.md':'2bddffa4d670237ffc72514c3c5b4be4b9dabdd7696e0c4e0759f7fd7c10e575',
           'recipient/binary/finite.py':'c780cea060f4a9efef064b239636162a7e8e84e40369abc1a1c4679dfbeb3041'}

def require(works,label):
    if not works:
        raise ValueError(label)

def dump(path, obj):
    with path.open('x') as f:
        json.dump(obj,f,indent=2,sort_keys=True); f.write('\n')

def loaded(path):
    return json.loads(path.read_bytes())

def directed(rank, expn):
    if rank == 1:
        return (F(1),F(1)),(F(0),F(0))
    with localcontext() as ctx:
        ctx.prec = 65
        log = Decimal(rank).ln()
        lo,hi=log.next_minus(),log.next_plus()
        lower=(expn*lo).next_minus().exp().next_minus()
        upper=(expn*hi).next_plus().exp().next_plus()
        return (F(lower),F(upper)),(F(lo),F(hi))

def bounded_print(q, digits=51):
    scale=10**digits
    return str(F(-(-q*scale//1),scale))

def price(covered,rational_lower):
    seed=F('0.00385248');rho=F(1,250);rows=[]
    for _ in range(4):
        end=(1-rho)*covered+rho*seed
        admitted=F(int(end*10**15)-1,10**15);margin=min(end-admitted,rho-admitted,1-rho-admitted)
        require(admitted>seed and margin>0,'strict three-term ordinary invoice')
        rows.append({'previous':str(seed),'endpoint':str(end),'claim':str(admitted),'minimum_slack':str(margin)})
        seed=admitted
    claim=F(min(int(seed*10**14),int(rational_lower*10**14))-8,10**14)
    return seed,claim,claim+F(7,10**14),rows

def decimal_str(q,digits):
    n=q*10**digits
    require(n.denominator==1,'exact decimal presentation')
    return f'0.{int(n):0{digits}d}'

def compute(a):
    progress=a.out.with_suffix('.progress.jsonl')
    def event(**data):
        with progress.open('a') as stream:
            stream.write(json.dumps(data)+'\n')
    event(stage='authenticating')
    paths={'peer/APPLICATION.json':a.peer/'APPLICATION.json','peer/APPLICATION-SOURCES.tar.gz':a.peer/'APPLICATION-SOURCES.tar.gz',
           'round347/BINARY.json':a.binary,'round348/price.json':a.prior_price,'round348/REPLAY.json':a.prior_signed,
           'round348/accept.json':a.prior_accept,'theorems/WEIGHTED-EXITS.md':a.weighted}
    require(a.prior_accept_sha=='35481cf9a929a3dd137a9e63134b7e97ee7c5408d4e675a3e8ad67b16d9a7b71','frozen predecessor acceptance')
    pins=dict(PINS,**{'round348/accept.json':a.prior_accept_sha})
    for name,p in paths.items():
        require(sha256(p.read_bytes()).hexdigest()==pins[name],name)
    with tarfile.open(paths['peer/APPLICATION-SOURCES.tar.gz']) as tape:
        names=tape.getnames()
        require(len(names)==len(set(names)),'repeated source path')
        for name,expected in MEMBERS.items():
            require(sha256(tape.extractfile(name).read()).hexdigest()==expected,name)
    peer=loaded(paths['peer/APPLICATION.json']);binary=loaded(a.binary);prior=loaded(a.prior_price);signed=loaded(a.prior_signed)
    accepted=loaded(a.prior_accept)
    require(signed['claim']==prior['claim']=='0.00389011519729' and signed['outer']['strict_count']==54 and signed['outer']['functional_count']==4,'complete signed comparator')
    require(F(accepted['claim'])==F(signed['claim']) and accepted['replay_sha256']==pins['round348/REPLAY.json'],'independent complete acceptance')
    old=binary['peer_finite'];sep=old['finite_separation'];cmp=old['independent_directed_compiler']
    native=peer['binary_native'];P={int(k):n for k,n in native['paid_all'].items()};T={int(k):n for k,n in native['productive_all'].items()}
    require(native['paid_all']==sep['paid'] and native['productive_all']==sep['targets'] and sum(P.values())==sep['source_paid_calls'] and sum(T.values())==sep['source_public_fields'],'distinct complete inventories')
    require(sum(k*n for k,n in P.items())==sep['source_paid_rank_mass'] and sep['specialized_initial_and_final']==0 and
            sep['owned_allocation_records_bound']=='2*{b0}^{v}'.format(b0=sum(T.values()),v=768) and
            sep['construction']=='chronological product; specialize low complete targets to owned zero; retain all original paid calls; split paid calls on disjoint axes','no hidden completion source')
    p,h,v,H=128,1024,768,299610000000000
    C=F('0.003890115276594');d=F(1,H*2**38);ul=F(peer['binary_raw'][1])-F(23731,H);floor=ul+F(1,10**11)
    require(cmp['product_exponent']==v and cmp['ambient_base']==134 and cmp['cutoff']==15 and cmp['productive_floor']==16 and cmp['H']==H and F(cmp['trial'])==C,'frozen actual source')
    require((H+h)<h*(1<<39) and C-F(4992,H)-F(2,10**13)>floor,'charged optimistic gate')
    prior_cap,prior_claim,prior_tested,_=price(C-F(23731,H)-d,F(peer['rational_raw'][0]))
    require((prior_cap,prior_claim,prior_tested)==tuple(map(F,(signed['cap'],signed['claim'],signed['tested']))),'previous complete output reconstructed')
    require(T[64] and T[8] and 64**256*8**512==16**768 and 256+512==v,'attained productive minimum')
    require(2**(20*h)<=15**(7*v) and (2**h*134**v)**10>=15**(21*v) and 16**50>=15**51,'three log normalization inequalities')
    require(7*v>h and 8*v*C<p,'all base ranks including 0 and 1')
    event(stage='full-paid-mean')
    t=Decimal('0.996109884723406');u=Decimal('0.2')
    pt_lo=tt_hi=numerator_hi=pu_hi=F(0)
    for rank in sorted(P.keys()|T.keys()):
        (lo,hi),(_,log_hi)=directed(rank,t)
        pt_lo+=P.get(rank,0)*lo
        tt_hi+=T.get(rank,0)*hi
        numerator_hi+=P.get(rank,0)*hi*log_hi
        pu_hi+=P.get(rank,0)*directed(rank,t+u)[0][1]
    alpha_lo=F(cmp['ratio_intervals'][0][0]);gamma_hi=F(cmp['ratio_intervals'][1][1])
    require(pt_lo/tt_hi>=alpha_lo,'independent positive alpha denominator')
    # gamma/alpha = P_(t+u)/(15^u P_t), so also check direct cancellation of T_t.
    require(pu_hi/(directed(15,u)[0][0]*pt_lo)<=gamma_hi/alpha_lo<1,'split upper direction')
    raw=numerator_hi/(pt_lo*directed(15,t)[1][0])
    split=2*(gamma_hi/alpha_lo)**v
    q=F(3,4);complete=raw+split
    require(complete<=q,'charged completed mean exceeds fixed bound')
    eta=F(old['uniform']['eta']['lower']);beta=F(51,50);limit=(q/beta)**p
    require(limit<eta,'fixed law leading coefficient')
    event(stage='tabulating-coefficients',last_complete_height=-1)
    # For Binomial(g+1,3/4), scale every numerator by (20^p)(4^129);
    # denominators use the uniform scale 50^p. Differences are exact integers.
    ns=[];ds=[];scale_n=20**p*4**(p+1);scale_d=50**p
    vals=[(7+20*k)**p for k in range(p+2)]
    for g in range(p+1):
        n=g+1
        ns.append(sum(comb(n,k)*3**k*vals[k] for k in range(n+1))*4**(p+1-n))
        ds.append((105+51*g)**p)
        event(stage='tabulating-coefficients',last_complete_height=g)
    ratios=[]
    for j in range(p+1):
        require(ds[0]>0 and ns[0]>=0,'positive difference basis')
        quotient=F(ns[0]*scale_d,ds[0]*scale_n)
        if quotient>=eta:
            event(stage='coefficient-exclusion',j=j,ratio=str(quotient),capacity=str(eta))
            raise ValueError(f'fixed sufficient coefficient {j} failed')
        ratios.append(quotient);event(stage='coefficient-accepted',j=j)
        ns=[y-x for x,y in zip(ns,ns[1:])];ds=[y-x for x,y in zip(ds,ds[1:])]
    require(ratios[-1]==limit and (F(1)/beta)**p>=eta,'top coefficient control and q=1 negative')
    num=(H+h)**p;den=h**p
    L=(num//den).bit_length();require((den<<(L-1))<=num<(den<<L) and (H+h)*L>2*H*p,'first strict loss and all-size tail')
    cap,k,tested,rows=price(C-F(L,H)-d,F(peer['rational_raw'][0]))
    require(k>floor and k<tested<cap,'complete price selection')
    out={'pins':pins,'archive_members':MEMBERS,'case':{'p':p,'h':h,'v':v,'H':H,'L':L,'q':str(q),'beta':str(beta)},
         'comparator':signed['claim'],'component':'finite positive price; fresh signed replay pending','uniform_loss':str(F(L,H)),'cover_loss':str(d),
         'raw_mean_upper':bounded_print(raw),'split_uplift_upper':bounded_print(split),'completion_upper':'0','completed_mean_upper':bounded_print(complete),
         'eta_lower':str(eta),'top_coefficient_ratio':str(limit),'all_coefficient_ratios':[str(x) for x in ratios],
         'worst_coefficient':ratios.index(max(ratios)),'worst_ratio_upper':bounded_print(max(ratios)),
         'covered':str(C-F(L,H)-d),'stages':rows,'cap':decimal_str(cap,15),'claim':decimal_str(k,14),'tested':decimal_str(tested,14),
         'gain':str(k-prior_claim),'percent':str(100*(k-prior_claim)/prior_claim),'old_relaxed_ceiling':str(ul),'separation':str(k-ul),
         'controls':['R348 complete price','first smaller L fails','all paid ranks at slab cap q=1 fails leading coefficient']}
    dump(a.out,out);event(stage='success')
    print('PASS',L,out['cap'],out['claim'],out['tested'],out['gain'],flush=True)

def main():
    parser=argparse.ArgumentParser()
    for key in ('peer','binary','prior-price','prior-signed','prior-accept','weighted','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--prior-accept-sha',required=True)
    parser.add_argument('--child',action='store_true',help=argparse.SUPPRESS)
    a=parser.parse_args()
    require(sys.implementation.name=='cpython' and sys.version_info[:2]==(3,12) and __debug__,'CPython 3.12 with assertions')
    if a.child:
        compute(a);return
    require(not any(x.exists() for x in (a.out,a.out.with_suffix('.progress.jsonl'),a.out.with_suffix('.timing.json'))),'new receipt and progress paths required')
    begin=time.monotonic()
    try:
        run=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=45)
        status=run.returncode
    except subprocess.TimeoutExpired:
        status=124
    dump(a.out.with_suffix('.timing.json'),{'limit_seconds':45,'elapsed_seconds':round(time.monotonic()-begin,6),'exit_code':status})
    raise SystemExit(status)
if __name__=='__main__':
    main()
