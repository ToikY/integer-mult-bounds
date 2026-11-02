#!/usr/bin/env python3
"""Audit PR6335's W2/W4 source-selection record against dependency N1.

The pinned drafts are parsed, not imported or executed. A passing run is an
interface gap certificate. It is not source adoption, a runtime seal, or a
selected-frontier change.
"""

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINNED = ROOT / "pinned"
UPSTREAM = "d34b84f1e1d9fb4bdcf26eda8817c3603fea3051"

W2_SHA = "fdeeb791c6cb0c03a5ab15903d51c3eb4cc5ff2a945c50d7f550acfe11376f3d"
W4_SHA = "6fc0577690c3865c1d67b4c288f860e5c81c8aebb3cffab18ab8a2269b12a572"
CONTROLS_SHA = "742f1de31551d43c2665ad6166577c104a0acc746b3503cc60c5f11798c9a24d"
IDENTITIES_SHA = "4665ede76e9238130f6fa9f1f66a24e267cd3501e684a4b8b6adbc67f8d3f73d"
DEPENDENCIES_SHA = "bacc5e4c834f8b3373c6135c272d8eab07fff2d60650c54616ffe45bb972eb49"

STATUS_LINE = 'info["status"] = "FAILED_EVIDENCE_RETAINED"'
TRAPS = (
    "Clamped",
    "DivisionByZero",
    "FloatOperation",
    "Inexact",
    "InvalidOperation",
    "Overflow",
    "Rounded",
    "Subnormal",
    "Underflow",
)
PRODUCERS_ABSENT = (
    "Not implemented/integrated in this source round; required before W5."
)


