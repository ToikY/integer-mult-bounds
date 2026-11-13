"""One exact coframe span test for incoming 995 at owned 1531's pre44261 cut."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm
import sys

PINS = {
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
CUT = 44261
BANK = (623, 732, 753, 1285, 1286, 1288, 1482, 1524)


def main(root):
    alarm(30)
    files = {name: (root/name).read_bytes() for name in PINS}
    assert {name: sha256(data).hexdigest() for name, data in files.items()} == PINS
    payload = decompress(files["ROLE902-WORD.json.gz"])
    assert sha256(payload).hexdigest() == WORD
    word = json.loads(payload)
    tape = word["program"]
    assert tape[CUT-1:CUT+6] == [
        ["ADD",1531,732,"-1",117], ["MOVE",1531,117,534,True],
        ["ADD",1531,995,"-4",534], ["MOVE",1531,534,541,True],
        ["SCALE",1531,"1/2",541], ["ADD",917,1531,"1",541], ["CLEAR",1531,541],
    ]
    assert tape[CUT+6] == ["MOVE",995,534,905,False]
    def span(frame):
        result = {0}
        for v in frame:
            assert v not in result
            result |= {x ^ v for x in result}
        return result
    frames = [word["frames"][i] for i in (117,534,541)]
    low, mid, high = map(span, frames)
    assert low < mid < high and list(map(len, frames)) == [5,6,7]
    charts = dict(enumerate(word["initial"]))
    for op, r, *args in tape[:CUT]:
        if op == "INIT":
            assert r not in charts
            charts[r] = args[0]
        if op == "MOVE":
            assert charts[r] == args[0]
            charts[r] = args[1]
        if op == "CLEAR":
            assert charts.pop(r) == args[0]
    assert tuple(sorted(r for r,c in charts.items() if c == 117)) == (*BANK,1531)
    assert charts[995] == 534 and charts[917] == 541
    gate = run_path(str(root/"gate.py"))
    rows = gate["exact_cut_rows"](tape[:CUT], [*BANK,995], word["public"])
    donors, target = rows[:-1], rows[-1]
    pivots = gate["basis"](donors)
    residual, recipe = gate["representation"](pivots,target)
    result = {"case_cap":1, "timeout_seconds":30, "cases_completed":1, "pins":PINS,
              "cut":CUT, "bank":BANK, "host":1531, "source":995, "recipient":917,
              "available_rank":len(pivots), "exact_paid_delta_native":{1:-2,2:1}}
    def evaluate(row, probe):
        return sum(c * probe.get(j,0) for j,c in row.items())
    if residual:
        entry = min(residual)
        assert entry not in pivots
        probe = {entry:1/residual[entry]}
        for key, (row, _) in sorted(pivots.items(), reverse=True):
            correction = evaluate(row, probe)
            if correction:
                probe[key] = -correction
        assert all(evaluate(row,probe) == 0 for row in donors)
        assert evaluate(target,probe) == 1
        result.update(status="EXACT_INCOMING_ABSORPTION_EXCLUSION", target_rank=len(pivots)+1,
                      probe=probe, target_evaluation=1, donor_evaluations=[0]*len(BANK))
    else:
        combined = {}
        for j,c in recipe.items():
            for k,v in donors[j].items():
                gate["add"](combined,k,c*v)
        assert combined == target
        result.update(status="NECESSARY_SPAN_SURVIVES_GRID_AND_PHYSICAL_PENDING", target_rank=len(pivots),
                      add_recipe={BANK[j]:-4*c for j,c in recipe.items()},
                      recipe_denominators=sorted({Q(-4*c).denominator for c in recipe.values()}))
    print(json.dumps(result,sort_keys=True,default=str),flush=True)
    alarm(0)


if __name__ == "__main__":
    assert __debug__
    main(Path(sys.argv[1]))
