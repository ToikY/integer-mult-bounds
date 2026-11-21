"""Verify the rank of each frozen three-delivery deletion from the literal BIT tape."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json
import runpy
import time

def dimension(values):
    basis = {}
    for row in values:
        while row:
            k = row.bit_length()
            if k not in basis:
                basis[k] = row
                break
            row ^= basis[k]
    return len(basis)

def altered(word, dropped, pulses, external=True):
    n = word['public']
    cells = [1 << i if external else 0 for i in range(n)] + [0]*word['owned_fields']
    for clock, (op,a,*args) in enumerate(word['program']):
        if op == 'MOVE':
            if clock in dropped:
                cells[a] = 0
            if clock in pulses:
                cells[a] ^= pulses[clock]
        elif op == 'ADD':
            cells[a] ^= cells[args[0]]
        elif op == 'SWAP':
            b = args[0]
            cells[a],cells[b] = cells[b],cells[a]
        elif op in ('INIT','CLEAR'):
            cells[a] = 0
        else:
            raise ValueError(op)
    return cells[:n]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('word',type=Path)
    ap.add_argument('operator',type=Path)
    ap.add_argument('receipt',type=Path)
    a = ap.parse_args()
    start = time.monotonic()
    assert sha256(a.operator.read_bytes()).hexdigest() == '36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349'
    m = runpy.run_path(str(a.operator))
    w = m['load_json'](a.word,'d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9',True)
    atlas = m['Atlas'](w['frames'])
    fwd, adj = [m['run_tape'](w,atlas,rev) for rev in (False, True)]
    assert fwd.output == m['expected_operator'](False) and adj.output == m['expected_operator'](True)
    assert fwd.dirty == adj.dirty == 3554
    ordered = sorted(fwd.packets,key=lambda k:fwd.packets[k].clock)
    pos = {k:j for j,k in enumerate(ordered)}
    pair_routes, destinations = defaultdict(list), defaultdict(list)
    for k in ordered:
        p = fwd.packets[k]
        pair_routes[p.source,p.receiver].append(k)
        destinations[p.receiver].append(k)
    rows = {k:p.arrival.row for k,p in fwd.packets.items()}
    cols = {k:p.arrival.row for k,p in adj.packets.items()}
    census, hist, total = {}, Counter(), 0
    out = dict(status='running', routes=census, rank_counts={},unvisited=None)
    for (src,dst), route_ids in sorted(pair_routes.items()):
        if len(route_ids)<2:
            continue
        digest = sha256()
        route_count = 0
        for i,j in combinations(route_ids,2):
            for k in destinations[dst]:
                if pos[k]>=pos[i]:
                    break
                if time.monotonic()-start>=30:
                    out.update(status='capped',next_case=[src,dst,k,i,j],tested=total,seconds=time.monotonic()-start)
                    a.receipt.write_text(json.dumps(out,indent=2)+'\n')
                    raise SystemExit(2)
                ids=(k,i,j)
                r=dimension(rows[x] for x in ids)
                c=dimension(cols[x] for x in ids)
                assert r==c==3, (ids,r,c)
                digest.update(f'{k},{i},{j},{r},{c}\n'.encode())
                hist['3']+=1
                route_count+=1
                total+=1
        census[f'{src}/{dst}']=dict(pair_labels=route_ids,earlier_bank_labels=destinations[dst],
                                      checked=route_count,ordered_ids_sha256=digest.hexdigest())
    assert total==115156 and len(census)==246
    labels=[1358,2291,3419]
    clocks=[fwd.packets[k].clock for k in labels]
    assert clocks==[2404,7018,20938]
    control=[]
    for n in range(4):
        tested=altered(w,set(clocks[:n]),{})
        defect=dimension(x^y for x,y in zip(tested,fwd.output,strict=True))
        assert defect==n
        control.append(defect)
    bits=altered(w,set(),{clock:1<<j for j,clock in enumerate(clocks)},external=False)
    pulse_columns=[]
    for j,k in enumerate(labels):
        column=sum(((b>>j)&1)<<i for i,b in enumerate(bits))
        assert column==cols[k]
        pulse_columns.append(hex(column))
    assert dimension(int(v,16) for v in pulse_columns)==3
    # Removing a later packet may suppress the effects of an earlier pulse.
    # These three columns have its exact feed-through removed by the frozen tape.
    cut=altered(w,set(clocks),{clock:1<<j for j,clock in enumerate(clocks)},external=False)
    actual=altered(w,set(clocks),{})
    for r,(original, damaged) in enumerate(zip(fwd.output,actual,strict=True)):
        predicted=0
        for j,k in enumerate(labels):
            if cut[r] & (1<<j):
                predicted^=rows[k]
        assert predicted==original^damaged
    out.update(status='exhausted',tested=total,rank_counts=dict(hist),unvisited=0,dirty_retires=[3554,3554],
               public_columns=w['public'],controls=dict(labels=labels,clocks=clocks,deleted_prefix_ranks=control,
               intact_injection_columns=pulse_columns,fully_cut_injection_coefficient_check=680),seconds=time.monotonic()-start)
    a.receipt.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],total,out['rank_counts'],control,out['seconds'])

if __name__ == '__main__':
    main()
