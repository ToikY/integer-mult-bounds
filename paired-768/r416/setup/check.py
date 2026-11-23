"""Check the written fixed-setup bound at exact #8094 and the Round 415 overlay."""

import argparse
import ast
from dataclasses import replace
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import runpy
from subprocess import run
from tarfile import open as tar_open
from tempfile import TemporaryDirectory

HEAD = "c20a08dc0a79a989e3515068560d5da371c0a2a8"
TIERED = "research/tiered-native-multiplier/"
WEIGHTED = "research/frequency-weighted-native-multiplier/"
PINS = {
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "prepare.py": "bc401e5c47d275617f3c7d162d56ea4c604ef3d4c6637ab2a8aa8627a570a9f6",
    "RESULT.json": "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
}
IMAGES = {
    "peer": "5b31cca69a8f10c78152ae030ae7c7ab156d22feec83347b887aa3fe78098ee7",
    "candidate": "37460b2be0a93ecfe110be25de5a4ea787c2d09973f926f680ea148453dc89e2",
}
LEGACY_SRC = "11d1c3209cb523a360ab9abaefb3122507fdf5cb469169890fe2dac636812c47"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate input key")
    return result


def digest(data):
    return sha256(data).hexdigest()


def install_image(preimage, patch):
    with TemporaryDirectory(prefix="fixed-setup-source-") as temp:
        path = Path(temp) / "installations.py"
        path.write_bytes(preimage)
        run(["git", "apply", "--no-index", "--include=installations.py", "--whitespace=nowarn", "-"],
            cwd=path.parent, input=patch, timeout=10, check=True)
        return path.read_bytes()


def read_profile(image):
    # This installs only the scalar Profile declarations, not a native directory.
    scope = {"__name__": "__main__"}
    exec(compile(image, "installations.py", "exec"), scope)
    return scope["PROFILES"]


def scalar_bits(profile):
    values = (
        profile.kappa.numerator, profile.kappa.denominator,
        profile.eta.numerator, profile.eta.denominator,
        profile.positive_stop_denominator,
    )
    return tuple(abs(x).bit_length() for x in values)


def encodings_fit(profile):
    return max(scalar_bits(profile)) <= 128 and profile.positive_stop_denominator > 0


def check_profiles(profiles):
    ordinary = [h for p in profiles.values() for h in p.rank_logs]
    gaussian = [p.complex_log for p in profiles.values()]
    heights = ordinary + gaussian
    assert len(ordinary) == 7 and len(gaussian) == 2
    assert min(heights) >= 1024 and max(ordinary) < 2**27 and max(gaussian) < 2**25
    assert all(encodings_fit(p) for p in profiles.values())
    width = max(92 * h + 1 for h in heights)
    exponent = max(1024 * h + 3 for h in heights)
    assert 92 * (2**27 - 1) + 1 < 2**34 < 2**38
    assert width < 2**38 and exponent < 2**38
    return {
        "ordinary_H": ordinary, "gaussian_H": gaussian,
        "maximum_92H_plus_one_bits": width,
        "maximum_control_exponent": exponent,
        "gaussian_carrier_bits_per_profile": [g + 1 for g in gaussian],
        "profile_scalar_bits": {k: scalar_bits(p) for k, p in profiles.items()},
    }


def serial_bound(actions):
    w = 1 << 38
    h = 2 * w + 2
    lookup = 8 * (4 * w * actions) * 512 * 128
    scalar = (1 << 16) * (h + 4) * ((7 * h + 9) + 8 * (h + 4))
    total = (actions + 1) * (lookup + scalar + (1 << 120)) * (1 << 32)
    return {"actions": actions, "w": w, "lookup": lookup, "scalar": scalar, "total": total}


