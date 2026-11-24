"""Apply the exact ordinary tariff solely to an authenticated Round 428 tree."""

from argparse import ArgumentParser
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import signal
from subprocess import run
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
PEER = Path("research/frequency-weighted-native-multiplier")
INSTALLATIONS = Path("research/tiered-native-multiplier/installations.py")
PINS = {
    "receipt.py": "c39a9f0e754348849a210a291989b68d234e7639633977b18f7b4afc231b94fe",
    "independent_price.py": "c78812589570aac1a18070ba74c60416aa1a2672789482d51b83082dd2bd72f9",
    "check_stage_seam.py": "dbaa72c655cc46e5db7264b6f7453a61f3e7ea0b3d76ba712f5e55746df09740",
    "runtime.patch": "72782749b01521fa307e4117eda263eeb21f3750dc4f0abcfd09354edf2bb8c8",
    "SOURCES.json": "434bdd0322622aa5dd7d592fe2b7fa2e19e5e741e2554ac094084164926708c2",
}
UNCHANGED = {
    "positive_debit.py": "0b81dbf6cca7397f540f4b525f059ffa4e6beef7106f756600963fd45e43d285",
    "check_ordinary_floor.py": "d66db3d6d01259216fc1823be7066e676541d820ea8a96a4c513a635e91eb244",
}
PREIMAGE = "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df"
OLD_IMAGE = "6dc565fad3b91bcb43ff71397897afcc54fd5f9d595a8f88b91234994d8e70be"
OLD_RESULT = "6894e85cec33111c46ca03a56ddad9a33cd913f267e4ec5c5d2ed95bc1adb8af"
OLD_RATE = "0.003900857312674"
NEW_RATE = "0.003900857313143"
SELECTOR = b'TERMINAL = Profile((31808, 502922, 7951907, 125730703, 134217727), 208653, Q(".003900857312674"), Q(1, 256))'
NEW_SELECTOR = SELECTOR.replace(b".003900857312674", b".003900857313143")


def digest(data):
    return sha256(data).hexdigest()


def authenticated(path, expected):
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise ValueError(f"Unexpected frozen source at {path.name!r}")
    return raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate manifest key {key!r}")
        result[key] = value
    return result


def replace_unique(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"Expected one source anchor, found {text.count(before)}: {before[:110]!r}")
    return text.replace(before, after, 1)


def image(preimage, patch, stage):
    with TemporaryDirectory(prefix="selector-", dir=stage) as temporary:
        target = Path(temporary) / "installations.py"
        target.write_bytes(preimage)
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(stage))
        run(["git", "apply", "--no-index", "--include=installations.py", "--whitespace=nowarn", "-"],
            cwd=temporary, env=env, input=patch, check=True, timeout=10)
        return target.read_bytes()


def inventory(root):
    files = {}
    for path in (root / "research").rglob("*"):
        if path.is_symlink():
            raise ValueError(f"A source symlink is outside this assembly: {path.relative_to(root)}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    return files


def materialize(frozen, stage):
    prior = {name: authenticated(frozen / PEER / name, pin) for name, pin in PINS.items()}
    for name, pin in UNCHANGED.items():
        authenticated(frozen / PEER / name, pin)
    preimage = authenticated(frozen / INSTALLATIONS, PREIMAGE)
    baseline = image(preimage, prior["runtime.patch"], stage)
    if digest(baseline) != OLD_IMAGE:
        raise ValueError("The installed Round 428 image differs")
    patch = replace_unique(prior["runtime.patch"], b"+" + SELECTOR, b"+" + NEW_SELECTOR)
    installed = image(preimage, patch, stage)
    if installed != replace_unique(baseline, SELECTOR, NEW_SELECTOR):
        raise ValueError("The selector patch made another change to installations.py")
    compile(installed, "installations.py", "exec")
    manifest = json.loads(prior["SOURCES.json"], object_pairs_hook=unique_object)
    pins = manifest["runtime_images"]["installations.py"]
    if pins != {"before": PREIMAGE, "after": OLD_IMAGE} or manifest["local_sources"]["runtime.patch"] != PINS["runtime.patch"]:
        raise ValueError("The old selector pins differ")
    pins["after"] = digest(installed)
    manifest["local_sources"]["runtime.patch"] = digest(patch)
    edits = runpy.run_path(str(HERE / "edits.py"))["EDITS"]
    changed = {
        "runtime.patch": patch,
        "SOURCES.json": (json.dumps(manifest, indent=2) + "\n").encode(),
    }
    for name, replacements in edits.items():
        text = prior[name].decode()
        for before, after in replacements:
            text = replace_unique(text, before, after)
        compile(text, name, "exec")
        changed[name] = text.encode()
    if set(changed) != set(PINS):
        raise ValueError("The changed source inventory differs")
    before = inventory(frozen)
    old_result = (PEER / "RESULT.json").as_posix()
    if old_result in before:
        authenticated(frozen / old_result, OLD_RESULT)
    candidate = stage / "candidate"
    shutil.copytree(frozen / "research", candidate / "research")
    (candidate / old_result).unlink(missing_ok=True)
    for name, raw in changed.items():
        (candidate / PEER / name).write_bytes(raw)
    after = inventory(candidate)
    differences = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    expected = {(PEER / name).as_posix() for name in changed}
    if differences - {old_result} != expected or old_result in after:
        raise ValueError("An unexpected source changed or a stale receipt survived")
    return candidate, {
        "scope": "Frozen source assembly and exact selector image only. Installed replay unrun.",
        "baseline_terminal_kappa": OLD_RATE,
        "projected_terminal_kappa": NEW_RATE,
        "projected_delta": "469/1000000000000000",
        "predecessor_result_sha256": OLD_RESULT,
        "installation_preimage_sha256": PREIMAGE,
        "old_installation_sha256": OLD_IMAGE,
        "candidate_installation_sha256": digest(installed),
        "changed": {p: {"before": before[p], "after": after[p]} for p in sorted(expected)},
        "candidate_RESULT": "not generated",
    }


def timeout(_signal, _frame):
    raise TimeoutError("Source assembly reached the 45-second cap")


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frozen, output = args.frozen.resolve(), args.output.resolve()
    if args.output.is_symlink() or output.exists() or output.is_relative_to(frozen):
        parser.error("--output must be a fresh path outside the frozen tree")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(45)
    try:
        with TemporaryDirectory(prefix="exact-ordinary-tariff-source-", dir=output.parent) as temporary:
            candidate, receipt = materialize(frozen, Path(temporary))
            (candidate / "TARIFF-ASSEMBLY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            candidate.rename(output)
        print(json.dumps(receipt, indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
