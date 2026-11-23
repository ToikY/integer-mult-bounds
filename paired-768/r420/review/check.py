"""Read-only verification of the prepared Round 420 price and selector."""

from argparse import ArgumentParser
import ast
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from math import isqrt
from pathlib import Path
import runpy
import subprocess
import tarfile
from tempfile import TemporaryDirectory

parser = ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
parser.add_argument("--frozen", type=Path, required=True)
parser.add_argument("--candidate", type=Path, required=True)
parser.add_argument("--composed", type=Path, required=True)
args = parser.parse_args()
publication = args.root.resolve()
weighted = "frequency-weighted-native-multiplier"
tiered = "tiered-native-multiplier"
prior = args.frozen.resolve() / "research"
current = args.candidate.resolve() / "research"
package = current / weighted
exact_input = args.composed.resolve()


def read_json(path):
    return json.loads(path.read_bytes())

def digest(data):
    return sha256(data).hexdigest()

def manifest(root):
    return {str(p.relative_to(root)): digest(p.read_bytes()) for p in root.rglob("*") if p.is_file()}

pins = read_json(publication / "r415/overlay/INPUTS.json")
assert pins["head"] == "c20a08dc0a79a989e3515068560d5da371c0a2a8"
for name, pin in pins["files"].items():
    data = (exact_input / name).read_bytes()
    assert len(data) == pin["size"] and digest(data) == pin["sha256"]
    assert sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == pin["git_blob"]

peer_pins = read_json(exact_input / "PEER-SOURCE.json")
with tarfile.open(exact_input / "peer8057.tar.gz") as peer:
    original = {m.name: peer.extractfile(m).read() for m in peer if m.isfile()}
assert {name: digest(data) for name, data in original.items()} == peer_pins["files_sha256"]

before, after = manifest(prior), manifest(current)
assert before.keys() == after.keys()
changed = {name for name in after if before[name] != after[name]}
expected = {"SOURCES.json", "check_stage_seam.py", "independent_price.py", "positive_debit.py", "receipt.py", "runtime.patch"}
assert changed == {f"{weighted}/{name}" for name in expected}
assert not (package / "RESULT.json").exists()
assert (package / "PREDECESSOR-RESULT.json").read_bytes() == original[f"research/{weighted}/RESULT.json"]
assert (package / "w5669_shortcut5.json.gz").read_bytes() == (exact_input / "w5669_shortcut5.json.gz").read_bytes()
allowed_peer_delta = expected | {
    "PREDECESSOR-RESULT.json", "w5669_shortcut5.json.gz", "check_cutoff.py",
    "check_ordinary_floor.py", "bootstrap.py", "check_exterior.py", "check_nested.py",
    "check_ownership.py", "check_placement.py", "grades.py", "verify.py",
}
for name, hex_digest in after.items():
    if name.startswith(f"{weighted}/") and name.split("/", 1)[1] in allowed_peer_delta:
        continue
    assert digest(original[f"research/{name}"]) == hex_digest, name

# Check the bootstrapped-weighted patch and manifest without bootstrapping.
source_pins = read_json(package / "SOURCES.json")
prior_pins = read_json(prior / weighted / "SOURCES.json")
runtime_patch = package / "runtime.patch"
for name, hex_digest in source_pins["local_sources"].items():
    assert digest((package / name).read_bytes()) == hex_digest
patch = runtime_patch.read_bytes()
old_patch = (prior / weighted / "runtime.patch").read_bytes()
assert old_patch.replace(b'.003900857269150', b'.003900857312000') == patch
preimage = (current / tiered / "installations.py").read_bytes()
with TemporaryDirectory() as temp:
    image = Path(temp) / "installations.py"
    profiles = []
    for predecessor_root, selected_pins in ((prior / weighted, prior_pins), (package, source_pins)):
        image.write_bytes(preimage)
        assert digest(image.read_bytes()) == selected_pins["runtime_images"]["installations.py"]["before"]
        subprocess.run(["git", "apply", "--no-index", "--include=installations.py", str(predecessor_root / "runtime.patch")],
                       cwd=temp, check=True)
        assert digest(image.read_bytes()) == selected_pins["runtime_images"]["installations.py"]["after"]
        profiles.append(runpy.run_path(str(image)))
