"""Pinned #7120 chart259 construction using the credited independent-helper split."""
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

from split import basis, check_cut, inverse, split
from support import L

SOURCE = "4f19c6ee57b74d7c3ea1863df0b33fe275a3a7511f77084f05726ee216ebdc34"


def operands(event):
    return (1, 2) if event[0] in ("ADD", "COPY") else (1,)


def inventory(word):
    public = word["public"]
    charts = word["initial"] + [None] * word["owned_fields"]
    frames = [L.span(frame) for frame in word["frames"]]
    paid = Counter()
    owned = []
    for event in word["program"]:
        op, role = event[:2]
        if op == "MOVE":
            u, v, private = event[2:]
            L.need(charts[role] == u and private == (role >= public), "MOVE source and ownership")
            L.need(frames[u] < frames[v] or frames[v] < frames[u], "Nested MOVE")
            paid[abs(len(word["frames"][u]) - len(word["frames"][v]))] += 1
            charts[role] = v
            if private:
                owned.append([op, role - public, u, v, private])
        elif op in ("INIT", "CLEAR"):
            frame = event[2]
            L.need(role >= public and charts[role] == (None if op == "INIT" else frame), "Owned lifetime")
            charts[role] = frame if op == "INIT" else None
            owned.append([op, role - public, frame])
        else:
            L.need(all(charts[event[j]] == event[-1] for j in operands(event)), "Scalar chart")
    L.need(charts == word["final"] + [None] * word["owned_fields"], "Final chart and ownership state")
    return paid, owned


def construct(word_path: Path, witness_path: Path, out: Path) -> dict:
    raw = gzip.decompress(word_path.read_bytes())
    L.need(sha256(raw).hexdigest() == SOURCE, "Exact source word")
    source = json.loads(raw)
    spec = json.loads(witness_path.read_bytes())
    n, p, f, k = source["public"], spec["pivot"], spec["frame"], spec["cut_after"]
    u, v = source["initial"][p], source["final"][p]
    L.need((n, p, f, k, u, v, spec["ranks"]) == (1489, 231, 259, 31846, 3, 246, [3, 5]), "Literal cut")
    a, b, c, d = check_cut(source, spec)
    G, J = basis(c, d, p, u), basis(a, b, p, f)
    scalars = [Fraction(e[-2]) for e in G + J + inverse(G) + inverse(J)]
    L.need(all(q.denominator & (q.denominator - 1) == 0 for q in scalars), "Dyadic scalar basis")
    result = split(source, spec)
    paid, owned = inventory(result)
    old_paid, old_owned = inventory(source)
    L.need((paid, owned) == (old_paid, old_owned), "All paid ranks and owned events preserved")
    L.need(result["program"][:len(G)] == inverse(G), "Input conjugation")
    L.need(result["program"][len(G)+k+1:len(G)+k+1+len(J)] == J, "Cut conjugation")
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    compressed = gzip.compress(payload, mtime=0)
    compressed = compressed[:9] + b"\xff" + compressed[10:]
    out.write_bytes(compressed)
    return {
        "status": "PASS_CHART259_LITERAL",
        "source_word_sha256": SOURCE,
        "word_sha256": sha256(payload).hexdigest(),
        "compressed_sha256": sha256(compressed).hexdigest(),
        "program_events": len(result["program"]),
        "public": result["public"],
        "owned_fields": result["owned_fields"],
        "cut_before": k + 1, "frame": f,
        "retained_role": p, "successor_role": n,
        "input_inverse": inverse(G), "cut_basis": J,
        "ordinary_delta": 2*(len(G)+len(J)),
        "productive_delta": {3: 1, 5: 1, 8: -1}, "paid_delta": {},
        "new_scalar_denominator_max": max(q.denominator for q in scalars),
        "new_scalar_numerator_max": max(abs(q.numerator) for q in scalars),
        "suffix_contacts": [i for i, event in enumerate(source["program"])
                            if i > k and any(event[j] == p for j in operands(event))],
    }


if __name__ == "__main__":
    print(json.dumps(construct(*map(Path, sys.argv[1:])), indent=2, sort_keys=True))
