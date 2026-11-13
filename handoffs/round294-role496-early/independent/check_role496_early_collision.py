"""Find and forward-replay an exact minimal-support collision on the fixed role496 bank."""
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
ROLE, START, END, CUT, FIRST_READ, CAP = 496,40952,40957,41782,43371,30
BANK = [496,903,984,1129]
UNIT = 1125*2**25
OMIT = {START,40954,40956}
REPLACEMENT = ["MOVE",ROLE,729,912,False]


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

    def fork(self):
        obj=object.__new__(type(self))
        obj.public=self.public
        obj.chart=self.chart.copy()
        obj.rows=[r.copy() for r in self.rows]
        obj.owners=self.owners.copy()
        obj.spaces=self.spaces
        return obj

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


def run_to_cut(word,spaces,rows,progress):
    tape=word["program"]
    old=State(word,spaces,rows)
    for i in range(START):
        progress["clock"]=i
        old.apply(i,tape[i])
    new=old.fork()
    assert old.chart[ROLE]==new.chart[ROLE]==729
    for i in range(START,CUT):
        progress["clock"]=i
        old.apply(i,tape[i])
        if i not in OMIT:
            new.apply(i,REPLACEMENT if i==END else tape[i])
    assert old.chart==new.chart and old.owners==new.owners
    assert [j for j,k in enumerate(old.chart) if k==912]==BANK
    assert all(old.rows[j]==new.rows[j] for j in (903,984,1129))
    return old,new


def find_sparse(old_row,edited_rows,public):
    single=0
    rays={}
    off_diagonal=[]
    for j in range(public):
        single+=1
        edited=tuple(row.get(j,0) for row in edited_rows)
        required=old_row.get(j,0)
        if not any(edited):
            if required:
                off_diagonal.append(j)
            continue
        pivot=next(v for v in edited if v)
        key=tuple(Fraction(x,pivot) for x in edited)
        normalized=Fraction(required,pivot)
        if key in rays:
            host,host_pivot,host_value=rays[key]
            if host_value!=normalized:
                scale=Fraction(-host_pivot,pivot)
                rays[key]=(host,host_pivot,host_value)
                yield {host:Fraction(1),j:scale},2,None
        else:
            rays[key]=(j,pivot,normalized)
    for j in off_diagonal:
        yield {j:Fraction(1)},1,single


def value(row):
    assert set(row)<={0}
    return Fraction(row.get(0,0),UNIT)


