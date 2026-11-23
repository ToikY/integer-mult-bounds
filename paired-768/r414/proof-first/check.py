"""Check the two ordinary paid routes against authenticated source anchors."""

import argparse
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tarfile

PINS = {
    "archive": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "prepare.py": "bc401e5c47d275617f3c7d162d56ea4c604ef3d4c6637ab2a8aa8627a570a9f6",
}
TIERED = "research/tiered-native-multiplier/"
WEIGHTED = "research/frequency-weighted-native-multiplier/"
TRIANGULAR = "inputs/triangular/"
INSTALLER = TIERED + "source/installer.tar.gz"
RETIMED = INSTALLER + "/retimed-source.tar.gz"
OLD = RETIMED + "/predecessor/predecessor-8030.tar.gz"
HASHES = {}


def digest(data):
    return sha256(data).hexdigest()


def member(parent, name, path):
    with tarfile.open(fileobj=BytesIO(parent)) as archive:
        item = archive.getmember(name)
        assert item.isfile()
        data = archive.extractfile(item).read()
    HASHES[path] = digest(data)
    return data


def anchors(data, *texts):
    assert all(x.encode() in data for x in texts), texts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--prepare", type=Path, required=True)
    args = parser.parse_args()
    archive = args.archive.read_bytes()
    prepare = args.prepare.read_bytes()
    assert digest(archive) == PINS["archive"]
    assert digest(prepare) == PINS["prepare.py"]
    installer = member(archive, INSTALLER, INSTALLER)
    retimed = member(installer, "retimed-source.tar.gz", RETIMED)
    predecessor = member(retimed, "predecessor/predecessor-8030.tar.gz", OLD)

    def original(name):
        return member(predecessor, name, f"{OLD}/{name}")

    carrier = original("ordinary_carrier.py")
    binary = original("binary_receiver.py")
    receiver = original(TRIANGULAR + "receiver.py")
    body = original(TRIANGULAR + "same_order_body.py")
    direct = original(TRIANGULAR + "direct_body.py")
    quotient = original(TRIANGULAR + "quotient_route.py")
    five = member(retimed, "five_exchange.py", RETIMED + "/five_exchange.py")
    patch = member(retimed, "receiver.patch", RETIMED + "/receiver.patch")
    machine = member(retimed, "machine.patch", RETIMED + "/machine.patch")
    tiered = member(archive, TIERED + "runtime.patch", TIERED + "runtime.patch")
    weighted = member(archive, WEIGHTED + "runtime.patch", WEIGHTED + "runtime.patch")
    production = member(installer, "production.patch", INSTALLER + "/production.patch")

    anchors(carrier, "previous = partial(ternary, maximum=stage - 1, profile=profile)",
            "direct = (digits + width - 1) // width <= rank**8",
            "backend = Receiver(rank, layout, previous, direct=direct, profile=profile)")
    anchors(binary, "class Receiver(PhysicalReceiver):", "core.serve_line(",
            "banks.start(job.owner)", "banks.install(job.owner, out)")
    anchors(body, "f, remainder = divmod(atoms, self.n)", "previous_swap=self.previous",
            "self.compiled,", "f=f,", "if rem or not unused:")
    anchors(patch, "+from five_exchange import direct_line, same_order_line",
            "+from five_exchange import same_order_line")
    anchors(direct, "def direct_route(", "core.previous(src, dst, width, p, g, s)",
            "previous_swap=core.previous")
    anchors(receiver, "if not frame.word:", "atoms=f,", "direct_line(self, source, target",
            "packet = self.high * body", "length = unused * packet",
            "for low in canonical_lows(self.n):", "pending.pop_forward(argument, length)",
            "answers.append(reply, length)", "pending.top != before",
            "type_route(completed, target, unused, self.low, packet, inverse=True)")
    anchors(quotient, "def free_count(n):", "return n * (n + 1) // 2",
            "for rows in low_rows(n):", "yield tuple(x for row in rows for x in row)")
    anchors(five, "yield partial(core.weighted, atoms=f,", "yield move(inverse_word(frame.word))",
            "pairs = corner_exchanges(*line(0), pivot)", "core.weighted, atoms=f,",
            "yield child(0, n - 1, True)", "for left, right in reversed(pairs):")
    anchors(machine, "+            run(self.recipe, jobs, Machine())",
            "from ordinary_carrier import ordinary_swap")
    for later in (machine, tiered, weighted, production, prepare):
        for symbol in (b"serve_line(", b"def direct_line", b"def same_order_line",
                       b"def direct_route", b"weighted_pair,", b"def canonical_lows"):
            assert not any(symbol in line and line[:1] in (b"+", b"-")
                           for line in later.splitlines()), symbol

    # The quotient mean decreases as x grows. N=9 suffices, and N=8
    # fails this particular rounded bound.
    upper = Fraction(2390, 1024)
    assert Fraction(21 * 3**7 + 3, 9 * 3**7 - 1) <= upper
    assert Fraction(21 * 3**6 + 3, 9 * 3**6 - 1) > upper
    assert 1 <= upper < Fraction(2391, 1024)
    assert upper / Fraction(2391, 1024) == Fraction(2390, 2391)

    print(json.dumps({
        "head": "c20a08dc0a79a989e3515068560d5da371c0a2a8",
        "cases": {
            "DIRECT": "Exactly one weighted(atoms=f); include both inverse basis routes in earlier/local charge.",
            "QUOTIENT": "One equal high-cardinality packet per canonical low; 1+2*len(pairs) weighted calls with atoms=f.",
        },
        "source_pins": PINS | HASHES,
        "same_stage_claim": "floor(c/N), both covered moments",
        "elapsed_cap_seconds": 180,
        "scope": "Static literal path and inherited mean, no installer or physical replay.",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
