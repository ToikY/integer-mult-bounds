"""Compare independently materialized runtime and checker source inventories."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

BASE = Path.cwd()
PEER = BASE/"peer-source"
FREQUENCY = "research/frequency-weighted-native-multiplier"
OLD = BASE/"../../round402/independent/checkout/research/p104-weighted-ordinary-debit-11239"
NEW = BASE/"checkout/research/p104-weighted-capped-allocation-490950"
CHECKS = ("check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py")


def digest(body):
    return hashlib.sha256(body).hexdigest()


def inventory(root):
    return {path.relative_to(root).as_posix(): digest(path.read_bytes())
            for path in sorted(root.rglob("*")) if path.is_file()}


def changes(a, b):
    return {file: (a.get(file), b.get(file)) for file in sorted(a.keys() | b.keys())
            if a.get(file) != b.get(file)}


def materialize(package, work):
    shutil.copytree(PEER, work/"inputs", dirs_exist_ok=True)
    source = work/"inputs"/FREQUENCY
    runpy.run_path(str(package/"prepare.py"))["materialize"](source)
    for name in CHECKS:
        shutil.copyfile(package/name, source/name)
    runtime = work/"runtime"
    assert not runtime.exists()
    subprocess.run([sys.executable, "-IB", str(source/"bootstrap.py"), str(runtime)],
                   check=True, env={**os.environ, "GIT_CEILING_DIRECTORIES": str(BASE)})
    return inventory(runtime), inventory(work/"inputs"), (runtime/"installations.py").read_text()


origin = inventory(PEER)
with TemporaryDirectory(prefix="operator-images-", dir=BASE) as temporary:
    directory = Path(temporary)
    before_runtime, before_source, before_calendar = materialize(OLD, directory/"old")
    after_runtime, after_source, after_calendar = materialize(NEW, directory/"new")
runtime_diff = changes(before_runtime, after_runtime)
source_diff = changes(before_source, after_source)
assert set(runtime_diff) == {"installations.py"}
assert set(source_diff) == {FREQUENCY+"/"+name for name in
                            ("SOURCES.json", "check_cutoff.py", "check_ordinary_floor.py",
                             "check_stage_seam.py", "independent_price.py", "receipt.py",
                             "runtime.patch")}
before_line = 'TERMINAL = Profile((8192, 124863, 524288), 490639, Q(".00389821412325"))'
after_line = 'TERMINAL = Profile((8192, 124649, 524288), 490950, Q(".003898214283192"))'
assert before_calendar.count(before_line) == 1
assert before_calendar.replace(before_line, after_line, 1) == after_calendar
assert len(after_runtime) == len(before_runtime)
assert after_runtime["raw_binary_stage.py"] == "e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0"
assert after_runtime["strong-bit.json.gz"] == "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
print(json.dumps({"old_source_vs_archive": changes(origin, before_source),
                  "new_source_vs_old": source_diff,
                  "runtime_changed_files": runtime_diff,
                  "sole_changed_runtime_line": {"prior": before_line, "candidate": after_line},
                  "old_runtime_sha256": before_runtime,
                  "new_runtime_sha256": after_runtime}, indent=2, sort_keys=True))
