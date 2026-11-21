# SPDX-License-Identifier: Apache-2.0
"""Exact rank and chronological dependence of all original ordered native MOVE legs."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip,json,runpy,sys,tarfile,tempfile,time

R354="326dcf53fa411dad88df648abe86097d52e1d3de594607e71f659ee7e1aa0be0"
R355="e500abed99a9caf5d4633ef77b119d05bace82adb5b3c9d16cf0f2e30ec031fd"
R355_CODE="97fc7367fcffaff5888a08974dfa762f609297f1144458cc59a9abfabf307ca0"


def need(flag,reason):
    if not flag: raise ValueError(reason)


def pin(p,h):
    b=p.read_bytes();need(sha256(b).hexdigest()==h,"source "+p.name);return b


def insert(basis,v,mask):
    while v:
        pivot=v.bit_length()-1
        if pivot not in basis:
            basis[pivot]=(v,mask)
            return None
        other,combo=basis[pivot];v^=other;mask^=combo
    return mask


def rank(rows):
    basis={}
    for x in rows:insert(basis,x,0)
    return len(basis)


def trace(word,charts,end,checkpoint):
    n=word["public"];tags=list(word["start"])+[None]*word["owned_fields"]
    forms=[1<<i for i in range(n)]+[0]*word["owned_fields"]
    moves=[];latest={};first_3430=None
    transmitted=None
    for i,e in enumerate(word["program"]):
        if i%512==0 and time.monotonic()>end:
            checkpoint.write_text(json.dumps({"last_clock":i-1,"moves":len(moves)})+"\n");raise TimeoutError("original tape cap")
        op,r,*args=e
        if op=="MOVE":
            a,b=args;need(tags[r]==a and r not in latest,"original owned/unique MOVE version")
            grade=charts.leg(a,b);tags[r]=b
            event={"clock":i,"owner":r,"a":a,"b":b,"grade":grade,"row":forms[r],"reads":[],"blocked":False,"end":None}
            latest[r]=event;moves.append(event)
        elif op=="ADD":
            s,c=args;need(s!=r and tags[s]==tags[r]==c,"legal original donor and destination")
            if s in latest:latest[s]["reads"].append((i,r))
            if r in latest:latest[r]["blocked"]=True
            if i==30338:
                ids=[1913,2607,2612,3226,3430];need(e==["ADD",3604,3226,585] and all(tags[j]==585 for j in ids),"five original incoming chart585 forms")
                transmitted={j:forms[j] for j in ids}
            if i>30338 and s==3430 and first_3430 is None:
                ids=[1913,2607,2612,3226];first_3430={"clock":i,"receiver":r,"chart":c,"unchanged_target":forms[s]==transmitted[s],
                                                         "four_still_live_unchanged":[j for j in ids if tags[j]==c and forms[j]==transmitted[j]]}
            forms[r]^=forms[s]
        elif op=="SWAP":
            s,=args
            for j in (r,s):
                if j in latest:latest[j]["blocked"]=True
            forms[r],forms[s]=forms[s],forms[r];tags[r],tags[s]=tags[s],tags[r]
        elif op=="INIT":
            need(tags[r] is None,"fresh owned slot")
            tags[r]=args[0];forms[r]=0
        else:
            need(op=="CLEAR" and tags[r]==args[0],"owned retirement")
            if r in latest and latest[r]["end"] is None:latest[r]["end"]=i
            tags[r]=None;forms[r]=0
    need(tags==list(word["final"])+[None]*word["owned_fields"] and not any(forms[n:]),"all original owner retirements")
    return moves,forms[:n],transmitted,first_3430


def main():
    p=ArgumentParser()
    for arg in ("peer","accept","r354-code","r355-code","r355","out"):
        p.add_argument("--"+arg,dest=arg.replace("-","_"),type=Path,required=True)
    args=p.parse_args();t0=time.monotonic()
    pin(args.r354_code,R354);old=runpy.run_path(str(args.r354_code))
    pin(args.r355_code,R355_CODE);previous=runpy.run_path(str(args.r355_code))
    prior=json.loads(pin(args.r355,R355));accepted=json.loads(pin(args.accept,old["ACCEPT"]))
    need(accepted["claim"]=="0.00389011527141" and prior["decision"]=="NO_SAME_CHART_LINEAR_DONOR_COMBINATION","baseline prices/repair exclusion")
    for k,h in old["PINS"].items():pin(args.peer/k,h)
    peer=json.loads((args.peer/"APPLICATION.json").read_bytes())
    w=json.loads(gzip.decompress((args.peer/"BINARY-CANDIDATE.json.gz").read_bytes()))
    with tarfile.open(args.peer/"APPLICATION-SOURCES.tar.gz") as a:
        blobs={k:old["pin"](a.extractfile(k).read(),h) for k,h in old["M"].items()}
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp)
        for k in list(old["M"])[:2]:(d/Path(k).name).write_bytes(blobs[k])
        sys.path.insert(0,tmp)
        import literal,price
        charts=literal.Charts(w["frames"]);need(literal.canonical(w)==peer["binary_word"]==prior["word"],"exact word")
        moves,columns,five,later=trace(w,charts,t0+30,args.out.with_suffix(".restart.json"))
        need(len(moves)==2803 and columns==literal.expected_rows(w["public"],False),"all forward public outputs and 2803 MOVEs")
        adj,ledger,_=literal.tape(w,charts,adjoint=True)
        need(adj==literal.expected_rows(w["public"],True) and ledger["paid"]==Counter(q["grade"] for q in moves),"adjoint and paid histograms")
        for j in (1913,2607,2612,3430):
            need(five[j]==int(prior["deadline_state"][str(j)]["form"],16),"R355 exact donor form")
        need(five[3226]==int(prior["target"],16) and rank(five.values())==5 and later and later["unchanged_target"],"five independent at chart 585")
        alt=previous["span"]([(j,five[j]) for j in (1913,2607,2612,3226)],five[3430],w["public"])
        need(not alt["in_span"] and alt["rank"]==4,"fixed-four alternate repair")
        groups=defaultdict(list)
        for m in moves:groups[m["a"],m["b"]].append(m)
        output=[];defects=Counter();repeat=Counter();deps=[];potential=[];nonzero_zero=0
        for key,events in sorted(groups.items()):
            basis={};sigs={};size=len(events);g=events[0]["grade"]
            for j,e in enumerate(events):
                if not e["row"]:nonzero_zero+=1
                m=e["row"]; combo=insert(basis,m,1<<j)
                if combo is not None:
                    prevs=[events[k]["clock"] for k in range(j) if combo>>k&1]
                    deps.append({"route":list(key),"victim":e["clock"],"prior_spanning_clocks":prevs})
                    # All chronologically earlier same-leg rows, each physically intact and
                    # live across all proposed reads. Full users and tails checked on one survivor.
                    if e["reads"] and not e["blocked"] and e["end"] is not None:
                        last=e["reads"][-1][0]
                        use=[a for a in events[:j] if a["end"] is not None and a["end"]>last and not a["blocked"]
                             and all(receiver!=a["owner"] for _,receiver in e["reads"])]
                        fit=previous["span"]([(i,x["row"]) for i,x in enumerate(use)],m,w["public"])
                        if fit["in_span"]:
                            ds=[use[i] for i in fit["donors"]]
                            potential.append((g,e,ds))
                if m and m in sigs:repeat[g]+=1
                sigs[m]=e
            defects[g]+=size-len(basis)
            output.append({"route":list(key),"grade":g,"moves":size,"rank":len(basis),"defect":size-len(basis),
                           "distinct_nonzero_forms":len(sigs)-(0 in sigs)})
        calls=36;k=F(accepted["claim"])
        def gross(hist):
            bill=price.moment({r:calls*n for r,n in hist.items()},k)
            return price.decimal_interval(bill,30)
        selected=None
        if potential:
            g,e,ds=sorted(potential,key=lambda x:(-x[0],x[1]["clock"]))[0]
            rew=[]
            for idx,instr in enumerate(w["program"]):
                if idx==e["clock"]:continue
                if instr[0]=="CLEAR" and instr[1]==e["owner"]:rew.append(["CLEAR",e["owner"],e["a"]]);continue
                if instr[0]=="ADD" and instr[2]==e["owner"] and idx>e["clock"]:
                    rew.extend([["ADD",instr[1],z["owner"],e["b"]] for z in ds]);continue
                rew.append(instr)
            edited=dict(w,program=rew)
            f,flog,_=literal.tape(edited,charts);b,blog,_=literal.tape(edited,charts,adjoint=True)
            need(f==columns and b==adj and flog["paid"]==blog["paid"],"changed forward, adjoint and restoration")
            caller=json.loads(gzip.decompress(blobs["source/research/paired-query-only-bit/EFREE-CALLER.json.gz"]))
            caller_events=Counter(q[0] for q in caller["events"])
            native_targets=Counter({int(k):n for k,n in peer["binary_native"]["productive"].items()})
            paid,target=literal.paired_invoice(caller,flog["paid"],native_targets,caller_events)
            old_paid=Counter({int(k):v for k,v in peer["binary_native"]["paid_all"].items()});old_paid[g]-=calls
            need(old_paid==paid,"all signed paid positions")
            ordinary=literal.ordinary(edited,caller,caller_events,paid,target)
            selected={"victim":e["clock"],"donors":[x["clock"] for x in ds],"reads":e["reads"],"grade":g,"new_ordinary":ordinary,
                      "new_word":literal.canonical(edited),"program_diff":len(rew)-len(w["program"]),"gross":gross({g:1})}
        evidence={"word":prior["word"],"peer_head":prior["head"],"r352_accept":old["ACCEPT"],"r355_receipt":R355,
                  "source_pins":old["PINS"],"member_pins":old["M"],"scope_moves":2803,"scope_clocks":len(w["program"]),
                  "physical_calls":calls,"groups":len(groups),"ordered_legs":output,"chronological_dependences":deps,
                  "defect_by_grade":dict(defects),"equal_nonzero_duplicates_by_grade":dict(repeat),"zero_forms":nonzero_zero,
                  "optimistic_shared_same_leg_36_call_gross":gross(defects),"optimistic_equal_only_gross":gross(repeat),
                  "physically_eligible_candidates":len(potential),"selected_native":selected,"five_input_rank":rank(five.values()),
                  "alternative_3430":alt,"sole_checked_later_3430_read":later,"unvisited_same_leg_arrivals":0}
        with args.out.open("x") as f:json.dump(evidence,f,indent=2,sort_keys=True);f.write("\n")
        print("PASS",len(groups),sum(defects.values()),sum(repeat.values()),len(potential),later,alt["separator_public_inputs"])


if __name__=="__main__":
    main()
