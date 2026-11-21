"""Necessary rank of a two-packet deletion on the same frozen directed route."""
import argparse
from collections import Counter,defaultdict
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import runpy
from time import monotonic

WORD="inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz"
GRAPH="inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py"
PINS={WORD:"d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",GRAPH:"4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e"}

def distinct(a,b):
    return bool(a and b and a!=b)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root',type=Path)
    ap.add_argument('result',type=Path)
    args=ap.parse_args()
    t=monotonic()
    for p,d in PINS.items():
        assert sha256((args.root/p).read_bytes()).hexdigest()==d
    w=json.loads(gzip.decompress((args.root/WORD).read_bytes()))
    g=runpy.run_path(str(args.root/GRAPH))
    S,F,M,R,clock=g['extract'](w)
    order=sorted(M,key=clock.get)
    C=g['basis'](S,M,R,order)
    V={h:1<<h for h in S}
    gr=defaultdict(list)
    for k in order:
        gr[M[k]].append(k)
        V[k]=g['combine'](R[k],V)
    out=dict(sources=PINS,routes={},survivors=[],rank_two=0,all_pairs=sum(len(L)*(len(L)-1)//2 for L in gr.values()))
    def save(status,restart):
        out.update(status=status,next_case=restart,seconds=monotonic()-t)
        args.result.write_text(json.dumps(out,indent=2)+'\n')
        print(status,'pairs',out['all_pairs'],'rank_two',out['rank_two'],'survivors',len(out['survivors']),out['seconds'])
    for (a,b),labels in sorted(gr.items()):
        if len(labels)<2:
            continue
        digest=sha256()
        record=out['routes'][f'{a}/{b}']=dict(labels=labels,grades=abs(w['frames'][str(a)]['dim']-w['frames'][str(b)]['dim']),tested=0)
        for i,j in combinations(labels,2):
            if monotonic()-t>=60:
                record['sha256']=digest.hexdigest()
                save('capped',[a,b,i,j])
                return
            x=distinct(V[i],V[j])
            y=distinct(C[i],C[j])
            digest.update(f'{i},{j},{int(x)},{int(y)}\n'.encode())
            record['tested']+=1
            if x and y:
                out['rank_two']+=1
            else:
                out['survivors'].append(dict(route=[a,b],labels=[i,j],clock=[clock[i],clock[j]],rows=[hex(V[i]),hex(V[j])],columns=[hex(C[i]),hex(C[j])]))
        record['sha256']=digest.hexdigest()
    save('exhausted',None)
if __name__=='__main__':
    main()
