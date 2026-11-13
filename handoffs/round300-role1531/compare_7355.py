"""Compare the exact owned readout rows on two authenticated words."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm
import sys

PINS = {
    "7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
BANK = [623, 732, 753, 1285, 1286, 1288, 1482, 1524]
PAIR = [["MOVE",1531,117,534,True],["ADD",1531,995,"-4",534],["MOVE",1531,534,541,True]]


def main():
    assert __debug__ and len(sys.argv) == 2
    alarm(30)
    root = Path(sys.argv[1])
    raw = {name:(root/name).read_bytes() for name in PINS}
    assert {name:sha256(data).hexdigest() for name,data in raw.items()} == PINS
    engine = run_path(str(root/"gate.py"))
    samples = []
    for name, cut in (("7334-WORD.json.gz",44242),("ROLE902-WORD.json.gz",44261)):
        word = json.loads(decompress(raw[name]))
        tape = word["program"]
        assert tape[cut:cut+3] == PAIR
        chart = dict(enumerate(word["initial"]))
        for op, dst, *p in tape[:cut]:
            if op == "INIT":
                assert dst not in chart
                chart[dst] = p[0]
            elif op == "MOVE":
                assert chart[dst] == p[0]
                chart[dst] = p[1]
            elif op == "CLEAR":
                assert chart.pop(dst) == p[0]
        assert sorted(r for r in chart if chart[r] == 117) == BANK+[1531]
        assert chart[995] == 534
        samples.append(engine["exact_cut_rows"](tape[:cut],BANK+[995,1531],word["public"]))
    before, after = samples
    def eval_probe(row, probe):
        return sum(v*probe.get(k,0) for k,v in row.items())
    old_probe = {236:Fraction(1)}
    current = {2:Fraction(1),7:Fraction(-1)}
    assert [eval_probe(r,old_probe) for r in before[:9]] == [0]*8+[-1]
    print(json.dumps(dict(pins=PINS, cuts=[44242,44261],
        changed_row_ids=[n for n,a,b in zip(BANK+[995,1531], before,after,strict=True) if a!=b],
        changed_entry_counts={n:sum(a.get(j,0)!=b.get(j,0) for j in a.keys()|b.keys())
                              for n,a,b in zip(BANK+[995,1531],before,after,strict=True)},
        old_probe_on_new=[str(eval_probe(r,old_probe)) for r in after],
        new_probe_on_old=[str(eval_probe(r,current)) for r in before]),sort_keys=True))
    alarm(0)


if __name__ == "__main__":
    main()
