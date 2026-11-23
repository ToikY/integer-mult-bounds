"""Replay one literal raw graph transaction on instrumented finite fields."""
import argparse
import ast
import gzip
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from types import SimpleNamespace as Record
import signal
import tarfile

NODE, DONOR = 104493, 94870
RANK, CHARTS = 5, (365, 529)
RAW_SHA = "86c30fd4a906830bb6f4b54cdc0be083bd2649bebf68da7383efd7beee223700"
TYPED_SHA = "0c268432c9d48798c17d927f2d900b5e69dfc6585166cd71f253913e389c3b47"
SIGNED_SHA = "316bb1a57ea8aa87fb2b565a4899c9b0b5a64ff1513c89e14a19d83ecd58e8e1"
WORD_SHA = "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149"
ARCHIVE_SHA = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"


def pinned(data, expected):
    assert sha256(data).hexdigest() == expected
    return data


def member(data, name):
    with tarfile.open(fileobj=BytesIO(data)) as archive:
        item = archive.getmember(name)
        assert item.isfile()
        return archive.extractfile(item).read()


def read_sources(package, signed):
    root = pinned((package / "peer8057.tar.gz").read_bytes(), ARCHIVE_SHA)
    nested = root
    for path in ("research/tiered-native-multiplier/source/installer.tar.gz",
                 "retimed-source.tar.gz", "predecessor/predecessor-8030.tar.gz",
                 "inputs/triangular/inputs/retained.tar.gz"):
        nested = member(nested, path)
    source = pinned(member(nested, RAW_SHA), RAW_SHA)
    typed = pinned(member(root, "research/frequency-weighted-native-multiplier/typed_raw.py"), TYPED_SHA)
    compressed = (package / "w5669_shortcut5.json.gz").read_bytes()
    word = json.loads(gzip.decompress(pinned(compressed, WORD_SHA)))
    evidence = json.loads(pinned(signed.read_bytes(), SIGNED_SHA))
    assert [tuple(pair[1:]) for pair in word["moves"] if pair[0] == NODE] == [CHARTS]
    terms, = (terms for node, terms in word["forms"] if node == NODE)
    assert terms == [[DONOR, "1"]]
    assert word["schedule"].count(NODE) == 1 and word["schedule"].index(DONOR) < word["schedule"].index(NODE)
    assert evidence["record"]["rank"] == RANK and evidence["node"] == NODE
    return source, typed, evidence["record"], [(i, Q(v)) for i, v in terms]