old, new = profiles
assert vars(old["ENTRY"]) == vars(new["ENTRY"])
old_profile, new_profile = old["TERMINAL"], new["TERMINAL"]
assert vars(old_profile) | {"kappa": new_profile.kappa} == vars(new_profile)
assert new_profile.rank_logs == (31808, 502922, 7951907, 125730703, 134217727)
assert new_profile.complex_log == 208653 and new_profile.eta == Q(1, 256)
assert new_profile.kappa == Q(".003900857312000")
assert digest(old_patch) != source_pins["local_sources"]["runtime.patch"]
assert prior_pins["runtime_images"]["installations.py"]["after"] != source_pins["runtime_images"]["installations.py"]["after"]
assert old["GAUSSIAN_C"] == new["GAUSSIAN_C"] and old["BINARY_C"] == new["BINARY_C"]

# Exercise the patched selector at the independently computed activation.
activation = runpy.run_path(str(current / tiered / "source/activation.py"))
stock = activation["resource_receipt"](new_profile)
assert stock == activation["resource_receipt"](old_profile)
selector = new["at_public"]
selector.__globals__["activation"] = lambda profile: activation["resource_receipt"](profile)["public_exponent_A"]
class Public:
    def __init__(self, bits):
        self.bits = bits
    def bit_length(self):
        return self.bits

assert selector(Public(stock["public_exponent_A"])) is new["ENTRY"]
assert selector(Public(stock["public_exponent_A"] + 1)) is new_profile
assert old_profile.kappa != new_profile.kappa