def fail(message):
    raise SystemExit("FAIL_H25_W2_W4_SELECTION_GAP: " + message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load(name):
    path = PINNED / name
    data = path.read_bytes()
    return data


def module_imports(source):
    tree = ast.parse(source)
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return sorted(set(names))


def imported_names(source, module):
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            found.extend(alias.name for alias in node.names)
    return found


def assignment_value(source, name):
    tree = ast.parse(source)
    found = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    found.append(ast.literal_eval(node.value))
    if len(found) != 1:
        fail("expected one module-level assignment of " + name)
    return found[0]


def line_text(source, number):
    lines = source.splitlines()
    if not 1 <= number <= len(lines):
        fail("missing source line " + str(number))
    return lines[number - 1].strip()


def n1_record(dependencies):
    rows = [row for row in dependencies["dependencies"] if row.get("id") == "N1"]
    if len(rows) != 1:
        fail("N1 must occur once")
    return rows[0]["dependency"]


def selection_facts(identity, dependencies, w2_source, w4_source, controls_source):
    profiles = identity["profiles"]
    by_source = {row["source"]: row for row in profiles}
    w2_key = next(key for key in by_source if key.endswith("/bounded_serialization.py"))
    w4_key = next(key for key in by_source if key.endswith("/parent_readback_v3_DRAFT_v2.py"))
    w2 = by_source[w2_key]
    w4 = by_source[w4_key]
    w2_imports = module_imports(w2_source)
    w4_imports = module_imports(w4_source)
    decimal_names = imported_names(w4_source, "decimal")
    selected = [row["source"] for row in profiles]
    n1 = n1_record(dependencies)
    return {
        "profile_count": len(profiles),
        "w2_imports_match_record": w2_imports == w2["direct_import_names_from_static_AST"],
        "w4_imports_match_record": w4_imports == w4["direct_import_names_from_static_AST"],
        "w2_omits_sys": "sys" not in w2_imports,
        "w4_has_decimal_and_re": "decimal" in w4_imports and "re" in w4_imports,
        "w4_omits_decimal_extension": "_decimal" not in w4_imports,
        "context_imported": "Context" in decimal_names and "localcontext" in decimal_names,
        "traps_imported": all(name in decimal_names for name in TRAPS),
        "context_absent_from_import_field": "Context" not in w4["direct_import_names_from_static_AST"],
        "traps_absent_from_import_field": all(
            name not in w4["direct_import_names_from_static_AST"] for name in TRAPS
        ),
        "controls_unselected": not any(path.endswith("new_failure_controls.py") for path in selected),
        "f05_selection_bit_absent": "f05_selected" not in identity and "F05_selected" not in identity,
        "source_adopted": identity["source_adopted"],
        "producers": identity["new_launcher_admission_receipt_producers"],
        "n1_names_extension_and_nonadoption": (
            "decimal/_decimal" in n1 and "No source adoption has occurred." in n1
            and "if selected" in n1 and "all original controls" in n1
        ),
        "f05_update_is_conditional": any(
            "if F05 selected" in item for item in identity["required_dependency_updates"]
        ),
        "status_line_490": line_text(w2_source, 490) == STATUS_LINE,
        "control_targets_same_hash": assignment_value(controls_source, "TARGET_SHA256") == w2["sha256"],
        "control_targets_line_490": assignment_value(controls_source, "PRIMARY_STATUS_LINE") == 490,
        "control_imports_sys": "sys" in module_imports(controls_source),
        "control_calls_settrace": "sys.settrace(" in controls_source,
    }


def require_gap(facts):
    expected = {
        "profile_count": 2,
        "w2_imports_match_record": True,
        "w4_imports_match_record": True,
        "w2_omits_sys": True,
        "w4_has_decimal_and_re": True,
        "w4_omits_decimal_extension": True,
        "context_imported": True,
        "traps_imported": True,
        "context_absent_from_import_field": True,
        "traps_absent_from_import_field": True,
        "controls_unselected": True,
        "f05_selection_bit_absent": True,
        "source_adopted": False,
        "producers": PRODUCERS_ABSENT,
        "n1_names_extension_and_nonadoption": True,
        "f05_update_is_conditional": True,
        "status_line_490": True,
        "control_targets_same_hash": True,
        "control_targets_line_490": True,
        "control_imports_sys": True,
        "control_calls_settrace": True,
    }
    for key, value in expected.items():
        if facts.get(key) != value:
            fail(key + " was " + repr(facts.get(key)) + ", expected " + repr(value))


def mutation_controls(identity, dependencies, w2_source, w4_source, controls_source):
    """Each mutant must change the fact that makes the published gap true."""
    checked = 0

    added_sys = json.loads(json.dumps(identity))
    w2 = next(row for row in added_sys["profiles"] if row["source"].endswith("bounded_serialization.py"))
    w2["direct_import_names_from_static_AST"] = sorted(
        set(w2["direct_import_names_from_static_AST"]) | {"sys"}
    )
    mutant = selection_facts(added_sys, dependencies, w2_source, w4_source, controls_source)
    if mutant["w2_imports_match_record"]:
        fail("mutation control missed an added sys import")
    checked += 1

    adopted = json.loads(json.dumps(identity))
    adopted["source_adopted"] = True
    mutant = selection_facts(adopted, dependencies, w2_source, w4_source, controls_source)
    if mutant["source_adopted"] is not True:
        fail("mutation control missed source_adopted")
    checked += 1

    closed = json.loads(json.dumps(dependencies))
    closed["dependencies"][0]["dependency"] = "Source adoption has occurred."
    mutant = selection_facts(identity, closed, w2_source, w4_source, controls_source)
    if mutant["n1_names_extension_and_nonadoption"]:
        fail("mutation control missed a rewritten N1 sentence")
    checked += 1

    moved = controls_source.replace("PRIMARY_STATUS_LINE = 490", "PRIMARY_STATUS_LINE = 491", 1)
    mutant = selection_facts(identity, dependencies, w2_source, w4_source, moved)
    if mutant["control_targets_line_490"]:
        fail("mutation control missed a moved status line")
    checked += 1
    return checked


def repository_root():
    current = ROOT
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    fail("repository root not found")


def upstream_bytes(path):
    spec = UPSTREAM + ":" + path
    root = repository_root()
    probe = subprocess.run(
        ["git", "cat-file", "-e", spec],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if probe.returncode != 0:
        return None
    return subprocess.check_output(["git", "show", spec], cwd=root)


def compare_upstream(manifest):
    compared = 0
    absent = 0
    for row in manifest["files"]:
        observed = upstream_bytes(row["upstream_path"])
        if observed is None:
            absent += 1
            continue
        if sha256(observed) != row["sha256"] or observed != (PINNED / row["name"]).read_bytes():
            fail("vendored bytes differ from " + UPSTREAM + ":" + row["upstream_path"])
        compared += 1
    if compared == 0 and absent != len(manifest["files"]):
        fail("partial upstream object lookup")
    return compared, absent


def main():
    blobs = {
        name: load(name)
        for name in (
            "identities.json",
            "next-dependencies.json",
            "bounded_serialization.py",
            "parent_readback_v3_DRAFT_v2.py",
            "new_failure_controls.py",
        )
    }
    expected = {
        "identities.json": IDENTITIES_SHA,
        "next-dependencies.json": DEPENDENCIES_SHA,
        "bounded_serialization.py": W2_SHA,
        "parent_readback_v3_DRAFT_v2.py": W4_SHA,
        "new_failure_controls.py": CONTROLS_SHA,
    }
    for name, digest in expected.items():
        if sha256(blobs[name]) != digest:
            fail("pin mismatch: " + name)
    manifest = json.loads((PINNED / "PINNED.json").read_text(encoding="utf-8"))
    if manifest["upstream_commit"] != UPSTREAM:
        fail("pin manifest names a different commit")
    listed = {row["name"]: row["sha256"] for row in manifest["files"]}
    if listed != expected:
        fail("pin manifest does not match the verifier constants")
    identity = json.loads(blobs["identities.json"].decode())
    dependencies = json.loads(blobs["next-dependencies.json"].decode())
    w2_row = next(row for row in identity["profiles"] if row["sha256"] == W2_SHA)
    w4_row = next(row for row in identity["profiles"] if row["sha256"] == W4_SHA)
    if w2_row["bytes"] != len(blobs["bounded_serialization.py"]):
        fail("W2 byte count differs from the identity record")
    if w4_row["bytes"] != len(blobs["parent_readback_v3_DRAFT_v2.py"]):
        fail("W4 byte count differs from the identity record")
    w2_source = blobs["bounded_serialization.py"].decode()
    w4_source = blobs["parent_readback_v3_DRAFT_v2.py"].decode()
    controls_source = blobs["new_failure_controls.py"].decode()
    facts = selection_facts(identity, dependencies, w2_source, w4_source, controls_source)
    require_gap(facts)
    mutations = mutation_controls(identity, dependencies, w2_source, w4_source, controls_source)
    compared, absent = compare_upstream(manifest)
    if compared != 5 and absent != 5:
        fail("upstream comparison was neither complete nor wholly absent")
    print("PASS_H25_W2_W4_SELECTION_GAP")
    print("n1_closed=false")
    print("source_adopted=false")
    print("f05_control_unselected=true")
    print("f05_selection_bit=absent")
    print("decimal_extension_unlisted=true")
    print("producers=not_implemented")
    print("mutation_controls=" + str(mutations))
    print("upstream_blobs_compared=" + str(compared))
    print("upstream_blobs_absent=" + str(absent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
