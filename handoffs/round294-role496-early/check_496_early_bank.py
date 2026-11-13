"""Price one role496 fusion and test its earlier paid-arrival restoration."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
import json

PINS = {
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
START, CUT, CAP = 40952, 41782, 30
FIRST_OUTWARD = 43371
FIRST_BANK = [496, 903, 984, 1129]
ROLE = 496
OMIT = {40954, 40956}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def hash_bytes(raw):
    return sha256(raw).hexdigest()


def serial(row):
    return {str(j): str(v) for j, v in sorted(row.items()) if v}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    args = parser.parse_args()
    stage = "authenticate"

    def timed_out(_signum, _frame):
        print(json.dumps(dict(status="CAP_UNRESOLVED", cap=CAP, stage=stage,
                              case=[ROLE, START, CUT])), flush=True)
        raise SystemExit(124)

    signal(SIGALRM, timed_out)
    alarm(CAP)
    try:
        for name, digest in PINS.items():
            require(hash_bytes((args.inputs / name).read_bytes()) == digest, name)
        app_bytes = (args.inputs / "ROLE902-APPLICATION.json").read_bytes()
        require(hash_bytes(app_bytes) == "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f", "Exact R292 application receipt")
        app = json.loads(app_bytes)
        require(app["status"] == "PASS_ROLE902_FINAL_APPLICATION",
                "Complete R292 application receipt")
        require(app.get("candidate_canonical_sha256") == WORD, "Application binds exact word")
        require(app["caller_sha256"] == PINS["7113-CALLER.json"], "Fixed signed caller")
        outer = app["outer"]
        require(outer["strict_count"] == 54 and outer["functional_count"] == 4
                and Q(outer["minimum_margin"]) > 0, "Complete outer gates")
        lo, hi = map(Q, app.get("raw_crossing", app.get("directed_crossing_bracket")))
        claim = Q(app.get("claim", app.get("conditional_claim")))
        require(claim == Q("0.003648411294790") and claim < lo < hi, "New R292 comparator")

        raw = decompress((args.inputs / "ROLE902-WORD.json.gz").read_bytes())
        require(hash_bytes(raw) == WORD, "Canonical #7544 + role902 word")
        word = json.loads(raw)
        tape = word["program"]
        expected = [
            ["MOVE", 496, 729, 730, False], ["MOVE", 230, 261, 730, False],
            ["ADD", 496, 230, "1", 730], ["MOVE", 994, 261, 730, False],
            ["ADD", 994, 496, "-1", 730], ["MOVE", 496, 730, 912, False],
        ]
        require(tape[START:START + 6] == expected
                and tape[FIRST_OUTWARD] == ["ADD", 220, 496, "-1/2", 912], "Fixed exact clocks")
        require(tape[41776:41782] == [
            ["MOVE", 1129, 575, 912, False], ["MOVE", 903, 791, 912, False],
            ["ADD", 1129, 903, "-1", 912], ["ADD", 903, 984, "-1", 912],
            ["ADD", 984, 903, "1/2", 912], ["SCALE", 903, "-1/2", 912],
        ], "Exact donor input versions at pre41782")
        require(all(event[1] != ROLE and
                    (event[0] not in ("ADD", "COPY") or event[2] != ROLE)
                    for event in tape[40960:FIRST_OUTWARD]),
                "Role496 restoration at pre41782 reaches its first old outward read")
        require(tape[41777] == ["MOVE", 903, 791, 912, False]
                and tape[40958] == ["MOVE", 984, 374, 912, False]
                and tape[41783] == ["MOVE", 984, 912, 228, False]
                and tape[41786] == ["MOVE", 903, 912, 148, False],
                "Earlier paid arrivals remain until the selected cut and leave before the outward read")
        require(tape[46168] == ["ADD", 992, 994, "1", 127]
                and tape[46169] == ["MOVE", 496, 912, 127, False],
                "Separate role994 deadline")
        require([len(word["frames"][j]) for j in (729, 730, 912)] == [4, 6, 7],
                "Price rank differences")

        stage = "directed_price"
        power = run_path(str(args.inputs / "pricing.py"))["power_bounds"]
        gross = [
            17 * (1 + power(2, hi)[0] - power(3, lo)[1]),
            17 * (1 + power(2, lo)[1] - power(3, hi)[0]),
        ]
        require(lo > 0 and hi < Q(1, 32) and 0 < gross[0] <= gross[1] < 1,
                "Strictly positive gross for one ascent fusion")
        print(json.dumps(dict(status="START", case=[ROLE, START, CUT], cap=CAP,
                              comparator_claim=str(claim), comparator_word=WORD,
                              gross=list(map(str, gross)), delta_paid={1: -17, 2: -17, 3: 17},
                              delta_productive={}, excluded_from_price="all ancillary repairs")),
              flush=True)

        stage = "exact_bank"
        active = word["initial"] + [None] * word["owned_fields"]
        for op, role, *rest in tape[:CUT]:
            if op == "MOVE":
                require(active[role] == rest[0], "Old chart chronology")
                active[role] = rest[1]
            elif op == "INIT":
                require(active[role] is None, "Old INIT lifecycle")
                active[role] = rest[0]
            elif op == "CLEAR":
                require(active[role] == rest[0], "Old CLEAR lifecycle")
                active[role] = None
        bank = [i for i, chart in enumerate(active) if chart == 912]
        require(bank == FIRST_BANK, "Complete actual chart912 bank")
        helpers = run_path(str(args.inputs / "gate.py"))
        edited = [event for i, event in enumerate(tape[:CUT]) if i not in OMIT]
        old_rows = helpers["exact_cut_rows"](tape[:CUT], bank, word["public"])
        edited_rows = helpers["exact_cut_rows"](edited, bank, word["public"])
        donors = [i for i in range(len(bank)) if bank[i] != ROLE]
        own = bank.index(ROLE)
        require(all(old_rows[i] == edited_rows[i] for i in donors),
                "Other actual bank rows unchanged")
        pivot = helpers["basis"]([edited_rows[i] for i in donors])
        reduce = helpers["representation"]
        wanted, supplied = [reduce(pivot, r)[0] for r in (old_rows[own], edited_rows[own])]
        a = None
        if supplied and wanted:
            lead = min(supplied)
            a = wanted.get(lead, Q(0)) / supplied[lead]
            if not a or wanted != {j: a * v for j, v in supplied.items()}:
                a = None
        elif not supplied and not wanted:
            a = Q(1)
        remaining, coefficients = reduce(helpers["basis"](edited_rows), old_rows[own])
        if a:
            residual = old_rows[own].copy()
            for j, v in edited_rows[own].items():
                helpers["add"](residual, j, -a * v)
            absent, coefficients = reduce(pivot, residual)
            require(not absent, "Reconstructed nonzero-self correction")
            coefficients = {bank[donors[j]]: v for j, v in coefficients.items()}
            coefficients[ROLE] = a
        print(json.dumps(dict(
            status=("PASSES_EARLY_BANK_ONLY" if a else "EXCLUDED_FIXED_EARLY_BANK"),
            cases_completed=1, unresolved=[], bank=bank, repair_cut=CUT, next_read=FIRST_OUTWARD,
            old_receiver_quotient=serial(wanted), edited_receiver_quotient=serial(supplied),
            full_bank_span_remainder=serial(remaining),
            restore_coefficients=serial(coefficients) if a else None,
            next_gate="Role994 pre46168 only on pass; earlier re-encodings and changed routes remain open"),
            sort_keys=True), flush=True)
    finally:
        alarm(0)


if __name__ == "__main__":
    assert __debug__
    main()