receipt_tree = ast.parse((package / "receipt.py").read_bytes())
prior_receipt_tree = ast.parse((prior / weighted / "receipt.py").read_bytes())
def assigned(tree, name):
    statement = next(n for n in tree.body if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
    return eval(compile(ast.Expression(statement.value), "", "eval"), {"Q": Q})

assert assigned(receipt_tree, "ORDINARY_DEBIT") == assigned(prior_receipt_tree, "ORDINARY_DEBIT") == Q(1414404, 2**20)
assert assigned(receipt_tree, "CHILD_TARIFF") == assigned(prior_receipt_tree, "CHILD_TARIFF") == Q(2391, 1024)
debit = assigned(receipt_tree, "DEBIT")
assert debit == assigned(ast.parse((package / "positive_debit.py").read_bytes()), "POSITIVE_DEBIT") == Q(1039701, 2**23)
setup_ref = read_json(publication / "r417/setup-receipt/RECEIPT.json")
setup_clock_file = current / tiered / "check_serial_setup.py"
setup_clock_ast = ast.parse(setup_clock_file.read_bytes())
clock = next(n for n in setup_clock_ast.body if isinstance(n, ast.FunctionDef) and n.name == "clock")
check = next(n for n in receipt_tree.body if isinstance(n, ast.FunctionDef) and n.name == "check")
setup_idx = next(i for i, n in enumerate(check.body) if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "setup")
env = {}
exec(compile(ast.Module(body=[clock], type_ignores=[]), "", "exec"), env)
env["native_clock"] = env["clock"]
exec(compile(ast.Module(body=check.body[setup_idx:setup_idx + 4], type_ignores=[]), "", "exec"), env)
assert env["setup"]["all_setup"] == setup_ref["expanded_setup_transitions"] < 2**228
assert setup_ref["stale_lookup_rejected"] and setup_ref["stale_lookup_mutation_transitions"] < env["setup"]["all_setup"]

scale = 1724 * 306 // 2
x_min = Q(scale, 4 * 258)
period = Q(257, 256)
assert 255 < x_min < 256 and 256 / x_min < period
assert 1 + Q(1, 256) == period

# Reconstruct the new envelope from the exact predecessor's charged factor.
proof = read_json(publication / "r419/cross-price/RECEIPT.json")
assert Q(proof["lower_x"]) == x_min and Q(proof["changed_period"]) == period
finite_source = read_json(exact_input / "RESULT.json")
def lookup(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = lookup(value, key)
            if found is not None:
                return found
    return None
coarse = Q(lookup(finite_source, "upper_factor"))
new_envelope = coarse * period / (1 + 1 / x_min)
grid = 1 << 256
def exp2_bound(exponent):
    lo = hi = 2 * grid
    a = b = grid
    for place in range(exponent.denominator.bit_length() - 2, -1, -1):
        lo = isqrt(lo * grid)
        hi = isqrt(hi * grid - 1) + 1
        if exponent.numerator & (1 << place):
            a = a * lo // grid
            b = (b * hi + grid - 1) // grid
    return Q(a, grid), Q(b, grid)

assert exp2_bound(debit - Q(1, 2**23))[1] < new_envelope < exp2_bound(debit)[0]
assert exp2_bound(debit)[1] < coarse < exp2_bound(Q(1039776, 2**23))[0]
guard = Q(5, 10**18)
kappa = new_profile.kappa
h = new_profile.complex_log
c = new["GAUSSIAN_C"]
ceiling = c - debit / h - guard
assert old_profile.kappa < c - Q(1039776, 2**23) / h - guard < kappa
assert c - debit / (h - 1) - guard < kappa < ceiling < kappa + Q(1, 10**15)
r = Q(0)
ordinary_debit = assigned(receipt_tree, "ORDINARY_DEBIT")
for i, depth in enumerate(new_profile.rank_logs):
    r = min(new_profile.eta, (249 * (new["BINARY_C"] - ordinary_debit / depth) + r) / 250)
    if i + 1 < len(new_profile.rank_logs):
        r = Q((r * 10**21).__floor__() - 1, 10**21)
assert r - guard > ceiling and Q(proof["positive_ceiling"]) == ceiling
assert Q(proof["ordinary_ceiling"]) == r - guard
assert kappa - old_profile.kappa == Q(857, 20000000000000)
assert kappa - Q(".003900857267786") == Q(22107, 500000000000000)

# Execute the actual seam arithmetic through its source-only boundary.
seam_path = package / "check_stage_seam.py"
seam = ast.parse(seam_path.read_bytes())
old_seam = ast.parse((prior / weighted / seam_path.name).read_bytes())
physical = {"verify_stage", "verify_tape"}
def physical_functions(tree):
    return {node.name: ast.dump(node) for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in physical}
assert physical_functions(seam).keys() == physical
assert physical_functions(seam) == physical_functions(old_seam)
seam_code = next(node for node in seam.body if isinstance(node, ast.FunctionDef) and node.name == "check")
start = next(i for i, n in enumerate(seam_code.body) if isinstance(n, ast.Assign))
stop = next(i for i, n in enumerate(seam_code.body) if isinstance(n, ast.Assert)
            and "strong-bit.json.gz" in ast.unparse(n))
arithmetic = ast.FunctionDef(name="check_arithmetic", args=seam_code.args,
    body=seam_code.body[start:stop] + [ast.Return(ast.Name(id="controls", ctx=ast.Load()))],
    decorator_list=[])
seam_env = dict(selector.__globals__, replace=replace,
                resource_receipt=activation["resource_receipt"],
                entrance_logs=activation["binary_entries"],
                qualify=runpy.run_path(str(current / tiered / "source/outer_budget.py"))["qualify"])
exec(compile(ast.fix_missing_locations(ast.Module(body=[arithmetic], type_ignores=[])),
             "seam arithmetic excerpt", "exec"), seam_env)
controls = seam_env["check_arithmetic"]()
expected_controls = read_json(publication / "r415/overlay/SEAM.json")["controls"]
assert set(controls) == set(expected_controls) | {"prior-gaussian-debit-at-new-rate"} and len(controls) == 18

typed_transport = ast.parse((package / "typed_transport.py").read_bytes())
assigned_periods = [ast.unparse(node.value) for node in ast.walk(typed_transport)
                    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "period"
                                                           for t in node.targets)]
assert "4 * ceil(Q(n, 4 * size))" in assigned_periods
print(json.dumps({
    "scope": "Pinned source readback only. Native replay unrun.",
    "verified_exact_8094_inputs": len(pins["files"]),
    "verified_predecessor_files": len(original),
    "compared_prepared_files": len(after),
    "changed": sorted(changed),
    "selector_installations_sha256": source_pins["runtime_images"]["installations.py"]["after"],
    "selector_activation": stock["public_exponent_A"],
    "period": str(period),
    "gaussian_debit": str(debit),
    "positive_ceiling": str(ceiling),
    "kappa": "0.003900857312000",
    "round417_setup_bound": env["setup"]["all_setup"],
    "candidate_RESULT": "absent",
    "source_seam_controls": controls,
}, indent=2))
