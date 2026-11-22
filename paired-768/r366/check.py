"""Scoped existing-arrival check at the first frozen R363 obstruction."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json
import subprocess
import sys
import time


PINS = {
    "inputs/BINARY-CANDIDATE.json.gz": "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326",
    "r363/result.json": "40634f32710849f1693d5e691c7c9c192ee2f2dedda8f642f17f592e4aa4f5b9",
    "r352/accept.json": "0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377",
}
CUT = 8105
PROPOSED = 530
CAP = 32


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def load(root):
    require(sys.version_info[:2] == (3, 12), "CPython 3.12 required")
    files = {}
    for name, expected in PINS.items():
        source = (root / name).read_bytes()
        require(sha256(source).hexdigest() == expected, f"source hash {name}")
        files[name] = source
    word = json.loads(gzip.decompress(files["inputs/BINARY-CANDIDATE.json.gz"]))
    frozen = json.loads(files["r363/result.json"])
    require(frozen["ranked"][0] == [328, 510, 530], "frozen top proposal")
    require(frozen["geometry_obstructions"][0][1] == [False, CUT, 330, PROPOSED, [5, 0, "1"]],
            "archived exact obstruction")
    return word


def dots(word, chart):
    source = word["frames"][str(chart)]
    target_annihilator = word["frames"][str(PROPOSED)]["A"][0]
    return [
        str(sum(Fraction(a) * Fraction(b) for a, b in zip(row, target_annihilator)))
        for row in source["B"]
    ]


def forward(word):
    program = word["program"]
    public = word["public"]
    owner_at = list(range(public)) + [None] * word["owned_fields"]
    contacts = {j: [] for j in range(public)}
    owner = None
    feeders = []
    for clock, (op, register, *args) in enumerate(program):
        if clock == CUT:
            require(op == "MOVE" and args == [330, 510] and register >= public,
                    "private receiver and original MOVE")
            owner = owner_at[register]
        if op == "INIT":
            require(owner_at[register] is None, "private ownership at INIT")
            new_owner = public + clock
            owner_at[register] = new_owner
            contacts[new_owner] = [(clock, "INIT", register, *args)]
        elif op == "SWAP":
            other = args[0]
            for role, partner in ((register, other), (other, register)):
                contacts[owner_at[role]].append((clock, "SWAP", role, partner))
            owner_at[register], owner_at[other] = owner_at[other], owner_at[register]
        elif op == "ADD":
            sender = args[0]
            contacts[owner_at[register]].append((clock, "ADD_RECEIVE", register, *args))
            contacts[owner_at[sender]].append((clock, "ADD_SEND", sender, register, args[1]))
            if clock < CUT and owner_at[register] == public + 8102:
                feeders.append((clock, owner_at[sender]))
        else:
            contacts[owner_at[register]].append((clock, op, register, *args))
            if op == "CLEAR":
                owner_at[register] = None
    transcript = contacts[owner]
    require(transcript[0] == (8102, "INIT", 2335, 330), "cut owner's creation")
    earlier = [entry for entry in transcript if entry[0] < CUT and entry[1] == "MOVE"]
    require(len(earlier) <= CAP, "direct arrival census exceeds cap")
    require(not earlier, "new direct arrival needs exact action and restoration test")
    next_read = next(entry for entry in transcript if entry[0] > CUT and entry[1] == "ADD_SEND")
    feeder_receipts = []
    for read, sender_owner in feeders:
        arrival = next(entry for entry in reversed(contacts[sender_owner])
                       if entry[0] < read and entry[1] == "MOVE")
        failures = dots(word, arrival[3])
        require(any(Fraction(x) for x in failures), "feeder transfer clears direct nesting gate")
        feeder_receipts.append({
            "read": read,
            "arrival": arrival,
            "donor_next_reads": [r for r in contacts[sender_owner] if r[0] > read and r[1] == "ADD_SEND"],
            "proposed_target_row_products": failures,
        })
    require(len(feeder_receipts) == 2, "input contact count")
    original = word["frames"]["510"]["A"][0]
    source = word["frames"]["330"]["B"]
    require(all(not sum(Fraction(a) * Fraction(b) for a, b in zip(row, original)) for row in source),
            "positive original chart containment")
    return {
        "dependencies": PINS,
        "cut": CUT,
        "case_cap": CAP,
        "case_scope": 1,
        "direct_arrival_count": len(earlier),
        "direct_arrival_clocks": earlier,
        "unvisited": 0,
        "required_receiver": register_at_cut(program),
        "lifetime": transcript,
        "first_post_cut_use": next_read,
        "feeder_contacts": feeder_receipts,
        "original_move_valid": True,
        "failed_target_chart": PROPOSED,
        "cut_source_row_products": dots(word, 330),
        "result": "NO_DIRECT_ALREADY_PAID_ARRIVAL",
    }


def register_at_cut(program):
    return program[CUT][1]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        result = forward(load(args.inputs))
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return 0
    begin = time.monotonic()
    try:
        run = subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]], timeout=45)
        code = run.returncode
    except subprocess.TimeoutExpired:
        code = 124
    print(f"discovery exit={code} elapsed={time.monotonic() - begin:.6f} cap=45")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
