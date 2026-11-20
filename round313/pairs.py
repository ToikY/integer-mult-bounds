"""Price fixed-order one-direction withdrawals on the #7830 binary word."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time

PINS = {
    'inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py':
        '4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e',
    'inputs/cache/parent/binary/independent/price.py':
        'd720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b',
    'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz':
        'd28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9',
    'inputs/cache/parent/binary/independent/literal.py':
        '4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c',
}

def reduce_row(row, echelon):
    remainder = 0
    while row:
        bit = 1 << (row.bit_length() - 1)
        row ^= echelon.get(bit, bit)
        if bit not in echelon:
            remainder |= bit
    return remainder

def price_pairs(word, engine, invoice, cap):
    start = time.monotonic()
    source, finish, moves, rows, clocks = engine['extract'](word)
    order = sorted(moves, key=clocks.get)
    adjoint = engine['basis'](source, moves, rows, order)
    forwards = {h: 1 << h for h in source}
    for packet in order:
        forwards[packet] = engine['combine'](rows[packet], forwards)
    cohorts = defaultdict(list)
    for h in range(222, word['public']):
        cohorts[source[h], finish[h]].append(h)
    cohorts = {key: hs for key, hs in cohorts.items() if len(hs) >= 2}
    all_pairs = [(i, j) for hs in cohorts.values() for i, j in combinations(hs, 2)]
    all_helpers = sorted({h for p in all_pairs for h in p})
    counts = []
    found = []
    common_packets = []
    summaries = []
    best = None
    def grade(a, b):
        return abs(word['frames'][str(a)]['dim'] - word['frames'][str(b)]['dim'])
    for reverse in (False, True):
        stock = defaultdict(dict)
        for h, chart in (finish if reverse else source).items():
            stock[chart][1 << h] = 1 << h
        withdrawals = defaultdict(list)
        common = []
        done = 0
        for k in reversed(order) if reverse else order:
            if time.monotonic() - start >= cap:
                return {'status': 'capped', 'completed': counts, 'orientation': reverse,
                        'packets_processed': done, 'next_packet': k}
            a,b = moves[k]
            dest = a if reverse else b
            value = (adjoint if reverse else forwards)[k]
            basis = stock[dest]
            residual = reduce_row(value, basis)
            if not residual:
                common.append(k)
            else:
                cov = {h: reduce_row(1 << h, basis) for h in all_helpers}
                for hs in cohorts.values():
                    seen = defaultdict(list)
                    for j in hs:
                        u = cov[j]
                        for i in seen.get(residual ^ u, ()):
                            withdrawals[i, j].append(k)
                        seen[u].append(j)
                basis[1 << (residual.bit_length() - 1)] = residual
            done += 1
        counts.append([reverse, done, len(all_pairs)])
        common_packets.append([reverse, common])
        hist = Counter()
        price_cache = {}
        for i,j in all_pairs:
            removed = withdrawals.get((i,j), ())
            bridge = grade(source[i], finish[i])
            bill = Counter(grade(*moves[k]) for k in (*common, *removed))
            bill[bridge] -= 1
            key = tuple(sorted((r,n*36) for r,n in bill.items() if n))
            if key not in price_cache:
                interval = invoice['moment'](dict(key), Fraction('0.003879928046155'))
                price_cache[key] = interval, invoice['decimal_interval'](interval, 24)
            interval, display = price_cache[key]
            hist[key] += 1
            if best is None or interval[1] > best[0]:
                best = interval[1], dict(reverse=reverse, pair=[i,j], withdrawn=removed,
                                        bridge=bridge, interval=display)
            if removed:
                found.append([reverse, i,j, removed])
        summaries.append([reverse, [[list(k),n,price_cache[k][1]] for k,n in sorted(hist.items())]])
    return dict(status='exhausted', completed=counts, nonempty_cohorts=list(cohorts.items()),
                common_packets=common_packets, pair_specific_withdrawals=found,
                charged_histograms=summaries, highest_upper=best[1], seconds=time.monotonic()-start)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('output', type=Path)
    args=p.parse_args()
    paths=[args.root / rel for rel in PINS]
    for path, expected in zip(paths, PINS.values()):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
    engine=runpy.run_path(str(paths[0]))
    sys.path.insert(0,str(paths[1].parent.resolve()))
    invoice=runpy.run_path(str(paths[1]))
    word=json.loads(gzip.decompress(paths[2].read_bytes()))
    assert engine['digest'](word)=='d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d'
    receipt=price_pairs(word,engine,invoice,60)
    receipt['input_sha256']=PINS
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'],receipt.get('completed'),receipt.get('highest_upper'),receipt.get('seconds'))

if __name__=='__main__':
    main()
