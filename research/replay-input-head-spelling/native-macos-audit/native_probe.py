"""Native observations for PR3007; uses its public fixture, never edits its sources.

ToikY, with substantial OpenAI Codex assistance. Apache-2.0.
Credit Nick Petalas/PR3007 and Arham Tahir/PR2994.
Usage: python3.12 -I -B native_probe.py EXACT_PR3007_CHECKOUT
"""
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

HEAD = '3cb500b743f36e13d21b6a46f126846bf36bad32'
BASE = '836b19bfa309ceafbc8ee32a15e8c4b10dde7e11'
ROOT = Path(sys.argv[1]).resolve()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE, timeout=30)


need(platform.system() == 'Darwin', 'native macOS required')
need(git(ROOT, 'rev-parse', 'HEAD').decode().strip() == HEAD, 'wrong audit head')
closure = ['scripts/research_package.py', 'scripts/new_research_package.py',
           'scripts/find_overlap.py', 'scripts/research_baseline.py',
           'scripts/verify_selected_result.py', 'tests/test_research_git_spelling.py',
           'tests/test_research_onboarding.py', 'tests/test_research_input_paths.py']
closure += [p.relative_to(ROOT).as_posix()
            for p in sorted((ROOT / 'research/replay-input-head-spelling').iterdir()) if p.is_file()]
hashes = {}
for name in closure:
    raw = (ROOT / name).read_bytes()
    need(raw == git(ROOT, 'show', HEAD + ':' + name), 'working bytes drift: ' + name)
    hashes[name] = hashlib.sha256(raw).hexdigest()
# A fresh namespace prevents stale bytecode from bypassing authenticated sources.
cache = tempfile.TemporaryDirectory(prefix='native-spelling-pycache-')
sys.pycache_prefix = cache.name
sys.path.insert(0, str(ROOT / 'tests'))
from test_research_git_spelling import GitInputSpellingTests
from test_research_onboarding import PackageTests, package

rows = []
for mode, created_form in ((mode, form) for mode in ('false', 'true') for form in ('NFC', 'NFD')):
    fixture = GitInputSpellingTests('runTest')
    fixture.setUp()
    try:
        fixture.git('config', 'core.precomposeunicode', mode)
        nfc, nfd = 'src/caf\u00e9.json', 'src/cafe\u0301.json'
        fixture.write(nfc if created_form == 'NFC' else nfd, b'original unicode\n')
        need((fixture.root / nfd).exists(), 'NFC and NFD do not alias on fixture volume')
        need((fixture.root / nfc).samefile(fixture.root / nfd), 'Unicode aliases differ physically')
        need((fixture.root / 'SRC/DEP.json').samefile(fixture.root / 'src/dep.json'), 'case-sensitive fixture volume')
        fixture.commit()
        tree = fixture.git('ls-tree', '-r', '--name-only', '-z', 'HEAD').split(b'\0')
        exact = next(name for name in (nfc, nfd) if name.encode() in tree)
        alias = nfd if exact == nfc else nfc
        fixture.manifest('alpha', [alias])
        before = fixture.commit()
        fixture.write(exact, b'changed unicode\n')
        fixture.commit()
        diff = fixture.git('diff', '--no-renames', '--name-only', '-z', before, 'HEAD')
        need(diff == exact.encode() + b'\0', 'Unicode diff was not target-only')
        fixture.rejected(before, alias)
        fixture.manifest('alpha', [exact])
        need(fixture.selected(before) == ['research/alpha'], 'exact Unicode input did not select consumer')
        rows.append({'mode': mode, 'created_form': created_form, 'unicode_same_file': True, 'case_same_file': True,
                     'head_spelling': exact, 'head_utf8_hex': exact.encode().hex(),
                     'diff_nul_hex': diff.hex(), 'alias_rejected_without_output': alias,
                     'canonical_selected': ['research/alpha']})
    finally:
        fixture.doCleanups()

    rename = GitInputSpellingTests('runTest')
    rename.setUp()
    try:
        rename.git('config', 'core.precomposeunicode', mode)
        rename.test_case_only_rename_selects_both_exact_consumers()
        rows[-1]['case_rename_selected'] = ['research/alpha', 'research/beta']
        rows[-1]['case_rename_diff_nul_hex'] = rename.git(
            'diff', '--no-renames', '--name-only', '-z', 'HEAD^', 'HEAD').hex()
    finally:
        rename.doCleanups()

