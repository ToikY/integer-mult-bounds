"""One exact conservative suffix gate for the proposed public helper1028 merge."""
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

PINS = {
    "COMPOSED-WORD.json.gz": "926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
    "COMPOSED-APPLICATION.json": "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "suffix_readout.py": "7514d10bc4a6c96a583f3619aaa869c360ffa80085d3bb2a732cb6b9f4821b67",
}
WORD = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
CUT, CAP = 36422, 30


def emit(**fields):
    print(json.dumps(fields, sort_keys=True, default=str), flush=True)


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    root = Path(sys.argv[1]).resolve()
    last = None

    def stop(_sig, _frame):
        emit(status="UNRESOLVED_CAP", last_completed=last, cap=CAP, cases_completed=0)
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, stop)
    signal.alarm(CAP)
    raw = {p:(root/p).read_bytes() for p in PINS}
    assert {p:sha256(value).hexdigest() for p,value in raw.items()} == PINS
    canonical = gzip.decompress(raw["COMPOSED-WORD.json.gz"])
    assert sha256(canonical).hexdigest() == WORD
    cert = json.loads(raw["COMPOSED-APPLICATION.json"])
    assert cert["status"] == "PASS_COMPOSED_7481_7542_FINAL_APPLICATION"
    assert cert["candidate_canonical_sha256"] == WORD and cert["claim_decimal"] == "0.003647969120276"
    word = json.loads(canonical)
    tape = word["program"]
    assert word["public"] == 1501 and len(tape) == 76491
    assert tape[36416] == ["MOVE",1024,3,23,False]
    assert tape[36417] == ["ADD",797,1024,"-1",23]
    assert tape[36418] == ["MOVE",1028,3,23,False]
    assert tape[36419] == ["ADD",1024,1028,"1/2",23]
    assert tape[36421] == ["MOVE",1028,23,302,False]
    source = run_path(str(root/"suffix_readout.py"))
    add = source["add"]
    z = {797:Q(1)}
    for clock,(op,r,*args) in enumerate(tape[CUT:],CUT):
        touched = [r,args[0]] if op in ("ADD","COPY") else [r]
        if (op == "COPY" or any(i >= word["public"] for i in touched)) and any(z.get(i) for i in touched):
            emit(status="EXCLUDED_CONSERVATIVE_GUARD",clock=clock,event=tape[clock],
                 coefficients={i:z[i] for i in touched if i in z},cases_completed=1,
                 scope="fixed suffix and exact preservation of old owned/COPY guard operands")
            return
        if op == "SCALE" and r in z:
            z[r] *= Q(args[0])
        elif op == "ADD":
            add(z,r,Q(args[1])*z.get(args[0],0))
        last = clock
    bank = {i for i,chart in enumerate(word["final"]) if chart == 127}
    outside = {i:value for i,value in z.items() if i not in bank}
    if outside:
        emit(status="EXCLUDED_FIXED_TERMINAL_BANK_OUTPUT", outside=outside, cases_completed=1)
        return
    v = source["adjoint"](tape[:36416], {1028:Q(1)})
    ell = source["to_output_coordinates"](v,word)
    assert source["to_input_coordinates"](ell,word) == v
    missing = {i:value for i,value in ell.items() if i not in bank}
    inner = sum(value*z.get(i,0) for i,value in ell.items())
    if missing or inner == 2:
        emit(status="EXCLUDED_FIXED_TERMINAL_READOUT",outside=missing,inner=inner,cases_completed=1)
        return
    emit(status="TERMINAL_RANK_ONE_SURVIVOR", z=z, ell=ell, inverse_denominator=2-inner,
         cases_completed=1, next="Emit and fully price the exact inverse on this chart before building.")
    signal.alarm(0)


if __name__ == "__main__":
    main()
