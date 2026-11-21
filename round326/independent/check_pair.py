"""Independent 8-column, primal rational-space contraction and directed price audit."""
import argparse
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

PIN = "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
K = Decimal("0.003879928046155")
N = 8


def reduce_rows(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for pivot, vector in sorted(basis.items()):
            if row[pivot]:
                coefficient = row[pivot]
                row = [v - coefficient * b for v, b in zip(row, vector)]
        pivot = next((i for i, v in enumerate(row) if v), None)
        if pivot is None:
            continue
        lead = row[pivot]
        row = [v / lead for v in row]
        for i, v in list(basis.items()):
            if v[pivot]:
                basis[i] = [a - v[pivot] * b for a, b in zip(v, row)]
        basis[pivot] = row
    return [basis[i] for i in sorted(basis)]


def null_basis(rows):
    echelon = reduce_rows(rows)
    pivots = {next(i for i, x in enumerate(r) if x): r for r in echelon}
    vectors = []
    for j in range(N):
        if j in pivots:
            continue
        v = [0] * N
        v[j] = 1
        for i, row in pivots.items():
            v[i] = -row[j]
        vectors.append(v)
    return vectors


def signed_price(old, new):
    # ln and exp are correctly rounded. Neighbours of every rounded operation
    # enclose its exact value, including the two rounded arithmetic reductions.
    total_low = total_high = Decimal(0)
    for rank in sorted(set(old) | set(new)):
        delta = old[rank] - new[rank]
        if not delta:
            continue
        low, high = power(rank)
        if delta < 0:
            low, high = high, low
        low = (low * delta).next_minus()
        high = (high * delta).next_plus()
        total_low = (total_low + low).next_minus()
        total_high = (total_high + high).next_plus()
    return (total_low * 36).next_minus(), (total_high * 36).next_plus()


@cache
def power(i):
    if i in (0, 1):
        return Decimal(i), Decimal(i)
    log = Decimal(i).ln()
    low = ((1 - K) * log.next_minus()).next_minus().exp().next_minus()
    high = ((1 - K) * log.next_plus()).next_plus().exp().next_plus()
    return low, high


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("word", type=Path)
    p.add_argument("out", type=Path)
    args = p.parse_args()
    begin = monotonic()
    getcontext().prec = 50
    data = args.word.read_bytes()
    assert sha256(data).hexdigest() == PIN
    w = json.loads(gzip.decompress(data))
    frames = {int(k): v['B'] for k, v in w['frames'].items()}
    dims = {k: len(v) for k, v in frames.items()}
    annihilator = {k: null_basis(v) for k, v in frames.items()}
    edges = Counter(tuple(sorted(op[-2:])) for op in w['program'] if op[0] == 'MOVE')
    internal = frames.keys() - set(w['start'] + w['final'])
    pairs = sorted((e for e in edges if set(e) <= internal), key=lambda t: (-edges[t], *t))
    visited = []
    report = dict(word_sha256=PIN, k=str(K), call_multiplicity=36, cap_pairs=64,
                  cap_seconds=60, total_pairs=len(pairs), ranked_pairs=pairs,
                  cases=visited, status="exhausted", strict_witness=None)
    stopped = False
    for u, v in pairs[:64]:
        if stopped:
            break
        boundary = Counter()
        old = Counter({abs(dims[u]-dims[v]): edges[(u, v)]})
        for (a, b), n in edges.items():
            if a in (u,v) and b not in (u,v):
                boundary[b] += n
            elif b in (u,v) and a not in (u,v):
                boundary[a] += n
            else:
                continue
            old[abs(dims[a]-dims[b])] += n
        for d in range(N+1):
            if monotonic()-begin >= 60:
                report.update(status="time-cap",next_case=[u,v,d])
                stopped=True
                break
            # Equal-dimensional incidences require equality (both constraints).
            small = [f for f in boundary if dims[f] <= d]
            large = [f for f in boundary if dims[f] >= d]
            lower = reduce_rows(row for f in small for row in frames[f])
            upper_dual = reduce_rows(row for f in large for row in annihilator[f])
            lower_in_upper = all(sum(a*b for a,b in zip(x,y))==0 for x in lower for y in upper_dual)
            new = Counter()
            for f,n in boundary.items():
                r = abs(dims[f]-d)
                if r:
                    new[r] += n
            low,high = signed_price(old, new)
            possible = lower_in_upper and len(lower)<=d<=8-len(upper_dual)
            case = dict(pair=[u,v],dimension=d,lower_rank=len(lower),upper_dimension=8-len(upper_dual),
                        contained=lower_in_upper, feasible=possible,old_paid=dict(old),new_paid=dict(new),
                        raw_saving_36=[str(low),str(high)])
            visited.append(case)
            if possible and low>0:
                basis = lower.copy()
                for vec in null_basis(upper_dual):
                    if len(basis) == d:
                        break
                    new_basis = reduce_rows([*basis,vec])
                    if len(new_basis)>len(basis):
                        basis=new_basis
                assert len(basis)==d
                report.update(status="positive",strict_witness=dict(case,primal=[[str(x) for x in r] for r in basis],
                        external_incidence=sorted(boundary.items()),mutual_moves=edges[(u,v)]))
                stopped=True
                break
    if not stopped and len(pairs)>64:
        report['status']='case-cap'
    report['elapsed_seconds']=monotonic()-begin
    report['unvisited_dimensions']=9*len(pairs)-len(visited)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],len(visited),len(pairs),report['elapsed_seconds'])
    if report['strict_witness']:
        print(report['strict_witness'])


if __name__ == '__main__':
    main()