def main():
    assert __debug__ and version_info[:2]==(3,12)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root",type=Path)
    args=parser.parse_args()
    start=perf_counter()
    progress={"stage":"authenticate","clock":None}

    def cap(_sig,_frame):
        emit(status="INDEPENDENT_CAP",progress=progress,completed=0,cap_seconds=CAP,seconds=perf_counter()-start)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    data={p:(args.input_root/p).read_bytes() for p in PINS}
    assert {p:sha256(raw).hexdigest() for p,raw in data.items()}==PINS
    raw=decompress(data["ROLE902-WORD.json.gz"])
    assert sha256(raw).hexdigest()==WORD
    word=loads(raw,object_pairs_hook=unique)
    app=loads(data["ROLE902-APPLICATION.json"],object_pairs_hook=unique)
    caller=loads(data["7113-CALLER.json"],object_pairs_hook=unique)
    assert word["public"]==1501 and len(word["program"])==76490 and caller["stages"]==17
    assert app["status"].startswith("PASS_") and app["candidate_canonical_sha256"]==WORD
    assert app["caller_sha256"]==PINS["7113-CALLER.json"] and Fraction(app["claim"])==Fraction("0.00364841129479")
    tape=word["program"]
    expected=[["MOVE",496,729,730,False],["MOVE",230,261,730,False],["ADD",496,230,"1",730],
              ["MOVE",994,261,730,False],["ADD",994,496,"-1",730],["MOVE",496,730,912,False],
              ["MOVE",984,374,912,False]]
    assert tape[START:END+2]==expected
    assert tape[40949][:3]==["ADD",1077,496] and tape[40959][:3]==["ADD",496,984]
    assert tape[FIRST_READ-1][0:2]==["MOVE",220] and tape[FIRST_READ-1][3]==912
    assert tape[FIRST_READ]==["ADD",220,496,"-1/2",912]
    assert tape[41776:CUT]==[["MOVE",1129,575,912,False],["MOVE",903,791,912,False],
        ["ADD",1129,903,"-1",912],["ADD",903,984,"-1",912],
        ["ADD",984,903,"1/2",912],["SCALE",903,"-1/2",912]]
    assert all(e[1]!=ROLE and not(e[0] in ("ADD","COPY") and e[2]==ROLE) for e in tape[CUT:FIRST_READ])
    assert [tape[i] for i in (41777,41783,41786)]==[["MOVE",903,791,912,False],
              ["MOVE",984,912,228,False],["MOVE",903,912,148,False]]
    spaces=[span(v) for v in word["frames"]]
    assert spaces[729]<spaces[730]<spaces[912] and [len(word["frames"][j]) for j in (729,730,912)]==[4,6,7]
    public=word["public"]
    progress["stage"]="full exact public forward coefficients"
    old,new=run_to_cut(word,spaces,[{j:UNIT} for j in range(public)],progress)
    progress["stage"]="minimal sparse witness"
    old_row=old.rows[ROLE]
    edited=[new.rows[j] for j in BANK]
    candidates=list(find_sparse(old_row,edited,public))
    assert candidates,"one- and two-coordinate search found no collision"
    probe,weight,_=min(candidates,key=lambda x:(x[1],tuple(x[0])))
    assert sum(old_row.get(j,0)*v for j,v in probe.items())!=0
    assert all(not sum(row.get(j,0)*v for j,v in probe.items()) for row in edited)
    progress["stage"]="literal sparse collision replay"
    probes=[]
    for x in ({},probe):
        raw_probe={j:v*UNIT for j,v in x.items()}
        assert all(v.denominator==1 for v in raw_probe.values())
        a,b=run_to_cut(word,spaces,[{0:int(raw_probe[j])} if j in raw_probe else {} for j in range(public)],progress)
        left,right=([value(s.rows[j]) for j in BANK] for s in (a,b))
        assert left==[Fraction(sum(old.rows[r].get(j,0)*v for j,v in x.items()),UNIT) for r in BANK]
        assert right==[0]*len(BANK)
        for i in range(CUT,FIRST_READ):
            progress["clock"]=i
            a.apply(i,tape[i]); b.apply(i,tape[i])
        before_first_read=[value(s.rows[ROLE]) for s in (a,b)]
        assert before_first_read==[left[0],right[0]]
        assert a.chart==b.chart and a.owners==b.owners
        assert value(a.rows[220])==value(b.rows[220])
        a.apply(FIRST_READ,tape[FIRST_READ]); b.apply(FIRST_READ,tape[FIRST_READ])
        probes.append({"input":x,"pre41782_old_bank":left,"pre41782_edited_bank":right,
                       "pre_first_outward496_old_and_edited":before_first_read,
                       "post_read_old220":value(a.rows[220]),"post_read_edited220":value(b.rows[220])})
    assert probes[0]["pre41782_old_bank"]==[0]*len(BANK)
    assert probes[1]["pre41782_old_bank"][BANK.index(ROLE)]!=0
    assert probes[1]["post_read_old220"]!=probes[0]["post_read_old220"]
    alarm(0)
    emit(status="PASS_INDEPENDENT_FIXED_EARLY_BANK_COLLISION",cases_completed=1,unresolved_in_scope=[],
         role=ROLE,repair_cut=CUT,first_outward_clock=FIRST_READ,bank_chart=912,complete_bank=BANK,old_and_edited_unchanged_donors=[903,984,1129],
         edited_omitted_old_clocks=sorted(OMIT),direct_old_clock=END,probes=probes,minimal_input_support=weight,
         one_coordinate_cases_checked=public,one_coordinate_collisions=sum(n==1 for _,n,_ in candidates),
         forward_rows_sha256=sha256(canonical({"old":{j:old.rows[j] for j in BANK},"edited":{j:new.rows[j] for j in BANK}})).hexdigest(),
         word_canonical_sha256=WORD,caller_head=CALLER,input_pins=PINS,cap_seconds=CAP,seconds=perf_counter()-start)


if __name__=="__main__":
    main()
