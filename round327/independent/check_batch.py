#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the second disjoint 64-pair batch using the hash-locked primal verifier."""
from argparse import ArgumentParser
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

PREDECESSOR = '4d74c9cf6a76d90ef5c5fc1d84f97547d7ecaa67101e13c893feeb982fc17047'


def replay(upstream, word, out):
    source = upstream.read_bytes()
    assert sha256(source).hexdigest() == PREDECESSOR
    text = source.decode()
    # The numerical methods and the 60 s clock remain the pinned predecessor's.
    # Change the starting pair and correct the remaining work across both rounds.
    changes = [
        ('for u, v in pairs[:64]:', 'for u, v in pairs[64:128]:'),
        ('if not stopped and len(pairs)>64:', 'if not stopped and len(pairs)>128:'),
        ("report['unvisited_dimensions']=9*len(pairs)-len(visited)",
         "report['unvisited_dimensions']=9*(len(pairs)-64)-len(visited)\n"
         "    report['start_pair_offset']=64\n"
         "    report['previously_tested_dimensions']=576"),
    ]
    for old, new in changes:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    sys.argv = [str(upstream),str(word),str(out)]
    exec(compile(text,str(upstream),'exec'),{'__name__':'__main__'})


def compare(independent, primary):
    independent = json.loads(independent.read_bytes())
    graph = json.loads(primary.read_bytes())
    assert independent['word_sha256'] == graph['word']
    assert Decimal(independent['k']) == Decimal(graph['kappa'])
    assert independent['total_pairs'] == graph['pool']
    assert independent['ranked_pairs'][64:128] == [row[1:] for row in graph['roster']]
    assert len(independent['cases']) == len(graph['cases'])
    dispositions = Counter()
    compared_intervals = 0
    for entry, claim in zip(independent['cases'],graph['cases']):
        assert entry['pair']+[entry['dimension']] == claim[:3]
        lo,hi = map(Fraction,entry['raw_saving_36'])
        geom = entry['feasible']
        old = Counter({int(r):n for r,n in entry['old_paid'].items()})
        new = Counter({int(r):n for r,n in entry['new_paid'].items()})
        old.subtract(new)
        hist = sorted([r,n] for r,n in old.items() if n)
        if len(claim)>4:
            assert hist == claim[4]
            graph_lo,graph_hi = [Fraction(n,graph['price_scale']) for n in claim[5]]
            assert max(lo,graph_lo) <= min(hi,graph_hi)
            compared_intervals += 1
        status = claim[3]
        if status == 'infeasible':
            assert not geom
        elif status == 'excluded-by-price':
            assert hi <= 0 or not hist
        else:
            assert geom
            assert (lo > 0 if status == 'positive' else hi < 0 if status == 'negative'
                    else not hist if status == 'neutral' else lo <= 0 <= hi)
        classification = 'impossible' if not geom else 'positive' if lo>0 else 'negative' if hi<0 else 'neutral' if not hist else 'uncertain'
        dispositions[(status,classification)] += 1
    winning = independent['strict_witness']
    assert graph['witness'] == (winning['pair']+[winning['dimension']] if winning else None)
    return dict(independent=independent['status'],primary=graph['status'],counts=
                [[a,b,v] for (a,b),v in sorted(dispositions.items())],
                price_intersections=compared_intervals,tested_dimensions=len(graph['cases']),
                remaining_dimensions=independent['unvisited_dimensions'],witness=graph['witness'])


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='mode',required=True)
    run=sub.add_parser('run')
    run.add_argument('predecessor',type=Path);run.add_argument('word',type=Path);run.add_argument('out',type=Path)
    check=sub.add_parser('compare')
    check.add_argument('independent',type=Path);check.add_argument('primary',type=Path);check.add_argument('out',type=Path)
    args=parser.parse_args()
    if args.mode=='run':
        replay(args.predecessor,args.word,args.out)
    else:
        result=compare(args.independent,args.primary)
        args.out.write_text(json.dumps(result,indent=2)+'\n')
        print(result)
