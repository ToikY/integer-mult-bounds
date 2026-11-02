"""Check that the shipped word is a price-null rearrangement of PR6167's word.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
The word, price and checker chain are PR6167's (Ali Romman) over PR6144 and PR5827; they are read
from the merged package research/p104-retained-operand-descent, authenticated by SOURCES.json pins.
"""
from collections import Counter
from contextlib import ExitStack
from pathlib import Path
import gzip
import json
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'p104-retained-operand-descent'
sys.path.insert(0, str(HERE))
from construct import matches_shipped

STATUS = 'PASS_P104_FRONTIER_SYMMETRIC_LADDERS_NO_NEW_KAPPA'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(path, pin):
    from hashlib import sha1, sha256
    raw = Path(path).read_bytes()
    need(sha256(raw).hexdigest() == pin['sha256'], 'Exact SHA256: ' + pin['path'])
    need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'],
         'Exact Git blob: ' + pin['path'])
    return raw


def chains(word):
    """Per public register: dimensions along its timeline, (initial, then every MOVE target)."""
    dim = [len(b) for b in word['frames']]
    out = {r: [dim[f]] for r, f in enumerate(word['initial'])}
    for e in word['program']:
        if e[0] == 'MOVE' and e[1] in out:
            out[e[1]].append(dim[e[3]])
    return out


def tax(chain, helper):
    """A register's net contribution to (paid - helpers) by rank: its jump sizes, minus its rank if it is a helper."""
    t = Counter(abs(y - x) for x, y in zip(chain, chain[1:]))
    if helper:
        t[chain[-1] - chain[0]] -= 1
    return t


def rearrangement(source, word):
    """Classify every public register whose timeline changed; the summed net rank tax must not move."""
    need(len(source['initial']) == len(word['initial']), 'Same public registers')
    main = set(source['live']) | {r + 112 for r in source['live']}
    old, new = chains(source), chains(word)
    kinds, delta = Counter(), Counter()
    for r in sorted(old):
        if old[r] == new[r] and source['initial'][r] == word['initial'][r] and source['final'][r] == word['final'][r]:
            continue
        helper = r not in main
        change = tax(new[r], helper)
        change.subtract(tax(old[r], helper))
        if helper and len(old[r]) == 2 and len(new[r]) == 2:
            kind = 'one-stop helper, endpoints moved'
            need(all(v == 0 for v in change.values()), 'A one-stop helper is price-null')
        elif Counter(abs(y - x) for x, y in zip(old[r], old[r][1:])) == Counter(abs(y - x) for x, y in zip(new[r], new[r][1:])) \
                and old[r][0] == new[r][0] and old[r][-1] == new[r][-1]:
            kind = 'same endpoints, same multiset of steps, stops reordered'
        else:
            kind = 'step multiset changed (cancels against the others)'
        kinds[kind] += 1
        for k, v in change.items():
            delta[k] += v
    need(all(v == 0 for v in delta.values()), 'Summed net rank tax unchanged')
    return dict(kinds)


