"""Check the four lifts, native maps, complete price and compiler.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged proof engines and source word retain the credits in NOTICE.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import gzip
import json
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
STATUS = 'PASS_P104_NATIVE_INPUT_LIFTING_KAPPA_003129111'
PROTECTED = {41, 42, 65, 106, 240, 400, 401, 403, 405, 410, 741,
             57, 81, 92, 224, 225, 227, 229, 234, 742}
DIRECTIONS = [
    (496, {496: '1', 639: '-1', 643: '-1/2'},
     {496: '1', 639: '-1', 643: '-1/2'}),
    (649, {649: '1', 648: '-1'}, {649: '1', 648: '-1', 198: '1'}),
    (663, {663: '1', 665: '-1'}, {663: '1', 665: '-1', 179: '1/2'}),
    (508, {508: '1', 631: '-1', 635: '-1/2'},
     {508: '1', 631: '-1', 635: '-1/2'}),
]


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid control accepted')


def delta(after, before):
    out = Counter(after)
    out.subtract(before)
    return {rank: count for rank, count in out.items() if count}


def protected_events(word):
    return [e for e in word['program'] if e[1] in PROTECTED or
            (e[0] in ('ADD', 'COPY') and e[2] in PROTECTED)]


def preparation(L, source, word):
    records = []
    occupied = set()
    main = set(source['live']) | {r + 112 for r in source['live']}
    for primary, h, a in DIRECTIONS:
        h, a = ({r: Q(q) for r, q in row.items()} for row in (h, a))
        L.need(h[primary] == a[primary] == 1 and not occupied.intersection(h),
               'Independent unit input directions')
        occupied.update(h)
        L.need(all(r not in main | PROTECTED and source['initial'][r] == 3 and
                   source['final'][r] == 127 for r in h), 'Only full helper inputs in each basis')
        values = [h.get(r, Q(0)) for r in range(source['public'] + source['owned_fields'])]
        departures, first = {}, {}
        for event in source['program']:
            op, r = event[:2]
            if op == 'MOVE' and event[2] == 3 and not event[4]:
                L.need(r not in first, 'One departure from the initial chart')
                first[r] = event[3]
                if values[r]:
                    departures[r] = values[r]
            elif op in ('INIT', 'CLEAR'):
                values[r] = Q(0)
            elif op == 'SCALE':
                values[r] *= Q(event[2])
            elif op == 'COPY':
                values[r] = Q(event[3]) * values[event[2]]
            elif op == 'ADD':
                values[r] += Q(event[3]) * values[event[2]]
        L.need(departures == a, 'Exact initial preparation response')
        frame = word['initial'][primary]
        common = L.span(word['frames'][frame])
        L.need(all(common <= L.span(source['frames'][first[r]]) for r in a),
               'Common native input subspace')
        records.append({'primary': primary, 'frame': frame, 'basis': word['frames'][frame],
                        'input_direction': h, 'departure_response': a})
    return records


def word_controls(L, word):
    controls = {}
    bad = deepcopy(word)
    bad['initial'][496] = 3
    controls['old_input_chart'] = reject(lambda: L.replay(bad))
    edits = [
        ('missing_first_carrier_subtraction', ['ADD', 639, 643, '-2', 3], None),
        ('missing_second_carrier_subtraction', ['ADD', 631, 635, '-2', 3], None),
        ('wrong_649_injection', ['ADD', 198, 649, '1', 597], ['ADD', 198, 649, '-1', 597]),
        ('wrong_663_injection', ['ADD', 179, 663, '1/2', 105], ['ADD', 179, 663, '-1/2', 105]),
        ('missing_output_basis', ['ADD', 635, 508, '1/2', 127], None),
        ('missing_carrier_move', ['MOVE', 635, 3, 1093, False], None),
    ]
    for label, event, replacement in edits:
        bad = deepcopy(word)
        L.need(bad['program'].count(event) == 1, 'Unique control event: ' + label)
        i = bad['program'].index(event)
        bad['program'][i:i+1] = [] if replacement is None else [replacement]
        controls[label] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['frames'][1093] = [1, 2, 4]
    controls['wrong_intersection'] = reject(lambda: L.replay(bad))
    return controls


def run(build_only):
    from support import SOURCE, WORD, authenticate, checkers, inputs, load, need, read
    from construct import construct, payload

    raw = inputs()
    source = json.loads(gzip.decompress(raw[WORD]))
    word = construct(source)
    need(gzip.decompress((HERE / 'WORD.json.gz').read_bytes()) == payload(word),
         'Every regenerated payload byte')
    need(all(type(e[4]) is bool for e in word['program'] if e[0] == 'MOVE'),
         'Boolean ownership flags')
    need(protected_events(word) == protected_events(source) and
         word['frames'][1091:1093] == source['frames'][1091:1093],
         'Protected events and frames unchanged')
    text = raw[SOURCE + 'pricing.py'].decode()
    for before, after in read(HERE / 'PRICING-EDITS.json'):
        need(text.count(before) == 1, 'Unique declared price edit')
        text = text.replace(before, after)
    need(text == (HERE / 'pricing.py').read_text(), 'Exact declared price edits')
    with checkers() as (L, root):
        directions = preparation(L, source, word)
        baseline, local = L.replay(source), L.replay(word)
        paid_delta, target_delta = delta(local['paid'], baseline['paid']), delta(local['helpers'], baseline['helpers'])
        need(paid_delta == {1: 1, 2: 1, 3: 1, 4: 2, 5: -4}, 'Exact local paid change')
        need(target_delta == {6: 1, 8: 3, 9: -4}, 'Exact productive target debit')
        need(tuple(local[k] for k in ('public_inputs', 'owned_fields', 'owned_lifetimes',
                                     'peak_owned_fields', 'real_scalar_allowance', 'paid_rank_mass')) ==
             (770, 29, 32, 13, 127088, 5946), 'Exact local inventory')
        controls = word_controls(L, word)
        print('PASS regeneration, input bases, arbitrary inputs, ownership and controls', flush=True)
        if build_only:
            return None
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401,
             'Every input column and output coefficient')
        print('PASS separate dense transpose', flush=True)
        native = L.native(word)
        C = load(root / 'research/p104-productive-controller/caller.py', 'lift_caller')
        caller = C.construct()
        need(caller == read(root / 'research/p104-productive-controller/CONTROLLER.json'),
             'Exact physical caller')
        physical = C.physical(caller, word)
        print('PASS native maps, absolute phases and complete physical caller', flush=True)
        P = load(HERE / 'pricing.py', 'lift_price')
        price = P.run(local, native, caller, physical)
        need(price['raw_root_interval'] ==
             ['78227955453/25000000000000', '312911821813/100000000000000'],
             'Exact rational crossing interval')
        E = load(root / 'research/higher-moment-strictification/verify.py', 'lift_comparison')
        old_paid = {int(r): n for r, n in price['paid'].items()}
        old_targets = {int(r): n for r, n in price['targets'].items()}
        for before, change in ((old_paid, paid_delta), (old_targets, target_delta)):
            for rank, count in change.items():
                before[rank] -= 18 * count
        old_margin = E.moment(old_targets, 1 - P.KAPPA)[1] - E.moment(old_paid, 1 - P.KAPPA)[0]
        need(old_margin < 0, 'The full source profile fails at the new claim')
        controls.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][3] -= 1
        controls['unpaid_carrier_move'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        bad['helpers'][6] -= 1
        controls['missing_target_debit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        for pin in read(HERE / 'SOURCES.json')['files']:
            if pin['usage'] == 'input':
                data = raw[pin['path']]
                controls['damaged_' + pin['path']] = reject(
                    lambda data=data, pin=pin: authenticate(bytes([data[0] ^ 1]) + data[1:], pin))
        print('PASS two interval engines, complete costs, compiler, outer checks and controls', flush=True)
        return P.encode(dict(
            status=STATUS, base_commit=read(HERE / 'SOURCES.json')['base_commit'],
            events=len(word['program']), directions=directions, source_local=baseline, local=local,
            paid_delta=paid_delta, target_delta=target_delta, separate_columns=columns, native=native,
            physical_caller=physical, complete_cost=price, source_margin_upper_at_new_claim=old_margin,
            controls=controls,
            limits=['All five inherited framework assumptions remain.',
                    'The uniform word and rounded multiplier are not materialized.',
                    'Author checks do not establish independent acceptance.',
                    'The selected frontier is unchanged.']))


def main():
    with tempfile.TemporaryDirectory(prefix='native-input-lift-cache-') as cache:
        sys.pycache_prefix = cache
        sys.path.insert(0, str(HERE))
        from support import need, read
        result = run('--build-only' in sys.argv)
    if result is not None:
        if '--write' in sys.argv:
            (HERE / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
        else:
            need(read(HERE / 'RESULT.json') == result, 'Exact retained result')
    print(STATUS + ('_BUILD' if result is None else ''), flush=True)


if __name__ == '__main__':
    main()