def audit(package):
    src = {name: (package / name).read_bytes() for name in PINS}
    assert {name: digest(data) for name, data in src.items()} == PINS
    prepare = runpy.run_path(str(package / "prepare.py"))
    original = json.loads(src["RESULT.json"], object_pairs_hook=unique)
    with tar_open(fileobj=BytesIO(src["peer8057.tar.gz"]), mode="r:gz") as archive:
        preimage = archive.extractfile(TIERED + "installations.py").read()
        patch = archive.extractfile(WEIGHTED + "runtime.patch").read().decode()
        legacy = archive.extractfile(TIERED + "check_serial_setup.py").read()
        ctor = archive.extractfile(WEIGHTED + "portable/compiler_state.py").read()
        receipt = archive.extractfile(WEIGHTED + "receipt.py").read().decode()
    assert digest(legacy) == LEGACY_SRC
    for name, value in (("runtime.patch", patch), ("receipt.py", receipt)):
        for before, after in prepare["EDITS"][name]:
            assert value.count(before) == 1
            value = value.replace(before, after, 1)
        if name == "runtime.patch":
            patch = value + prepare["RAW_FLOOR_PATCH"] + prepare["SHORTCUT_PATCH"]
        else:
            receipt = value
    assert 'setup = native_clock()' in receipt
    assert 'native_setup_transition_upper=setup["all_setup"]' in receipt
    assert b"tuple(binary_recipe(h) for h in profile.rank_logs)" in ctor
    assert b"numerical_recipe(profile.complex_log)" in ctor
    assert b".open()" not in ctor and b".width" not in ctor

    prior_k = '.003900857267786'
    newer_k = '.003900857269150'
    assert patch.splitlines().count(next(line for line in patch.splitlines()
                                         if line.startswith('+TERMINAL = ') and prior_k in line)) == 1
    patched = {"peer": patch, "candidate": patch.replace(prior_k, newer_k, 1)}
    output = {}
    for label, source in patched.items():
        image = install_image(preimage, source.encode())
        assert digest(image) == IMAGES[label]
        profiles = read_profile(image)
        output[label] = check_profiles(profiles)
        for tier, profile in profiles.items():
            assert list(profile.rank_logs) == original[tier]["ordinary_H"]
            assert profile.complex_log == original[tier]["numerical_H"]
        assert profiles["terminal"].kappa == Fraction(prior_k if label == "peer" else newer_k)
    terminal = profiles["terminal"]
    assert not encodings_fit(replace(terminal, kappa=Fraction(1, 1 << 128)))
    assert not encodings_fit(replace(terminal, positive_stop_denominator=0))

    # Execute only the extracted pure arithmetic function, without its tests or imports.
    clock, = [node for node in ast.parse(legacy).body
              if isinstance(node, ast.FunctionDef) and node.name == "clock"]
    scope = {}
    exec(compile(ast.Module(body=[clock], type_ignores=[]), "check_serial_setup.py:clock", "exec"), scope)
    original_bound = serial_bound(1 << 68)
    assert scope["clock"]()["all_setup"] == original_bound["total"] == original["native_setup_transition_upper"]

    # Charge the full inherited allowance, not only the smaller recipe subtotal.
    recipe_actions = 2 * 2048 * ((1 << 25) + 1) + 9 * (1 << 24)
    expanded = serial_bound((1 << 68) + (1 << 40))
    wrong_lookup_only = (expanded["actions"] + 1) * (
        original_bound["lookup"] + expanded["scalar"] + (1 << 120)) * (1 << 32)
    assert recipe_actions == 137589952512 < 1 << 40
    assert original_bound["total"] < wrong_lookup_only < expanded["total"] < 1 << 228
    assert expanded["total"] == 217364571993743287866367176320080817069553173293686105666269057384448
    return {
        "head": HEAD, "package_sha256": PINS, "installation_sha256": IMAGES,
        "archived_source_sha256": {
            TIERED + "check_serial_setup.py": digest(legacy),
            TIERED + "installations.py": digest(preimage),
            WEIGHTED + "portable/compiler_state.py": digest(ctor),
        },
        "profiles": output, "nine_recipe_action_allowance": recipe_actions,
        "legacy": original_bound, "expanded": expanded, "stale_lookup_only": wrong_lookup_only,
        "nominal_exponent_cap": 228, "remaining_slack": (1 << 228) - expanded["total"],
        "scope": "Pinned scalar declaration and action-bound arithmetic; fixed compiler census unrun.",
    }


if __name__ == "__main__":
    assert __debug__
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--package-root", required=True, type=Path)
    print(json.dumps(audit(args.parse_args().package_root), indent=2))
