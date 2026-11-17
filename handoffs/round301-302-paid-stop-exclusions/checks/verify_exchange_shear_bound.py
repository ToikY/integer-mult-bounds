"""Check the at-most-two-shear exclusion on every frozen R301 orientation."""
import argparse
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import signal

WORD_PIN = "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d"
CANONICAL_PIN = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
EXCHANGE_PIN = "41cca0f2c6f01905b0ab601d3a13191125dd158628a2cfeb336c2ed3330ec0ac"


def checked_bytes(path, pin):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == pin, f"SHA-256 mismatch: {path.name}"
    return data


def main():
    assert __debug__, "Run without -O"
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--word", type=Path, required=True)
    p.add_argument("--frozen", type=Path, required=True)
    args = p.parse_args()
    signal.alarm(30)
    canonical = decompress(checked_bytes(args.word, WORD_PIN))
    assert sha256(canonical).hexdigest() == CANONICAL_PIN
    tape = json.loads(canonical)["program"]
    catalog, result = [json.loads(line) for line in checked_bytes(args.frozen, EXCHANGE_PIN).splitlines()]
    rows = catalog["priced"]
    frozen_tested = [r["case"] for r in result["tested"]]
    assert rows == frozen_tested + result["unresolved"]
    assert len(rows) == 710 and len(frozen_tested) == 8
    seen, counts = set(), Counter()
    for row in rows:
        aid, bid = row["roles"]
        first, last = row["block"][0], row["block"][-1]
        identity = (aid, bid, row["entry"], row["exit"], tuple(row["block"]))
        assert identity not in seen
        seen.add(identity)
        count, clocks = 0, []
        for clock in range(first, last + 1):
            event = tape[clock]
            op, destination, *tail = event
            touched = (destination, tail[0]) if op in ("ADD", "COPY") else (destination,)
            if aid not in touched and bid not in touched:
                continue
            clocks.append(clock)
            assert tail[-1] == row["charts"][1]
            if op == "ADD":
                assert touched in ((aid, bid), (bid, aid))
                count += 1
            else:
                assert op == "SCALE" and Fraction(tail[0]) != 0
        assert clocks == row["block"] and count in (1, 2)
        counts[count] += 1
    assert counts == {1: 403, 2: 307}
    receipt = {"status": "PASS_AT_MOST_TWO_MUTUAL_ADD_STRUCTURE", "word_canonical_sha256": CANONICAL_PIN,
               "word_gzip_sha256": WORD_PIN, "frozen_sha256": EXCHANGE_PIN,
               "orientations": len(seen), "explicit_matrix_count_this_check": 0,
               "mutual_add_histogram": dict(counts), "structural_exclusions": len(seen)}
    print(json.dumps(receipt, sort_keys=True))
    signal.alarm(0)


if __name__ == "__main__":
    main()
