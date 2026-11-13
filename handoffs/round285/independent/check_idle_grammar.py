"""Authenticate the retained #7481 signed-idle closure and exercise its typed gates."""
import argparse
import ast
from collections import Counter
from gzip import decompress
from hashlib import sha256
from io import BytesIO
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from tarfile import open as tar_open
from time import perf_counter

PINS = {
    "TARIFF-SOURCE.json": "b7633ef72463b079ead5298e9f7b10ddc3365e6474d63f49ce125d26f69ad079",
    "producer54/validation_signed/run.py": "af1ec8e27b39fdcfe8c1c5ec3eae14c1124c62b5cdcf3c1218482b6291c6ceef",
    "producer54/validation_signed/RESULT.json": "e5c8d8c0cf4d3f3fc60ffe70eb084cf6c9eadf8e646c74b48762501bf5367474",
    "producer54/validation_signed/adapted/check_odd_physical_binding.py": "5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98",
    "producer54/validation_signed/adapted/check_odd_fixed_tape_counts.py": "e6246e9f8fbeae3077d82e585eafd3647c1a8758c58f33c7c13e7efa6c1e42bb",
    "producer54/validation_signed/adapted/check_odd_partial_admission.py": "35bd43f18bae916363fda120ff8ada7460ffb7920821596f599c88a556398117",
    "producer54/validation_signed/adapted/emit_odd_type_ab.py": "6fd9f61f9ba6c726524d1a585d0201b0eac61829ccae6be598f0f0fc1cb64f1a",
}
INPUTS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
}
INNER = "research/signed-caller-8x9/replay/supplier7112/short-caller/"
PINS_7113 = {
    INNER + "upstream_application.py": "d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184",
    INNER + "DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    INNER + "signed_child.py": "ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
    "research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json": INPUTS["7113-CALLER.json"],
}
COMPILER_PINS = {
    "compiler/SIGNED-RESULT.json": "e5c8d8c0cf4d3f3fc60ffe70eb084cf6c9eadf8e646c74b48762501bf5367474",
    "compiler/check_odd_physical_binding.py": "5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98",
    "compiler/check_odd_fixed_tape_counts.py": "e6246e9f8fbeae3077d82e585eafd3647c1a8758c58f33c7c13e7efa6c1e42bb",
    "compiler/check_odd_partial_admission.py": "35bd43f18bae916363fda120ff8ada7460ffb7920821596f599c88a556398117",
    "compiler/upstream_application.py": PINS_7113[INNER + "upstream_application.py"],
}
ARCHIVE_7113 = "research/p104-cohort-short-caller/inputs/pr7113.tar"
ARCHIVE_7113_SHA = "617341e053d7d4bc971ff3690ab2db01b1da8b3847ac4a71cc68f044b532efb5"
BINDER = "producer54/validation_signed/adapted/check_odd_physical_binding.py"
REPORT = "producer54/validation_signed/RESULT.json"
CAP = 30


def digest(raw):
    return sha256(raw).hexdigest()


def emit(**data):
    print(dumps(data, sort_keys=True), flush=True)


def authenticate(root, pins):
    data = {name: (root / name).read_bytes() for name in pins}
    assert {name: digest(raw) for name, raw in data.items()} == pins
    return data


def member(raw, path):
    with tar_open(fileobj=BytesIO(raw)) as archive:
        item = archive.getmember(path)
        assert item.isfile()
        return archive.extractfile(item).read()


def signed_archive(root, spec):
    name = spec["source_root"]
    blob = (root / name).read_bytes()
    followed = []
    for item in spec["chain"]:
        assert name == item["archive"] and digest(blob) == item["archive_sha256"]
        if name.endswith("/pr7116.tar"):
            signed = member(blob, ARCHIVE_7113)
            assert digest(signed) == ARCHIVE_7113_SHA
            followed.append({"archive": name, "member": ARCHIVE_7113, "member_sha256": ARCHIVE_7113_SHA})
            return signed, followed
        name = item["member"]
        blob = member(blob, name)
        assert digest(blob) == item["member_sha256"]
        followed.append(item)
    raise AssertionError("Missing signed archive path")


