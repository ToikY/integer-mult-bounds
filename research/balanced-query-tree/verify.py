"""Replay the unchanged native source and the new complete caller.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import controller
import module_check
import physical
import pricing
from source_bindings import sources, need, SOURCE

STATUS = 'PASS_BALANCED_QUERY_TREE_KAPPA_00314933'


def run():
    module = module_check.run()
    word = controller.construct()
    need(pricing.encode(word) == json.loads((HERE/'CONTROLLER.json').read_bytes()), 'Complete emitted caller payload')
    caller = controller.replay(word)
    controls = controller.controls(word)
    print('PASS exact module, complete Laurent caller and failure controls', flush=True)
    with sources() as (L, local_word, source_count):
        local = L.replay(local_word)
        previous = json.loads((SOURCE/'RESULT.json').read_bytes())
        need(pricing.encode(local) == previous['local'], 'Unchanged complete PR6167 local invoice')
        columns = L.reverse_columns(local_word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All native input columns')
        print('PASS authenticated P104 word, ownership and separate dense transpose', flush=True)
        native = L.native(local_word)
        maps = physical.physical(word, local_word, L)
        need(maps['full_calls'] == 19 and maps['physical_contacts'] == 7904, 'All fresh native contacts')
        print('PASS native maps, absolute phases and every new main/idle target', flush=True)
        price = pricing.run(local, native, word, maps, L)
        print('PASS complete invoice, two interval engines, compiler and outer ledger', flush=True)
        return pricing.encode({'status': STATUS, 'source_files_authenticated': source_count,
                               'module': module, 'caller': caller, 'local': local,
                               'columns': columns, 'native': native, 'physical': maps,
                               'price': price, 'caller_controls': controls,
                               'assumptions': ['native_all_columns', 'owned_erasure', 'compiler',
                                               'precision_tape', 'analytic_recovery']})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.write_result:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    else:
        need(result == json.loads((HERE/'RESULT.json').read_bytes()), 'Exact complete receipt')
    print(STATUS)


if __name__ == '__main__':
    main()
