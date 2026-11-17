"""One #7605 fixed-prefix swap-then-delete gate. CPython >=3.10."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm
import sys

PINS = {
    "word7605.json.gz": "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d",
    "FINAL7605.json": "f24baa73a60d084a6d613dad914f1237a5890a049a183b993af39c75dde99add",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    }


def observed(evt, role):
    return role == evt[1] or (evt[0] in ("ADD", "COPY") and role == evt[2])


def span(frame):
    elements = {0}
    for value in frame:
        assert value not in elements
        elements |= {value ^ prior for prior in elements}
    return elements


def main(root):
    alarm(30)
    data = {name:(root/name).read_bytes() for name in PINS}
    assert {name:sha256(content).hexdigest() for name,content in data.items()} == PINS
    final = json.loads(data["FINAL7605.json"])
    assert final["caller_sha256"] == PINS["7113-CALLER.json"]
    callers = sum(event[0] == "J" for event in json.loads(data["7113-CALLER.json"])["events"])
    assert callers == 17
    raw = decompress(data["word7605.json.gz"])
    word = json.loads(raw)
    assert sha256(raw).hexdigest() == final["candidate_canonical_sha256"]
    tape = word["program"]
    assert len(tape) == 76636
    source, receiver, earlier, consumer = 396, 564, 1158, 504
    assert tape[38667] == ["MOVE",receiver,3,457,False]
    assert tape[38668] == ["ADD",earlier,receiver,"-1",457]
    assert tape[41705] == ["MOVE",earlier,457,844,False]
    assert tape[41706] == ["ADD",428,earlier,"-1",844]
    assert tape[42140] == ["ADD",receiver,source,"1",457]
    assert tape[42327] == ["MOVE",source,457,844,False]
    assert tape[42328] == ["ADD",source,428,"1",844]
    assert tape[42448] == ["MOVE",receiver,457,895,False]
    assert tape[42449] == ["ADD",consumer,receiver,"1",895]
    assert tape[42450] == ["MOVE",1396,363,895,False]
    assert [k for k in range(38669,41706) if observed(tape[k],earlier)] == [41705]
    assert [k for k in range(38669,42449) if observed(tape[k],receiver)] == [42140,42448]
    assert [k for k in range(42141,42449) if observed(tape[k],source)] == [42327,42328]
    assert all(word["initial"][r] == 3 and word["final"][r] == 127 for r in (source,receiver))
    frames = word["frames"]
    assert list(map(lambda f: len(frames[f]), (3,457,844,895))) == [0,3,6,6]
    assert span(frames[3]) < span(frames[457]) < span(frames[844])
    amend = {38667:[["MOVE",receiver,3,844,False]],38668:[],
             41706:[["ADD",earlier,receiver,"-1",844],tape[41706]],
             42140:[],42327:[],42328:[["ADD",receiver,428,"1",844]],
             42448:[["MOVE",source,457,895,False]]}
    trial = [out for clock,event in enumerate(tape[:42449])
             for out in amend.get(clock,[event])]
    for prefix,expected in ((tape[:42449],[consumer,receiver]),(trial,[source,consumer])):
        current = dict(enumerate(word["initial"]))
        for op,r,*args in prefix:
            if op == "MOVE":
                assert current[r] == args[0]
                current[r] = args[1]
            elif op == "INIT":
                assert r not in current
                current[r] = args[0]
            elif op == "CLEAR":
                assert current.pop(r) == args[0]
            else:
                assert current[r] == args[-1]
                if op in ("ADD","COPY"):
                    assert current[args[0]] == args[-1]
        assert sorted(r for r in current if current[r] == 895) == expected
    low,high = map(Q,final["raw_crossing"])
    power = run_path(str(root/"pricing.py"))["power_bounds"]
    lower = callers*(2*power(3,high)[0]-power(6,low)[1])
    upper = callers*(2*power(3,low)[1]-power(6,high)[0])
    assert 0 < lower <= upper < 1
    gate = run_path(str(root/"gate.py"))
    rows = gate["exact_cut_rows"]
    old_504,old_564 = rows(tape[:42449],[consumer,receiver],word["public"])
    new_396,new_504 = rows(trial,[source,consumer],word["public"])
    assert old_504 == new_504
    pivots = gate["basis"]([new_396,new_504])
    residual,recipe = gate["representation"](pivots,old_564)
    rec = {"cut":42449,"fixed_bank":[source,consumer],"target":receiver,
           "source_pins":PINS,"paid_delta":{"3":-34,"6":17},
           "gross_interval":[str(lower),str(upper)],"rank":len(pivots)}
    if residual:
        col = min(residual)
        probe = {col:1/residual[col]}
        def evaluate(row):
            return sum(v*probe.get(k,0) for k,v in row.items())
        for pivot,(vector,_) in sorted(pivots.items(),reverse=True):
            if val := evaluate(vector):
                probe[pivot] = -val
        assert [evaluate(row) for row in (new_396,new_504,old_564)] == [0,0,1]
        rec.update(status="EXCLUDE_FIXED_PREFIX_C1_AT_FIRST_READ", separator=probe,
                   target_rank=len(pivots)+1)
    else:
        rec.update(status="FIRST_READ_SPAN_PASSES_OTHER_GATES_PENDING", readout=recipe)
    print(json.dumps(rec, sort_keys=True, default=str))
    alarm(0)


if __name__ == "__main__":
    assert __debug__ and len(sys.argv) == 2
    main(Path(sys.argv[1]))
