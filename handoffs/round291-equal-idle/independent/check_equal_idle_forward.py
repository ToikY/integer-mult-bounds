"""Replay the two equal Type B idle masks on literal forward columns."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import lcm
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "COMPOSED-APPLICATION.json": "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "COMPOSED-WORD.json.gz": "926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
}
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
HEAD = "d6be7d620c9c8337104daeb09fe01196eced5fe3"
WORD = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
START, LAST, CAP, OFFSET, COUNT = 1887, 1940, 30, 36, 36
ROLES = tuple(range(OFFSET, OFFSET + COUNT))
MASK = [3, 4, 5, 6, 7, 8]


def emit(**fields):
    print(dumps(fields, sort_keys=True, default=str), flush=True)


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON key"
    return result


def geometry(word, caller):
    assert caller["ambient_rank"] == 9+8*caller["stages"] == 145
    q = word["ports"][15]
    assert 0 < q < (1 << 9)
    groups = [tuple(range(9+8*j, 17+8*j)) for j in range(caller["stages"])]
    minus = sum(1 << j for j in (25, 26))
    plus = 0
    assert groups[2] == tuple(range(25,33))
    signatures = []
    for labels in (plus, minus):
        # C_f=((1+i)I+(1-i)X_f)/2 gives eigenvalue 1 or i on a Walsh vector.
        eigen_powers = [(sum((labels >> j) & 1 for j in block)) % 4 for block in groups]
        assert not (labels & q) and all(power in (0,2) for power in eigen_powers)
        assert (2*sum(eigen_powers[j-1] for j in MASK)) % 4 == 0
        signatures.append([1 if power == 0 else -1 for power in eigen_powers])
    assert signatures[0] == [1]*17 and signatures[1] == [1,1,-1]+[1]*14
    return signatures, {"port":15, "native_q_axis":q, "q_eigenvalue":1, "width":1,
                        "minus_walsh_axes":[25,26], "B3":-1,"other_bodies":1,
                        "square_translation_eigenvalues":[1,1]}


def scalar_map(events, bodies, initial, reverse=False):
    a = initial.copy()
    tape = reversed(events) if reverse else events
    for event in tape:
        tag = event[0]
        if tag == "A":
            continue
        if tag == "J":
            _, j, a_roles, (r, s, alpha, beta) = event
            assert all(p < OFFSET for p in a_roles) and r in ROLES and s in ROLES and r != s
            x, y = a[r-OFFSET], a[s-OFFSET]
            alpha, beta = Q(alpha), Q(beta)
            d = bodies[j-1]
            if reverse:
                a[r-OFFSET], a[s-OFFSET] = d*((1+alpha*beta)*x-alpha*y), d*(-beta*x+y)
            else:
                a[r-OFFSET], a[s-OFFSET] = d*(x+alpha*y), d*(beta*x+(1+alpha*beta)*y)
            continue
        assert tag == "B"
        _, op, r, *args = event
        assert r in ROLES
        i = r-OFFSET
        if op in ("ADD", "SWAP"):
            j = args[0]-OFFSET
            assert 0 <= j < COUNT and i != j
            if op == "ADD":
                p = Q(args[1])
                a[i] += (-p if reverse else p)*a[j]
            else:
                a[i], a[j] = a[j], a[i]
        elif op == "SCALE":
            p = Q(args[0])
            assert p
            a[i] = a[i]/p if reverse else p*a[i]
        elif op == "LAMBDA":
            assert args[0] in (-1,1)  # q=+1, so both signed normalizer choices evaluate to 1.
        else:
            assert op in ("IDLE_ONE", "IDLE_ODD") and (len(args) == 1 if op == "IDLE_ONE" else args[1:] == [-1])
            selected = args[0]
            assert selected and len(set(selected)) == len(selected) and all(1 <= k <= len(bodies) for k in selected)
            # q^{-1}=1 as well for the signed odd form on these two fibres.
            for k in selected:
                a[i] *= bodies[k-1]
    return a


def sparse(vector):
    return {r:v for r,v in zip(ROLES, vector, strict=True) if v}


def differences(old, changed, source):
    return [[r, source, a, b, a-b] for r,a,b in zip(ROLES,old,changed,strict=True) if a != b]


def main():
    assert __debug__ and version_info[:2] == (3,12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    args = parser.parse_args()
    started = perf_counter()
    done = []
    phase = "authentication"

    def capped(_sig, _frame):
        emit(status="INDEPENDENT_CAP", phase=phase, completed_columns=done, cap_seconds=CAP,
             seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM,capped)
    alarm(CAP)
    raw = {p:(args.inputs/p).read_bytes() for p in PINS}
    assert {p:sha256(value).hexdigest() for p,value in raw.items()} == PINS
    caller = loads(raw["7113-CALLER.json"],object_pairs_hook=unique)
    app = loads(raw["COMPOSED-APPLICATION.json"],object_pairs_hook=unique)
    word = decompress(raw["COMPOSED-WORD.json.gz"])
    assert sha256(word).hexdigest() == WORD
    word = loads(word,object_pairs_hook=unique)
    assert app["caller_sha256"] == PINS["7113-CALLER.json"] and app["candidate_canonical_sha256"] == WORD
    assert app["status"] == "PASS_COMPOSED_7481_7542_FINAL_APPLICATION" and app["claim_decimal"] == "0.003647969120276"
    assert caller["types"]["B"]["ports"] == [15,17,27,34,35,42,47,55]
    assert caller["types"]["B"]["offset"] == caller["types"]["B"]["roles"] == OFFSET == COUNT
    events = caller["events"]
    assert len(events) == 4783
    assert events[START] == events[LAST] == ["B","IDLE_ONE",OFFSET,MASK]
    original = events[START:LAST+1]
    proposed = original[1:-1]  # On both fibres the whole square translation is +1.
    omitted = original[1:]
    assert all(e[0] == "B" for e in original)
    assert Counter(e[1] for e in proposed) == {"ADD":31,"SWAP":19,"SCALE":2}
    (ones, signed), specialization = geometry(word,caller)
    phase = "paired signed and unit forward columns"
    mismatches, mutation = [], []
    witness = None
    for source in ROLES:
        basis = [Q(r == source) for r in ROLES]
        expected = scalar_map(proposed,ones,basis)
        assert scalar_map(original,ones,basis) == scalar_map(omitted,ones,basis) == expected
        baseline = scalar_map(original,signed,basis)
        edited = scalar_map(proposed,signed,basis)
        mutant = scalar_map(omitted,signed,basis)
        assert edited == expected
        changes = differences(baseline,edited,source)
        mismatches.extend(changes)
        mutation.extend(differences(baseline,mutant,source))
        if changes and witness is None:
            witness = {"unit_input_role":source, "old_output":sparse(baseline), "proposed_output":sparse(edited)}
        done.append(source)
    assert mutation, "omitted mutation never changed signed action"
    endpoint = None
    if witness:
        phase = "full normalized caller distinguishing input"
        basis = [Q(r == witness["unit_input_role"]) for r in ROLES]
        prefix = events[:START]
        initial = scalar_map(prefix,signed,basis,reverse=True)
        assert scalar_map(prefix,signed,initial) == basis
        scale = lcm(*(v.denominator for v in initial))
        integral = [v*scale for v in initial]
        assert all(v.denominator == 1 for v in integral)
        old_out = scalar_map(events,signed,integral)
        new_out = scalar_map(events[:START]+proposed+events[LAST+1:],signed,integral)
        full_diff = differences(old_out,new_out,witness["unit_input_role"])
        assert full_diff
        for final in (old_out, new_out):
            stage = scalar_map(events[LAST+1:],signed,final,reverse=True)
            expected = witness["old_output"] if final == old_out else witness["proposed_output"]
            assert stage == [scale*expected.get(r,0) for r in ROLES]
        endpoint = {"initial_scale":scale, "integral_normalized_input":sparse(integral),
                    "first_difference":full_diff[0], "differing_rows":len(full_diff)}
    alarm(0)
    emit(status="INDEPENDENT_FIXED_SQUARE_EXCLUSION" if witness else "INDEPENDENT_FIXED_SQUARE_SUPPORT_ONLY",
         cases_completed=1, unresolved=[], completed_columns=done, clock_pair=[START,LAST], role=OFFSET,
         square_mask=MASK, all_unit_control_equal=True, specialization=specialization,
         mismatch_entries=mismatches, first_boundary_witness=witness,
         omitted_clock=START, first_omitted_mutant_mismatch=mutation[0], full_signed_endpoint=endpoint,
         caller_head=CALLER, comparator_head=HEAD, comparator_canonical_sha256=WORD,
         input_pins=PINS, cap_seconds=CAP, seconds=perf_counter()-started)


if __name__ == "__main__":
    main()
