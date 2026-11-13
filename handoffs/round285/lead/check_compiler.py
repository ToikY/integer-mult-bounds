"""Replay the exact physical binder and probe the proposed partial-volume opcode."""
from collections import Counter
from copy import deepcopy
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, version_info

PINS = {
    'inputs/7113-CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/7481-APPLICATION.json': '1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799',
    'inputs/7481-WORD.json.gz': 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9',
    'compiler/upstream_application.py': 'd98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184',
    'compiler/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
    'compiler/check_odd_physical_binding.py': '5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98',
    'compiler/check_odd_fixed_tape_counts.py': 'e6246e9f8fbeae3077d82e585eafd3647c1a8758c58f33c7c13e7efa6c1e42bb',
    'compiler/check_odd_partial_admission.py': '35bd43f18bae916363fda120ff8ada7460ffb7920821596f599c88a556398117',
    'compiler/SIGNED-RESULT.json': 'e5c8d8c0cf4d3f3fc60ffe70eb084cf6c9eadf8e646c74b48762501bf5367474',
}


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    root = Path(argv[1]).resolve()
    results = {}

    def cap(_signum, _frame):
        print(json.dumps(dict(status='UNRESOLVED_CAP', completed=results), sort_keys=True), flush=True)
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(30)
    raw = {path: (root / path).read_bytes() for path in PINS}
    assert {path: sha256(data).hexdigest() for path, data in raw.items()} == PINS
    caller = json.loads(raw['inputs/7113-CALLER.json'])
    application = json.loads(raw['inputs/7481-APPLICATION.json'])
    native = decompress(raw['inputs/7481-WORD.json.gz'])
    assert sha256(native).hexdigest() == application['candidate_canonical_sha256']
    word = json.loads(native)
    frozen = json.loads(raw['compiler/SIGNED-RESULT.json'])['checks']
    binding = frozen['ODD-PHYSICAL-BINDING.json']
    invoice = frozen['ODD-ADMISSION-PARTIAL.json']['invoice']
    phases = json.loads(raw['compiler/DATA-PHASES.json'])
    source = root / 'compiler/upstream_application.py'
    adapter = raw['compiler/check_odd_physical_binding.py'].decode()
    start = adapter.index('a=source.read_text()')
    stop = adapter.index('invoice={"P":rec["paid"]')
    owners = set(word['live']) | {r+112 for r in word['live']}
    owners |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    stage_count = caller['stages']
    env = dict(source=source, stages=stage_count, ambient=9+8*stage_count,
               helper_count=word['public']-len(owners),
               main_count=sum(kind['roles']*len(kind['ports']) for kind in caller['types'].values()))
    exec(compile(adapter[start:stop], 'exact #7481 physical adapter', 'exec'), env)
    assert sha256(env['a'].encode()).hexdigest() == binding['patched_application_sha256']
    bind = env['env']['complex_application']
    exact = bind(word, caller, {'invoice': invoice}, phases)
    assert json.loads(json.dumps(exact)) == binding['occurrence_and_geometry']
    results['baseline'] = exact['paid_positions']
    assert caller['types']['B']['ports'][0] == 15 and word['ports'][15] == 81
    for clock, role in ((1339, 68), (1340, 69)):
        assert caller['events'][clock] == ['B', 'IDLE_ODD', role, [8], -1]

    def reject(replacement, billed, expected):
        candidate = deepcopy(caller)
        candidate['events'][1339] = replacement
        try:
            bind(word, candidate, {'invoice': billed}, phases)
        except ValueError as error:
            assert str(error) == expected, str(error)
        else:
            raise AssertionError('mutation unexpectedly bound')

    reject(['B', 'IDLE_ODD', 68, [8], -1, {'rank': 13, 'volume': '11/8'}],
           invoice, 'one complete signed child')
    results['fractional_payload'] = 'one complete signed child'
    # The physical binder can ignore an unknown tag. Require it to fail the
    # actual paid occurrence/invoice equality, rather than claiming a tag error.
    billed = deepcopy(invoice)
    billed['P'] = dict(billed['P'])
    billed['P']['9'] -= len(caller['types']['B']['ports'])
    billed['P']['13'] = len(caller['types']['B']['ports'])
    reject(['B', 'IDLE_ODD_PARTIAL', 68, [8], -1, {'rank': 13, 'volume': '11/8'}],
           billed, 'independent P invoice')
    results['unknown_fractional_tag'] = 'independent P invoice'
    for name in ('check_odd_fixed_tape_counts.py', 'check_odd_partial_admission.py'):
        text = raw['compiler/' + name].decode()
        assert 'paid_positions' in text if name.endswith('counts.py') else 'P[8*len(e[3])+' in text
    alarm(0)
    print(json.dumps(dict(status='FIXED_GRAMMAR_EXCLUDES_PARTIAL_IDLE', port=15,
                          clocks=[1339, 1340], cap_seconds=30, pins=PINS,
                          outcomes=results, unresolved_outside_scope='changed supplier/compiler'),
                     sort_keys=True))


if __name__ == '__main__':
    main()
