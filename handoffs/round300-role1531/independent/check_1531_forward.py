"""Independently replay the fixed owned1531 incoming-shear support gate."""
import argparse
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import lcm
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "ROLE902-WORD.json.gz":"6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "ROLE902-APPLICATION.json":"a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "7113-CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
ROLE, SOURCE, RECIPIENT, CUT, CAP = 1531, 995, 917, 44261, 30
BANK = [623, 732, 753, 1285, 1286, 1288, 1482, 1524]
UNIT = 1125*2**25


def emit(**record):
    print(dumps(record,sort_keys=True,default=str),flush=True)


def unique(pairs):
    obj=dict(pairs)
    assert len(obj)==len(pairs),"duplicate JSON key"
    return obj


def canonical(x):
    return dumps(x,sort_keys=True,separators=(",",":")).encode()


def span(basis):
    v={0}
    for a in basis:
        assert a not in v and 0<a<512
        v.update(a^x for x in tuple(v))
    return v


@cache
def exact(value):
    x=Fraction(value)
    assert x
    return x.numerator,x.denominator


class State:
    def __init__(self,word,spaces,rows):
        self.public=word["public"]
        self.chart=word["initial"]+[None]*word["owned_fields"]
        self.rows=rows+[{} for _ in range(word["owned_fields"])]
        self.owners={}
        self.spaces=spaces

    def apply(self,i,event):
        op,role,*tokens=event
        if op=="INIT":
            assert role>=self.public and not self.rows[role] and self.chart[role] is None and role not in self.owners
            self.chart[role]=tokens[0]
            self.owners[role]=i
        elif op=="CLEAR":
            assert self.chart[role]==tokens[0] and role in self.owners
            self.chart[role]=None
            self.rows[role]={}
            del self.owners[role]
        elif op=="MOVE":
            a,b,owned=tokens
            assert self.chart[role]==a and owned==(role>=self.public)==(role in self.owners)
            assert self.spaces[a]<self.spaces[b] or owned and self.spaces[b]<self.spaces[a]
            self.chart[role]=b
        else:
            assert op in ("ADD","COPY","SCALE")
            source=role if op=="SCALE" else tokens[0]
            assert self.chart[role]==self.chart[source]==tokens[-1] and ((role==source)==(op=="SCALE"))
            p,q=exact(tokens[-2])
            read=self.rows[source]
            changed={}
            for j,value in read.items():
                scaled,rem=divmod(value*p,q)
                assert not rem
                if scaled:
                    changed[j]=scaled
            if op=="ADD":
                write=self.rows[role]
                for j,value in changed.items():
                    total=write.get(j,0)+value
                    if total:
                        write[j]=total
                    else:
                        write.pop(j,None)
            else:
                if op=="COPY":
                    assert not self.rows[role] and role in self.owners
                self.rows[role]=changed


def prove_literal(word):
    tape=word["program"]
    old=[["ADD",ROLE,732,"-1",117],["MOVE",ROLE,117,534,True],
         ["ADD",ROLE,SOURCE,"-4",534],["MOVE",ROLE,534,541,True],
         ["SCALE",ROLE,"1/2",541],["ADD",RECIPIENT,ROLE,"1",541],
         ["CLEAR",ROLE,541],["MOVE",SOURCE,534,905,False]]
    assert tape[CUT-1:CUT+7]==old
    assert all(e[0]!="CLEAR" or e[1]!=ROLE for e in tape[CUT:CUT+5])
    spaces=[span(v) for v in word["frames"]]
    assert spaces[117]<spaces[534]<spaces[541] and [len(spaces[j]) for j in (117,534,541)]==[32,64,128]
    return tape,spaces


def combine(rows, multipliers):
    out={}
    for row,weight in zip(rows,multipliers,strict=True):
        for j,v in row.items():
            out[j]=out.get(j,0)+weight*v
    return {j:v for j,v in out.items() if v}


