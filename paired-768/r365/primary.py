"""One whole-invoice test for physically swapping two unanchored adjacent binary charts."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip,json,runpy,subprocess,sys,tarfile,tempfile,time

PINS={
    'inputs/APPLICATION.json':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f',
    'inputs/APPLICATION-SOURCES.tar.gz':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
    'inputs/BINARY-CANDIDATE.json.gz':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326',
    'r352/accept.json':'0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377',
    'r360/directed.py':'798589c4bcdd19413bb270367b08862482d827191b66344810d1c05c7186be41',
}
def require(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def save(path,obj):
    with path.open('x') as f:json.dump(obj,f,sort_keys=True,indent=2);f.write('\n')
def run(a):
    root=a.inputs
    for name,h in PINS.items():require(digest(root/name)==h,name)
    peer=json.loads((root/'inputs/APPLICATION.json').read_bytes());word=json.loads(gzip.decompress((root/'inputs/BINARY-CANDIDATE.json.gz').read_bytes()))
    math=runpy.run_path(str(root/'r360/directed.py'));S=math['SCALE'];old=math['OLD'];rat=math['UPPER']
    require(F(json.loads((root/'r352/accept.json').read_bytes())['claim'])==old==F('.00389011527141') and rat==F(peer['rational_raw'][1]),'both supplier bounds')
    with tarfile.open(root/'inputs/APPLICATION-SOURCES.tar.gz') as arc:
        src=arc.extractfile('parent/binary/independent/literal.py').read()
        cb=arc.extractfile('source/research/paired-query-only-bit/EFREE-CALLER.json.gz').read()
    require(sha256(src).hexdigest()==math['LITERAL'] and sha256(cb).hexdigest()==math['CALLER'],'exact caller and independent native')
    caller=json.loads(gzip.decompress(cb))
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'literal.py';p.write_bytes(src);lit=runpy.run_path(str(p))
    require(lit['canonical'](word)==peer['binary_word']==math['WORD'],'exact #8027 native')
    ch=lit['Charts'](word['frames']);dim=ch.rank;flags=set(word['start'][:222]+word['final'][:222]);pg=word['program'];n=word['public'];ops=Counter(r[0] for r in caller['events']);no=peer['binary_native']
    nativeP=Counter();nativeT=Counter();entries={};inc=defaultdict(set);pairs=set()
    def add(kind,i,x,y):
        key=(kind,i);require(key not in entries,'unique operation key')
        g=ch.leg(x,y);require(kind=='M' or dim[y]>dim[x],'old oriented helper')
        entries[key]=(x,y,g);inc[x].add(key);inc[y].add(key)
        (nativeP if kind=='M' else nativeT)[g]+=1
        if x not in flags and y not in flags and dim[x]!=dim[y]:pairs.add(tuple(sorted((x,y))))
    for i,raw in enumerate(pg):
        if raw[0]=='MOVE':add('M',i,*raw[2:])
    for owner,(x,y) in enumerate(zip(word['start'][222:],word['final'][222:]),222):add('H',owner,x,y)
    P,T=lit['paired_invoice'](caller,nativeP,nativeT,ops);ordinary=lit['ordinary'](word,caller,ops,P,T)
    as_hist=lambda s:Counter({int(i):j for i,j in s.items()})
    require((P,T,ordinary)==(as_hist(no['paid_all']),as_hist(no['productive_all']),no['ordinary']) and
            sum(nativeP.values())==2803 and sum(nativeT.values())==408 and n==630 and ops['LOCAL']==36,'full control census')
    for reverse in (False,True):
        rows,ledger,_=lit['tape'](word,ch,adjoint=reverse);require(rows==lit['expected_rows'](n,reverse) and ledger['paid']==nativeP,'control native basis')
    fixed_claim,static=math['static_guards']();baseline=T.copy();baseline.subtract(P)
    bL,bU=math['moment'](baseline,1-old);old_raw_cap=F(peer['binary_raw'][1])
    def stage(**v):
        with a.out.with_suffix('.progress.jsonl').open('a') as f:f.write(json.dumps(v)+'\n')
    stage(step='all paid and helper incidences pinned',pairs=len(pairs))
    profiles={};cases=[];by_case={};eligible=[];stats=Counter();rawmax=None;maxmargin=None;maxdelta=None
    for ia,(x,y) in enumerate(sorted(pairs)):
        def sub(r):return y if r==x else x if r==y else r
        keys=inc[x]|inc[y];joint=sorted(inc[x]&inc[y]);require(joint and all(set(entries[z][:2])=={x,y} for z in joint),'shared edge')
        pp=nativeP.copy();tt=nativeT.copy();bad=None
        for z in sorted(keys):
            s,t,g=entries[z];l,r=sub(s),sub(t)
            changed_g=abs(dim[r]-dim[l]) if z[0]=='M' else dim[r]-dim[l]
            if z in joint and z[0]=='M':
                require((l,r)==(t,s) and changed_g==g,'swapped mutual paid grade stays paid')
            if changed_g<=0:
                bad=['paid_zero_distinct_labels' if z[0]=='M' else 'nonpositive_productive',z,s,t,l,r];break
            h=pp if z[0]=='M' else tt;h[g]-=1;h[changed_g]+=1
        case={'pair':[x,y],'union_count':len(keys),'shared_keys':joint};cases.append(case)
        if bad:
            case['state']=bad[0];case['witness']=bad[1:];stats[bad[0]]+=1;continue
        pp,tt=+pp,+tt
        cp=P.copy();ct=T.copy()
        for g in nativeP.keys()|pp:cp[g]+=36*(pp[g]-nativeP[g])
        for g in nativeT.keys()|tt:ct[g]+=36*(tt[g]-nativeT[g])
        cp,ct=+cp,+ct;ident=tuple(sorted(cp.items())),tuple(sorted(ct.items()))
        if ident not in profiles:
            signed=ct.copy();signed.subtract(cp)
            margin=math['moment'](signed,1-old);upper=math['upper_bound'](signed)
            deriv=sum(v*math['power'](r,1-(rat if v>0 else old),True)[v<0] for r,v in signed.items() if v)
            state=('unchanged_both_histograms' if cp==P and ct==T else 'raw_ceiling' if upper<=old else
                   'old_raw_separation_unresolved' if math['moment'](signed,1-old_raw_cap)[0]<=0 else math['price_gates'](ct,cp))
            profiles[ident]=(state,upper,margin[1],deriv)
        state,upper,mu,deriv=profiles[ident];stats[state]+=1
        rawmax=upper if rawmax is None else max(rawmax,upper);maxmargin=mu if maxmargin is None else max(maxmargin,mu)
        maxdelta=mu-bL if maxdelta is None else max(maxdelta,mu-bL)
        case.update(state=state,upper=str(upper),margin_upper=str(F(mu,S)),negative_derivative_lower=str(F(deriv,S)))
        by_case[x,y]=(pp,tt,cp,ct)
        if state=='PASS':eligible.append((-mu,x,y))
        if ia%128==0:stage(step='price',last_pair=[x,y])
    eligible.sort();selected=eligible[:128];failed=[];best=None
    stage(step='geometry',eligible=len(eligible),cap=len(selected))
    for _,x,y in selected:
        def sub(r):return y if r==x else x if r==y else r
        offending=None
        for z in sorted(inc[x]|inc[y]):
            s,t,_=entries[z];l,r=sub(s),sub(t)
            low,high=sorted((l,r),key=dim.get)
            require(dim[low]<dim[high] and (z[0]=='M' or l==low),'admitted grade mandatory')
            u=ch.frames[low][0];v=ch.frames[high][1]
            f=next(((i,j,q) for i,row in enumerate(u) for j,col in enumerate(v) if (q:=sum(a*b for a,b in zip(row,col)))),None)
            if f:
                i,j,q=f;offending=dict(pair=[x,y],key=z,original=[s,t],changed=[l,r],low=low,high=high,row_pair=[i,j],dot=str(q));break
            require(ch.leg(l,r)==abs(dim[l]-dim[r]),'nested dual views')
        if offending:failed.append(offending);continue
        tape=[]
        for o,r,*z in pg:
            if o=='MOVE':tape.append([o,r,*map(sub,z)])
            elif o=='ADD':tape.append([o,r,z[0],sub(z[1])])
            elif o in ('INIT','CLEAR'):tape.append([o,r,sub(z[0])])
            else:require(o=='SWAP','typed operand');tape.append([o,r,z[0]])
        w=dict(word,start=list(map(sub,word['start'])),final=list(map(sub,word['final'])),program=tape)
        require(w['start'][:222]==word['start'][:222] and w['final'][:222]==word['final'][:222] and ch.main_contacts(w['start'],w['final'])==111,'fixed caller')
        np,nt,cp,ct=by_case[x,y]
        for rev in (False,True):
            rows,lg,_=lit['tape'](w,ch,adjoint=rev);require(rows==lit['expected_rows'](n,rev) and lg['paid']==np,'signed candidate')
        tar=Counter(ch.leg(s,t) for s,t in zip(w['start'][222:],w['final'][222:]));pp,tt=lit['paired_invoice'](caller,lg['paid'],tar,ops)
        require((pp,tt)==(cp,ct) and tar==nt and lit['ordinary'](w,caller,ops,pp,tt)==ordinary,'all paid productive and ordinary unchanged-volume checks')
        gone=next(i for i,z in enumerate(tape) if z[0]=='CLEAR')
        try:lit['tape'](w,ch,omit=gone)
        except ValueError:pass
        else:raise ValueError('omission control failed')
        best=dict(pair=[x,y],canonical=lit['canonical'](w),paid=dict(cp),productive=dict(ct),ordinary=ordinary,coefficient_count_each=n*n,
                  pending='physical arbitrary-index source proof, tape precision, and complete signed multiplication replay')
        with a.out.with_suffix('.candidate.json.gz').open('xb') as f:f.write(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0))
        break
    inventory=a.out.with_suffix('.cases.json');save(inventory,cases)
    stage(step='close',visited=len(failed)+int(bool(best)))
    save(a.out,dict(status='SIGNED_NATIVE_CANDIDATE' if best else 'NO_VERIFIED_GAIN',pins=PINS,program=peer['binary_word'],comparator=str(old),rational_upper=str(rat),
        control={'paid_native':nativeP,'productive_native':nativeT,'public':n,'ports':111,'caller':ops['LOCAL'],'ordinary':ordinary,'signed_coefficients_per_orientation':n*n},
        assignments=len(pairs),case_inventory_sha=digest(inventory),counts=dict(stats),distinct_price_profiles=len(profiles),
        whole_relaxed_raw_cap=str(rawmax) if rawmax is not None else None,absolute_margin_upper=str(F(maxmargin,S)) if maxmargin is not None else None,
        max_change_in_margin=str(F(maxdelta,S)) if maxdelta is not None else None,both_old_margins=list(map(str,(F(bL,S),F(bU,S)))),
        checked_geometry_rejections=failed,ranked=[[x,y] for _,x,y in eligible],unvisited=[[x,y] for _,x,y in eligible[len(failed)+int(bool(best)):]],
        candidate=best,fixed_complete_trial=static['trial'],fixed_conditional_lower_claim=str(fixed_claim)))
    print('assignments',len(pairs),'states',dict(stats),'price profiles',len(profiles),'geometry',len(failed)+int(bool(best)),'candidate',None if best is None else best['pair'])
def main():
    p=ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--child',action='store_true')
    a=p.parse_args();require(sys.version_info[:2]==(3,12) and __debug__,'CPython 3.12')
    if a.child:run(a);return
    require(not any(f.exists() for f in (a.out,*[a.out.with_suffix(s) for s in ('.cases.json','.progress.jsonl','.timing.json','.candidate.json.gz')])),'fresh basename')
    start=time.monotonic()
    try:rc=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=45).returncode
    except subprocess.TimeoutExpired:rc=124
    save(a.out.with_suffix('.timing.json'),dict(exit=rc,seconds=round(time.monotonic()-start,6),discovery_cap=45,verification_reserve=15,concrete_cap=128));raise SystemExit(rc)
if __name__=='__main__':main()
