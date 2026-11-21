# SPDX-License-Identifier: Apache-2.0
"""One complete live chart donor span after a single paid transfer knockout."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip,json,runpy,sys,tarfile,tempfile

SOURCE="326dcf53fa411dad88df648abe86097d52e1d3de594607e71f659ee7e1aa0be0"
PREVIOUS="1c82c88222277886117a5c2a5e23220abd5d69f7967b54256fc64ecc025f5015"
CUT,READ,DELETED,RECEIVER,CHART=15264,30338,3226,3604,585


def need(flag,text):
    if not flag: raise ValueError(text)


def snapshot(w,charts,target):
    n=w["public"]; rows=[1<<i for i in range(n)]+[0]*w["owned_fields"]
    tags=list(w["start"])+[None]*w["owned_fields"]
    generation=[0]*len(tags);birth=[-1]*len(tags);last=[-1]*len(tags)
    available=None
    for i,e in enumerate(w["program"]):
        op,r,*args=e
        if i==READ:
            need(e==["ADD",RECEIVER,DELETED,CHART] and tags[RECEIVER]==tags[DELETED]==CHART and rows[DELETED]==0,"named zero donor/receiver deadline")
            available={j:{"form":rows[j],"generation":generation[j],"birth":birth[j],"last":last[j]} for j in range(len(tags)) if tags[j]==CHART}
        if i==CUT:
            need(e==["MOVE",DELETED,0,CHART] and tags[r]==0 and rows[r]==target and charts.leg(0,CHART)==7,"original independent sender form")
            rows[r]=0;tags[r]=CHART;birth[r]=i;generation[r]+=1
        elif op=="INIT":
            need(tags[r] is None,"clean owner slot");generation[r]+=1;birth[r]=i;tags[r]=args[0];rows[r]=0
        elif op=="CLEAR":
            need(tags[r]==args[0],"owned retirement");tags[r]=None;rows[r]=0
        elif op=="MOVE":
            old,new=args;need(tags[r]==old and charts.leg(old,new)>0,"chart transfer")
            tags[r]=new
        elif op=="ADD":
            s,c=args;need(s!=r and tags[s]==tags[r]==c,"live donors")
            rows[r]^=rows[s];last[s]=i
        elif op=="SWAP":
            s,=args;need(tags[r] is not None and tags[s] is not None,"live swaps")
            rows[r],rows[s]=rows[s],rows[r];tags[r],tags[s]=tags[s],tags[r];last[s]=i
        else:raise ValueError(op)
        last[r]=i
    need(available is not None and tags==list(w["final"])+[None]*w["owned_fields"] and not any(rows[n:]),"all knockout lifetimes closed")
    return available,rows[:n]


def span(rows,target,cols):
    piv={};representatives={}
    for j,form in rows:
        mask=1<<j
        while form:
            pivot=form.bit_length()-1
            if pivot not in piv:
                piv[pivot]=form;representatives[pivot]=mask;break
            form^=piv[pivot];mask^=representatives[pivot]
    form=target;mask=0
    while form:
        pivot=form.bit_length()-1
        if pivot not in piv:break
        form^=piv[pivot];mask^=representatives[pivot]
    if not form:
        chosen=[j for j,_ in rows if mask>>j&1]
        got=0
        for j,row in rows:
            if j in chosen:got^=row
        need(got==target,"concrete donor witness")
        return {"rank":len(piv),"in_span":True,"donors":chosen}
    # Solve dot(pivot rows,z)=0, dot(target,z)=1 over public inputs, with
    # unconstrained coordinates zero except the leading residual coordinate.
    free=form.bit_length()-1; z=1<<free
    for j,row in sorted(piv.items()):
        need(not (z>>j&1),"pivot disjoint from free coordinate")
        if (row&z).bit_count()&1:z|=1<<j
    need((target&z).bit_count()%2==1 and all((r&z).bit_count()%2==0 for _,r in rows),"dual separator verifies all donors")
    return {"rank":len(piv),"in_span":False,"separator_hex":hex(z),"separator_public_inputs":[i for i in range(cols) if z>>i&1]}


def main():
    ap=ArgumentParser()
    for name in ("peer","accept","previous","source","out"):ap.add_argument("--"+name,type=Path,required=True)
    a=ap.parse_args()
    need(sha256(a.source.read_bytes()).hexdigest()==SOURCE,"immutable R354 helper")
    old=runpy.run_path(str(a.source));pin=old["pin"]
    prior=json.loads(pin(a.previous.read_bytes(),PREVIOUS));accepted=json.loads(pin(a.accept.read_bytes(),old["ACCEPT"]))
    need(accepted["claim"]=="0.00389011527141" and prior["minimum_changed_entry"]==[171,4] and prior["adjoint_output_indices"]==[171],"accepted comparator and prior site")
    for name,h in old["PINS"].items():pin((a.peer/name).read_bytes(),h)
    w=json.loads(gzip.decompress((a.peer/"BINARY-CANDIDATE.json.gz").read_bytes())); peer=json.loads((a.peer/"APPLICATION.json").read_bytes())
    with tarfile.open(a.peer/"APPLICATION-SOURCES.tar.gz") as t:
        src={k:pin(t.extractfile(k).read(),h) for k,h in old["M"].items()}
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);path=d/"literal.py";path.write_bytes(src["parent/binary/independent/literal.py"]);literal=runpy.run_path(str(path))
    n=w["public"];need(literal["canonical"](w)==peer["binary_word"]==prior["word"],"unchanged native")
    Fwd=int(prior["forward_hex"],16);charts=literal["Charts"](w["frames"]); avail,terminal=snapshot(w,charts,Fwd)
    orig=literal["expected_rows"](n,False);oldout=orig.copy();oldout[171]^=Fwd
    need(terminal==oldout,"knockout forward damage")
    cut_ops=[["CLEAR",DELETED,0],["INIT",DELETED,CHART]]
    reset=dict(w,program=w["program"][:CUT]+cut_ops+w["program"][CUT+1:])
    rev,_,_=literal["tape"](reset,charts,adjoint=True)
    u=literal["expected_rows"](n,True)
    for j in prior["forward_input_indices"]:u[j]^=1<<171
    need(rev==u,"knockout adjoint and completion")
    legal=[(j,x["form"]) for j,x in avail.items() if j not in (DELETED,RECEIVER)]
    exact=span(legal,Fwd,n);relaxed=span([*legal,(RECEIVER,avail[RECEIVER]["form"])],Fwd,n)
    result={"word":prior["word"],"head":prior["head"],"source_pins":old["PINS"],"archive_pins":old["M"],"prior_check":SOURCE,"prior_site":PREVIOUS,"comparator_accept":old["ACCEPT"],
            "cut":CUT,"read":READ,"chart":CHART,"deleted":DELETED,"receiver":RECEIVER,"target":hex(Fwd),
            "target_weight":Fwd.bit_count(),"knockout_adjoint_outputs":[171],"all_other_forward_and_adjoint_endpoints_preserved":True,
            "live_at_chart":len(avail),"legal_other_banks":len(legal),"nonzero_legal_rows":sum(bool(x) for _,x in legal),
            "exact":exact,"relaxed_includes_receiver":relaxed,"deadline_state":{str(j):dict(x,form=hex(x["form"])) for j,x in avail.items()},
            "tested_receivers":1,"unvisited_paid_cuts":2802}
    if exact["in_span"]:
        donors=exact["donors"]
        splice=dict(w,program=w["program"][:CUT]+cut_ops+w["program"][CUT+1:READ]+[["ADD",RECEIVER,j,CHART] for j in donors]+w["program"][READ+1:])
        f,flog,_=literal["tape"](splice,charts);bt,blog,_=literal["tape"](splice,charts,adjoint=True)
        need(f==orig and bt==literal["expected_rows"](n,True) and flog["paid"]==blog["paid"],"all arbitrary public returns and adjoint")
        caller=json.loads(gzip.decompress(src["source/research/paired-query-only-bit/EFREE-CALLER.json.gz"]))
        events=Counter(e[0] for e in caller["events"])
        T=Counter({int(k):v for k,v in peer["binary_native"]["productive"].items()})
        paid,targets=literal["paired_invoice"](caller,flog["paid"],T,events)
        oldP=Counter({int(k):v for k,v in peer["binary_native"]["paid_all"].items()});oldP[7]-=36
        need(paid==oldP,"36 removed rank seven charges")
        ordinary=literal["ordinary"](splice,caller,events,paid,targets)
        result.update(decision="LITERAL_SPLICE_NATIVE_REPLAYED_PENDING_FINITE_AND_SIGNED",ordinary=ordinary,
                      native_program_delta=len(splice["program"])-len(w["program"]),candidate_word=literal["canonical"](splice))
    else:
        result.update(decision="NO_SAME_CHART_LINEAR_DONOR_COMBINATION",built=0)
    with a.out.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print(result["decision"],len(avail),len(legal),exact,relaxed)


if __name__=="__main__":
    main()
