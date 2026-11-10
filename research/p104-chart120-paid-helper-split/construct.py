"""Exact portable chart-120 constructor for pinned #7115.

The normalized row and column rules retain the prior chart split audits.
Credit the #7115 and independent-helper predecessors. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

SOURCE = "ae30929ff3b5f6b49a5edac78e2164acfbf809113d0b9f03249ef940dd7b2491"
TARGET = "ff51fcc949bc50a31230a784822ab6f0d079c9102abf22c75746b2b5cdd09553"


def display(counter):
    return {k: v for k, v in sorted(counter.items()) if v}


def update(v,k,a):
    x=v.get(k,Q(0))+a
    if x:v[k]=x
    else:v.pop(k,None)


def row(vector,events):
    v=vector.copy()
    for e in reversed(events):
        op,r=e[:2]
        a=v.get(r,Q(0))
        if not a or op=='MOVE':continue
        if op in ('INIT','CLEAR'):
            del v[r]
        elif op=='SCALE':
            update(v,r,a*(Q(e[-2])-1))
        elif op=='COPY':
            del v[r]
            update(v,e[2],a*Q(e[-2]))
        elif op=='ADD':
            update(v,e[2],a*Q(e[-2]))
        else:raise AssertionError(op)
    return v


def column(vector,events):
    v=vector.copy()
    for e in events:
        op,r=e[:2]
        if op=='MOVE':continue
        if op in ('INIT','CLEAR'):
            v.pop(r,None)
        elif op=='SCALE':
            update(v,r,v.get(r,Q(0))*(Q(e[-2])-1))
        elif op=='COPY':
            value=Q(e[-2])*v.get(e[2],Q(0))
            v.pop(r,None)
            update(v,r,value)
        elif op=='ADD':
            update(v,r,Q(e[-2])*v.get(e[2],Q(0)))
        else:raise AssertionError(op)
    return v


def operands(e):
    return (1,2) if e[0] in ('ADD','COPY') else (1,)


def inverse(events):
    return [[*e[:-2],str(-Q(e[-2])),e[-1]] for e in reversed(events)]


def span(basis):
    out = {0}
    for value in basis:
        assert value not in out
        out |= {v ^ value for v in out}
    return out


def construct(native_package: Path, witness_path: Path, out: Path) -> dict:
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    raw = gzip.decompress((native_package / "WORD.json.gz").read_bytes())
    assert sha256(raw).hexdigest() == SOURCE
    w = json.loads(raw)
    old = w["program"]
    n = w["public"]
    witness_data = json.loads(witness_path.read_bytes())
    witness = witness_data.get("witness", witness_data)
    p, cut, f = [witness[k] for k in ("pivot", "cut", "chart")]
    u, v = witness["helper_boundary"]
    h, middle, k = witness["charged_move"]
    move = witness["charged_move_index"]
    role = 962
    assert old[move] == ["MOVE", role, h, k, False] and middle == f
    assert (n, p, cut, f, u, v, move) == (1485, 1447, 38670, 120, 597, 127, 38668)
    contacts = lambda q, start, end: [i for i in range(start, end)
        if any(old[i][j] == q for j in operands(old[i]))]
    assert contacts(role, move, 38707) == [move]
    assert contacts(role, 38707, 38708) == [38707]
    a, b, c, d = ({int(j): Q(v) for j, v in witness[s].items()} for s in ("a", "b", "c", "d"))
    unit = {p: Q(1)}
    assert c == d == unit and not witness["endpoint_basis"]
    assert row(a, old[:cut]) == c and column(b, old[cut:]) == d
    assert sum(q * b.get(j, 0) for j, q in a.items()) == 1
    assert row(unit, old) == column(unit, old) == unit
    J = witness["cut_basis"]
    assert row(unit, J) == a and column(b, J) == unit
    assert all(e[0] == "ADD" and Q(e[-2]).denominator & (Q(e[-2]).denominator-1) == 0 for e in J)

    def shift(event, rebind=False):
        event = event.copy()
        for j in operands(event):
            if event[j] >= n:
                event[j] += 1
            elif rebind and event[j] == p:
                event[j] = n
        return event

    program = [shift(e) if i != move else ["MOVE", role, h, f, False]
               for i, e in enumerate(old[:cut])]
    program += J + [shift(e, True) for e in inverse(J)] + [["MOVE", role, f, k, False]]
    program += [shift(e, True) for e in old[cut:]]
    final = w["final"] + [v]
    final[p] = f
    new = dict(w, public=n+1, initial=w["initial"]+[f], final=final, program=program)
    charts = new["initial"] + [None] * w["owned_fields"]
    frame_spans = [span(frame) for frame in w["frames"]]
    assert frame_spans[u] < frame_spans[f] < frame_spans[v]
    assert frame_spans[h] < frame_spans[f] < frame_spans[k]
    paid = Counter()
    for e in program:
        op, r = e[:2]
        if op == "MOVE":
            assert charts[r] == e[2] and e[4] == (r >= n+1)
            a0, b0 = (frame_spans[j] for j in e[2:4])
            assert a0 < b0 or b0 < a0
            paid[abs(len(w["frames"][e[2]])-len(w["frames"][e[3]]))] += 1
            charts[r] = e[3]
        elif op == "INIT":
            assert r >= n+1 and charts[r] is None
            charts[r] = e[2]
        elif op == "CLEAR":
            assert r >= n+1 and charts[r] == e[2]
            charts[r] = None
        else:
            assert all(charts[e[j]] == e[-1] for j in operands(e))
    assert charts == final + [None] * w["owned_fields"]
    paid.subtract(abs(len(w["frames"][e[2]])-len(w["frames"][e[3]])) for e in old if e[0]=="MOVE")
    assert display(paid) == {3:1,4:1,7:-1}
    assert [shift(e) for e in old if e[0] in ("INIT","CLEAR") or e[0]=="MOVE" and e[4]] == [
        e for e in program if e[0] in ("INIT","CLEAR") or e[0]=="MOVE" and e[4]]
    new_unit = {n: Q(1)}
    assert row(unit, program) == column(unit, program) == unit
    assert row(new_unit, program) == column(new_unit, program) == new_unit
    touched = {role,p,n} | {e[j] for e in J for j in operands(e)}
    for r in touched - {n}:
        for act in (row, column):
            old_axis = act({r:Q(1)}, old)
            assert act({r:Q(1)}, program) == {j+(j>=n):v for j,v in old_axis.items()}
    payload = json.dumps(new, sort_keys=True, separators=(",", ":")).encode()
    assert sha256(payload).hexdigest() == TARGET
    compressed = gzip.compress(payload, mtime=0)
    # Canonicalize the gzip OS marker across Python/zlib versions.
    expected = compressed[:9] + b"\xff" + compressed[10:]
    with out.open("xb") as fp:
        fp.write(expected)
    return {
        "status": "PASS_LITERAL_CHART120_CONSTRUCTION",
        "source_sha256": SOURCE, "word_sha256": TARGET,
        "compressed_sha256": sha256(expected).hexdigest(),
        "cut": cut, "chart": f, "charged_move_index": move,
        "retained_role": p, "successor_role": n,
        "public_roles": new["public"], "owned_fields": new["owned_fields"],
        "program_events": len(program), "paid_delta": display(paid),
        "productive_delta": {4: 2, 8: -1},
        "rebound_original_positions": contacts(p, cut, len(old)),
    }


if __name__ == "__main__":
    print(json.dumps(construct(*map(Path, sys.argv[1:])), indent=2, sort_keys=True))
