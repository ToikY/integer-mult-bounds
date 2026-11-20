"""Test a pure e_h read and pure e_h write at one chart with zero extra MOVEs."""
import argparse
from collections import defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
from time import monotonic

WORD = "inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz"
GRAPH = "inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py"
DIGEST = {WORD: "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",
          GRAPH: "4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e"}

class Span:
    def __init__(self, entries):
        self.rows = {}
        for _, label, row in entries:
            use = 1 << label
            while row:
                k = row.bit_length()-1
                if k not in self.rows:
                    self.rows[k] = (row, use)
                    break
                a,b = self.rows[k]
                row ^= a
                use ^= b

    def solve(self, target):
        use = 0
        while target:
            k = target.bit_length()-1
            if k not in self.rows:
                return None
            a,b = self.rows[k]
            target ^= a
            use ^= b
        return use

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root',type=Path)
    ap.add_argument('output',type=Path)
    args = ap.parse_args()
    begin = monotonic()
    for path,wanted in DIGEST.items():
        if sha256((args.root/path).read_bytes()).hexdigest()!=wanted:
            raise ValueError(path)
    edge = runpy.run_path(str(args.root/GRAPH))
    w = json.loads(gzip.decompress((args.root/WORD).read_bytes()))
    S,F,M,R,clocks = edge['extract'](w)
    order = sorted(M,key=clocks.get)
    send = edge['basis'](S,M,R,order)
    val = {h:1<<h for h in S}
    for k in order:
        val[k] = edge['combine'](R[k],val)
    frames = {int(c):f for c,f in w['frames'].items()}
    A,B = {},{}
    for c,f in frames.items():
        A[c],B[c] = ([list(map(Fraction,x)) for x in f[t]] for t in ('A','B'))

    @cache
    def included(c,d):
        return frames[c]['dim'] < frames[d]['dim'] and all(
            not sum(a*b for a,b in zip(v,u)) for v in B[c] for u in A[d])

    result = dict(source=DIGEST,all=2*len(frames)*(len(S)-222),charts={},witness=None)
    def save(status,rr,chart,helper):
        result.update(status=status,next_id=[rr,chart,helper],seconds=monotonic()-begin)
        for row in result['charts'].values():
            row['dimension_eligible']=hex(sum(1<<h for h in row['dimension_eligible']))
        args.output.write_text(json.dumps(result,indent=2)+'\n')

    for rev in (False,True):
        start,finish = (F,S) if rev else (S,F)
        # Time is in paid packet boundaries. Terminal rows are always injectable;
        # the terminal label equals the corresponding public label (at most 679).
        read,write = defaultdict(list),defaultdict(list)
        for h in S:
            read[start[h]].append((-1,h,1<<h))
            write[finish[h]].append((len(M),h,1<<h))
        for p,k in enumerate(reversed(order) if rev else order):
            s,d = M[k][::-1] if rev else M[k]
            read[d].append((p,k,send[k] if rev else val[k]))
            write[s].append((p,k,val[k] if rev else send[k]))
        for c in sorted(frames):
            P,Q = Span(read[c]),Span(write[c])
            row = dict(dimension_eligible=[],all_time=[],causal_rejected=[])
            result['charts'][f'{int(rev)}/{c}']=row
            for h in range(222,len(S)):
                if monotonic()-begin>=60:
                    save('capped',int(rev),c,h)
                    return
                a,b = start[h],finish[h]
                if frames[a]['dim']>frames[b]['dim']:
                    a,b = b,a
                if not frames[a]['dim']<frames[c]['dim']<frames[b]['dim']:
                    continue
                row['dimension_eligible'].append(h)
                v = 1<<h
                if P.solve(v) is None or Q.solve(v) is None:
                    continue
                if not included(a,c) or not included(c,b):
                    continue
                row['all_time'].append(h)
                # Earliest readable prefix maximizes available suffix. Only
                # incoming packet indices can change the read space.
                events = sorted(read[c])
                lo,hi = 1,len(events)
                while lo<hi:
                    mid=(lo+hi)//2
                    if Span(events[:mid]).solve(v) is None:
                        lo=mid+1
                    else:
                        hi=mid
                cut = events[lo-1][0]
                donors=Span(events[:lo]).solve(v)
                sinks=Span([x for x in write[c] if x[0]>cut]).solve(v)
                if sinks is not None:
                    result['witness'] = dict(reverse=rev,chart=c,helper=h,after_packet_index=cut,
                        read_labels=list(edge['indices'](donors)), injected_labels=list(edge['indices'](sinks)))
                    save('witness',int(rev),c,h+1)
                    return
                row['causal_rejected'].append([h,cut])
    save('exhausted',None,None,None)

if __name__=='__main__':
    main()
