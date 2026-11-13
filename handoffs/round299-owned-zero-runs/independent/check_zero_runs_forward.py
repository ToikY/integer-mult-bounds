"""Check the frozen owned MOVE runs by exact chronological forward replay."""
import argparse
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
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
CAP = 30
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


def touched(role,event):
    return event[1]==role or event[0] in ("ADD","COPY") and event[2]==role


def contact_chart(event):
    op=event[0]
    assert op in ("CLEAR","COPY","SCALE","ADD")
    return event[-1]


def unpack_cases(raw):
    document=loads(raw,object_pairs_hook=unique)
    if isinstance(document,dict):
        document=next(document[k] for k in ("cases","ordered_cases","top_cases","ranked_cases","top") if k in document)
    assert isinstance(document,list) and 0<len(document)<=8
    out=[]
    for case in document:
        if isinstance(case,list):
            role,first,next_clock=case
            moves=None
        else:
            role=case["role"]
            moves=case.get("moves",case.get("move_clocks"))
            if moves and isinstance(moves[0],list):
                moves=[x[0] for x in moves]
            first=next((case[k] for k in ("first_move","first_move_clock","first") if k in case), moves[0] if moves else None)
            next_clock=next(case[k] for k in ("next_contact","next_contact_clock","next_clock","next") if k in case)
            if isinstance(next_clock,list):
                next_clock=next_clock[0]
        assert all(type(n) is int for n in (role,first,next_clock)) and 0<=first<next_clock
        if moves is not None:
            assert moves==sorted(set(moves)) and moves[0]==first and moves[-1]<next_clock
        out.append((role,first,next_clock,moves))
    assert len({x[:3] for x in out})==len(out)
    return out


def check_cases(word,spaces,cases):
    tape=word["program"]
    all_roles=range(word["public"],word["public"]+word["owned_fields"])
    index={role:[] for role,_,_,_ in cases}
    for clock,event in enumerate(tape):
        for role in index.keys() & set(event[1:3] if event[0] in ("ADD","COPY") else event[1:2]):
            index[role].append(clock)
    out=[]
    for role,first,next_clock,declared_moves in cases:
        assert role in all_roles and next_clock<len(tape)
        contacts=index[role]
        k=contacts.index(first)
        assert k and tape[contacts[k-1]][0]!="MOVE"
        moves=[]
        while tape[contacts[k]][0]=="MOVE":
            moves.append(contacts[k]); k+=1
        assert contacts[k]==next_clock and (declared_moves is None or moves==declared_moves)
        assert moves and all(tape[i][1]==role and tape[i][-1] is True for i in moves)
        ranks=[abs(len(word["frames"][tape[i][2]])-len(word["frames"][tape[i][3]])) for i in moves]
        assert all(ranks)
        owner_init=next(i for i in reversed(contacts[:k]) if tape[i][0]=="INIT")
        assert all(tape[i][0]!="CLEAR" for i in contacts[:k] if i>owner_init)
        next_event=tape[next_clock]
        assert touched(role,next_event) and tape[moves[-1]][3]==contact_chart(next_event)
        source=tape[moves[0]][2]
        for i in moves:
            a,b=tape[i][2:4]
            assert a==source and (spaces[a]<spaces[b] or spaces[b]<spaces[a])
            source=b
        out.append({"role":role,"first_move":first,"next_contact":next_clock,"moves":moves,
                    "move_edges":[tape[i][2:4] for i in moves],"ranks":ranks,
                    "owned_rise_ranks":[r for i,r in zip(moves,ranks,strict=True) if spaces[tape[i][2]]<spaces[tape[i][3]]],
                    "original_owner_init":owner_init,"previous_contact":contacts[contacts.index(first)-1],
                    "next_operation":next_event})
    return out


def nonzero(row):
    if not row:
        return None
    j=min(row)
    return {"input":j,"coefficient":Fraction(row[j],UNIT)}


