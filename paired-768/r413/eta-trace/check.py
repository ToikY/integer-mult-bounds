"""Reconstruct the ordinary η domain and exact seven-profile clock bounds."""
import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
import json
from math import ceil
from pathlib import Path
import signal
from tarfile import open as tar_open

ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
ETA_PROOF = "2cf917cb25145644c44c4ab981f3f4e4fd5f53719a54424d8c5bf6ed31749e72"
COMPOSED = {
    "prepare.py": "bc401e5c47d275617f3c7d162d56ea4c604ef3d4c6637ab2a8aa8627a570a9f6",
    "RESULT.json": "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
    "check_ordinary_floor.py": "d66db3d6d01259216fc1823be7066e676541d820ea8a96a4c513a635e91eb244",
    "check_stage_seam.py": "b790eb6855afa255a609eaaf88a46ed9e8b04232671cca4d0f8bd0bad27f11ac",
}
TIERED = "research/tiered-native-multiplier/"
ATOM = "1f3e60a5baae12a679ae64ad8fc7e5456f2040862fb938a99541fdd0b2018ac0"


def digest(data):
    return sha256(data).hexdigest()


def authenticate(path, expected):
    data = path.read_bytes()
    assert digest(data) == expected, str(path)
    return data


def member(data, name):
    with tar_open(fileobj=BytesIO(data)) as archive:
        entry = archive.getmember(name)
        assert entry.isfile()
        return archive.extractfile(entry).read()


def isolated_function(data, symbol, globals_):
    """Load the pinned standard-library-only arithmetic definition."""
    tree = ast.parse(data)
    definition, = (node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name == symbol)
    partial_tree = ast.Module(body=[definition], type_ignores=[])
    exec(compile(partial_tree, "<pinned function>", "exec"), globals_)
    return globals_[symbol]


def inspect_sources(package, proof, archive):
    assert b"2660000(j+2)<2^j" in proof
    assert b"ceil_root(e,256)" in proof
    assert b"2401/1024" in package["prepare.py"]
    assert b'Q(".003900857267786"), Q(1, 256)' in package["prepare.py"]
    assert b'assert ordinary.level_floor == 4474' in package["prepare.py"]
    assert b"LOWER=4474" in package["check_ordinary_floor.py"]
    assert b"all_size_stock(word, c, intervals, unit)" in package["check_ordinary_floor.py"]
    assert b"stage_for_width_log" not in package["prepare.py"]

    installer = member(archive, TIERED + "source/installer.tar.gz")
    retimed = member(installer, "retimed-source.tar.gz")
    blob8030 = member(retimed, "predecessor/predecessor-8030.tar.gz")
    retained = member(blob8030, "inputs/triangular/inputs/retained.tar.gz")
    retained_atoms = member(retained, ATOM)
    assert digest(retained_atoms) == ATOM
    carrier = member(blob8030, "ordinary_carrier.py")
    triangular = member(blob8030, "inputs/triangular/triangular_ordinary.py")
    old_clock = member(archive, TIERED + "CLOCK.md")
    assert b"2660000(j+2)<2^j" in old_clock
    assert b"25,818,582" in old_clock
    assert b"component_width = ceil_root(digits**eta.numerator, eta.denominator)" in carrier
    assert b"direct = (digits + width - 1) // width <= rank**8" in carrier
    assert b"c, r = divmod(e - k, width)" in triangular
    machine_patch = member(retimed, "machine.patch")
    assert b"+def stage_for_width_log(available, maximum, rank_logs):" in machine_patch
    assert b"+    stage = stage_for_width_log(digits.bit_length()-1, maximum, profile.rank_logs)" in machine_patch
    assert not any(b"component_width" in line for line in machine_patch.splitlines()
                   if line[:1] in (b"+", b"-"))
    for patch in (member(installer, "production.patch"), member(retimed, "receiver.patch"),
                  member(archive, TIERED + "runtime.patch"),
                  member(archive, "research/frequency-weighted-native-multiplier/runtime.patch")):
        assert not any(b"component_width" in line for line in patch.splitlines()
                       if line[:1] in (b"+", b"-"))
    source_paths = {
        TIERED + "CLOCK.md": digest(old_clock),
        TIERED + "source/installer.tar.gz/retimed-source.tar.gz/machine.patch": digest(machine_patch),
        TIERED + "source/installer.tar.gz/retimed-source.tar.gz/predecessor/predecessor-8030.tar.gz/ordinary_carrier.py": digest(carrier),
        TIERED + "source/installer.tar.gz/retimed-source.tar.gz/predecessor/predecessor-8030.tar.gz/inputs/triangular/triangular_ordinary.py": digest(triangular),
        TIERED + "source/installer.tar.gz/retimed-source.tar.gz/predecessor/predecessor-8030.tar.gz/inputs/triangular/inputs/retained.tar.gz/" + ATOM: ATOM,
    }
    root = isolated_function(retained_atoms, "ceil_root", {})
    nondyadic = [(1 << 256) + 1, (1 << 257) - 1, (1 << 512) + 123]
    for n in nondyadic:
        r = root(n, 256)
        assert r > 0 and (r - 1)**256 < n <= r**256
    return source_paths


