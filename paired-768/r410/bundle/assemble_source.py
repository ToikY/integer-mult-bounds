"""Assemble the one exact source candidate into a new isolated directory."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from subprocess import check_output
import ast
import json

HERE = Path(__file__).resolve().parent
BASE = "aea1699415250d865f7a635f4df0b76f406c47b4"
PREDECESSOR = "research/p104-period-debit-25bit"
PACKAGE = "research/p104-matched-suffix-25bit"
INPUT_PIN = "46591f0f0d4a5cbbc5620d7e2312b18f3b73147be456ceb1cf9f728ec13e4ed3"
CHANGED = (
    "retune.py", "check_scaled.py", "check_setup_expanded.py",
    "matched_positive_debit.py", "matched_price_support.py", "check_matched_allocator.py",
)


def unique(entries):
    data = dict(entries)
    if len(data) != len(entries):
        raise ValueError("Duplicate path key")
    return data


def load(data):
    return json.loads(data, object_pairs_hook=unique)


def digest(data):
    return sha256(data).hexdigest()


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def inherited_inputs(baseline):
    assert check_output(["git", "-C", baseline, "rev-parse", "HEAD"]).decode().strip() == BASE
    assert not check_output(["git", "-C", baseline, "status", "--porcelain"])
    pins = (HERE/"BASELINE-INPUTS.json").read_bytes()
    assert digest(pins) == INPUT_PIN
    baseline_pin = load(pins)
    assert baseline_pin["head"] == BASE
    assert len(baseline_pin["files"]) == 30 and baseline_pin["files"].keys() == baseline_pin["modes"].keys()
    inputs = {}
    for path, expected in baseline_pin["files"].items():
        name = Path(path).relative_to(PREDECESSOR)
        assert len(name.parts) == 1
        file = baseline/path
        data = file.read_bytes()
        assert digest(data) == expected, path
        assert ("100755" if file.stat().st_mode & 0o100 else "100644") == baseline_pin["modes"][path], path
        inputs[str(name)] = data
    return inputs


def new_runner(source, out):
    text = source.decode()
    node = next(
        item for item in ast.parse(text).body if isinstance(item, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "PINS" for target in item.targets)
    )
    pins = ast.literal_eval(node.value)
    names = CHANGED + ("PREDECESSOR-RESULT.json",)
    pins.update({name: digest((out/name).read_bytes()) for name in names})
    code = text.splitlines(keepends=True)
    code[node.lineno-1:node.end_lineno] = ["PINS = " + json.dumps(pins, indent=4) + "\n"]
    return "".join(code).replace("PASS_25BIT_PERIOD_SIGNED", "PASS_25BIT_MATCHED_SIGNED").replace(
        "p104-scaled-", "p104-matched-")


def assemble(baseline, destination):
    source = inherited_inputs(baseline)
    paths = load((HERE/"OVERRIDES-SHA256.json").read_bytes())
    assert set(paths) == {*CHANGED, "README.md", "PROOF.md", "NOTICE.md", "SETUP-PROOF.md"}
    overrides = {name: (HERE/"overrides"/name).read_bytes() for name in paths}
    assert all(digest(data) == paths[name] for name, data in overrides.items())
    destination.mkdir(parents=True, exist_ok=False)
    folder = destination/PACKAGE
    folder.mkdir(parents=True)
    replaced = {*overrides, "RESULT-460.json", "PREDECESSOR-RESULT.json",
                "verify.py", "verify_setup.py", "VERIFY.json", "TASK.json"}
    for file, data in source.items():
        if file not in replaced:
            (folder/file).write_bytes(data)
    for file, data in overrides.items():
        (folder/file).write_bytes(data)
    (folder/"PREDECESSOR-RESULT.json").write_bytes(source["RESULT-460.json"])
    for file in ("verify.py", "verify_setup.py"):
        (folder/file).write_text(new_runner(source[file], folder))

    manifest = load(source["VERIFY.json"].replace(PREDECESSOR.encode(), PACKAGE.encode()))
    manifest["inputs"].extend(f"{PACKAGE}/{name}" for name in (*CHANGED, "SETUP-PROOF.md")
                             if f"{PACKAGE}/{name}" not in manifest["inputs"])
    manifest["commands"][0]["checks"] = "Reconstruct the actual allocator and matched factor, price both tiers, reject the adjacent debit and verify signed placements."
    manifest["commands"][1]["checks"] = "Check the stopped #8087 cap, signed owner calendar, both cutoffs and direct and compiled seams."
    save_json(folder/"VERIFY.json", manifest)
    card = load(source["TASK.json"])
    card.update(actual_scope="Exact offset-eight matched interior suffix at the charged 25-bit profile",
                scope_change_reason="The matched phase integral lowers the covered Gaussian bound on the unchanged typed calendar.",
                stop_rule="One profile at (8192,38102,604363;18531230) and κ=.003898460003746. Require all eight registered checks.",
                outcome="partial",
                evidence="The one-case exact price, source assembly and arithmetic controls passed. The actual result regeneration and independent signed replay remain open.",
                ai_assistance="OpenAI Codex materially assisted proof, implementation and receipt checking.")
    card["open_questions"] = [{
        "question": "Does the entire exact matched profile pass the registered independent signed replay?",
        "why_it_matters": "The projected arithmetic requires an actual installed caller, ownership, precision and setup check.",
        "first_step": "Run the pinned native gate, regenerate RESULT-460.json, and use the eight registered checks.",
        "blocked_by": "The local 8 GiB disk reserve must be available before launching native replay.",
    }]
    save_json(folder/"TASK.json", card)
    assert not (folder/"RESULT-460.json").exists()
    for file in folder.glob("*.py"):
        compile(file.read_bytes(), file.name, "exec")
    hashes = {str(file.relative_to(destination)):digest(file.read_bytes())
              for file in sorted(folder.iterdir())}
    save_json(destination/"SOURCE-ASSEMBLY.json", {
        "baseline": BASE, "candidate_package": PACKAGE, "files": hashes,
        "expected_unrun_output": f"{PACKAGE}/RESULT-460.json",
        "status": "source-only; scientific acceptance requires the exact generated result and independent signed replay",
    })
    print("PASS_MATCHED_SOURCE_ONLY", len(hashes), flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    assert __debug__
    assemble(args.baseline.resolve(), args.destination.resolve())


if __name__ == "__main__":
    main()
