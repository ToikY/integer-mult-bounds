#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent literal replay of single-packet perturbations for (238, 672)."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import runpy
import signal
from time import monotonic

ENGINE = '36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349'
OWNERS = (238, 672)
TARGET = sum(1 << i for i in OWNERS)


def reduce_row(basis, row, carry=0):
    while row:
        pivot = row & -row
        if pivot not in basis:
            break
        saved, carried = basis[pivot]
        row ^= saved
        carry ^= carried
    return row, carry


def insert(basis, row, carry):
    row, carry = reduce_row(basis, row, carry)
    if row:
        basis[row & -row] = row, carry
        return 0
    return carry


def labels(bits):
    return [i for i in range(bits.bit_length()) if (bits >> i) & 1]


def verify(package):
    engine = package / 'sources/binary_operator.py'
    assert sha256(engine.read_bytes()).hexdigest() == ENGINE
    op = runpy.run_path(str(engine))
    word = op['load_json'](package / 'sources/WORD.json.gz', op['WORD_GZIP'], True)
    assert op['canonical_hash'](word) == op['WORD']
    atlas = op['Atlas'](word['frames'])
    forward, adjoint = [op['run_tape'](word, atlas, r) for r in (False, True)]
    for reverse, tape in enumerate((forward, adjoint)):
        assert tape.output == op['expected_operator'](reverse) and tape.dirty == 3554
    basis = {}
    for obs in forward.stock[8]:
        insert(basis, obs.row, 1 << obs.label)
        residual, relation = reduce_row(basis, TARGET)
        if not residual:
            break
    else:
        raise ValueError('target has no reader')
    cut = obs.time
    stock_without = {}
    for item in forward.stock[8]:
        if item.time < cut:
            insert(stock_without, item.row, 0)
    assert reduce_row(stock_without, TARGET)[0] != 0
    sends = [p for p in forward.packets.values() if p.source == 8 and p.clock > cut]
    locations = {p.clock:1 << j for j, p in enumerate(sends)}
    n = word['public']
    cells = [0] * (n + word['owned_fields'])
    observations = defaultdict(list)
    for i, chart in enumerate(word['start']):
        observations[chart].append((-1, 1 << i, 0))
    changed_charts = [set() for p in sends]
    changed_packets = [0 for p in sends]
    packet = n
    for clk, (kind, a, *args) in enumerate(word['program']):
        if kind == 'MOVE':
            pulse = cells[a] ^ locations.get(clk, 0)
            cells[a] = pulse
            obs = forward.packets[packet]
            assert (obs.clock, obs.source, obs.receiver) == (clk, *args)
            observations[obs.receiver].append((clk, obs.arrival.row, pulse))
            for j in labels(pulse):
                changed_charts[j].add(obs.receiver)
                changed_packets[j] += 1
            packet += 1
        elif kind == 'ADD':
            cells[a] ^= cells[args[0]]
        elif kind == 'SWAP':
            b, = args
            cells[a], cells[b] = cells[b], cells[a]
        else:
            assert kind in ('INIT', 'CLEAR')
            cells[a] = 0
    first = [dict() for p in sends]
    for c, items in observations.items():
        basis = {}
        for time, row, pulse in items:
            # Without restricting the clock, any combination of cached chart
            # reads is legal. A null baseline row with odd pulse acquires parity.
            newly = insert(basis, row, pulse)
            for j in labels(newly):
                first[j].setdefault(c, time)
    cases = []
    for j, p in enumerate(sends):
        col = sum(1 << i for i, mask in enumerate(cells[:n]) if mask & (1 << j))
        assert col == adjoint.packets[p.arrival.label].arrival.row
        future_pass = []
        for c, time in sorted(first[j].items()):
            future = {}
            for s in forward.packets.values():
                if s.source == c and s.clock > time:
                    insert(future, adjoint.packets[s.arrival.label].arrival.row, 0)
            for i, chart in enumerate(word['final']):
                if chart == c:
                    insert(future, 1 << i, 0)
            if not reduce_row(future, col ^ TARGET)[0]:
                future_pass.append(c)
        cases.append(dict(send=p.arrival.label, clock=p.clock, receiver=p.receiver,
                          changed_charts=sorted(changed_charts[j]), changed_packets=changed_packets[j],
                          terminal_column=hex(col), earliest_relations=first[j], compensation=future_pass))
    # Corrupt the pulse on the later of two identical old observations; the
    # null relation must then acquire it. Suppressing the pulse removes it.
    for mask in (0, (1 << len(sends)) - 1):
        basis = {}
        assert insert(basis, TARGET, 0) == 0
        assert insert(basis, TARGET, mask) == mask
    orig = [atlas.grade(word['start'][i], word['final'][i]) for i in OWNERS]
    flip = [atlas.grade(word['start'][i], word['final'][j]) for i, j in zip(OWNERS, reversed(OWNERS))]
    return dict(engine=ENGINE, word_gzip=op['WORD_GZIP'], canonical_word=op['WORD'],
                read_clock=cut, read_labels=labels(relation), source_obs_before_cut_residual=hex(reduce_row(stock_without,TARGET)[0]),
                baseline_rows=n, dirty_per_direction=3554, observed_charts=len(observations),
                terminal_owner_grades=orig, exchanged_owner_grades=flip, cases=cases,
                corruption_control='duplicate two target rows, toggle every individual pulse bit: exactly toggled bits detected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('package', type=Path)
    parser.add_argument('primary', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    signal.alarm(60)
    start = monotonic()
    receipt = verify(args.package)
    primary = json.loads(args.primary.read_bytes())
    assert primary['status'] == 'exhausted' and primary['restart'] is None
    assert (receipt['read_clock'],receipt['read_labels']) == (primary['first_read_clock'],primary['parity_labels'])
    assert [[c['send'],c['clock'],c['receiver']] for c in receipt['cases']] == primary['eligible_sends']
    assert len(primary['cases']) == len(receipt['cases'])
    for independent, case in zip(receipt['cases'], primary['cases']):
        assert case['complete'] and (independent['send'],independent['changed_charts'],independent['terminal_column']) == (case['send'],case['changed_charts'],case['column'])
        assert list(independent['earliest_relations'].items()) == [(r['chart'],r['cut']) for r in case['zero_relations']]
        assert not independent['compensation']
    receipt['primary_match'] = True
    receipt['seconds'] = monotonic() - start
    args.out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['read_clock'],[(c['send'],len(c['changed_charts']),c['changed_packets']) for c in receipt['cases']],receipt['terminal_owner_grades'],receipt['exchanged_owner_grades'],receipt['seconds'])