def patched_closure(sources, inner, app, caller, word):
    source = inner[INNER + "upstream_application.py"].decode()
    source = source[:source.index("def inverse(matrix):")]
    binder = ast.parse(sources[BINDER])
    patches = [node.value for node in binder.body
               if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
               and isinstance(node.value.func, ast.Name) and node.value.func.id == "patch"]
    for patch in patches:
        old, new, *count = [ast.literal_eval(arg) for arg in patch.args]
        assert source.count(old) == (count[0] if count else 1)
        source = source.replace(old, new)
    expected = loads(sources[REPORT])["checks"]["ODD-PHYSICAL-BINDING.json"]
    assert digest(source.encode()) == expected["patched_application_sha256"]
    assert "need(len(selected)==1 and a[1:]==[-1], 'one complete signed child')" in source
    assert "occurrences.append([ci,op,owner,rank]); P[rank] += 1" in source
    assert "owner = ['query_scratch',ci,pi] if op == 'QUERY' else ['main',pi,r]" in source
    node = next(n for n in ast.walk(ast.parse(source))
                if isinstance(n, ast.If) and ast.unparse(n.test) == "op in ('QUERY', 'IDLE_ONE', 'IDLE_ODD')")
    assert expected["caller_sha256"] == app["caller_sha256"]
    return node, expected


