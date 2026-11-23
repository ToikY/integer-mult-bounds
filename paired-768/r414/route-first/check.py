"""Authenticate fixed direct and quotient route anchors without running the installer."""

from argparse import ArgumentParser
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from tarfile import open as tar_open

ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
PREPARE = "bc401e5c47d275617f3c7d162d56ea4c604ef3d4c6637ab2a8aa8627a570a9f6"
TRI = "inputs/triangular/"


def digest(data):
    return sha256(data).hexdigest()


def member(archive, name):
    with tar_open(fileobj=BytesIO(archive)) as open_archive:
        entry = open_archive.getmember(name)
        assert entry.isfile(), name
        return open_archive.extractfile(entry).read()


def has(data, *strings):
    for part in strings:
        assert part.encode() in data, part


def targets(patch):
    return {line[6:].decode() for line in patch.splitlines() if line.startswith(b"+++ b/")}


def check(archive, prepare):
    assert digest(archive) == ARCHIVE and digest(prepare) == PREPARE
    installer = member(archive, "research/tiered-native-multiplier/source/installer.tar.gz")
    retimed = member(installer, "retimed-source.tar.gz")
    prior = member(retimed, "predecessor/predecessor-8030.tar.gz")
    receipt = {}

    def load(data, name, key=None):
        result = member(data, name)
        receipt[key or name] = digest(result)
        return result

    replacement = load(retimed, "receiver.patch")
    machine = load(retimed, "machine.patch")
    exchange = load(retimed, "five_exchange.py")
    carrier = load(prior, "ordinary_carrier.py", "predecessor/ordinary_carrier.py")
    binary = load(prior, "binary_receiver.py", "predecessor/binary_receiver.py")
    receiver = load(prior, TRI + "receiver.py")
    same = load(prior, TRI + "same_order_body.py")
    lows = load(prior, TRI + "quotient_route.py")
    high_patches = [load(installer, "production.patch"),
                    load(archive, "research/tiered-native-multiplier/runtime.patch"),
                    load(archive, "research/frequency-weighted-native-multiplier/runtime.patch")]
    physical = {TRI + name for name in
                ("receiver.py", "direct_body.py", "same_order_body.py", "quotient_route.py")}
    physical.add("five_exchange.py")
    assert not (set().union(*(targets(p) for p in high_patches)) & physical)
    assert not (targets(machine) & physical)
    assert targets(replacement) & physical == {TRI + "receiver.py", TRI + "direct_body.py"}
    has(prepare, "RAW_FLOOR_PATCH", "SHORTCUT_PATCH", "+++ b/raw_binary_stage.py",
        "+++ b/strong_complex.py")
    for name in physical:
        assert f"+++ b/{name}".encode() not in prepare
    has(replacement, "from five_exchange import direct_line, same_order_line",
        "from five_exchange import same_order_line")
    has(carrier, "direct = (digits + width - 1) // width <= rank**8",
        "previous = partial(ternary, maximum=stage - 1, profile=profile)",
        "backend = Receiver(rank, layout, previous, direct=direct, profile=profile)")
    assert b"stage_for_width_log" in machine
    has(binary, "core.serve_line(", "banks.install(job.owner, out)")
    has(receiver, "if not self.direct and shape[", 'self.small.weighted(source, target, **shape)',
        "atoms=f,", "direct_line(self, source, target, frame, f, unused, older, gap, suffix, weight)",
        "for low in canonical_lows(self.n):", "pending.pop_forward(argument, length)",
        "heights=self.high,", "answers.append(reply, length)",
        "type_route(completed, target, unused, self.low, packet, inverse=True)")
    has(lows, "def canonical_lows(n):", "for rows in low_rows(n):", "def free_count(n):")
    has(same, "f, remainder = divmod(atoms, self.n)", "previous_swap=self.previous,",
        "self.compiled,", "f=f,")
    has(exchange, 'yield partial(core.weighted, atoms=f, available=unused, older=older * head,',
        'yield move(inverse_word(frame.word))', 'core.weighted, atoms=f, available=unused, older=rows * front,',
        'yield child(0, n - 1, True)', 'for left, right in reversed(pairs):')
    return {
        "head": "c20a08dc0a79a989e3515068560d5da371c0a2a8",
        "source_digests": receipt,
        "cases": {
            "DIRECT": "one weighted child at floor(c/N), matching prior-only basis paths",
            "QUOTIENT": "every canonical low, equal-volume full packets, 1+2|pairs| children at floor(c/N)"
        },
        "scope": "Static route anchors; full paid physical and owner replay unrun.",
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--prepare", required=True, type=Path)
    args = parser.parse_args()
    assert __debug__
    print(json.dumps(check(args.archive.read_bytes(), args.prepare.read_bytes()), indent=2))


if __name__ == "__main__":
    main()