def per_tier(data, eta, terminal):
    assert Q(1, 258) < eta < Q(1, 250)
    assert 2 * eta > Q(1, 250)
    assert data["stock"]["binary_cuts"]
    cuts = []
    table = []
    q = Q(data["kappa"]) + Q(5, 10**18)
    charged = list(map(Q, data["ordinary_rates"]))
    assert charged[-1] == q < eta and eta + q < Q(1, 2)
    assert not terminal or Q(39, 10000) < q  # old clamp rejects the terminal booking
    for h, b in zip(data["ordinary_H"], charged, strict=True):
        previous = cuts[-1] if cuts else 0
        entrance = max(ceil(Q(250*(h+64), 249)), previous+h+64)
        cuts.append(entrance)
        assert entrance > h and (not previous or previous + 2 < h)
        threshold = ceil(Q(2*h+64) / (1-eta))
        uniform = ceil(Q(250*(2*h+64), 249))
        assert (1-eta)*(threshold-1) < 2*h+64 <= (1-eta)*threshold
        assert threshold <= uniform < 3*h < 8*h
        u_bits = (eta * h - 1).__floor__()
        exponent = 162402 if len(cuts) == 1 else 28726102
        surcharge = None if terminal else max(0, exponent-944*h)
        if terminal:
            assert h >= 8192
            assert u_bits >= 30
            # At j=30 and thereafter, 2^j grows by a larger consecutive
            # ratio than 2660000(j+2). Use small exact base arithmetic only.
            assert 2660000*32 < 2**30 and Q(33,32) < 2
        table.append(dict(
            height=h, predecessor_cut=previous, native_cut=entrance,
            quotient_width_log=threshold, uniform_quotient_width_log=uniform,
            min_component_log2=u_bits, early_surcharge_bits=surcharge,
            paid_rate=str(b), eta_slack=str(eta-b)))
    assert cuts == data["stock"]["binary_cuts"]
    assert 5200*258+480+259*5060 < 2660000
    assert 5200*258+258*5060 < 2660000
    return table


def run(args):
    assert __debug__
    proof = authenticate(args.eta_proof, ETA_PROOF)
    package = {name: authenticate(args.composed / name, expected)
               for name, expected in COMPOSED.items()}
    archive = authenticate(args.archive, ARCHIVE)
    paths = inspect_sources(package, proof, archive)
    result = json.loads(package["RESULT.json"])
    entry = per_tier(result["entry"], Q(39, 10000), False)
    terminal = per_tier(result["terminal"], Q(1, 256), True)
    assert len(entry) == 2 and len(terminal) == 5
    assert [r["early_surcharge_bits"] for r in entry] == [0, 25818582]
    assert sum(r["early_surcharge_bits"] for r in entry) == 25818582
    # The 2401 geometric sum is paid as in the preceding reserve audit.
    assert (128 + 3*len(terminal) + 320*sum(r["height"] for r in terminal)
            == result["terminal"]["log2_B"])
    assert (40 + 22 + 16384*sum(r["height"] for r in entry) + 25818582
            == result["entry"]["log2_B"])
    assert 24*(4474+2) < 25*4474 and 4474 % 2 == 0
    return dict(
        status="PASS_ETA_DOMAIN_AND_ORDINARY_CLOCK_AT_SEVEN_LITERAL_RECIPES",
        elapsed_cap_seconds=30, entry=entry, terminal=terminal,
        eta_lift_head="af73b476d5fdeaa763e0bff2dd87b2ecaf097c49",
        composed_head="c20a08dc0a79a989e3515068560d5da371c0a2a8",
        eta_lift_proof_sha256=ETA_PROOF, composed_sha256=COMPOSED,
        archive_sha256=ARCHIVE, archive_member_sha256=paths,
        controls=["old terminal eta rejects claimed booked rate",
                  "quotient lower-adjacent threshold is insufficient",
                  "three source-executed nondyadic integer roots"],
        limitations=["fixed inherited all-column, ownership, compiler, tape/precision and recovery premises",
                     "signed installed replay and nine-recipe setup census unrun",
                     "source-anchor and exact parameter audit, no astronomical typed native opening"])


def stop(_signal, _frame):
    raise TimeoutError("Seven-record check exceeded thirty seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eta-proof", required=True, type=Path)
    parser.add_argument("--composed", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    signal.signal(signal.SIGALRM, stop)
    signal.alarm(30)
    try:
        print(json.dumps(run(parser.parse_args()), indent=2))
    finally:
        signal.alarm(0)