# Complete metadata, using the predecessor's same source-pinned fixture schema.
# Authenticate the baseline runner before contrasting the repaired validator.
old_raw = git(ROOT, 'show', BASE + ':scripts/research_package.py')
need(hashlib.sha256(old_raw).hexdigest() ==
     '51e8ee72b1c99de7060c4cc83aabcc54ff1a572bad31f31a6d0102dcc0aae0aa', 'baseline SHA drift')
with tempfile.TemporaryDirectory(prefix='native-spelling-baseline-') as tmp:
    old_path = Path(tmp) / 'baseline.py'
    old_path.write_bytes(old_raw)
    spec = importlib.util.spec_from_file_location('source_authenticated_baseline', old_path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    metadata = []
    canonical_metadata = []
    for mode, created_form in ((mode, form) for mode in ('false', 'true') for form in ('NFC', 'NFD')):
        fixture = PackageTests('runTest')
        fixture.setUp()
        try:
            git(fixture.root, 'config', 'core.precomposeunicode', mode)
            fixture.ready()
            (fixture.root / 'src').mkdir()
            (fixture.root / 'src/dep.json').write_text('dependency\n', encoding='utf-8')
            created_name = 'src/caf\u00e9.json' if created_form == 'NFC' else 'src/cafe\u0301.json'
            (fixture.root / created_name).write_text('unicode\n', encoding='utf-8')
            git(fixture.root, 'add', '--all')
            git(fixture.root, '-c', 'gc.auto=0', 'commit', '-qm', 'native dependencies')
            tree = git(fixture.root, 'ls-tree', '-r', '--name-only', '-z', 'HEAD').decode().split('\0')
            exact = next(n for n in ('src/caf\u00e9.json', 'src/cafe\u0301.json') if n in tree)
            alias = 'src/cafe\u0301.json' if exact == 'src/caf\u00e9.json' else 'src/caf\u00e9.json'
            path = fixture.target / 'VERIFY.json'
            manifest = json.loads(path.read_bytes())
            for name in ('SRC/dep.json', 'src/DEP.json', 'SRC/DEP.json', alias):
                manifest['inputs'] = ['input.txt', name]
                path.write_text(json.dumps(manifest), encoding='utf-8')
                old.validate(fixture.root, 'research/fixture')
                try:
                    package.validate(fixture.root, 'research/fixture')
                except ValueError as error:
                    need('exact Git-tracked input' in str(error), 'wrong rejection boundary')
                else:
                    raise ValueError('native metadata alias accepted: ' + name)
                metadata.append({'mode': mode, 'created_form': created_form, 'alias': name, 'baseline_accepts': True, 'repair_rejects': True})
            manifest['inputs'] = ['input.txt', 'src/dep.json', exact]
            path.write_text(json.dumps(manifest), encoding='utf-8')
            old.validate(fixture.root, 'research/fixture')
            package.validate(fixture.root, 'research/fixture')
            canonical_metadata.append({'mode': mode, 'created_form': created_form,
                                       'inputs': manifest['inputs'], 'baseline_pass': True, 'repair_pass': True})
        finally:
            fixture.doCleanups()

report = {'status': 'PASS_NATIVE_MACOS_HEAD_SPELLING', 'head': HEAD, 'baseline': BASE,
          'platform': platform.platform(), 'machine': platform.machine(),
          'python': platform.python_version(), 'git': git(ROOT, '--version').decode().strip(),
          'unicode_and_rename': rows, 'full_metadata_alias_comparisons': metadata,
          'canonical_metadata_fixtures': canonical_metadata, 'canonical_validator_calls': 8,
          'fresh_import_cache': True, 'source_sha256': hashes,
          'scope': 'Native macOS, precomposeunicode false/true, same-file aliases. No Windows, physical tracked-name collisions, concurrent writers, hosted CI or supplier claim.'}
print(json.dumps(report, indent=2, ensure_ascii=True))
cache.cleanup()
