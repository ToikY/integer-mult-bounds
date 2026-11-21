"""Screen grade-eight helper splits at the funded packet-724 midpoint of #7991."""
from argparse import ArgumentParser
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
from time import monotonic

PIN = {
    "sources/WORD.json.gz": "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",
    "sources/binary_operator.py": "36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349",
    "sources/bit_native.py": "4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e",
    "round322/split.py": "71d9d6278bb13f2cb66b57d818e2f6ad4c50ab291c741475091e31af25a6702c",
}
SPLICE = "b3faa53e42b1952148c3df462228292109f12b44ed528ffd39ce96503be2a14d"


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("round322", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    start = monotonic()
    for key, pin in PIN.items():
        path = args.round322 if key == "round322/split.py" else args.package / key
        assert sha256(path.read_bytes()).hexdigest() == pin, key
    word = json.loads(gzip.decompress((args.package / "sources/WORD.json.gz").read_bytes()))
    native = runpy.run_path(str(args.package / "sources/bit_native.py"))
    operator = runpy.run_path(str(args.package / "sources/binary_operator.py"))
    support = runpy.run_path(str(args.round322))["pulse"]
    assert word["program"][157] == ["MOVE", 724, 8, 328]
    mid = 270
    word["program"][157:158] = [["MOVE", 724, 8, mid], ["MOVE", 724, mid, 328]]
    assert operator["canonical_hash"](word) == SPLICE
    atlas = operator["Atlas"](word["frames"])
    s, f, edges, rows, clocks = native["extract"](word)
    order = sorted(edges, key=clocks.get)
    columns = native["basis"](s, edges, rows, order)
    values = {i: 1 << i for i in s}
    for k in order:
        values[k] = native["combine"](rows[k], values)
    assert [atlas.grade(*edges[k]) for k in (724, 725)] == [3, 2]
    cuts = []
    for reverse in (False, True):
        beginnings, ends = (f, s) if reverse else (s, f)
        reads = [(-1,i,1 << i) for i in s if beginnings[i] == mid]
        sends = [(len(word["program"]),i,1 << i) for i in s if ends[i] == mid]
        for k in order:
            a, b = edges[k][::-1] if reverse else edges[k]
            time = len(word["program"])-1-clocks[k] if reverse else clocks[k]
            if b == mid:
                reads.append((time, k, columns[k] if reverse else values[k]))
            if a == mid:
                sends.append((time, k, values[k] if reverse else columns[k]))
        cut = len(word["program"])-1-158 if reverse else 157
        cuts.append((beginnings, ends, [z for z in reads if z[0] <= cut], [z for z in sends if z[0] > cut]))
    helpers = list(range(222, word["public"]))
    assert len(helpers) == 458
    report = dict(pins=PIN, splice=SPLICE, status="exhausted", next_owner=None, tested=[], grade_eight=[],
                  geometry=[], cases=[], witness=None)
    for h in helpers:
        if monotonic() - start >= 60:
            report.update(status="capped",next_owner=h)
            break
        report["tested"].append(h)
        if atlas.grade(s[h], f[h]) != 8:
            continue
        report["grade_eight"].append(h)
        if (atlas.grade(s[h], mid), atlas.grade(mid, f[h])) != (4,4):
            continue
        report["geometry"].append(h)
        for reverse, (beginnings, ends, reads, sends) in enumerate(cuts):
            a = sum(1 << i for i in s if beginnings[i] == beginnings[h])
            b = sum(1 << i for i in s if ends[i] == ends[h])
            reason, witness = support(reads,sends,a,b,1 << h,bool(reverse))
            report["cases"].append([h,reverse,reason])
            if witness:
                report.update(status="conditional-support-witness",witness=witness)
                break
        if report["witness"]:
            break
    report["seconds"] = monotonic()-start
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(report["status"], len(report["tested"]), len(report["grade_eight"]), len(report["geometry"]),
          Counter(c[-1] for c in report["cases"]), report["witness"], report["seconds"])


if __name__ == "__main__":
    main()
