"""Independent literal event and opposite-pivot replay of the reported pair decisions."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import time


def remainder(value, stock):
    kept = 0
    while value:
        bit = value & -value
        entry = stock.get(bit)
        if entry is None:
            value ^= bit
            kept ^= bit
        else:
            value ^= entry
    return kept


def replay(word, receipt, deadline):
    n = word['public']
    frames = word['frames']
    moves = {clock:n+i for i,clock in enumerate(t for t,op in enumerate(word['program']) if op[0]=='MOVE')}
    expected = {(rev,i,j): ids for rev,i,j,ids in receipt['pair_specific_withdrawals']}
    results = []
    for reverse in (False,True):
        start = word['final' if reverse else 'start']
        finish = word['start' if reverse else 'final']
        cohorts = defaultdict(list)
        stock = defaultdict(dict)
        for h,chart in enumerate(start):
            stock[chart][1<<h] = 1<<h
            if h>=222:
                cohorts[chart,finish[h]].append(h)
        cohorts = [hs for hs in cohorts.values() if len(hs)>1]
        rows = [1<<i for i in range(n)] + [0]*word['owned_fields']
        score = defaultdict(list)
        ranks = {}
        common = []
        for i in range(len(word['program'])-1,-1,-1) if reverse else range(len(word['program'])):
            op, r, *args = word['program'][i]
            if op == 'MOVE':
                if time.monotonic() >= deadline:
                    raise TimeoutError((reverse, i))
                a,b=args
                dest = a if reverse else b
                graph = stock[dest]
                residual = remainder(rows[r],graph)
                k=moves[i]
                ranks[k] = abs(frames[str(a)]['dim'] - frames[str(b)]['dim'])
                if not residual:
                    common.append(k)
                else:
                    for hs in cohorts:
                        by_residual=defaultdict(list)
                        for h in hs:
                            v = remainder(1<<h,graph)
                            by_residual[v].append(h)
                        for v, members in by_residual.items():
                            other = v ^ residual
                            if v < other and other in by_residual:
                                for h in members:
                                    for j in by_residual[other]:
                                        score[min(h,j),max(h,j)].append(k)
                    graph[residual&-residual]=residual
            elif op=='ADD':
                s=args[0]
                if reverse:
                    rows[s] ^= rows[r]
                else:
                    rows[r] ^= rows[s]
            elif op=='SWAP':
                s=args[0]
                rows[r], rows[s] = rows[s], rows[r]
            elif op in ('INIT','CLEAR'):
                rows[r]=0
            else:
                raise ValueError(op)
        for h in range(n):
            public=1<<h
            if reverse and h <111:
                public ^= 1 << (h+111)
            if not reverse and 111<=h<222:
                public ^= 1 << (h-111)
            assert rows[h]==public
        assert common==dict(receipt['common_packets'])[reverse]
        counts=Counter()
        for hs in cohorts:
            for i,j in combinations(hs,2):
                ids=score.get((i,j),[])
                assert ids==expected.pop((reverse,i,j),[]), (reverse,i,j)
                bill=Counter(ranks[k] for k in ids+common)
                charge=abs(frames[str(start[i])]['dim']-frames[str(finish[i])]['dim'])
                bill[charge]-=1
                counts[tuple(sorted((r,36*v) for r,v in bill.items() if v))]+=1
        reported={tuple(tuple(row) for row in h):count
                  for h,count,interval in dict(receipt['charged_histograms'])[reverse]}
        assert reported==counts
        results.append(dict(reverse=reverse,packets=len(moves),pairs=sum(counts.values()),
                            identical_bills=counts[()],public_checks=n))
    assert not expected
    return results


def main():
    p=argparse.ArgumentParser()
    p.add_argument('word',type=Path)
    p.add_argument('receipt',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    start=time.monotonic()
    raw=args.word.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9'
    word=json.loads(gzip.decompress(raw))
    result=replay(word,json.loads(args.receipt.read_bytes()),start+15)
    out=dict(status='verified',scope=result,seconds=time.monotonic()-start)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(out)
if __name__=='__main__':
    main()
