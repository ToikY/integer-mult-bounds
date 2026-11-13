"""Replay two literal inputs indistinguishable to the fixed chart127 repair."""
import argparse
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

ENGINE = "9b44d0a0233c0f9e26662f939ff15be71534809deb3b732baba0346379a06049"
CAP = 30


def inverse_endpoint(word, y):
    """Invert the authenticated old normalized all-input endpoint blockwise."""
    hosted = word["hosted"]
    assert [hosted[k] for k in ("alpha", "beta", "alpha2", "beta2")] == ["-1", "1/2", "-1", "0"]
    a_ports = set(hosted["Dports"])
    x = y.copy()
    for port, p in enumerate(word["live"]):
        r = p + 112
        a, b = y.get(p, Q(0)), y.get(r, Q(0))
        if port in a_ports:
            x[r] = b-a
        else:
            x[p], x[r] = b+a/2, b-a/2
    for p, r in zip(hosted["X2"], hosted["Y2"]):
        x[p] = y.get(p, Q(0)) + y.get(r, Q(0))
    return {r: v for r, v in x.items() if v}


def endpoints(engine, word, spaces, probe, state):
    old = engine["FieldState"](word, probe, spaces)
    new = engine["FieldState"](word, probe, spaces)
    difference = engine["difference"]
    v, first_delta = None, None
    for clock, event in enumerate(word["program"]):
        state["clock"] = clock
        if clock == 36416:
            v = old.logical(1028)
            assert old.values == new.values and old.chart == new.chart
            new.apply(["ADD", 1024, 1028, "1/2", 3], clock)
        if clock == 36422:
            first_delta = difference(old, new)
            assert first_delta == ({797: -v/2} if v else {})
            assert old.chart == new.chart and old.owned == new.owned
        op, r, *args = event
        touched = [r, args[0]] if op in ("ADD", "COPY") else [r]
        if clock >= 36422 and (op == "COPY" or any(p >= word["public"] for p in touched)):
            assert all(old.logical(p) == new.logical(p) for p in touched)
        old.apply(event, clock)
        if clock not in (36418, 36419):
            new.apply(["MOVE", 1028, 3, 302, False] if clock == 36421 else event, clock)
        assert old.owned == new.owned
    assert v is not None and first_delta is not None
    assert old.chart == new.chart == dict(enumerate(word["final"]))
    assert not old.owned and not new.owned
    return old.values, new.values, v, first_delta


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    args = parser.parse_args()
    start = perf_counter()
    state = {"clock": None}
    parent = Path(__file__).resolve().with_name("check_1028_forward.py")
    assert sha256(parent.read_bytes()).hexdigest() == ENGINE
    engine = run_path(str(parent))
    emit = engine["emit"]

    def cap(_sig, _frame):
        emit(status="INDEPENDENT_CAP", last_entered_clock=state["clock"], cap_seconds=CAP,
             seconds=perf_counter()-start)
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(CAP)
    pins = engine["PINS"]
    data = {p: (args.input_root/p).read_bytes() for p in pins}
    assert {p: sha256(raw).hexdigest() for p, raw in data.items()} == pins
    raw = decompress(data["COMPOSED-WORD.json.gz"])
    assert sha256(raw).hexdigest() == engine["WORD"]
    word = loads(raw, object_pairs_hook=engine["unique"])
    cert = loads(data["COMPOSED-APPLICATION.json"], object_pairs_hook=engine["unique"])
    assert cert["status"] == "PASS_COMPOSED_7481_7542_FINAL_APPLICATION"
    assert cert["candidate_canonical_sha256"] == engine["WORD"] and cert["claim_decimal"] == "0.003647969120276"
    spaces = engine["source_conditions"](word)
    bank = {i for i, chart in enumerate(word["final"]) if chart == 127}
    assert 797 in bank and 142 not in bank
    v = engine["pullback"](word["program"][:36416], 1028)

    def historical_donor(input_vector):
        return sum(v.get(r, 0)*entry for r, entry in input_vector.items())

    off_bank = historical_donor(inverse_endpoint(word, {142: Q(1)}))
    self_coefficient = historical_donor(inverse_endpoint(word, {797: Q(1)}))
    assert off_bank and self_coefficient != 2
    t = off_bank / (2-self_coefficient)
    desired = {142: Q(1), 797: t}
    probe = inverse_endpoint(word, desired)
    zero_old, zero_new, zero_donor, _ = endpoints(engine, word, spaces, {}, state)
    assert not zero_old and not zero_new and zero_donor == 0
    old, new, donor, first_delta = endpoints(engine, word, spaces, probe, state)
    assert old == desired and new == {142: Q(1)}
    assert donor == 2*t and first_delta == {797: -t}
    assert all(new.get(r, 0) == zero_new.get(r, 0) for r in bank)
    assert old[797] != zero_old.get(797, 0)
    alarm(0)
    emit(status="PASS_INDEPENDENT_FIXED_TERMINAL_READOUT_EXCLUSION", cases_completed=1,
         cap_seconds=CAP, seconds=perf_counter()-start,
         bank_chart=127, bank_size=len(bank), outside_role=142, outside_chart=word["final"][142],
         output_role=797, exact_outside_coefficient=off_bank, exact_self_coefficient=self_coefficient,
         initial_probes=[{}, probe], original_final_states=[zero_old, old], edited_final_states=[zero_new, new],
         old_source1028_at_pre36416=[zero_donor, donor], actual_pre36422_delta=first_delta,
         candidate_canonical_sha256=engine["WORD"], caller_head=engine["CALLER"],
         input_pins=pins, independent_engine_sha256=ENGINE)


if __name__ == "__main__":
    main()
