# SPDX-License-Identifier: Apache-2.0
"""All supports injecting one independent helper into departures from one literal source chart."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json,runpy,sys,tarfile,tempfile

H354="326dcf53fa411dad88df648abe86097d52e1d3de594607e71f659ee7e1aa0be0"
H357="5e172d879ac6438ecfce1152c543fdd025c3f99cb369d0ee21655118cc8d61b0"
H358="bacbcf2c77a7f8b36cf3f27749bc05539cc2a18a3020654e405a266a36618ce4"
R358="bc62287d9b4c38a1722eebd98decfdef5c092ddd159795235e77fc8dd78892e1"
R357="ee8e207c2352db335abf746293353aa36039613b589c0042513b6e6fbe0ff599"


def need(ok,reason):
    if not ok:raise ValueError(reason)


def verified(p,h):
    raw=p.read_bytes();need(sha256(raw).hexdigest()==h,"source "+p.name);return raw


def circuit_basis(columns):
    rows={};relations=[]
    for j,demand in enumerate(columns):
        trace=1<<j
        while demand:
            i=(demand&-demand).bit_length()-1
            if i not in rows:
                rows[i]=(demand,trace);break
            old,combo=rows[i];demand^=old;trace^=combo
        if not demand:
            # This clock is the unique newest member. Such relations are independent.
            need(trace.bit_length()==j+1,"independent new nullspace direction")
            relations.append(trace)
    need(len(rows)+len(relations)==len(columns),"rank-nullity")
    return len(rows),relations


def best_support(kernels,end):
    # Exact minimum distance. R358 gives the strict lower bound three, so a
    # triple is decisive even if other chart-nullspaces contain many vectors.
    best=None;position=0;complete=True
    for chart,events,relations in kernels:
        if not relations:continue
        vector=0
        for i in range(1,1<<len(relations)):
            if i%64==1 and monotonic()>end:
                complete=False;break
            vector^=relations[(i&-i).bit_length()-1]
            position+=1
            count=vector.bit_count()
            if best is None or count<best[0]:
                support=[e for j,e in enumerate(events) if vector>>j&1]
                need(count>=3,"R358 excludes weights one and two")
                check=0
                for e in support:check^=e[-1]
                need(check==0,"independent verification of returned support")
                best=(count,chart,support)
                if count==3:return best,True,position
        if not complete:break
    return best,complete,position


def main():
    p=ArgumentParser()
    for k in ("peer","r354-code","r357-code","r358-code","r357","r358","accept","out"):
        p.add_argument("--"+k,dest=k.replace("-","_"),type=Path,required=True)
    a=p.parse_args();start=monotonic();end=start+30
    for f,h in [(a.r354_code,H354),(a.r357_code,H357),(a.r358_code,H358)]:verified(f,h)
    seed=runpy.run_path(str(a.r354_code));rev=runpy.run_path(str(a.r357_code));port=runpy.run_path(str(a.r358_code))
    pair=json.loads(verified(a.r358,R358));fixed=json.loads(verified(a.r357,R357));accept=json.loads(verified(a.accept,seed["ACCEPT"]))
    need(accept["claim"]=="0.00389011527141" and pair["all_equal_pairs"]==0 and fixed["total_defect"]==0,"old signed result and two known controls")
    for name,h in seed["PINS"].items():verified(a.peer/name,h)
    peer=json.loads((a.peer/"APPLICATION.json").read_bytes());word=json.loads(gzip.decompress((a.peer/"BINARY-CANDIDATE.json.gz").read_bytes()))
    with tarfile.open(a.peer/"APPLICATION-SOURCES.tar.gz") as arc:
        data={k:seed["pin"](arc.extractfile(k).read(),h) for k,h in seed["M"].items()}
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)
        for k in list(seed["M"])[:2]:(tmp/Path(k).name).write_bytes(data[k])
        sys.path.insert(0,td)
        import literal,price
        charts=literal.Charts(word["frames"]);n=word["public"]
        need(literal.canonical(word)==peer["binary_word"]==pair["word"]==fixed["word"],"actual native word")
        move,cols=rev["reverse"](word,charts,end,a.out.with_suffix(".restart.json"))
        need(cols==literal.expected_rows(n,True),"all transposed outputs")
        f,log,_=literal.tape(word,charts)
        need(f==literal.expected_rows(n,False) and log["paid"]==Counter(e[4] for e in move),"old forward action and all owned retirements")
        groups=defaultdict(list);hashes=sha256()
        for e in move:
            i,r,A,B,g,v=e
            hashes.update(f"{i} {r} {A} {B} {v:x}\n".encode())
            groups[A].append(e)
        need(hashes.hexdigest()==fixed["demand_stream_sha256"] and len(groups)==635 and len(move)==2803,"fixed actual matrix")
        summary=[];kernels=[];gross_terms=Counter();defect=0;maximum=0
        for A,events in sorted(groups.items()):
            events.sort();columns=[e[-1] for e in events]
            need(all(columns) and len(set(columns))==len(events),"R358 equality test independently reproduced")
            rank,relations=circuit_basis(columns);capacity=8-charts.rank[A]
            # Physical helper grade cannot exceed ambient dimension minus starting dimension.
            gross_terms[capacity]+=len(relations);defect+=len(relations);maximum=max(maximum,len(relations))
            summary.append({"source":A,"source_rank":charts.rank[A],"moves":len(events),"rank":rank,"nullity":len(relations)})
            if capacity>0:kernels.append((A,events,relations))
        bill=price.moment({g:36*k for g,k in gross_terms.items() if g>0},F(accept["claim"]))
        best,finished,searched=best_support(kernels,end)
        result={"head":fixed["head"],"word":fixed["word"],"price_comparator":accept["claim"],"r358":R358,"r357":R357,
                "r354_checker":H354,"r357_checker":H357,"r358_checker":H358,"r352_accept":seed["ACCEPT"],
                "pins":seed["PINS"],"member_pins":seed["M"],"moves":len(move),"source_charts":len(groups),"all_sources":summary,
                "total_nullity":defect,"maximum_nullity":maximum,"grade_capacity_counts":dict(sorted(gross_terms.items())),
                "gross_36_calls_interval":price.decimal_interval(bill,30),"eligible_nullvectors_examined":searched,
                "minimum_support_verified":finished,"unvisited_move_positions":0,"selected":None}
        if best:
            count,source,es=best
            result["selected"]={"chart":source,"weight":count,"clocks":[e[0] for e in es],"owners":[e[1] for e in es]}
            if finished:
                test=port["candidate"](word,charts,literal,es,end)
                if test["status"]=="NATIVE_FORWARD_ADJOINT_PASS":
                    new=test.pop("word");paid=test.pop("paid");caller=json.loads(gzip.decompress(data["source/research/paired-query-only-bit/EFREE-CALLER.json.gz"]))
                    T=Counter({int(k):v for k,v in peer["binary_native"]["productive"].items()});T[test["grade"]]+=1
                    ev=Counter(x[0] for x in caller["events"]);p1,t1=literal.paired_invoice(caller,paid,T,ev)
                    need(p1==Counter({int(k):v for k,v in peer["binary_native"]["paid_all"].items()}),"full signed paid positions")
                    test["ordinary"]=literal.ordinary(new,caller,ev,p1,t1)
                    test["productive_credit_interval"]=price.decimal_interval(price.moment({test["grade"]:36},F(accept["claim"])),30)
                result["selected"]["decoder"]=test
            else:result["selected"]["decoder"]={"status":"MINIMUM_NOT_YET_VERIFIED"}
        with a.out.open("x") as fp:json.dump(result,fp,sort_keys=True,indent=2);fp.write("\n")
        print("COMPLETE_KERNELS",len(move),len(groups),defect,maximum,best and best[:2],finished,result["selected"] and result["selected"]["decoder"]["status"])


if __name__=="__main__":
    main()
