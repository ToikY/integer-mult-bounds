# SPDX-License-Identifier: Apache-2.0
"""One access-ordered scan of the literal paired binary MOVE stream."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,runpy,tarfile,tempfile

HEAD="fb9b6a7b0d27da1cf98430893a3016bf811e2aa4"
WORD="b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69"
PINS={"BINARY-CANDIDATE.json.gz":"74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326",
      "APPLICATION.json":"587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f",
      "APPLICATION-SOURCES.tar.gz":"d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968"}
MEMBERS={"parent/binary/independent/literal.py":"4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c",
         "source/research/paired-query-only-bit/EFREE-CALLER.json.gz":"757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
         "recipient/binary/finite.py":"c780cea060f4a9efef064b239636162a7e8e84e40369abc1a1c4679dfbeb3041"}
ACCEPT="0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377"


def ck(test,reason):
    if not test: raise ValueError(reason)


def lock(raw,pin):
    ck(sha256(raw).hexdigest()==pin,"source "+pin)
    return raw


def accesses(word,charts,deadline=float("inf"),checkpoint=None):
    last={};previous={};versions=Counter();moves=Counter();before=Counter();interrupted=Counter()
    pairs=[];hist=Counter();named=Counter();opcounts=Counter()
    tags=list(word["start"])+[None]*word["owned_fields"]
    for i,row in enumerate(word["program"]):
        if i%512==0 and monotonic()>deadline:
            if checkpoint: checkpoint({"last_completed_clock":i-1,"last_access":last,"previous_moves":previous,"observed_moves":sum(moves.values())})
            raise TimeoutError("original program scan")
        op,r,*args=row; opcounts[op]+=1
        if op=="MOVE":
            a,b=args
            ck(r>=word["public"] and tags[r]==a,"owned MOVE chronology")
            hist[charts.leg(a,b)]+=1; named[str((a,b))]+=1
            before[last[r][0]]+=1
            if r in previous:
                j,A,B,ver=previous[r]
                if last[r][0]=="MOVE":
                    ck(last[r][1]==j and B==a and ver==versions[r],"same owner, chart, lifetime")
                    if A==b:
                        leg=0;typ="same literal chart"
                    else:
                        try: leg=charts.leg(A,b);typ="nested"
                        except ValueError: leg=None;typ="nonnested or equal-dimensional distinct"
                    pairs.append({"owner":r,"lifetime":ver,"first_clock":j,"second_clock":i,"charts":[A,B,b],
                                  "old_legs":[charts.leg(A,B),charts.leg(B,b)],"new_leg":leg,"class":typ})
                else:
                    interrupted[last[r][0]]+=1
            previous[r]=(i,a,b,versions[r]);moves[r]+=1;tags[r]=b
        elif op=="INIT":
            ck(tags[r] is None,"fresh lifetime");versions[r]+=1;tags[r]=args[0]
        elif op=="CLEAR":
            ck(tags[r]==args[0],"retired chart");tags[r]=None
        elif op=="ADD":
            s,c=args;ck(tags[s]==tags[r]==c,"two charted operands")
            last[s]=("ADD_source",i); last[r]=("ADD_destination",i);continue
        elif op=="SWAP":
            s,=args;ck(tags[r] is not None and tags[s] is not None,"owned swap")
            tags[r],tags[s]=tags[s],tags[r];last[s]=(op,i)
        else: raise ValueError(op)
        last[r]=(op,i)
    ck(tags==word["final"]+[None]*word["owned_fields"],"final chart and all owners restored")
    return dict(clocks=len(word["program"]),last_clock=len(word["program"])-1,ops=dict(sorted(opcounts.items())),
                moves=sum(moves.values()),owned_move_registers=len(moves),move_counts_per_register=dict(sorted(Counter(moves.values()).items())),
                moves_by_immediate_preceding_access=dict(sorted(before.items())), repeated_owner_last_access_blockers=dict(sorted(interrupted.items())),
                unobstructed_pairs=pairs, paid=dict(sorted(hist.items())))


def controls(literal):
    rows=[[int(i==j) for j in range(8)] for i in range(8)]
    frame=lambda ids:{"dim":len(ids),"B":[rows[i] for i in ids],"A":[rows[i] for i in range(8) if i not in ids]}
    C=literal["Charts"]({"1":frame([0]),"2":frame([0,1]),"3":frame([0,1,2]),"4":frame([1])})
    def toy(end=3,mid=None):
        pr=[["INIT",3,1],["ADD",3,0,1],["MOVE",3,1,2],*(mid or []),["MOVE",3,2,end],["ADD",1,3,end],["CLEAR",3,end]]
        return {"public":3,"owned_fields":1,"start":[1,end,2],"final":[1,end,2],"program":pr}
    for end in (3,1):
        w=toy(end);good=accesses(w,C)["unobstructed_pairs"]
        ck(len(good)==1 and good[0]["new_leg"]== (2 if end==3 else 0),"legal nested and exact identity controls")
        direct=dict(w,program=w["program"][:2]+([["MOVE",3,1,end]] if end!=1 else [])+w["program"][4:])
        for adjoint in (False,True):
            x,_,_=literal["tape"](w,C,adjoint=adjoint)
            y,_,_=literal["tape"](direct,C,adjoint=adjoint)
            ck(x==y,"all synthetic columns and adjoint")
    ck(accesses(toy(4),C)["unobstructed_pairs"][0]["new_leg"] is None,"distinct nonnested endpoint")
    for e in (["ADD",2,3,2],["ADD",3,2,2],["SWAP",2,3]):
        ck(not accesses(toy(mid=[e]),C)["unobstructed_pairs"],"intervening observation or mutation")
    ck(not accesses(toy(mid=[["CLEAR",3,2],["INIT",3,2]]),C)["unobstructed_pairs"],"retired lifetime")
    return ["nested_forward_adjoint","equal_endpoint_roundtrip_forward_adjoint","distinct_equal_dimension","ADD_both_operands","SWAP_both_operands","retire_and_reinitialize"]


def main():
    p=ArgumentParser()
    p.add_argument("--peer",required=True,type=Path);p.add_argument("--accept",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    a=p.parse_args(); start=monotonic()
    accepted=json.loads(lock(a.accept.read_bytes(),ACCEPT))
    ck(accepted["peer_head"]==HEAD and accepted["claim"]=="0.00389011527141","frozen signed frontier")
    for k,v in PINS.items():lock((a.peer/k).read_bytes(),v)
    native=json.loads((a.peer/"APPLICATION.json").read_bytes())
    word=json.loads(gzip.decompress((a.peer/"BINARY-CANDIDATE.json.gz").read_bytes()))
    with tarfile.open(a.peer/"APPLICATION-SOURCES.tar.gz") as t:
        blobs={k:lock(t.extractfile(k).read(),v) for k,v in MEMBERS.items()}
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"literal.py";path.write_bytes(blobs["parent/binary/independent/literal.py"]);lit=runpy.run_path(str(path))
    ck(lit["canonical"](word)==native["binary_word"]==WORD,"canonical word")
    caller=json.loads(gzip.decompress(blobs["source/research/paired-query-only-bit/EFREE-CALLER.json.gz"]))
    events=Counter(r[0] for r in caller["events"]);ck(events["LOCAL"]==native["binary_native"]["calls"]==36,"signed 36-call word")
    ctl=controls(lit);charts=lit["Charts"](word["frames"])
    scan=accesses(word,charts,start+30,lambda d:a.out.with_suffix(".restart.json").write_text(json.dumps(d)))
    ck(scan["ops"]==native["binary_native"]["instructions"] and scan["clocks"]==39600 and scan["moves"]==2803,"complete exact scope")
    ck({int(k):v for k,v in native["binary_native"]["paid"].items()}==scan["paid"],"paid scan matches independently signed source")
    # Outside the discovery scan, replay both original directions as controls.
    for adj in (False,True):
        values,log,_=lit["tape"](word,charts,adjoint=adj)
        ck(values==lit["expected_rows"](word["public"],adj) and log["paid"]==scan["paid"],"native forward and adjoint")
    T=Counter({int(k):v for k,v in native["binary_native"]["productive"].items()})
    P=Counter(scan["paid"]);paid,targets=lit["paired_invoice"](caller,P,T,events)
    ordinary=lit["ordinary"](word,caller,events,paid,targets)
    ck(ordinary==native["binary_native"]["ordinary"],"full 36-call ordinary invoice")
    result={"peer_head":HEAD,"word":WORD,"accept":ACCEPT,"pins":PINS,"archive_members":MEMBERS,"controls":ctl,"scan":scan,
            "signed_calls":36,"ordinary":ordinary,"adjoint_public_columns":word["public"],"forward_public_columns":word["public"]}
    eligible=[q for q in scan["unobstructed_pairs"] if q["new_leg"] is not None]
    if not eligible:
        result.update(decision="FAMILY_EXHAUSTED",unvisited_pairs=0,fully_charged_net_saving="0",optimistic_disjoint_total="0")
    else:
        result.update(decision="DIRECT_ROUTES_REQUIRE_REPRICE_AND_PHASE_PROOF",eligible=eligible,
                      unvisited_pairs=0)
    with a.out.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print(result["decision"],scan["moves"],len(scan["unobstructed_pairs"]),len(eligible),scan["owned_move_registers"])


if __name__=="__main__":
    main()
