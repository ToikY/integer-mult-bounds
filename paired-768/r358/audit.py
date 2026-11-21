# SPDX-License-Identifier: Apache-2.0
"""Preserve all old outputs after adding one independent binary input at two departures."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from time import monotonic
import gzip,json,runpy,sys,tarfile,tempfile

C357="5e172d879ac6438ecfce1152c543fdd025c3f99cb369d0ee21655118cc8d61b0"
R357="ee8e207c2352db335abf746293353aa36039613b589c0042513b6e6fbe0ff599"
C354="326dcf53fa411dad88df648abe86097d52e1d3de594607e71f659ee7e1aa0be0"


def need(ok,why):
    if not ok: raise ValueError(why)


def verified(p,expected):
    raw=p.read_bytes();need(sha256(raw).hexdigest()==expected,"source "+p.name);return raw


def candidate(w,ch,lit,pair,deadline):
    n=w["public"];N=n+w["owned_fields"]
    source=pair[0][2];starts={q[0] for q in pair}
    # Every old x row with the appended coefficient on z, after two online injections.
    forms=[1<<j for j in range(n)]+[0]*w["owned_fields"];tags=list(w["start"])+[None]*w["owned_fields"]
    captures=defaultdict(list);known=defaultdict(set)
    def observe(reg,clk):
        c=tags[reg];y=forms[reg]
        if c is None or c==source or ch.rank[c]<=ch.rank[source] or not y or y in known[c]:return
        try:g=ch.leg(source,c)
        except ValueError:return
        known[c].add(y);captures[c].append((clk,reg,y))
    for r in range(n):observe(r,-1)
    for i,e in enumerate(w["program"]):
        if i%512==0 and monotonic()>deadline:return {"status":"CAPPED","next_clock":i}
        op,r,*a=e
        if op=="INIT":tags[r]=a[0];forms[r]=0
        elif op=="CLEAR":tags[r]=None;forms[r]=0
        elif op=="ADD":forms[r]^=forms[a[0]]
        elif op=="SWAP":
            s=a[0];tags[r],tags[s]=tags[s],tags[r];forms[r],forms[s]=forms[s],forms[r];observe(s,i)
        else:
            if i in starts:forms[r]^=1<<n
            tags[r]=a[1]
        observe(r,i)
    need(forms[:n]==lit.expected_rows(n,False),"both injections cancel on every original output")
    order=sorted(captures,key=lambda c:(-(ch.rank[c]-ch.rank[source]),c))
    cut=None
    for c in order:
        if monotonic()>deadline:return {"status":"CAPPED_DECODER","next_chart":c}
        stages=captures[c];basis={}
        for j,(_,_,v) in enumerate(stages):
            combo=1<<j
            while v:
                k=v.bit_length()-1
                if k not in basis:basis[k]=(v,combo);break
                row,mask=basis[k];v^=row;combo^=mask
        z=1<<n;combo=0
        while z:
            k=z.bit_length()-1
            if k not in basis:break
            row,mask=basis[k];z^=row;combo^=mask
        if not z:
            cut=(c,[(i,r) for j,(i,r,v) in enumerate(stages) if combo>>j&1]);break
    if cut is None:return {"status":"NO_EXACT_COCHART_READOUT","charts":order,"nonzero_chart_forms":sum(map(len,captures.values()))}
    c,witness=cut
    newid=n;scratch=N+1
    def remap(r):return r if r<n else r+1
    additions=defaultdict(list)
    for i,r in witness:additions[i].append(["ADD",scratch,remap(r),c])
    seq=[["INIT",scratch,c]]+additions[-1]
    for i,e in enumerate(w["program"]):
        op,r,*args=e;x=remap(r)
        if i in starts:seq.append(["ADD",x,newid,source])
        if op in ("ADD","SWAP"):args=[remap(args[0]),*args[1:]]
        seq.append([op,x,*args]);seq.extend(additions[i])
    seq.extend([["SWAP",newid,scratch],["CLEAR",scratch,source]])
    word=dict(w,public=n+1,owned_fields=w["owned_fields"]+1,start=w["start"]+[source],final=w["final"]+[c],program=seq)
    f,flog,_=lit.tape(word,ch);b,blog,_=lit.tape(word,ch,adjoint=True)
    need(f==lit.expected_rows(n+1,False) and b==lit.expected_rows(n+1,True) and flog["paid"]==blog["paid"],"new independent productive return, all old values and owned retirement")
    return {"status":"NATIVE_FORWARD_ADJOINT_PASS","source":source,"destination":c,"grade":ch.leg(source,c),"readouts":witness,
            "candidate_word":lit.canonical(word),"program_delta":len(seq)-len(w["program"]),"word":word,"paid":flog["paid"]}


def main():
    p=ArgumentParser()
    for key in ("peer","r354-code","r357-code","r357","accept","out"):
        p.add_argument("--"+key,dest=key.replace("-","_"),type=Path,required=True)
    a=p.parse_args();t0=monotonic();end=t0+30
    verified(a.r354_code,C354);old=runpy.run_path(str(a.r354_code))
    verified(a.r357_code,C357);last=runpy.run_path(str(a.r357_code))
    prior=json.loads(verified(a.r357,R357));accept=json.loads(verified(a.accept,old["ACCEPT"]))
    need(prior["total_defect"]==0 and accept["claim"]=="0.00389011527141","R357 and R352 controls")
    for k,h in old["PINS"].items():verified(a.peer/k,h)
    with tarfile.open(a.peer/"APPLICATION-SOURCES.tar.gz") as a_src:
        blobs={k:old["pin"](a_src.extractfile(k).read(),h) for k,h in old["M"].items()}
    w=json.loads(gzip.decompress((a.peer/"BINARY-CANDIDATE.json.gz").read_bytes()));peer=json.loads((a.peer/"APPLICATION.json").read_bytes())
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)
        for k in list(old["M"])[:2]:(tmp/Path(k).name).write_bytes(blobs[k])
        sys.path.insert(0,td)
        import literal,price
        charts=literal.Charts(w["frames"]);need(literal.canonical(w)==prior["word"]==peer["binary_word"],"peer literal")
        demands,reverse=last["reverse"](w,charts,end,a.out.with_suffix(".restart.json"))
        need(reverse==literal.expected_rows(w["public"],True),"all 630 public outputs")
        buckets=defaultdict(list);sig=sha256()
        for i,r,A,B,g,v in demands:
            sig.update(f"{i} {r} {A} {B} {v:x}\n".encode());buckets[A,v].append((i,r,A,B,g,v))
        need(sig.hexdigest()==prior["demand_stream_sha256"] and all(v for A,v in buckets),"all 2803 authentic demands")
        matched=Counter();kernel=Counter();pairs=[];repeated=[];by_source=Counter()
        for (src,v),block in sorted(buckets.items()):
            by_source[src]+=len(block)
            if len(block)<2:continue
            ordered=sorted(block)
            need(len({e[3] for e in block})==len(block),"same ordered leg duplicates were excluded in R357")
            # Even if every unresolved return and all routing were free, any new
            # productive grade cannot exceed the gap to ambient dimension 8.
            grade=8-charts.rank[src]
            matched[grade]+=len(block)//2;kernel[grade]+=len(block)-1
            repeated.append({"source":src,"dimension":charts.rank[src],"demand":hex(v),"moves":[[i,r,B,g] for i,r,A,B,g,row in ordered]})
            pairs.extend((grade,i,j) for i,j in combinations(ordered,2))
        def gross(cnt):
            return price.decimal_interval(price.moment({r:36*n for r,n in cnt.items() if r>0},F(accept["claim"])),30)
        info={"head":prior["head"],"word":prior["word"],"comparison":accept["claim"],"r357":R357,"r357_checker":C357,"r354_checker":C354,
              "pins":old["PINS"],"archive_pins":old["M"],"scope_moves":len(demands),"source_charts":len(by_source),"distinct_source_demand_signatures":len(buckets),
              "repeated_signatures":repeated,"all_equal_pairs":len(pairs),"disjoint_pair_limit":sum(matched.values()),"independent_pair_injection_limit":sum(kernel.values()),
              "optimistic_disjoint_36_call_gross":gross(matched),"optimistic_all_encoded_36_call_gross":gross(kernel),
              "other_native_paid_change":0,"selected":None,"unvisited_signature_positions":0}
        priority=sorted(pairs,key=lambda x:(-x[0],x[1][0],x[2][0]))
        if priority and priority[0][0]>0:
            grade,first,second=priority[0]
            test=candidate(w,charts,literal,[first,second],end)
            if test["status"]=="NATIVE_FORWARD_ADJOINT_PASS":
                new=test.pop("word");paid=test.pop("paid");caller=json.loads(gzip.decompress(blobs["source/research/paired-query-only-bit/EFREE-CALLER.json.gz"]))
                ev=Counter(x[0] for x in caller["events"]);T=Counter({int(k):v for k,v in peer["binary_native"]["productive"].items()});T[test["grade"]]+=1
                signed_paid,signed_t=literal.paired_invoice(caller,paid,T,ev)
                need(signed_paid==Counter({int(k):v for k,v in peer["binary_native"]["paid_all"].items()}),"all paid native and caller positions")
                test.update(ordinary=literal.ordinary(new,caller,ev,signed_paid,signed_t),gross=gross({test["grade"]:1}))
            info["selected"]={"clocks":[first[0],second[0]],"owners":[first[1],second[1]],"source":first[2],"destinations":[first[3],second[3]],"test":test}
        with a.out.open("x") as f:json.dump(info,f,sort_keys=True,indent=2);f.write("\n")
        print("PASS_EQUALITY_SCREEN",len(demands),len(buckets),len(repeated),len(pairs),info["selected"] and info["selected"]["test"]["status"])


if __name__=="__main__":
    main()
