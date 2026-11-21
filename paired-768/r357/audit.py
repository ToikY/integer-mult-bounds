# SPDX-License-Identifier: Apache-2.0
"""Exact recipient-output demands at each native MOVE, in reverse chronology."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,runpy,sys,tarfile,tempfile

SOURCE="c6585b2bf3ea1563f0bb25058a296774cb9206e6ae86bfdfbb7385e57a80d64b"
FORWARD="245c57639941873096fd13f2962a7a239eed23cc3e60317ffe8b09d6beb0abf3"
SOURCE354="326dcf53fa411dad88df648abe86097d52e1d3de594607e71f659ee7e1aa0be0"


def need(ok,txt):
    if not ok: raise ValueError(txt)


def locked(path,pin):
    raw=path.read_bytes();need(sha256(raw).hexdigest()==pin,"source "+path.name);return raw


def reverse(w,charts,deadline,out):
    n=w["public"];N=n+w["owned_fields"]
    rows=[1<<j for j in range(n)]+[0]*w["owned_fields"]
    tags=list(w["final"])+[None]*w["owned_fields"]
    result=[]
    for i in range(len(w["program"])-1,-1,-1):
        if i%512==0 and monotonic()>deadline:
            out.write_text(json.dumps({"next_reverse_clock":i,"moves_read":len(result)})+"\n");raise TimeoutError("reverse tape")
        op,r,*args=w["program"][i]
        if op=="CLEAR":
            need(tags[r] is None,"transpose lifetime opens");tags[r]=args[0];rows[r]=0
        elif op=="INIT":
            need(tags[r]==args[0],"transpose retirement");tags[r]=None;rows[r]=0
        elif op=="ADD":
            s,c=args;need(s!=r and tags[s]==tags[r]==c,"transpose chart");rows[s]^=rows[r]
        elif op=="SWAP":
            s,=args;need(tags[s] is not None and tags[r] is not None,"transpose live swap")
            rows[s],rows[r]=rows[r],rows[s];tags[s],tags[r]=tags[r],tags[s]
        else:
            a,b=args;need(op=="MOVE" and tags[r]==b,"post-MOVE chart before adjoint")
            result.append((i,r,a,b,charts.leg(b,a),rows[r]));tags[r]=a
    need(tags==list(w["start"])+[None]*(N-n) and not any(rows[n:]),"all transposed private lifetimes")
    return result,rows[:n]


def main():
    p=ArgumentParser()
    for arg in ("peer","accept","r354-code","r356-code","forward","out"):
        p.add_argument("--"+arg,dest=arg.replace("-","_"),type=Path,required=True)
    args=p.parse_args();start=monotonic()
    locked(args.r356_code,SOURCE);lib=runpy.run_path(str(args.r356_code))
    locked(args.r354_code,SOURCE354);old=runpy.run_path(str(args.r354_code))
    census=json.loads(locked(args.forward,FORWARD));prior=json.loads(locked(args.accept,old["ACCEPT"]))
    need(prior["claim"]=="0.00389011527141" and census["groups"]==2354 and not sum(census["defect_by_grade"].values()),"accepted frontier and forward R356")
    for name,h in old["PINS"].items():locked(args.peer/name,h)
    w=json.loads(gzip.decompress((args.peer/"BINARY-CANDIDATE.json.gz").read_bytes()));peer=json.loads((args.peer/"APPLICATION.json").read_bytes())
    with tarfile.open(args.peer/"APPLICATION-SOURCES.tar.gz") as tar:
        src={k:old["pin"](tar.extractfile(k).read(),h) for k,h in old["M"].items()}
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp)
        for k in list(old["M"])[:2]:(d/Path(k).name).write_bytes(src[k])
        sys.path.insert(0,tmp)
        import literal,price
        need(literal.canonical(w)==census["word"]==peer["binary_word"],"exact signed word")
        charts=literal.Charts(w["frames"])
        demand,adj=reverse(w,charts,start+30,args.out.with_suffix(".restart.json"))
        need(adj==literal.expected_rows(w["public"],True) and len(demand)==2803,"all output covectors and frozen scope")
        forwards,ordinary,_,_=lib["trace"](w,charts,start+30,args.out.with_suffix(".restart.json"))
        need(ordinary==literal.expected_rows(w["public"],False),"all public forward endpoints")
        by_clock={e["clock"]:e for e in forwards};groups=defaultdict(list)
        tape_digest=sha256()
        for i,r,a,b,g,row in demand:
            e=by_clock[i];need((r,a,b,g)==(e["owner"],e["a"],e["b"],e["grade"]),"paired physical clock/owner")
            tape_digest.update(f"{i} {r} {a} {b} {row:x}\n".encode())
            groups[a,b].append((i,row))
        by_route={tuple(e["route"]):e for e in census["ordered_legs"]}
        need(groups.keys()==by_route.keys(),"same ordered forward legs")
        profile=Counter();duplicate=Counter();zero=0;rows=[];dependencies=[];legal=[]
        for route,events in sorted(groups.items()):
            fwd=by_route[route];g=fwd["grade"]
            need(len(events)==fwd["rank"]==fwd["moves"]==lib["rank"]([by_clock[i]["row"] for i,_ in events]),"reconstructed forward independence")
            basis={};seen=set()
            for j,(i,row) in enumerate(events):
                zero+=not row
                if row and row in seen:duplicate[g]+=1
                seen.add(row)
                dep=lib["insert"](basis,row,1<<j)
                if dep is None:continue
                spans=[events[k][0] for k in range(j) if dep>>k&1]
                got=0
                for si,form in events[:j]:
                    if si in spans:got^=form
                need(got==row,"complete downstream dependence")
                e=by_clock[i]
                # After removal, this original owner retains the exact incoming chart/form.
                # Its later donor ADDs can be redirected or dropped; destructive touches
                # must not invalidate the retained form before compensation.
                avail=(not e["blocked"] and e["end"] is not None and all(i<x<e["end"] for x in spans))
                dependencies.append({"victim":i,"route":list(route),"downstream_hex":hex(row),"compensating_moves":spans,"source_owner_survives":avail})
                if avail:legal.append((g,i,spans))
            n=len(events);profile[g]+=n-len(basis)
            rows.append({"route":list(route),"grade":g,"count":n,"rank":len(basis),"defect":n-len(basis)})
        def gross(hist):
            return price.decimal_interval(price.moment({g:36*n for g,n in hist.items()},F(prior["claim"])),30)
        selected=None
        if legal:
            g,i,spans=sorted(legal,key=lambda x:(-x[0],x[1]))[0];victim=by_clock[i];owner=victim["owner"];a=victim["a"]
            edits=[]
            for j,e in enumerate(w["program"]):
                if j==i:continue
                if j in spans:
                    target=by_clock[j]["owner"];need(target!=owner and by_clock[j]["a"]==a,"compensation donor and frame")
                    edits.append(["ADD",target,owner,a])
                if j>i and e[0]=="ADD" and e[2]==owner:continue
                if j==victim["end"]:edits.append(["CLEAR",owner,a])
                else:edits.append(e)
            word=dict(w,program=edits)
            f,flog,_=literal.tape(word,charts);b,blog,_=literal.tape(word,charts,adjoint=True)
            works=f==ordinary and b==adj and flog["paid"]==blog["paid"]
            selected={"victim":i,"compensating_moves":spans,"native_action_pass":works,"program_delta":len(edits)-len(w["program"])}
            if works:
                caller=json.loads(gzip.decompress(src["source/research/paired-query-only-bit/EFREE-CALLER.json.gz"]))
                ev=Counter(x[0] for x in caller["events"]);native_targets=Counter({int(k):v for k,v in peer["binary_native"]["productive"].items()})
                paid,T=literal.paired_invoice(caller,flog["paid"],native_targets,ev)
                original=Counter({int(k):v for k,v in peer["binary_native"]["paid_all"].items()});original[g]-=36
                need(original==paid,"complete paid changes")
                selected.update(ordinary=literal.ordinary(word,caller,ev,paid,T),gross=gross({g:1}),word=literal.canonical(word))
        out={"head":census["peer_head"],"word":census["word"],"price_comparator":prior["claim"],"forward_census":FORWARD,
             "source_pins":old["PINS"],"archive_pins":old["M"],"r352_accept":old["ACCEPT"],"r354_checker":SOURCE354,"r356_checker":SOURCE,
             "demand_stream_sha256":tape_digest.hexdigest(),"moves":len(demand),"clocks":len(w["program"]),"groups":len(groups),
             "ordered_legs":rows,"total_defect":sum(profile.values()),"by_grade":dict(sorted(profile.items())),"zero_demands":zero,
             "nonzero_equal_demands_by_grade":dict(sorted(duplicate.items())),"chronological_dependence_witnesses":dependencies,
             "available_compensating_paths":len(legal),"optimistic_36_call_all_defects":gross(profile),"selected":selected,
             "unvisited_original_moves":0,"forward_columns":w["public"],"adjoint_columns":w["public"]}
        with args.out.open("x") as f:json.dump(out,f,sort_keys=True,indent=2);f.write("\n")
        print("COMPLETE",len(demand),len(groups),sum(profile.values()),sum(duplicate.values()),zero,len(legal),selected and selected["native_action_pass"])


if __name__=="__main__":
    main()