def run(word,spaces,records,state):
    public=word["public"]
    snapshot={}
    by_clock={}
    for record in records:
        for name in ("first_move","next_contact"):
            by_clock.setdefault(record[name],[]).append((name,record))
    s=State(word,spaces,[{j:UNIT} for j in range(public)])
    for clock,event in enumerate(word["program"][:max(by_clock)+1]):
        state["clock"]=clock
        for name,record in by_clock.get(clock,()):
            key=record["role"],record["first_move"],record["next_contact"]
            r=record["role"]
            assert s.owners[r]==record["original_owner_init"]
            row=s.rows[r]
            if name=="first_move":
                assert s.chart[r]==event[2]
                snapshot[key]=row.copy()
                record["pre_first_frame"]=s.chart[r]
                record["pre_first_zero"]=not row
                record["pre_first_row_support"]=len(row)
                record["first_exact_nonzero"]=nonzero(row)
            else:
                assert s.chart[r]==contact_chart(event)
                assert row==snapshot.pop(key)
                record["pre_next_frame"]=s.chart[r]
                record["pre_next_row_unchanged"]=True
                record["pre_first_row_sha256"]=sha256(canonical(row)).hexdigest()
                if event[:2]==["COPY",r]:
                    assert not row
                    record["copy_zero_destination_verified"]=True
                elif event[:1]==["COPY"]:
                    assert not s.rows[event[1]]
                    record["copy_zero_destination_verified"]=True
        s.apply(clock,event)
        for name,record in by_clock.get(clock,()):
            if name=="next_contact":
                r=record["role"]
                record["post_next_row_support"]=len(s.rows[r])
                record["post_next_owner_active"]=r in s.owners
    assert not snapshot
    return max(by_clock)


def main():
    assert __debug__ and version_info[:2]==(3,12)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_root",type=Path)
    p.add_argument("cases",type=Path)
    p.add_argument("cases_sha256")
    p.add_argument("--tested-count",type=int,help="run just this many front cases in the primary receipt")
    args=p.parse_args()
    t=perf_counter()
    state={"stage":"authenticate","clock":None}

    def cap(_sig,_frame):
        emit(status="INDEPENDENT_CAP",progress=state,cap_seconds=CAP,seconds=perf_counter()-t)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    raw={p:(args.input_root/p).read_bytes() for p in PINS}
    assert {p:sha256(v).hexdigest() for p,v in raw.items()}==PINS
    w=decompress(raw["ROLE902-WORD.json.gz"])
    assert sha256(w).hexdigest()==WORD
    w,app,caller=(loads(x,object_pairs_hook=unique) for x in (w,raw["ROLE902-APPLICATION.json"],raw["7113-CALLER.json"]))
    assert app["status"]=="PASS_ROLE902_FINAL_APPLICATION" and app["candidate_canonical_sha256"]==WORD
    assert app["caller_sha256"]==PINS["7113-CALLER.json"] and Fraction(app["claim"])==Fraction("0.003648411294790")
    assert w["public"]==1501 and w["owned_fields"]==68 and len(w["program"])==76490 and caller["stages"]==17
    spec=args.cases.read_bytes()
    assert sha256(spec).hexdigest()==args.cases_sha256
    cases=unpack_cases(spec)
    count=len(cases) if args.tested_count is None else args.tested_count
    assert 1<=count<=len(cases)
    cases=cases[:count]
    spaces=[span(frame) for frame in w["frames"]]
    state["stage"]="literal owned MOVE chronology"
    records=check_cases(w,spaces,cases)
    state["stage"]="exact arbitrary-input forward rows"
    final=run(w,spaces,records,state)
    alarm(0)
    emit(status="PASS_INDEPENDENT_OWNED_RUN_FORWARD",cases_completed=len(records),cases=records,
         zero_pre_first_cases=sum(r["pre_first_zero"] for r in records),last_processed_old_event=final,
         cap_seconds=CAP,cases_sha256=args.cases_sha256,word_canonical_sha256=WORD,caller_head=CALLER,
         input_pins=PINS,seconds=perf_counter()-t)


if __name__=="__main__":
    main()
