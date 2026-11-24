"""Check the expanded setup arithmetic on exact #8097's published profile."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path


PIN = "f3ff96fb44169735871b27c1a22dd3f499e20a77401896fe53845f546aa1c9f5"
WORD = 2**38
BASE_ACTIONS = 2**68
ADDED_ACTIONS = 2**40


def serial_bound(actions):
    width = 2 * WORD + 2
    lookup = 8 * (4 * WORD * actions) * 512 * 128
    local = 2**16 * (width + 4) * (7 * width + 9) + 8 * 2**16 * (width + 4)**2
    return (actions + 1) * (lookup + local + 2**120) * 2**32


def check(path):
    payload = path.read_bytes()
    assert sha256(payload).hexdigest() == PIN
    result = json.loads(payload)
    entry, terminal = result["entry"], result["terminal"]
    heights = [*entry["ordinary_H"], *terminal["ordinary_H"]]
    positive = [entry["numerical_H"], terminal["numerical_H"]]
    recipes = len(heights) + len(positive)
    assert recipes == 10 and max(heights) == 2**28 - 1
    assert 1024 * max(heights) + 3 < WORD < 1024 * (max(heights) + 1) + 3
    assert max(positive) < 2**25
    overhead = 2 * 2048 * (2**25 + 1) + recipes * 2**24
    assert overhead == 137606729728 < ADDED_ACTIONS
    legacy = serial_bound(BASE_ACTIONS)
    expanded = serial_bound(BASE_ACTIONS + ADDED_ACTIONS)
    assert result["native_setup_transition_upper"] == legacy < expanded < 2**228
    return {
        "scope": "Independent setup arithmetic only. Exact original peer checkout remains untouched.",
        "source_sha256": {
            "peer8097/research/p104-10shortcut-3type-28bit-6stage/RESULT.json": PIN
        },
        "recorded_serial_actions": BASE_ACTIONS,
        "expanded_serial_actions": BASE_ACTIONS + ADDED_ACTIONS,
        "observed_profile_recipe_count": recipes,
        "structural_action_upper": overhead,
        "legacy_reported_transition_upper": legacy,
        "expanded_transition_upper": expanded,
        "setup_power": 228,
        "installed_census": "pending",
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    print(json.dumps(check(parser.parse_args().result), indent=2))