def compare(state,tape,first,label):
    role_owner=state.owners[ROLE]
    start=state.rows[ROLE].copy()
    source=state.rows[SOURCE].copy()
    recipient=state.rows[RECIPIENT].copy()
    before={r:state.rows[r].copy() for r in BANK}
    assert state.chart[ROLE]==117 and state.chart[SOURCE]==534 and state.chart[RECIPIENT]==541
    assert [j for j,ch in enumerate(state.chart) if ch==117]==BANK+[ROLE]
    records={}
    for i in range(CUT,CUT+6):
        if label=="original":
            state.apply(i,tape[i])
        elif i==CUT:
            for e in first:
                state.apply(i,e)
            state.apply(i,["MOVE",ROLE,117,541,True])
        elif i not in (CUT+1,CUT+2):
            state.apply(i,tape[i])
        assert state.rows[SOURCE]==source and all(state.rows[r]==row for r,row in before.items())
        if i<CUT+5:
            assert state.owners[ROLE]==role_owner
        else:
            assert ROLE not in state.owners and state.chart[ROLE] is None and not state.rows[ROLE]
        if i in (CUT+2,CUT+3,CUT+4):
            records[i]=(state.rows[ROLE].copy(),state.rows[RECIPIENT].copy())
    return role_owner,start,source,recipient,records


def verify_endpoint_action(old, changed):
    _, owner0, source, recipient0, stamps=old
    _, new_owner0, new_source, new_recipient0, new_stamps=changed
    assert owner0==new_owner0 and source==new_source and recipient0==new_recipient0
    assert stamps[CUT+2][0]==combine([owner0,source],[1,-4])
    assert stamps[CUT+3][0]==combine([owner0,source],[Fraction(1,2),-2])
    assert stamps[CUT+4][1]==combine([recipient0,owner0,source],[1,Fraction(1,2),-2])
    return combine([stamps[CUT+4][1],new_stamps[CUT+4][1]],[1,-1])


def scalar(row):
    assert not row.keys()-{0}
    return Fraction(row.get(0,0),UNIT)


def prefix(word,spaces,rows,state):
    s=State(word,spaces,rows)
    for i,event in enumerate(word["program"][:CUT]):
        state["clock"]=i
        s.apply(i,event)
    assert s.owners[ROLE]<CUT-1 and word["program"][s.owners[ROLE]][:2]==["INIT",ROLE]
    return s


def fork(s):
    result=State.__new__(State)
    result.public=s.public
    result.chart=s.chart.copy()
    result.rows=[row.copy() for row in s.rows]
    result.owners=s.owners.copy()
    result.spaces=s.spaces
    return result