def run():
    pins = {r['path']: r for r in json.loads((HERE / 'SOURCES.json').read_text())['files']}
    root_dir = HERE.parent.parent
    for name, pin in pins.items():
        if pin['usage'] == 'input':
            authenticate(root_dir / name, pin)
    base_raw = (BASE / 'WORD.json.gz').read_bytes()
    source = json.loads(gzip.decompress(base_raw))
    shipped = (HERE / 'WORD.json.gz').read_bytes()
    word = json.loads(gzip.decompress(shipped))
    need(matches_shipped(word, shipped), 'Canonical payload')
    need(word != source, 'A different word')
    changed = sorted(k for k in word if word[k] != source[k])
    need(set(word) == set(source) and changed == ['final', 'initial', 'program'],
         'Only initial frames, final frames and events differ: ' + str(changed))
    need(word['frames'] == source['frames'], 'Same frame table')
    main = set(source['live']) | {r + 112 for r in source['live']}
    moved = [r for r in range(len(word['initial']))
             if (word['initial'][r], word['final'][r]) != (source['initial'][r], source['final'][r])]
    need(moved and all(r not in main for r in moved), 'Only helper endpoints move')
    need(len(word['program']) == len(source['program']) == 22821, 'Exact event count')
    census = lambda p: Counter(e[0] for e in p)
    need(all(census(word['program'])[k] == census(source['program'])[k] for k in ('MOVE', 'INIT', 'CLEAR', 'SCALE')),
         'Same MOVE, INIT, CLEAR and SCALE census')
    kinds = rearrangement(source, word)
    differing = sum(1 for a, b in zip(source['program'], word['program']) if a != b)
    print('PASS %d helper endpoints moved, %d events differ; summed net rank tax unchanged: %s'
          % (len(moved), differing, json.dumps(kinds, sort_keys=True)), flush=True)
    with ExitStack() as contexts:
        S = load(BASE / 'sources.py', 'base_sources')
        parent = contexts.enter_context(S.sources())
        cursor = contexts.enter_context(load(parent / 'sources.py', 'base_source_top').sources())
        for depth in range(7):
            module = load(cursor / 'sources.py', 'base_source_' + str(depth))
            cursor, root = contexts.enter_context(module.sources())
        L = load(parent / 'local.py', 'local')
        L.ROOT = root
        baseline, local = L.replay(source), L.replay(word)
        for key in ('public_inputs', 'owned_fields', 'owned_lifetimes', 'peak_owned_fields'):
            need(local[key] == baseline[key], 'Unchanged replay field: ' + key)
        net = lambda d: {r: d['helpers'].get(r, 0) - d['paid'].get(r, 0) for r in set(d['helpers']) | set(d['paid'])}
        need({r: v for r, v in net(local).items() if v} == {r: v for r, v in net(baseline).items() if v},
             'Per-rank helpers minus paid calls unchanged')
        need(sum(local['paid'].values()) == sum(baseline['paid'].values()), 'Same number of paid moves')
        print('PASS replay: paid minus helper count is the same at every rank; paid and helper histograms differ', flush=True)
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All input columns')
        print('PASS separate transpose: 799 columns, 638,401 coefficients', flush=True)
        native = L.native(word)
        C = load(root / 'research/p104-productive-controller/caller.py', 'base_caller')
        caller = C.construct()
        physical = C.physical(caller, word)
        P = load(BASE / 'pricing.py', 'retained_operand_price')
        price = P.run(local, native, caller, physical)
        ref = json.loads((BASE / 'RESULT.json').read_text())['complete_cost']
        need(price['raw_root_interval'] == ref['raw_root_interval'], 'Same raw crossing')
        ranks = set(price['paid']) | set(price['targets']) | set(ref['paid']) | set(ref['targets'])
        for r in ranks:
            need(price['targets'].get(r, 0) - price['paid'].get(r, 0) == ref['targets'].get(r, 0) - ref['paid'].get(r, 0),
                 'Same net invoice at rank ' + str(r))
        need(sum(price['paid'].values()) == sum(ref['paid'].values()), 'Same paid call total')
        need(sum(price['targets'].values()) == sum(ref['targets'].values()), 'Same productive field total')
        print('PASS native maps, physical caller and complete price: same net invoice and raw crossing as PR6167', flush=True)
        return dict(status=STATUS, helper_endpoints_moved=len(moved), events_differing=differing, rearranged=kinds,
                    raw_root_interval=price['raw_root_interval'], paid=price['paid'], targets=price['targets'],
                    paid_pr6167=ref['paid'], targets_pr6167=ref['targets'],
                    local_paid=local['paid'], local_helpers=local['helpers'],
                    local_paid_pr6167=baseline['paid'], local_helpers_pr6167=baseline['helpers'],
                    net_by_rank={str(r): local['helpers'].get(r, 0) - local['paid'].get(r, 0) for r in sorted(set(local['helpers']) | set(local['paid']))})


def main():
    with tempfile.TemporaryDirectory(prefix='frontier-symmetric-ladders-') as cache:
        sys.pycache_prefix = cache
        result = run()
    result = json.loads(json.dumps(result))
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads((HERE / 'RESULT.json').read_text()) == result, 'Exact retained result')
    print(STATUS, flush=True)


if __name__ == '__main__':
    main()
