"""Reverse every Type A output row on the fixed signed B9 relocation interval."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "ROLE902-APPLICATION.json": "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
HEAD = "99438c43df7aac1e5dbcc43c1578fcd886c119ec"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
START, STOP, CAP = 1448, 1746, 30
ROLES = list(range(36))


def emit(**record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def unique(pairs):
    x = dict(pairs)
    assert len(x) == len(pairs), "duplicate JSON keys"
    return x


def exact_pin(raw, key):
    assert sha256(raw).hexdigest() == PINS[key]
    return raw


def pull_row(tape, out, body):
    row = [Q(i == out) for i in ROLES]
    for tag, op, dst, *args in reversed(tape):
        assert tag == "A" and dst in ROLES
        if op == "IDLE_ONE":
            stages, = args
            assert stages and len(stages) == len(set(stages))
            for stage in stages:
                row[dst] *= body[stage-1]
        elif op == "LAMBDA":
            sign, = args
            assert sign in (-1,1)
            # Both signed Lambda variants specialize to ((1+i sign)+(1-i sign))/2=1 at q=+1.
        else:
            src,*params = args
            assert src in ROLES and src != dst
            if op == "SWAP":
                assert not params
                row[dst], row[src] = row[src], row[dst]
            else:
                coefficient, = params
                if op == "QUERY":
                    assert coefficient in (-1,1)
                    rate = Q(1)  # q^{±1} at the fixed physical central sector.
                else:
                    assert op == "ADD"
                    rate = Q(coefficient)
                    assert rate
                row[src] += rate*row[dst]
    return row


def geometry(word, caller):
    assert caller["ambient_rank"] == 9+8*caller["stages"] == 145
    axes = [tuple(range(9+8*j,17+8*j)) for j in range(17)]
    assert axes[8] == tuple(range(73,81))
    walsh = (1<<73)|(1<<74)
    by_stage = [sum(1 for a in group if walsh>>a&1)%4 for group in axes]
    assert by_stage == [0]*8+[2]+[0]*8
    ports = caller["types"]["A"]["ports"]
    assert ports == word["hosted"]["Dports"] and len(ports) == 96
    vectors = {p:word["ports"][p] for p in ports}
    assert all(0 < q < 512 and (q&walsh).bit_count()%2==0 for q in vectors.values())
    return tuple((-1 if p == 2 else 1) for p in by_stage), {
        "width":1, "minus_Walsh_axes":[73,74], "B9_axes":list(axes[8]),
        "B9_eigenvalue":-1, "other_body_eigenvalue":1, "central_q_eigenvalue":1,
        "central_axes_verified_for_ports":len(vectors), "first_port":ports[0], "first_port_central_axis":vectors[ports[0]],
    }


def main():
    assert __debug__ and version_info[:2] == (3,12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    parser.add_argument("word", type=Path, help="pinned role902-WORD.json.gz, explicit root if separate")
    args = parser.parse_args()
    started = perf_counter()
    done = []

    def cap(_sig,_frame):
        emit(status="INDEPENDENT_CAP", completed_rows=done, unresolved_rows=[r for r in ROLES if r not in done],
             cap_seconds=CAP, seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    raw = decompress(exact_pin(args.word.read_bytes(),"ROLE902-WORD.json.gz"))
    assert sha256(raw).hexdigest() == WORD
    word = loads(raw,object_pairs_hook=unique)
    app, caller = (loads(exact_pin((args.input_root/p).read_bytes(),p),object_pairs_hook=unique)
                   for p in ("ROLE902-APPLICATION.json","7113-CALLER.json"))
    assert app["status"] == "PASS_ROLE902_FINAL_APPLICATION" and app["candidate_canonical_sha256"] == WORD
    assert app["caller_sha256"] == PINS["7113-CALLER.json"] and Q(app["claim"]) == Q("0.003648411294790")
    body, specialization = geometry(word,caller)
    unit = [1]*17
    tape = caller["events"]
    assert len(tape) == 4783 and caller["types"]["A"]["offset"] == 0 and caller["types"]["A"]["roles"] == len(ROLES)
    old = tape[START:STOP]
    assert old[0] == ["A","IDLE_ONE",1,[2,3,4,5,6,7,8]]
    assert old[-1] == ["A","IDLE_ONE",11,[9,10]]
    assert tape[1742] == ["A","IDLE_ONE",10,[9]]
    assert [tape[i] for i in (1449,1744,1746)] == [["A","ADD",1,0,"2"],
                                                    ["A","ADD",11,0,"2"],
                                                    ["A","ADD",11,0,"-2"]]
    assert all(x[0] == "A" for x in old)
    assert Counter(x[1] for x in old) == {"ADD":262,"IDLE_ONE":16,"SWAP":8,"LAMBDA":8,"QUERY":4}
    new = [*old]
    new[0] = ["A","IDLE_ONE",1,[2,3,4,5,6,7,8,9]]
    new[-1] = ["A","IDLE_ONE",11,[10]]
    omitted = [x for i,x in enumerate(old,START) if i != 1742]
    reference = [["A","ADD",0,1,"-3/2"],["A","QUERY",1,2,-1],["A","LAMBDA",0,-1]]
    assert pull_row(reference,0,body)[:3] == [Q(1),Q(-3,2),Q(0)]
    assert pull_row(reference,1,body)[:3] == [Q(0),Q(1),Q(1)]
    changes, control = [], []
    old_rows, new_rows = [], []
    for out in ROLES:
        all_plus = pull_row(old,out,unit)
        assert all_plus == pull_row(new,out,unit) == pull_row(omitted,out,unit)
        a,b,m = (pull_row(x,out,body) for x in (old,new,omitted))
        old_rows.append(a)
        new_rows.append(b)
        for i, (v,w,mut) in enumerate(zip(a,b,m,strict=True)):
            if v != w:
                changes.append({"input":i,"output":out,"before":v,"after":w,"difference":w-v})
            if v != mut:
                control.append({"input":i,"output":out,"before":v,"after":mut,"difference":mut-v})
        done.append(out)
    changes.sort(key=lambda d:(d["input"],d["output"]))
    control.sort(key=lambda d:(d["input"],d["output"]))
    assert control
    encoded = dumps([old_rows,new_rows],separators=(",",":"),default=str).encode()
    alarm(0)
    emit(status="PASS_INDEPENDENT_TYPE_A_B9_EXCLUSION" if changes else "INDEPENDENT_SPECIALIZATION_SUPPORT_ONLY",
         cases_completed=1,unresolved=[],interval=[START,STOP],completed_rows=done,
         first_witness=changes[0] if changes else None,all_difference_entries=changes,
         one_omitted_1742_control=control[0],one_omitted_1742_changed_entries=len(control),
         unit_body_full_matrix_equal=True,physical_specialization=specialization,exact_pair_of_matrices_sha256=sha256(encoded).hexdigest(),
         comparator_head=HEAD,word_canonical_sha256=WORD,caller_head=CALLER,input_pins=PINS,cap_seconds=CAP,seconds=perf_counter()-started)


if __name__ == "__main__":
    main()
