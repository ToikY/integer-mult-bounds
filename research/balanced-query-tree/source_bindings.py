"""Authenticate the unchanged P104 source and open its pinned verifier chain.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The archive readers and source word are retained predecessor work.
"""
from contextlib import contextmanager, ExitStack
from hashlib import sha1, sha256
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/p104-retained-operand-descent'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_bytes())
    checked = 0
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT / pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source SHA256: ' + pin['path'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'],
             'Source Git blob: ' + pin['path'])
        checked += 1
    need(checked > 0, 'Nonempty authenticated source inventory')
    return checked


@contextmanager
def sources():
    checked = authenticate()
    sys.path.insert(0, str(SOURCE))
    source = load(SOURCE / 'sources.py', 'sources')
    constructor = load(SOURCE / 'construct.py', 'balanced_source_construct')
    with ExitStack() as contexts:
        parent = contexts.enter_context(source.sources())
        cursor = contexts.enter_context(source.load(parent / 'sources.py', 'balanced_source_top').sources())
        for depth in range(7):
            module = source.load(cursor / 'sources.py', 'balanced_source_' + str(depth))
            cursor, root = contexts.enter_context(module.sources())
        local = source.load(parent / 'local.py', 'local')
        local.ROOT = root
        word = constructor.construct(source.base_word())
        need(constructor.matches_shipped(word, (SOURCE / 'WORD.json.gz').read_bytes()),
             'Complete regenerated PR6167 payload')
        yield local, word, checked
