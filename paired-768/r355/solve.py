"""One cut-word receiver-span check for the grade-seven binary delivery."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
import gzip,json
from pathlib import Path
import runpy,subprocess,sys,tarfile,tempfile,time

OMIT,READ,SENDER,RECEIVER,CHART=15264,30338,3226,3604,585
PINS={'BINARY-CANDIDATE.json.gz':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326','APPLICATION-SOURCES.tar.gz':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968','APPLICATION.json':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f'}
def check(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):
    return sha256(p.read_bytes()).hexdigest()
def read(p):
    return json.loads(p.read_bytes())
def save(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
def bits(x):return [i for i in range(x.bit_length()) if x>>i&1]

def solve(donors,target):
    pivots={}
    for i,(_,row,_) in enumerate(donors):
        v,comb=row,1<<i
        for p in sorted(pivots,reverse=True):
            if v>>p&1:v^=pivots[p][0];comb^=pivots[p][1]
        if v:pivots[v.bit_length()-1]=(v,comb)
    rem=target;coeff=0
    for p in sorted(pivots,reverse=True):
        if rem>>p&1:rem^=pivots[p][0];coeff^=pivots[p][1]
    if rem:
        witness=rem&-rem
        for p,(row,_) in sorted(pivots.items()):
            if (row&witness).bit_count()%2:witness^=1<<p
        check(all((row&witness).bit_count()%2==0 for _,row,_ in donors) and
              (target&witness).bit_count()%2==1,'every donor annihilated; target one')
        return len(pivots),None,witness
    rows=[donors[i] for i in bits(coeff)]
    v=0
    for _,row,_ in rows:v^=row
    check(v==target,'exact donor combination');return len(pivots),rows,None

def run(a):
    for name,expected in PINS.items():check(digest(a.peer/name)==expected,name)
    check(digest(a.probe)=='a44c23d978b9fd3e34229e90b3a7c6fe1b2c31873f70dd05d24114c11fb60772','full boundary receipt')
    check(digest(a.accept)=='0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377','complete comparator')
    previous=read(a.probe);accepted=read(a.accept);peer=read(a.peer/'APPLICATION.json')
    check(previous['clock']==OMIT and previous['owner']==SENDER and previous['adjoint_mask']['indices']==[171] and
          previous['forward_mask']['weight']==113 and 4 in previous['forward_mask']['indices'] and
          previous['first_forward_read']['clock']==READ and accepted['claim']==previous['comparator'],'R354 known-good cut')
    word=json.loads(gzip.decompress((a.peer/'BINARY-CANDIDATE.json.gz').read_bytes()))
    with tarfile.open(a.peer/'APPLICATION-SOURCES.tar.gz') as tar:
        source=tar.extractfile('parent/binary/independent/literal.py').read()
    check(sha256(source).hexdigest()=='4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c','literal source')
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/'literal.py';path.write_bytes(source);native=runpy.run_path(str(path))
    check(native['canonical'](word)==peer['binary_word']==previous['word'],'literal bank word')
    charts=native['Charts'](word['frames']);n=word['public'];owned=word['owned_fields']
    tags=word['start'][:]+[None]*owned;bank=[1<<i for i in range(n)]+[0]*owned
    last=[-1]*len(bank);source_form=None
    # Replay exactly the proposed cut: no paid transfer at OMIT. Every other
    # instruction until the read must remain executable with the actual chart tags.
    for clock in range(READ):
        k,r,*args=word['program'][clock]
        if clock==OMIT:
            check([k,r,*args]==['MOVE',SENDER,0,CHART] and tags[r]==0,'one omitted transfer')
            source_form=bank[r];continue
        if OMIT<clock:
            check(r!=SENDER and not(k in ('ADD','SWAP') and args[0]==SENDER),'post-cut stale use')
        if k=='INIT':
            chart,=args;check(r>=n and tags[r] is None and not bank[r],'open');tags[r]=chart;last[r]=clock
        elif k=='CLEAR':
            chart,=args;check(r>=n and tags[r]==chart,'owned erase');tags[r]=None;bank[r]=0;last[r]=clock
        elif k=='ADD':
            donor,chart=args;check(r!=donor and tags[r]==tags[donor]==chart,'ADD on legal operands')
            bank[r]^=bank[donor];last[r]=clock
        elif k=='SWAP':
            b,=args;check(r!=b and None not in (tags[r],tags[b]),'swap')
            tags[r],tags[b]=tags[b],tags[r];bank[r],bank[b]=bank[b],bank[r];last[r]=last[b]=clock
        else:
            aa,bb=args;check(k=='MOVE' and r>=n and tags[r]==aa and charts.leg(aa,bb)>0,'retained MOVE')
            tags[r]=bb;last[r]=clock
    check(word['program'][READ]==['ADD',RECEIVER,SENDER,CHART] and tags[RECEIVER]==CHART and tags[SENDER]==0 and
          source_form==bank[SENDER]==int(previous['forward_mask']['hex'],16),'preserved old value under literal omission')
    donors=[(r,bank[r],last[r]) for r,ch in enumerate(tags) if ch==CHART and r not in (SENDER,RECEIVER)]
    rank,combo,witness=solve(donors,source_form)
    rec={'status':'EXCLUDED_SAME_CLOCK_OTHER_DONOR_SPAN' if witness is not None else 'EXACT_SAME_CLOCK_SPAN_SURVIVES',
         'peer_head':'fb9b6a7b0d27da1cf98430893a3016bf811e2aa4','pins':PINS,'comparator':accepted['claim'],
         'cut':[OMIT,READ,SENDER,RECEIVER,CHART],'original_forward_weight':source_form.bit_count(),'target':hex(source_form),
         'adjoint_output':[171],'omitted_move_count':1,'native_calls':36,'receiver_form':hex(bank[RECEIVER]),'receiver_last_writer':last[RECEIVER],
         'legal_donor_rank':rank,'legal_other_donors':[{'id':r,'row':hex(x),'last_writer':t} for r,x,t in donors],
         'gross_upper_at_comparator':previous['gross_36_calls_at_comparator'][1],'open_repairs':['sender chart at CLEAR 39393','physical native scalar/caller and precision charges','fresh complete application'],
         'other_sites_tested':0,'selected_combination':None if combo is None else [r for r,_,_ in combo]}
    if witness is not None:
        rec.update(separating_input=hex(witness),separating_input_indices=bits(witness),
                   receiver_value_on_separator=(bank[RECEIVER]&witness).bit_count()%2,
                   old_addend_value_on_separator=(source_form&witness).bit_count()%2,
                   donor_values_on_separator=[(row&witness).bit_count()%2 for _,row,_ in donors])
    else:
        # Literal local XORs have fixed controllers and use only different live donors.
        check(all(r not in (SENDER,RECEIVER) for r,_,_ in combo),'no self updates')
        program=word['program'];edit=[]
        for clock,op in enumerate(program):
            if clock==OMIT:continue
            if clock==READ:edit.extend([['ADD',RECEIVER,r,CHART] for r,_,_ in combo])
            elif clock==39393:
                check(op==['CLEAR',SENDER,CHART],'sender retirement');edit.append(['CLEAR',SENDER,0])
            else:edit.append(op)
        cand=dict(word,program=edit)
        for rev in (False,True):
            observed,charges,_=native['tape'](cand,charts,adjoint=rev)
            check(observed==native['expected_rows'](n,rev),'exact literal basis/adjoint')
            check(sum(charges['paid'].values())==2802 and charges['paid'].get(7,0)==0,'entire paid change')
        rec.update(candidate_canonical=native['canonical'](cand),paid_move_difference_per_call=-1,extra_native_adds_per_call=len(combo)-1,
                   corrected_clear=['CLEAR',SENDER,0],candidate_status='literal direction checks passed; broader complete stock and scientific pricing pending')
    save(a.out,rec)
    print(rec['status'],len(donors),rank,rec.get('separating_input_indices'),rec['selected_combination'],flush=True)
def main():
    cli=ArgumentParser()
    for k in ('peer','probe','accept','out'):cli.add_argument('--'+k,type=Path,required=True)
    cli.add_argument('--child',action='store_true');a=cli.parse_args()
    check(sys.version_info[:2]==(3,12) and __debug__,'CPython 3.12')
    if a.child:run(a);return
    t=a.out.with_suffix('.timing.json');check(not t.exists() and not a.out.exists(),'fresh output')
    begin=time.monotonic()
    try:code=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=30).returncode
    except subprocess.TimeoutExpired:code=124
    save(t,{'exit':code,'seconds':round(time.monotonic()-begin,6),'limit':30,'reserve':10});raise SystemExit(code)
if __name__=='__main__':main()