def literal_branch(source):
    tree = ast.parse(source)
    raw, = (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ComplexRaw")
    graph, = (node for node in raw.body if isinstance(node, ast.FunctionDef) and node.name == "graph")
    start, = (i for i, node in enumerate(graph.body) if isinstance(node, ast.For)
              and isinstance(node.iter, ast.Subscript)
              and isinstance(node.iter.value, ast.Name) and node.iter.value.id == 'g'
              and isinstance(node.iter.slice, ast.Constant) and node.iter.slice.value == 'schedule')
    branch = ast.parse("def transaction(self, clock, call, cols, a, g, sample, held, terminals, plans, centers): pass").body[0]
    branch.body = graph.body[start:]
    tree.body.append(branch)
    namespace = {}
    exec(compile(ast.fix_missing_locations(tree), "raw48.py", "exec"), namespace)
    return namespace


def quarter(value, turn):
    x, y = value
    return ((x, y), (-y, x), (-x, -y), (y, -x))[turn % 4]


class Field:
    def __init__(self, data=()):
        self.data = dict(data)
        self.live = True

    def blank(self):
        assert self.live
        return Field()

    def clear(self):
        assert self.live
        self.data.clear()

    def scale_add(self, other, scale):
        assert self.live and other.live and not self.data
        self.data = {addr: tuple(scale * x for x in value) for addr, value in other.data.items()}

    def scale(self, scale):
        assert self.live
        self.data = {addr: tuple(scale * x for x in value) for addr, value in self.data.items()}

    def phase(self, phase, suffix):
        assert self.live and suffix == 0
        self.data = {addr: quarter(value, phase(addr)) for addr, value in self.data.items()}

    def retire(self):
        assert self.live
        self.live = False

    def replace(self, other):
        assert self.live and other.live and self is not other
        self.data = other.data
        other.retire()


class Columns:
    window, offset, suffix = 1, 0, 0

    def row(self, field, target, source=None):
        assert field.live
        if source is None:
            mask = sum(1 << i for i in target)
            field.data = {addr ^ mask: value for addr, value in field.data.items()}
        else:
            row = list(zip(target, source, strict=True))
            field.data = {addr ^ sum(((addr >> i) & 1) << j for j, i in row): value
                          for addr, value in field.data.items()}


def direct_monomial(data, chart, cols):
    """Independent dense-bit formula for each sampled address across column bundles."""
    result = {}
    for addr, value in data.items():
        target, phase = addr >> (9 * cols) << (9 * cols), chart["phase"] * cols
        for j in range(cols):
            x = sum(((addr >> (i * cols + j)) & 1) << i for i in range(9))
            phase += sum(q * ((x >> i) & 1) for i, q in enumerate(chart["linear_Z4"]))
            phase += sum(2 * ((x >> i) & (x >> k) & 1)
                         for i, row in enumerate(chart["quadratic_rows"])
                         for k in range(i + 1, 9) if row >> k & 1)
            for i, row in enumerate(chart["matrix_rows"]):
                bit = ((row & x).bit_count() ^ (chart["offset"] >> i)) & 1
                target |= bit << (i * cols + j)
        result[target] = quarter(value, phase)
    return result


def execute(raw, typed, record, terms, header, bad_tag=False):
    cols = 2 * (header - 1)
    start = {1 | 1 << (9 * cols + 3): (9, -15),
             13 | 1 << (9 * cols + 5): (21, 6)}
    donor, target = Field(start.items()), Field([(9, (18, 24))])
    item = raw["ComplexRaw"].__new__(raw["ComplexRaw"])
    item.fields = {"terminal": target}
    item.cursor, item.low, item.bundle = 0, 0, 1
    item.columns, item.Job = Columns(), lambda owner, axes: Record(owner=owner, axes=tuple(axes))
    graph = {"schedule": [NODE], "first_output": NODE}
    a = Record(forms={NODE: terms}, moves={NODE: CHARTS}, odd=3,
               factors={CHARTS: (RANK, raw["monomial"](record["right"]),
                                       raw["monomial"](record["left"]))})
    graph_source = raw["transaction"](item, 11, 3, cols, a, graph, donor, {DONOR: donor},
                                      {0: target}, {0: ("helper", (), ())}, tuple(range(9)))
    role = ("return", 11, 3, NODE)
    targets = [Record(tag="target", rank=RANK)]
    word = Record(targets=targets, paid=[Record(tag=role if not bad_tag else role[:-1] + (NODE+1,), rank=RANK)])
    physical = Record(raw=lambda _ports, width: graph_source if width == cols else ())
    runner = typed["TypedRaw"](word, physical)
    jobs = runner.native([item.Job("terminal", range(RANK * cols))], header)
    if bad_tag:
        try:
            next(jobs)
        except ArithmeticError as err:
            assert str(err) == "A raw loan differs from its source"
            assert target.data == {9: (18, 24)} and donor.live
            return {"wrong_return_tag_rejected": True}
        raise AssertionError("The typed path accepted the wrong return tag")
    job = next(jobs)
    token = (item, 0)
    assert job.owner == token and job.axes == tuple(range(RANK * cols))
    assert set(item.fields) == {"terminal", token} and item.fields["terminal"] is target
    assert target.data == {9: (18, 24)}
    exposed = item.fields[token]
    right = direct_monomial(start, record["right"], cols)
    assert exposed.data == right
    # Instrument a returning child with a nontrivial signed payload and substitution.
    returned_data = {addr ^ 1: quarter(value, 1) for addr, value in right.items()}
    replacement = Field(returned_data.items())
    item.fields[token] = replacement
    exposed.retire()
    assert next(jobs, None) is None
    expected = {addr: tuple(Q(x, 3) for x in value)
                for addr, value in direct_monomial(returned_data, record["left"], cols).items()}
    assert item.fields == {"terminal": target} and target.live and target.data == expected
    assert not exposed.live and not replacement.live and not donor.live
    assert {addr >> (9 * cols) for addr in target.data} == {8, 32}
    return {"typed_header": header, "column_bundle_width": cols, "paid_axes": len(job.axes),
            "fresh_token_retired": True, "terminal_owner_identity_preserved": True,
            "dirty_spectator_addresses_preserved": True}


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--signed-receipt", type=Path, required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("one owner fixture timed out")))
    signal.alarm(30)
    source, code, record, terms = read_sources(args.package, args.signed_receipt)
    raw, typed = literal_branch(source), {}
    exec(compile(code, "typed_raw.py", "exec"), typed)
    result = {"scope": "Literal graph node and terminal loop; one synthetic typed kind-1 transaction",
              "relay": NODE, "charts": CHARTS, "raw_sha256": RAW_SHA, "typed_sha256": TYPED_SHA,
              "positive": execute(raw, typed, record, terms, 3),
              "negative": execute(raw, typed, record, terms, 3, bad_tag=True),
              "unrun": ["real paid child", "actual complete raw graph", "kind-0 splitting", "adjoint physical path"]}
    print(json.dumps(result, indent=2))
    signal.alarm(0)


if __name__ == "__main__":
    main()
