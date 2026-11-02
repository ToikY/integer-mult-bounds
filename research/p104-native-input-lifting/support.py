"""Read the pinned word and open the unchanged checker chain.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The archive reader and checker chain retain the credits in NOTICE.
"""
from contextlib import ExitStack, contextmanager
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/p104-retained-operand-descent/'
WORD = 'research/p104-frontier-compression-2/WORD.json.gz'
INPUTS = {WORD, *(SOURCE + name for name in
                 ('sources.py', 'SOURCES.json', 'inputs/pr5827-source.tar', 'pricing.py'))}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin['sha256'], 'Exact source SHA256: ' + pin['path'])
    blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
    need(sha1(blob).hexdigest() == pin['git_blob'], 'Exact source Git blob: ' + pin['path'])


def inputs():
    pins = [pin for pin in read(HERE / 'SOURCES.json')['files'] if pin['usage'] == 'input']
    need(len(pins) == len(INPUTS) and {p['path'] for p in pins} == INPUTS,
         'Complete live source inventory')
    out = {}
    for pin in pins:
        raw = (ROOT / pin['path']).read_bytes()
        authenticate(raw, pin)
        out[pin['path']] = raw
    return out


@contextmanager
def checkers():
    inputs()
    source = load(ROOT / SOURCE / 'sources.py', 'lift_source_reader')
    with ExitStack() as contexts:
        parent = contexts.enter_context(source.sources())
        cursor = contexts.enter_context(load(parent / 'sources.py', 'lift_source_top').sources())
        for depth in range(7):
            reader = load(cursor / 'sources.py', 'lift_source_' + str(depth))
            cursor, root = contexts.enter_context(reader.sources())
        local = load(parent / 'local.py', 'local')
        local.ROOT = root
        yield local, root