def main():
    assert __debug__ and version_info[:2]==(3,12)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("inputs",type=Path)
    p.add_argument("primary",type=Path)
    p.add_argument("primary_sha256")
    args=p.parse_args()
    t=perf_counter()
    state={"stage":"authentication","clock":None}

    def cap(_sig,_frame):
        emit(status="INDEPENDENT_CAP",progress=state,cases_completed=0,cap_seconds=CAP,seconds=perf_counter()-t)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    raw={k:(args.inputs/k).read_bytes() for k in PINS}
    assert {k:sha256(v).hexdigest() for k,v in raw.items()}==PINS
    pc=args.primary.read_bytes()
    assert sha256(pc).hexdigest()==args.primary_sha256
    lead=loads(pc,object_pairs_hook=unique)
    assert lead["cases_completed"]==lead["case_cap"]==1 and lead["timeout_seconds"]==CAP
    assert lead["cut"]==CUT and lead["host"]==ROLE and lead["source"]==SOURCE and lead["recipient"]==RECIPIENT
    assert lead["bank"]==BANK and lead["exact_paid_delta_native"]=={"1":-2,"2":1}
    packed=decompress(raw["ROLE902-WORD.json.gz"])
    assert sha256(packed).hexdigest()==WORD
    word,app,caller=(loads(x,object_pairs_hook=unique) for x in (packed,raw["ROLE902-APPLICATION.json"],raw["7113-CALLER.json"]))
    assert app["status"]=="PASS_ROLE902_FINAL_APPLICATION" and app["candidate_canonical_sha256"]==WORD
    assert app["caller_sha256"]==PINS["7113-CALLER.json"] and Fraction(app["claim"])==Fraction("0.003648411294790")
    assert word["public"]==1501 and len(word["program"])==76490 and caller["stages"]==17
    tape,spaces=prove_literal(word)
    public=word["public"]
    state["stage"]="chronological exact public forward rows"
    base=prefix(word,spaces,[{j:UNIT} for j in range(public)],state)
    owner=base.owners[ROLE]
    digest=sha256(canonical({r:base.rows[r] for r in BANK+[ROLE,SOURCE,RECIPIENT]})).hexdigest()
    assert SOURCE not in BANK+[ROLE] and RECIPIENT not in BANK+[ROLE,SOURCE]
    state["stage"]="independent literal cut result"
    if lead["status"]=="EXACT_INCOMING_ABSORPTION_EXCLUSION":
        probe={int(k):Fraction(v) for k,v in lead["probe"].items()}
        assert all(0<=j<public and v for j,v in probe.items())
        value=lambda r:sum(Fraction(v,UNIT)*probe.get(j,0) for j,v in base.rows[r].items())
        assert value(SOURCE)==lead["target_evaluation"]==1
        assert [value(r) for r in BANK]==lead["donor_evaluations"]==[0]*len(BANK)
        scale=lcm(*(v.denominator for v in probe.values()))
        integral={j:int(v*scale) for j,v in probe.items()}
        replay=prefix(word,spaces,[{0:integral[j]*UNIT} if j in integral else {} for j in range(public)],state)
        assert all(not replay.rows[r] for r in BANK) and scalar(replay.rows[SOURCE])==scale
        zero=prefix(word,spaces,[{} for _ in range(public)],state)
        assert not any(zero.rows[r] for r in BANK+[ROLE,SOURCE,RECIPIENT])
        before=compare(fork(replay),tape,[],"original")
        after=compare(replay,tape,[],"direct")
        difference=verify_endpoint_action(before,after)
        assert scalar(difference)==-2*scale
        report={"status":"PASS_INDEPENDENT_1531_FIXED_DONOR_EXCLUSION","separator":probe,"integral_separator":integral,
                "scale":scale,"owned1531_before_move":scalar(before[1]),"zero_owned1531_before_move":0,
                "full_bank_including_host_collision":not before[1],"source995_before_move":scalar(before[2]),
                "chart117_donor_values":[0]*len(BANK),"recipient917_before_move":scalar(before[3]),
                "old917_after_outward":scalar(before[4][CUT+4][1]),
                "no_supported_shear_917_after_outward":scalar(after[4][CUT+4][1]),
                "old_minus_edited_917_after_outward":scalar(difference)}
    else:
        assert lead["status"]=="NECESSARY_SPAN_SURVIVES_GRID_AND_PHYSICAL_PENDING"
        recipe={int(k):Fraction(v) for k,v in lead["add_recipe"].items()}
        assert recipe.keys()<=set(BANK)
        assert combine([base.rows[r] for r in BANK],[recipe.get(r,0) for r in BANK])==combine([base.rows[SOURCE]],[-4])
        early=[["ADD",ROLE,r,str(v),117] for r,v in sorted(recipe.items()) if v]
        before=compare(fork(base),tape,[],"original")
        after=compare(base,tape,early,"direct")
        assert not verify_endpoint_action(before,after) and before[4]==after[4]
        report={"status":"PASS_INDEPENDENT_1531_NORMALIZED_ACTION_ONLY","early_recipe":early}
    alarm(0)
    emit(**report,cases_completed=1,unresolved_in_scope=[],bank=BANK,cut=CUT,original_owner_init=owner,
         first_outward=CUT+4,clear=CUT+5,old_source995_later_move=CUT+6,receiver=RECIPIENT,
         word_canonical_sha256=WORD,caller_head=CALLER,forward_rows_sha256=digest,
         input_pins=PINS,primary_sha256=args.primary_sha256,cap_seconds=CAP,seconds=perf_counter()-t)


if __name__=="__main__":
    main()
