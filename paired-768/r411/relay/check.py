"""Replay the exact five-relay rational word with no runtime installation."""

from argparse import ArgumentParser
from hashlib import sha1, sha256
from pathlib import Path
from time import monotonic
import gzip
import json
import runpy
import signal

HEAD = "c20a08dc0a79a989e3515068560d5da371c0a2a8"
BLOB = "2381d62342e3caa457e1ef498f05ba98dcc1b11c"
GZIP = "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149"
WORD = "ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35"
PREDECESSOR = "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
LAYOUT = "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
SOURCE = "b33575085bcaf8e646ad7656d1f8d2c7ad402712e6b49efd307fc926f2fb39b0"
GRID = 154113755636630124932500335624192000
RELAYS = ((95398, 99468, 412, 798, 922), (97628, 100531, 614, 795, 917),
          (95050, 101275, 392, 1037, 918), (95056, 95425, 411, 1038, 921),
          (96741, 96743, 365, 1028, 529))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique(pairs):
    data = {}
    for key, val in pairs:
        need(key not in data, f"Repeated key {key}")
        data[key] = val
    return data


def authenticate(raw, claim):
    need(sha256(raw).hexdigest() == claim, f"Expected exact SHA-256 {claim}")
    return raw


def moves(word):
    return {label: (a, b) for label, a, b in word["moves"]}


def topology(word, move):
    rows = dict(word["forms"])
    order = word["schedule"]
    first = word["first_output"]
    ends = word["final"]
    out = set(range(first, first + len(ends)))
    need(len(order) == len(rows) == len(word["forms"]) and set(order) == rows.keys()
         and rows.keys() == move.keys() | out and not (move.keys() & out), "Exact paid/output topology")
    arrived = {~i: chart for i, chart in enumerate(word["initial"])}
    for label in order:
        required = move[label][0] if label in move else ends[label-first]
        donors = [j for j, _ in rows[label]]
        need(len(donors) == len(set(donors)) and all(arrived.get(j) == required for j in donors),
             f"Topological chart-local donor of {label}")
        if label in move:
            arrived[label] = move[label][1]
    return rows


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--word", type=Path, required=True)
    p.add_argument("--source-manifest", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    signal.alarm(30)
    start = monotonic()
    raw = authenticate(a.word.read_bytes(), GZIP)
    need(sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest() == BLOB, "Exact Git blob ID")
    new = json.loads(gzip.decompress(raw), object_pairs_hook=unique)
    pins = json.loads(authenticate(a.source_manifest.read_bytes(), SOURCE), object_pairs_hook=unique)
    for key, val in pins.items():
        authenticate((a.source/key).read_bytes(), val)
    engine = runpy.run_path(str(a.source / "verify_bidirectional.py"))
    rebuild = runpy.run_path(str(a.source / "verify_split_helpers.py"))
    before, layout = rebuild["rebuild"]()
    old, _ = engine["reconstruct"](before, engine["read"]("BANK-FACTORS.json.gz"))
    canonical = engine["canonical"]
    need(canonical(old) == PREDECESSOR and canonical(new) == WORD and canonical(layout) == LAYOUT,
         "Both canonical word hashes and exact inherited layout")
    need(all(new[k] == old[k] for k in ("initial","final","frames","first_output"))
         and len(new["initial"]) == len(new["final"]) == 1291, "All original owner endpoints")
    old_m, new_m = moves(old), moves(new)
    need(len(old_m) == 5674 and len(new_m) == 5669, "Chronological transfer count")
    retired = old_m.items()-new_m.items()
    added = new_m.items()-old_m.items()
    need(len(retired) == 10 and len(added) == 5, "Only five relay substitutions in paid edges")
    old_rows = dict(old["forms"])
    rows = topology(new, new_m)
    span = engine["inspect"].__globals__["frame_span"]
    finished = []
    for x, y, f, middle, target in RELAYS:
        need((x, (f, middle)) in retired and (y, (middle, target)) in retired
             and x in dict(old_rows[y]), f"Original named relay {x}→{y}")
        direct = [j for j, edge in added if edge == (f,target)]
        need(len(direct) == 1, "One direct typed replacement")
        fa, fm, ft = (span(old["frames"][index]) for index in (f,middle,target))
        need(fa < fm < ft, "Strict nested frames throughout the relay")
        tags = (len(fm)-len(fa),len(ft)-len(fm),len(ft)-len(fa))
        grade = [v.bit_length()-1 for v in (len(fa),len(fm),len(ft))]
        finished.append({"removed":[x,y],"inserted":direct[0],"charts":[f,middle,target],
                         "dimensions":grade,"paid_grades":[grade[1]-grade[0],grade[2]-grade[1],grade[2]-grade[0]]})
    del old, before, old_rows
    # This is the only full map replay. It rejects an unapplied or wrong
    # source re-encoding whenever it changes the original terminal map.
    work, grid, bits = engine["forward"](new,layout)
    compatible = GRID % grid == 0
    signal.alarm(0)
    result = {"head":HEAD,"word_git_blob":BLOB,"word_archive_sha256":GZIP,"word_sha256":WORD,
              "predecessor_word":PREDECESSOR,"source_manifest_sha256":SOURCE,
              "source_sha256_by_path":pins,"layout_sha256":LAYOUT,"relays":finished,
              "owners":1291,"chart_local_rows":len(rows),"moves":len(new_m),
              "finite_forward_replays":1,"rational_products":work,"minimum_product_grid":grid,
              "literal_peak_bits":bits,"installed_product_grid":GRID,"grid_compatible":compatible,
              "status":"SOURCE_ONLY_FORWARD_PASS" if compatible else "SOURCE_GRID_OBSTRUCTION",
              "elapsed_seconds":round(monotonic()-start,3),"cap_seconds":30}
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if not compatible:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
