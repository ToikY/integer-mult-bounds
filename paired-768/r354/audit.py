# SPDX-License-Identifier: Apache-2.0
"""A single rank-seven crossing: one extra GF(2) column tracks downstream influence."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip,json,runpy,sys,tarfile,tempfile

ACCEPT="0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377"
SCAN="6b16cc29bbe0901772a5fe8426e613247931bb0ec7b612d84aed741c21780721"
PINS={"APPLICATION.json":"587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f",
      "APPLICATION-SOURCES.tar.gz":"d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968",
      "BINARY-CANDIDATE.json.gz":"74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"}
M={"parent/binary/independent/literal.py":"4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c",
   "parent/binary/independent/price.py":"d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b",
   "source/research/paired-query-only-bit/EFREE-CALLER.json.gz":"757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"}
CLOCK=15264;OWNER=3226


def need(ok,msg):
    if not ok: raise ValueError(msg)


def pin(b,h):
    need(sha256(b).hexdigest()==h,"source "+h);return b


def support(v):
    return [i for i in range(v.bit_length()) if v>>i&1]


def extra_column(w,charts,lib,reverse):
    n=w["public"]; rows=[1<<i for i in range(n)]+[0]*w["owned_fields"]
    tags=list(w["final" if reverse else "start"])+[None]*w["owned_fields"]
    contacts=[];before=None;after=None
    for clock in (range(len(w["program"])-1,-1,-1) if reverse else range(len(w["program"]))):
        op,r,*args=w["program"][clock]
        if not reverse and (r==OWNER or op in ("ADD","SWAP") and args[0]==OWNER):
            contacts.append([clock,op,r,*args])
        if op in ("INIT","CLEAR"):
            if (op=="INIT")!=reverse:
                need(tags[r] is None,"unused destination");tags[r]=args[0]
            else:
                need(tags[r]==args[0],"retirement");tags[r]=None
            rows[r]=0
        elif op=="ADD":
            s,c=args;need(tags[r]==tags[s]==c,"ADD chart")
            if reverse:rows[s]^=rows[r]
            else:rows[r]^=rows[s]
        elif op=="SWAP":
            s,=args;rows[r],rows[s]=rows[s],rows[r];tags[r],tags[s]=tags[s],tags[r]
        elif op=="MOVE":
            a,b=(args[::-1] if reverse else args)
            need(tags[r]==a and charts.leg(a,b)>0,"legal literal MOVE")
            if clock==CLOCK:
                need(r==OWNER and args==[0,585] and charts.leg(a,b)==7,"sole frozen cut")
                before=rows[r];need(before>>n==0,"extra bit fresh")
                rows[r]^=1<<n; after=rows[r]&((1<<n)-1)
            tags[r]=b
        else:raise ValueError(op)
    need(tags==list(w["start" if reverse else "final"])+[None]*w["owned_fields"] and not any(rows[n:]),"complete owned lifetime")
    baseline=[x&((1<<n)-1) for x in rows[:n]]
    need(before==after and baseline==lib["expected_rows"](n,reverse),"all original independent terminal columns")
    transported=sum((r>>n)<<i for i,r in enumerate(rows[:n]))
    return before,transported,contacts


def main():
    p=ArgumentParser()
    for k in ("peer","accept","scan","out"):p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args();accept=json.loads(pin(a.accept.read_bytes(),ACCEPT));scan=json.loads(pin(a.scan.read_bytes(),SCAN))
    need(accept["outcome"]=="PASS_COMPLETE_INDEPENDENT_40TH_MOMENT_ACCEPTANCE" and scan["scan"]["paid"]["7"]==1,"verified comparator and exclusive grade")
    for k,h in PINS.items():pin((a.peer/k).read_bytes(),h)
    peer=json.loads((a.peer/"APPLICATION.json").read_bytes())
    w=json.loads(gzip.decompress((a.peer/"BINARY-CANDIDATE.json.gz").read_bytes()))
    with tarfile.open(a.peer/"APPLICATION-SOURCES.tar.gz") as tar:
        src={k:pin(tar.extractfile(k).read(),h) for k,h in M.items()}
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)
        for k in list(M)[:2]:(d/Path(k).name).write_bytes(src[k])
        sys.path.insert(0,td)
        import literal,price
        lib=vars(literal);charts=literal.Charts(w["frames"])
        need(literal.canonical(w)==scan["word"]==peer["binary_word"] and w["program"][CLOCK]==["MOVE",OWNER,0,585],"immutable word and cut")
        caller=json.loads(gzip.decompress(src[list(M)[2]]));calls=Counter(e[0] for e in caller["events"])["LOCAL"]
        need(calls==36 and peer["binary_native"]["paid"]["7"]==1,"actual paired multiplicity")
        T={int(k):n for k,n in peer["binary_native"]["productive_all"].items()}
        P={int(k):n for k,n in peer["binary_native"]["paid_all"].items()}
        S=price.signed_profile(T,P); R=S.copy();R[7]+=calls
        raw_lo,raw_hi=map(Q,peer["binary_raw"]);rat_hi=Q(peer["rational_raw"][1]);k=Q(accept["claim"])
        need(price.moment(S,raw_lo)[0]>0>price.moment(S,raw_hi)[1],"original exact raw comparison")
        spare=price.moment(R,rat_hi);gross=price.scale(price.price(7,k),calls)
        need(spare[0]>0 and 0<gross[0]<gross[1]<252*price.GRID and rat_hi>k,"ideal complete ceiling and exact gross interval")
        f,b_from_mark,touches=extra_column(w,charts,lib,False);b,f_from_mark,_=extra_column(w,charts,lib,True)
        need(f==f_from_mark and b==b_from_mark and touches[0][1]=="INIT" and touches[-1][1]=="CLEAR","cross-checked direct and transposed cut form")
        need(w["program"][CLOCK-1]!=w["program"][CLOCK] and charts.rank[585]!=charts.rank[0],"wrong-clock and chart controls")
        # The extra column is an independently varied perturbation at this one cut.
        # Setting its coefficient to the original form models an erased transport.
        sf,sb=support(f),support(b)
        prior=max(t for t in touches if t[0]<CLOCK); follow=min(t for t in touches if t[0]>CLOCK)
        result={"pins":dict(sorted(PINS.items())),"archive_pins":dict(sorted(M.items())),"prior_scan":SCAN,"comparator_accept":ACCEPT,
                 "head":accept["peer_head"],"word":peer["binary_word"],"frozen":{"clock":CLOCK,"owner":OWNER,"old_chart":0,"new_chart":585,"grade":7},
                 "owner_touches":touches,"previous_touch":prior,"next_touch":follow,"forward_input_indices":sf,"adjoint_output_indices":sb,
                 "forward_hex":hex(f),"adjoint_hex":hex(b),"all_public_columns_each_direction":w["public"],"lifetime_count":sum(t[1]=="INIT" for t in touches),
                 "cross_perturbations_verified":True,"minimum_changed_entry":[sb[0],sf[0]] if sf and sb else None,
                 "affected_matrix_entries":len(sf)*len(sb),"raw_gross_no_repair_interval":price.decimal_interval(gross,30),
                 "ideal_native_margin_at_rational_upper":price.decimal_interval(spare,30),"optimistic_net_complete_upper":str(rat_hi),
                 "calls":calls,"tested_sites":1,"other_moves_unvisited":2802,
                 "decision":"BOTH_ZERO_CRITERION_EXCLUDED" if sf or sb else "REQUIRE_FULL_ZERO_CHART_REPLACEMENT"}
        with a.out.open("x") as handle:json.dump(result,handle,indent=2,sort_keys=True);handle.write("\n")
        print(result["decision"],len(sf),len(sb),result["minimum_changed_entry"])


if __name__=="__main__":
    main()
