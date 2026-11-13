"""Check the helper1028 chronology using both literal old and edited scalar tapes."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "COMPOSED-WORD.json.gz":"926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
    "COMPOSED-APPLICATION.json":"d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "7113-CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
WORD = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
EARLY, CUT, CAP = 36416, 36422, 30


def emit(**fields):
    print(dumps(fields,sort_keys=True,default=str),flush=True)


def unique(pairs):
    out=dict(pairs)
    assert len(out)==len(pairs),"duplicate JSON keys"
    return out


def add(row,r,coefficient):
    value=row.get(r,0)+coefficient
    if value:
        row[r]=value
    else:
        row.pop(r,None)


def pullback(tape, output):
    live={output:Q(1)}
    for op,r,*a in reversed(tape):
        value=live.get(r,0)
        if not value:
            continue
        if op in ("INIT","CLEAR"):
            del live[r]
        elif op=="SCALE":
            live[r]=Q(a[0])*value
        elif op in ("ADD","COPY"):
            if op=="COPY":
                del live[r]
            add(live,a[0],Q(a[1])*value)
        else:
            assert op=="MOVE"
    return live


def contacts(tape,r,lo,hi):
    return [i for i in range(lo,hi) if tape[i][1]==r or tape[i][0] in ("ADD","COPY") and tape[i][2]==r]


def bit_span(basis):
    out={0}
    for g in basis:
        assert g not in out
        out|={x^g for x in out}
    return out


def source_conditions(word):
    t=word["program"]
    assert len(t)==76491 and word["public"]==len(word["initial"])==1501
    exact={
        36416:["MOVE",1024,3,23,False],36417:["ADD",797,1024,"-1",23],
        36418:["MOVE",1028,3,23,False],36419:["ADD",1024,1028,"1/2",23],
        36421:["MOVE",1028,23,302,False],36422:["ADD",1029,1028,"1/2",302],
    }
    for i,event in exact.items():
        if i==36422:
            assert t[i][:3]==event[:3] and t[i][-1]==302 and Q(t[i][3])
        else:
            assert t[i]==event
    assert t[36415][:3]==["ADD",1338,1028] and t[36415][-1]==3
    assert contacts(t,1028,36415,CUT+1)==[36415,36418,36419,36421,CUT]
    assert contacts(t,1024,EARLY,CUT)==[36416,36417,36419]
    assert t[36865][:3]==["ADD",797,1025] and t[38073][:3]==["ADD",774,797]
    p=set(word["live"])|{r+112 for r in word["live"]}|set(word["hosted"]["X2"])|set(word["hosted"]["Y2"])
    assert len(p)==400 and 1028 not in p
    spaces=[bit_span(frame) for frame in word["frames"]]
    assert spaces[3]<spaces[23]<spaces[302] and [len(spaces[i]) for i in (3,23,302)]==[1,2,8]
    return spaces


class FieldState:
    def __init__(self,word,probe,spaces):
        self.public=word["public"]
        self.chart=dict(enumerate(word["initial"]))
        self.values=probe.copy()
        self.owned={}
        self.guards=Counter()
        self.paid=Counter()
        self.spaces=spaces

    def apply(self,event,clock):
        op,r,*a=event
        self.guards[op]+=1
        if op=="INIT":
            assert r>=self.public and r not in self.chart and r not in self.owned and r not in self.values
            self.chart[r]=a[0]
            self.owned[r]=clock
        elif op=="CLEAR":
            assert r in self.owned and self.chart.pop(r)==a[0]
            del self.owned[r]
            self.values.pop(r,None)
        elif op=="MOVE":
            src,dst,flag=a
            assert self.chart[r]==src and flag==(r in self.owned)==(r>=self.public)
            assert self.spaces[src]<self.spaces[dst] or flag and self.spaces[dst]<self.spaces[src]
            self.chart[r]=dst
            rank=abs(len(self.spaces[src]).bit_length()-len(self.spaces[dst]).bit_length())
            self.paid[rank]+=1
        else:
            donor=r if op=="SCALE" else a[0]
            assert op in ("ADD","COPY","SCALE") and self.chart[r]==self.chart[donor]==a[-1]
            assert (donor==r)==(op=="SCALE")
            coefficient=Q(a[-2])
            assert coefficient
            if op=="SCALE":
                if r in self.values:
                    self.values[r]*=coefficient
            else:
                if op=="COPY":
                    assert r not in self.values
                add(self.values,r,coefficient*self.values.get(donor,0))

    def logical(self,r):
        return self.values.get(r,Q(0))


def difference(old,new):
    return {r:new.logical(r)-old.logical(r) for r in sorted(old.values.keys()|new.values.keys())
            if old.logical(r)!=new.logical(r)}


def compare(word,spaces,tape,probe,target,state):
    old=FieldState(word,probe,spaces)
    new=FieldState(word,probe,spaces)
    control=None
    for clock,event in enumerate(tape):
        state["clock"]=clock
        if clock==EARLY:
            assert old.values==new.values and old.chart==new.chart and old.logical(1028)==target
            new.apply(["ADD",1024,1028,"1/2",3],clock)
        if clock==CUT:
            assert old.chart==new.chart and old.owned==new.owned
            assert difference(old,new)=={797:-target/2}
            paid=Counter(new.paid)
            paid.subtract(old.paid)
            assert {r:v for r,v in paid.items() if v}=={1:-1,2:-1,3:1}
            guard_new=Counter(new.guards)
            guard_new.subtract(old.guards)
            assert {op:v for op,v in guard_new.items() if v}=={"MOVE":-1}
            control={"early_delta":difference(old,new),"native_paid_delta":{1:-1,2:-1,3:1},
                     "program_prefix_scalar_counts_equal":True}
        op,r,*args=event
        touched=(r,args[0]) if op in ("ADD","COPY") else (r,)
        if clock>=CUT and (op=="COPY" or any(r>=word["public"] for r in touched)):
            hit={r:new.logical(r)-old.logical(r) for r in touched if old.logical(r)!=new.logical(r)}
            if hit:
                assert control is not None
                # The primary is normalized to a unit e797 impulse. The actual
                # edit on this probe scales that response by -target/2.
                scale=-target/2
                return {
                    "status":"PASS_INDEPENDENT_ACTUAL_GUARD_DIVERGENCE","first_guard_clock":clock,
                    "event":event,"actual_guard_difference":hit,
                    "unit_e797_witness":{r:v/scale for r,v in hit.items()},
                    "old_guard_operands":{r:old.logical(r) for r in touched},
                    "edited_guard_operands":{r:new.logical(r) for r in touched},
                    "owned_live_before_guard":len(old.owned),"earlier_old_activity_counts":old.guards,
                    "earlier_edited_activity_counts":new.guards,"cut_control":control,
                }
        old.apply(event,clock)
        if clock in (36418,36419):
            continue
        new.apply(["MOVE",1028,3,302,False] if clock==36421 else event,clock)
        assert old.owned==new.owned
    assert control is not None and not old.owned and not new.owned
    assert old.chart==new.chart==dict(enumerate(word["final"]))
    z={r:-2*v/target for r,v in difference(old,new).items()}
    outside={r:v for r,v in z.items() if word["final"][r]!=127}
    return {"status":"PASS_INDEPENDENT_TERMINAL_OUTPUT_EXCLUSION" if outside else "INDEPENDENT_TERMINAL_OUTPUT_SUPPORT_ONLY",
            "normalized_suffix_impulse":z,"nonchart127_output":outside,"cut_control":control}


def main():
    assert __debug__ and version_info[:2]==(3,12)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root",type=Path)
    parser.add_argument("--lead",type=Path)
    parser.add_argument("--lead-sha256")
    args=parser.parse_args()
    start=perf_counter()
    state={"clock":None}

    def cap(_sig,_frame):
        emit(status="INDEPENDENT_CAP",last_entered_clock=state["clock"],cap_seconds=CAP,seconds=perf_counter()-start)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    data={p:(args.input_root/p).read_bytes() for p in PINS}
    assert {p:sha256(raw).hexdigest() for p,raw in data.items()}==PINS
    raw=decompress(data["COMPOSED-WORD.json.gz"])
    assert sha256(raw).hexdigest()==WORD
    word=loads(raw,object_pairs_hook=unique)
    cert=loads(data["COMPOSED-APPLICATION.json"],object_pairs_hook=unique)
    assert cert["status"]=="PASS_COMPOSED_7481_7542_FINAL_APPLICATION" and cert["candidate_canonical_sha256"]==WORD
    assert cert["claim_decimal"]=="0.003647969120276"
    caller=loads(data["7113-CALLER.json"],object_pairs_hook=unique)
    assert caller["stages"]==sum(e[0]=="J" for e in caller["events"])==17
    spaces=source_conditions(word)
    tape=word["program"]
    covector=pullback(tape[:EARLY],1028)
    assert covector and all(0<=r<word["public"] for r in covector)
    first=min(covector)
    probe={first:1/covector[first]}
    result=compare(word,spaces,tape,probe,Q(1),state)
    assert (args.lead is None)==(args.lead_sha256 is None)
    if args.lead is not None:
        lead_raw=args.lead.read_bytes()
        assert sha256(lead_raw).hexdigest()==args.lead_sha256
        lead=loads(lead_raw,object_pairs_hook=unique)
        if result["status"]=="PASS_INDEPENDENT_ACTUAL_GUARD_DIVERGENCE":
            assert lead["status"]=="EXCLUDED_CONSERVATIVE_GUARD"
            assert result["first_guard_clock"]==lead["clock"] and result["event"]==lead["event"]
            assert result["unit_e797_witness"]=={int(r):Q(v) for r,v in lead["coefficients"].items()}
        elif result["nonchart127_output"]:
            assert lead["status"]=="EXCLUDED_FIXED_TERMINAL_BANK_OUTPUT"
            assert result["nonchart127_output"]=={int(r):Q(v) for r,v in lead["outside"].items()}
    emit(**result,probe=probe,source1028_before_early_event=1,cut=CUT,cap_seconds=CAP,
         candidate_canonical_sha256=WORD,caller_head=CALLER,pins=PINS,
         lead_sha256=args.lead_sha256,seconds=perf_counter()-start)
    alarm(0)


if __name__=="__main__":
    main()