def paid_branch(node, caller, word):
    upstream_node = ast.Module(body=[node], type_ignores=[])
    compiled = compile(upstream_node, "<exact paid branch>", "exec")

    def need(valid, message):
        if not valid:
            raise ValueError(message)

    def dot(x, y):
        return (x & y).bit_count() % 2

    def terms(pairs):
        out = Counter()
        for k, v in pairs:
            out[k] += v
        return out

    def subtract(a, b):
        return {k: a.get(k, 0)-b.get(k, 0) for k in a.keys() | b.keys()
                if a.get(k, 0) != b.get(k, 0)}

    def translation(t):
        assert len(t) == 1
        vector, coefficient = next(iter(t.items()))
        assert coefficient == 2
        return vector

    def run(clock, event):
        tag, op, r, *a = event
        env = dict(ci=clock, op=op, r=r, a=a, kind=caller["types"][tag],
                   expected_stages=caller["stages"], word=word, need=need, dot=dot,
                   terms=terms, sub=subtract, translation=translation, occurrences=[], P=Counter(),
                   query_uses=0, idle_uses=0, lambda_uses=0)
        exec(compiled, env)
        return env["P"], env["occurrences"]

    return run


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("input_root", type=Path)
    parser.add_argument("--compiler-root", action="store_true",
                        help="read hash-pinned compiler/ sources instead of the nested archive")
    args = parser.parse_args()
    started = perf_counter()
    stages = []

    def timeout(_signal, _frame):
        emit(status="UNRESOLVED_CAP", completed=stages, cap_seconds=CAP, seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM, timeout)
    alarm(CAP)
    pinned = authenticate(args.input_root, INPUTS)
    if args.compiler_root:
        compiler = authenticate(args.source_root, COMPILER_PINS)
        sources = {BINDER: compiler["compiler/check_odd_physical_binding.py"],
                   REPORT: compiler["compiler/SIGNED-RESULT.json"]}
        inner = {INNER + "upstream_application.py": compiler["compiler/upstream_application.py"]}
        tape_source = compiler["compiler/check_odd_fixed_tape_counts.py"]
        checked_pins, chain = COMPILER_PINS, []
        stages.append("exact directly pinned #7481 compiler files")
    else:
        sources = authenticate(args.source_root, PINS)
        archive, chain = signed_archive(args.source_root, loads(sources["TARIFF-SOURCE.json"]))
        inner = {p: member(archive, p) for p in PINS_7113}
        assert {p: digest(raw) for p, raw in inner.items()} == PINS_7113
        tape_source = sources["producer54/validation_signed/adapted/check_odd_fixed_tape_counts.py"]
        checked_pins = PINS
        stages.append("exact #7481 replay chain and #7113 physical source")
    caller = loads(pinned["7113-CALLER.json"])
    app = loads(pinned["7481-APPLICATION.json"])
    word_raw = decompress(pinned["7481-WORD.json.gz"])
    assert digest(word_raw) == app["candidate_canonical_sha256"]
    word = loads(word_raw)
    node, expected = patched_closure(sources, inner, app, caller, word)
    branch = paid_branch(node, caller, word)
    fixed = expected["occurrence_and_geometry"]
    assert caller["events"][1339:1341] == [["B","IDLE_ODD",68,[8],-1], ["B","IDLE_ODD",69,[8],-1]]
    assert caller["types"]["B"]["ports"][0] == 15 and word["ports"][15] == 81
    assert fixed["paid"]["9"] == 32 and fixed["paid_positions"] == 110519
    if args.compiler_root:
        invoice_sources = [compiler["compiler/check_odd_partial_admission.py"]]
    else:
        child = inner[INNER + "signed_child.py"].decode()
        assert "if (row ^ col) >> (9*width):" in child and "for j in range(9*width):" in child
        invoice_sources = [sources[path] for path in (
            "producer54/validation_signed/run.py",
            "producer54/validation_signed/adapted/check_odd_partial_admission.py",
            "producer54/validation_signed/adapted/emit_odd_type_ab.py",
        )]
    for raw_source in invoice_sources:
        source = raw_source.decode().replace(chr(34), chr(39))
        assert "P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports" in source or "paid[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports" in source
    tape = tape_source.decode()
    assert "if e[:2]==[\"B\",\"IDLE_ODD\"]" in tape and "+signed_idle" in tape
    paid = Counter()
    for event in word["program"]:
        if event[0] == "MOVE":
            paid[abs(len(word["frames"][event[3]]) - len(word["frames"][event[2]]))] += caller["stages"]
    named = []
    signed_occurrences = []
    for clock, event in enumerate(caller["events"]):
        if event[0] == "J":
            continue
        op = event[1]
        actual, occurrences = branch(clock, event)
        paid.update(actual)
        if op == "IDLE_ODD":
            signed_occurrences.extend(occurrences)
            named.extend(occ for occ in occurrences if clock in (1339, 1340) and occ[2][1] == 15)
    assert paid == {int(k): v for k, v in fixed["paid"].items()}
    assert len(signed_occurrences) == 32
    assert named == [[1339, "IDLE_ODD", ["main",15,68],9], [1340, "IDLE_ODD", ["main",15,69],9]]
    stages.append("exact 32 signed idle occurrences and independently rebuilt paid histogram")
    rejects = {}
    for name, mutation in {
        "append_fractional_geometry": ["B", "IDLE_ODD", 68, [8], -1, {"rank": 13, "volume": "11/8", "port": 15}],
        "give_second_stage": ["B", "IDLE_ODD", 68, [8,9], -1],
    }.items():
        try:
            branch(1339, mutation)
        except ValueError as exc:
            assert str(exc) == "one complete signed child"
            rejects[name] = str(exc)
        else:
            raise AssertionError("An untyped child was accepted: " + name)
    invented = ["B", "IDLE_PARTIAL", 68, [8], -1, {"rank": 13, "volume": "11/8", "port": 15}]
    assert branch(1339, invented) == (Counter(), [])
    attempted = paid.copy()
    attempted[9] -= 1
    attempted[13] = 1
    actual = paid.copy()
    actual[9] -= 8
    assert actual != attempted and 13 not in actual
    rejects["custom_opcode_with_claimed_rank13"] = "no emitted occurrence; mismatched paid histogram"
    stages.append("exact local branch mutants")
    emit(status="PASS_RETAINED_IDLE_GRAMMAR_EXCLUDES_ONE_PARTIAL_RANK13_CHILD", completed=stages,
         source_pins=checked_pins, input_pins=INPUTS,
         inner_7113_pins={} if args.compiler_root else PINS_7113, archive_chain=chain,
         patched_application_sha256=expected["patched_application_sha256"], controls=rejects,
         old_paid_positions=fixed["paid_positions"], old_rank_nine_positions=fixed["paid"]["9"],
         signed_occurrences=signed_occurrences, named_pair_occurrences=named,
         independent_paid_histogram=dict(paid),
         actual_port=15, central_axis=81, body_axes=list(range(65,73)), old_clocks=[1339,1340],
         one_call_rank13_volume_11_over_8=False, scope="retained grammar and invoice only",
         cap_seconds=CAP, seconds=perf_counter()-started)
    alarm(0)


if __name__ == "__main__":
    main()
