#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Literal chart-270 funded split check; all clocks are zero-based."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import runpy
import signal
from time import monotonic

PINS = {
    'sources/WORD.json.gz': 'd28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9',
    'sources/binary_operator.py': '36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349',
    'sources/bit_native.py': '4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e',
}
MODIFIED = 'b3faa53e42b1952148c3df462228292109f12b44ed528ffd39ce96503be2a14d'


def rational_rank(rows):
    pivots = {}
    for row in rows:
        row = list(map(Fraction, row))
        for j in range(len(row)):
            x = row[j]
            if not x:
                continue
            if j not in pivots:
                pivots[j] = [z/x for z in row]
                break
            row = [a - x*b for a, b in zip(row, pivots[j])]
    return len(pivots)


def rank2(vectors):
    pivots = {}
    for row in vectors:
        while row:
            b = row & -row
            if b not in pivots:
                pivots[b] = row
                break
            row ^= pivots[b]
    return len(pivots)


def apply_to_column(rows, column):
    return sum(((x & column).bit_count() % 2) << i for i, x in enumerate(rows))


def constraints(column, end, start, inverse_rows, n):
    preimage = apply_to_column(inverse_rows, column)
    return (column & ~end) | ((preimage & ~start) << n)


def main(package):
    for path, digest in PINS.items():
        assert sha256((package / path).read_bytes()).hexdigest() == digest, path
    op = runpy.run_path(str(package / 'sources/binary_operator.py'))
    graph = runpy.run_path(str(package / 'sources/bit_native.py'))
    word = op['load_json'](package / 'sources/WORD.json.gz', op['WORD_GZIP'], True)
    assert op['canonical_hash'](word) == op['WORD']
    atlas = op['Atlas'](word['frames'])
    n = word['public']
    assert n == 680 and word['program'][157] == ['MOVE', 724, 8, 328]
    old = [op['run_tape'](word, atlas, reverse) for reverse in (False, True)]
    word['program'][157:158] = [['MOVE', 724, 8, 270], ['MOVE', 724, 270, 328]]
    assert op['canonical_hash'](word) == MODIFIED
    taps = [op['run_tape'](word, atlas, reverse) for reverse in (False, True)]
    for r in (0, 1):
        assert old[r].output == taps[r].output == op['expected_operator'](r)
        assert old[r].dirty == taps[r].dirty == 3554
        assert len(old[r].packets) == 2874 and len(taps[r].packets) == 2875
    # Cross-check packet identification and port/path grades against the source engine.
    s, f, edges, rows, clocks = graph['extract'](word)
    assert [(k, edges[k], clocks[k]) for k in (724, 725)] == [(724, (8,270),157),(725,(270,328),158)]
    columns = graph['basis'](s, edges, rows, sorted(edges,key=clocks.get))
    assert all(columns[k] == v.arrival.row for k, v in taps[1].packets.items())
    frames = {int(k):v['B'] for k,v in word['frames'].items()}

    @cache
    def distance(a,b):
        x, y = frames[a], frames[b]
        # Direct rational row-space dimension; independent of dual annihilators.
        if rational_rank(x+y) != max(len(x),len(y)):
            return 0
        return abs(len(x)-len(y))

    assert (distance(8,328),distance(8,270),distance(270,328)) == (5,3,2)
    tested = list(range(222,n))
    grade8 = [h for h in tested if distance(s[h],f[h]) == 8]
    eligible = [h for h in grade8 if distance(s[h],270) == distance(270,f[h]) == 4]
    cohorts = {(s[h],f[h]) for h in eligible}
    assert cohorts == {(0,1)}
    cases = []
    for reverse in (0,1):
        earlier = taps[reverse]
        later = taps[1-reverse]
        start = f if reverse else s
        end = s if reverse else f
        begin, finish = (1,0) if reverse else (0,1)
        now = len(word['program']) -1-158 if reverse else 157
        mask_a = sum(1 << i for i in start if start[i] == begin)
        mask_b = sum(1 << i for i in end if end[i] == finish)
        stock = [x for x in earlier.stock[270] if x.time <= now]
        future = [(p.arrival.label, later.packets[p.arrival.label].arrival.row) for p in earlier.packets.values()
                  if p.source == 270 and p.arrival.time > now]
        future += [(~i,1<<i) for i in end if end[i] == 270]
        vectors = [v for _,v in future]
        # This baseline transfer is involutory. Use the literal matrix rows as
        # the inverse on columns (not their transpose).
        basis_images = [apply_to_column(earlier.output,1<<i) for i in range(n)]
        assert all(apply_to_column(earlier.output,v) == 1<<i for i,v in enumerate(basis_images))
        response_rank = rank2(vectors)
        constraints_rank = rank2(constraints(v,mask_b,mask_a,earlier.output,n) for v in vectors)
        assert constraints_rank == response_rank
        # If an arbitrary new unit response for an eligible helper were allowed,
        # it must survive both endpoint restrictions: this control adds one dimension.
        h = eligible[0]
        assert constraints(1<<h,mask_b,mask_a,earlier.output,n) == 0
        assert rank2(vectors+[1<<h])-constraints_rank == 1
        cases.append(dict(reverse=bool(reverse),cut=now,endpoints=[begin,finish],
                          start_owners=mask_a.bit_count(),end_owners=mask_b.bit_count(),
                          stock_labels=[o.label for o in stock],future_labels=[k for k,_ in future],
                          response_rank=response_rank,endpoint_constraint_rank=constraints_rank,
                          supported_response_dimension=response_rank-constraints_rank,
                          granted_unit_control_owner=h,granted_unit_supported_dimension=1))
    return dict(pins=PINS,archive_head='6b18f13fcb612eadb2eb0df450a4da344013585f',old=op['WORD'],
                splice=MODIFIED,old_new_packets=[2874,2875],old_new_path_grades=[[5],[3,2]],
                public_maps_checked=['old forward','new forward','old adjoint','new adjoint'],
                dirty_retirements_each=3554,checked_packet_columns=2875,tested=tested,
                grade_eight=grade8,geometry=eligible,cohorts=sorted(cohorts),cuts=cases,
                orientation_owner_exclusions=2*len(eligible),unresolved_within_scope=0,
                higher_gates='q/k pairing, construction and complete pricing skipped: no supported pulse')


if __name__ == '__main__':
    ap=ArgumentParser()
    ap.add_argument('package', type=Path)
    ap.add_argument('primary_receipt', type=Path)
    ap.add_argument('out', type=Path)
    args=ap.parse_args()
    signal.alarm(60)
    start=monotonic()
    data=main(args.package)
    primary=json.loads(args.primary_receipt.read_bytes())
    for key in ('tested','grade_eight','geometry','splice'):
        assert data[key] == primary[key]
    assert primary['status']=='exhausted' and primary['next_owner'] is None
    assert [(h,r,'no_pulse') for h in data['geometry'] for r in (0,1)] == [tuple(x) for x in primary['cases']]
    data['primary_match']=True
    data['seconds']=monotonic()-start
    args.out.write_text(json.dumps(data,indent=2)+'\n')
    print(len(data['tested']),len(data['geometry']),data['orientation_owner_exclusions'],
          [(z['response_rank'], z['endpoint_constraint_rank'],len(z['future_labels'])) for z in data['cuts']],data['seconds'])
