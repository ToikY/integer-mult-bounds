"""Test a single paid injection followed by one zero-relation decoder on the frozen word."""
from argparse import ArgumentParser
from collections import defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path
import runpy
from time import monotonic

WORD='d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9'
GRAPH='4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e'

class Span:
    def __init__(self):
        self.basis={}
    def reduce(self, value, tag=0):
        while value:
            k=value.bit_length()-1
            if k not in self.basis:
                break
            v,t=self.basis[k]
            value^=v
            tag^=t
        return value,tag
    def add(self,value,tag):
        r,t=self.reduce(value,tag)
        if r:
            self.basis[r.bit_length()-1]=r,t
        return (r,t)
    def solve(self,value):
        rest,tag=self.reduce(value)
        return None if rest else tag

def run(package, owners, source, deadline, receipt):
    raw=(package/'sources/WORD.json.gz').read_bytes()
    engine=package/'sources/bit_native.py'
    assert sha256(raw).hexdigest()==WORD and sha256(engine.read_bytes()).hexdigest()==GRAPH
    w=json.loads(gzip.decompress(raw))
    g=runpy.run_path(str(engine))
    inputs,outputs,moves,eq,clock=g['extract'](w)
    order=sorted(moves,key=clock.get)
    columns=g['basis'](inputs,moves,eq,order)
    n=len(inputs)
    old={i:1<<i for i in inputs}
    read=defaultdict(list)
    send=defaultdict(list)
    for i,a in inputs.items():
        read[a].append((-1,i,old[i]))
        send[outputs[i]].append((len(w['program']),i,1<<i))
    for k in order:
        old[k]=g['combine'](eq[k],old)
        a,b=moves[k]
        read[b].append((clock[k],k,old[k]))
        send[a].append((clock[k],k,columns[k]))
    target=sum(1<<i for i in owners)
    reader=Span()
    for first,k,v in read[source]:
        reader.add(v,1<<k)
        readout=reader.solve(target)
        if readout is not None:
            break
    else:
        raise ValueError('source cannot read target')
    receipt.update(first_read_clock=first,parity_labels=list(g['indices'](readout)))
    ss=[k for k in order if moves[k][0]==source and clock[k]>first]
    receipt['eligible_sends']=[[k,clock[k],moves[k][1]] for k in ss]
    for k in ss:
        if monotonic()>=deadline:
            receipt['restart']=[k,None]
            return
        pulse={i:0 for i in inputs}
        for j in order:
            pulse[j]=g['combine'](eq[j],pulse)^(j==k)
        actual=sum(g['combine'](eq[~i],pulse)<<i for i in outputs)
        assert actual==columns[k]
        changed=sorted({moves[j][1] for j in order if pulse[j]})
        case={'send':k,'column':hex(actual),'changed_charts':changed,'zero_relations':[],'complete':False}
        receipt['cases'].append(case)
        for c in changed:
            if monotonic()>=deadline:
                receipt['restart']=[k,c]
                return
            basis=Span()
            for cut,j,row in read[c]:
                basis.add(row|(pulse[j]<<n),1<<j)
                rel=basis.solve(1<<n)
                if rel is not None:
                    break
            else:
                continue
            future=Span()
            for pos,label,col in send[c]:
                if pos>cut:
                    future.add(col,1<<label)
            required=target^actual
            labels=future.solve(required)
            entry=dict(chart=c,cut=cut,labels=list(g['indices'](rel)),response=hex(required),
                       missing_response=hex(future.reduce(required)[0]))
            case['zero_relations'].append(entry)
            if labels is not None:
                entry['future_injections']=list(g['indices'](labels))
                receipt['status']='witness'
                receipt['witness']=[k,c,cut]
                return
        case['complete']=True
    receipt['status']='exhausted'

def main():
    parser=ArgumentParser()
    parser.add_argument('package',type=Path)
    parser.add_argument('out',type=Path)
    opts=parser.parse_args()
    start=monotonic()
    out=dict(word=WORD,graph=GRAPH,owners=[238,672],source_chart=8,status='capped',cases=[],restart=None)
    run(opts.package,out['owners'],out['source_chart'],start+60,out)
    out['seconds']=monotonic()-start
    opts.out.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],out['first_read_clock'],out['eligible_sends'],[len(c['zero_relations']) for c in out['cases']],out['seconds'])
if __name__=='__main__':
    main()
