"""Enumerate replacements of a complete internal chart of the authenticated BIT tape."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('root', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--public', action='store_true')
a = p.parse_args()
start = time.monotonic()
word_path = a.root / 'inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz'
assert hashlib.sha256(word_path.read_bytes()).hexdigest() == 'd28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9'
word = json.loads(gzip.decompress(word_path.read_bytes()))
price_path = a.root / 'inputs/cache/parent/binary/independent/price.py'
assert hashlib.sha256(price_path.read_bytes()).hexdigest() == 'd720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b'
sys.path.insert(0,str(price_path.parent.resolve()))

price = runpy.run_path(str(price_path))
from math import lcm
def integers(row):
    q = list(map(Fraction, row))
    den = lcm(*(x.denominator for x in q))
    return {i:int(x*den) for i,x in enumerate(q) if x}

body = {int(c):[integers(v) for v in f['B']] for c,f in word['frames'].items()}
ann = {int(c):[integers(v) for v in f['A']] for c,f in word['frames'].items()}
@cache
def grade(a,b):
    if a == b:
        return 0
    if len(body[a]) > len(body[b]):
        return grade(b,a)
    d = len(body[b]) - len(body[a])
    if d and all(sum(v*test.get(i,0) for i,v in row.items())==0 for row in body[a] for test in ann[b]):
        return d
    return -1

paid = defaultdict(Counter)
targets = defaultdict(Counter)
for op,*v in word['program']:
    if op == 'MOVE':
        c,d = v[-2:]
        assert grade(c,d)>0
        paid[c][d] += 1
        paid[d][c] += 1
for c,d in zip(word['start'][222:],word['final'][222:]):
    assert grade(c,d)>0
    targets[c][d] += 1
    targets[d][c] += 1
endpoints=set(word['start']+word['final'])
main=set(word['start'][:222]+word['final'][:222])
charts = sorted((endpoints-main) if a.public else (body.keys()-endpoints), key=lambda c:(sum(paid[c].values()),c))
k = Fraction('0.003879928046155')
@cache
def price_hist(hist):
    return price['moment']({i:36*n for i,n in enumerate(hist) if n},k)
result = dict(input=word_path.name,mode='helper-endpoint' if a.public else 'internal',pool=[len(charts),len(body)-1],tested=0,admitted=0,neutral=0,next_case=None,hit=None)
for c in charts:
    cs = sorted(paid[c].keys() | targets[c].keys())
    old = [0]*9
    for n in cs:
        old[grade(c,n)] += paid[c][n]-targets[c][n]
    for d in sorted(body.keys()-{c}):
        if time.monotonic()-start > 60:
            result['next_case']=[c,d]
            break
        result['tested']+=1
        hist=old.copy()
        for n in cs:
            g=grade(d,n)
            if g<0 or (targets[c][n] and g==0):
                break
            if g:
                hist[g] -= paid[c][n]-targets[c][n]
        else:
            result['admitted']+=1
            if not any(hist):
                result['neutral']+=1
            else:
                margin=price_hist(tuple(hist))
                if margin[0]>0:
                    result['hit']=dict(chart=c,replacement=d,old_hist=old,signed_change=hist,
                                       net_36=price['decimal_interval'](margin,22),incident=dict(paid[c]),
                                       endpoints=dict(targets[c]))
                    break
    if result['hit'] or result['next_case']:
        break
result['seconds']=time.monotonic()-start
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
