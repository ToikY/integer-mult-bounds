"""One exact four-field simultaneous signed wrapper feasibility test."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

START, STOP, CAP = 1448, 1746, 30
BANK = (0, 1, 10, 11)
PINS = {
    "ROLE902-APPLICATION.json": "a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def emit(**fields):
    print(json.dumps(fields, sort_keys=True, default=str), flush=True)


def matrix(block, q, b9, reverse=False):
    rows = [[Q(i == j) for j in range(36)] for i in range(36)]
    for kind, op, r, *p in reversed(block) if reverse else block:
        assert kind == "A"
        if op in ("ADD", "QUERY"):
            assert op == "ADD" or p[1] in (-1, 1)
            v = Q(p[1]) if op == "ADD" else Q(q)
            rows[r] = [a + (-v if reverse else v) * b
                       for a, b in zip(rows[r], rows[p[0]])]
        elif op == "SWAP":
            rows[r], rows[p[0]] = rows[p[0]], rows[r]
        elif op == "IDLE_ONE":
            if 9 in p[0]:
                rows[r] = [b9 * a for a in rows[r]]
        else:
            assert op == "LAMBDA" and p[0] in (-1, 1)
    return rows


def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(36) if a[i][k] and b[k][j])
             for j in range(36)] for i in range(36)]


def solve(equations):
    pivots = {}
    for key, coefficients, constant in equations:
        row = [*coefficients, constant]
        provenance = {key: Q(1)}
        for pivot, (prior, sources) in sorted(pivots.items()):
            v = row[pivot]
            if v:
                row = [a-v*b for a,b in zip(row, prior)]
                for k,x in sources.items():
                    provenance[k] = provenance.get(k,0)-v*x
        i = next((i for i,v in enumerate(row[:-1]) if v),None)
        if i is None:
            if row[-1]:
                return None, {"identity": {k:str(v) for k,v in provenance.items() if v},
                              "contradiction":str(row[-1])}
            continue
        v = row[i]
        pivots[i] = ([x/v for x in row], {k:x/v for k,x in provenance.items() if x})
    free = [i for i in range(16) if i not in pivots]
    forms = [[Q(0)]*(1+len(free)) for _ in range(16)]
    for k,i in enumerate(free,1):
        forms[i][k] = Q(1)
    for i,(row,_) in sorted(pivots.items(),reverse=True):
        forms[i][0] = row[-1]
        for j in range(i+1,16):
            if row[j]:
                forms[i] = [a-row[j]*b for a,b in zip(forms[i],forms[j])]
    return forms, {"equation_rank":len(pivots),"free_variables":len(free)}


def pick_invertible(forms):
    # Forms belong to X=S-I. Insert the actual diagonal of S before testing determinant.
    forms = [row.copy() for row in forms]
    for i in range(4):
        forms[5*i][0] += 1
    determinant = {}
    for p in permutations(range(4)):
        value = {(): Q((-1)**sum(p[i]>p[j] for i in range(4) for j in range(i+1,4)))}
        for i,j in enumerate(p):
            product = {}
            for monomial,x in value.items():
                for k,y in enumerate(forms[4*i+j]):
                    if not y:
                        continue
                    key = tuple(sorted((*monomial,k))) if k else monomial
                    product[key] = product.get(key,0)+x*y
            value = {k:x for k,x in product.items() if x}
        for k,x in value.items():
            determinant[k] = determinant.get(k,0)+x
    determinant = {k:x for k,x in determinant.items() if x}
    if not determinant:
        return None
    choices = [1]
    for variable in range(1,len(forms[0])):
        # Degree ≤4. A nonzero polynomial cannot vanish at all five integers.
        for v in range(5):
            specialized = {}
            for k,x in determinant.items():
                key = tuple(i for i in k if i != variable)
                specialized[key] = specialized.get(key,0)+x*v**(len(k)-len(key))
            specialized = {k:x for k,x in specialized.items() if x}
            if specialized:
                determinant = specialized
                choices.append(v)
                break
        else:
            raise AssertionError("Nonzero determinant polynomial vanished")
    return [sum(a*b for a,b in zip(form,choices))-(i%5==0)
            for i,form in enumerate(forms)]


def inverse_square(a):
    n = len(a)
    x = [row.copy()+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k = next(i for i in range(j,n) if x[i][j])
        x[j], x[k] = x[k], x[j]
        p = x[j][j]
        x[j] = [t/p for t in x[j]]
        for i in range(n):
            if i != j and x[i][j]:
                p = x[i][j]
                x[i] = [u-p*v for u,v in zip(x[i],x[j])]
    return [r[n:] for r in x]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("inputs",type=Path)
    root = parser.parse_args().inputs
    stage = "authentication"

    def expired(_signum,_frame):
        emit(status="WRAPPER_CASE_UNRESOLVED_AT_CAP",cap_seconds=CAP,stage=stage)
        raise SystemExit(124)

    signal(SIGALRM,expired)
    alarm(CAP)
    try:
        raw = {name:(root/name).read_bytes() for name in PINS}
        assert all(sha256(data).hexdigest()==PINS[name] for name,data in raw.items())
        app = json.loads(raw["ROLE902-APPLICATION.json"])
        c = json.loads(raw["7113-CALLER.json"])
        assert app["status"]=="PASS_ROLE902_FINAL_APPLICATION"
        assert app["candidate_canonical_sha256"]=="bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
        assert app["caller_sha256"]==PINS["7113-CALLER.json"]
        assert Q(app["claim"])==Q("0.003648411294790")
        assert c["types"]["A"]["offset"]==0 and c["types"]["A"]["roles"]==36
        assert len(c["types"]["A"]["ports"])==96
        contacts = {
            1447: (1, "-2"), 1449: (1, "2"), 1741: (10, "2"),
            1743: (10, "-2"), 1744: (11, "2"), 1746: (11, "-2"),
        }
        for clock, (role, coefficient) in contacts.items():
            assert c["events"][clock] == ["A", "ADD", role, 0, coefficient]
        old = c["events"][START:STOP]
        assert old[0]==["A","IDLE_ONE",1,[2,3,4,5,6,7,8]]
        assert old[-1]==["A","IDLE_ONE",11,[9,10]]
        assert c["events"][1742]==["A","IDLE_ONE",10,[9]]
        new = old.copy()
        new[0] = ["A","IDLE_ONE",1,[2,3,4,5,6,7,8,9]]
        new[-1] = ["A","IDLE_ONE",11,[10]]
        stage = "price"
        lo,hi = map(Q,app["raw_crossing"])
        h = run_path(str(root/"pricing.py"))["power_bounds"]
        gross = (96*(h(16,hi)[0]+h(56,hi)[0]-h(8,lo)[1]-h(64,lo)[1]),
                 96*(h(16,lo)[1]+h(56,lo)[1]-h(8,hi)[0]-h(64,hi)[0]))
        assert 0<gross[0]<gross[1]<96
        emit(status="START",cap_seconds=CAP,case_cap=1,bank=BANK,
             paid_delta={8:96,16:-96,56:-96,64:96},target_delta={},gross=gross)

        stage = "signed matrix controls"
        profiles = {}
        eye = [[Q(i==j) for j in range(36)] for i in range(36)]
        for q in (1,-1):
            m = matrix(old,q,1)
            assert matrix(new,q,1)==m
            im = matrix(old,q,1,reverse=True)
            assert multiply(m,im)==eye
            po,pn = matrix(old,q,-1),matrix(new,q,-1)
            profiles[q] = (m,im,multiply(im,po),multiply(im,pn),po,pn)
        old_m,new_m = profiles[1][-2:]
        assert [(i,j,str(new_m[i][j]-old_m[i][j])) for i in range(36) for j in range(36)
                if old_m[i][j]!=new_m[i][j]] == [(1,1,"-2"),(11,0,"4"),(11,11,"2")]

        stage = "simultaneous fixed-bank equations"
        equations = []
        for q,(m,im,ro,rn,_,_) in profiles.items():
            for i in range(36):
                for j in range(36):
                    if i in BANK or j in BANK:
                        coefficients = [rn[i][a]*(b==j)-(i==a)*ro[b][j]
                                        for a in BANK for b in BANK]
                        equations.append((f"q={q}:intertwine:{i},{j}",coefficients,ro[i][j]-rn[i][j]))
                    elif ro[i][j]!=rn[i][j]:
                        equations.append((f"q={q}:intertwine:{i},{j}",[Q(0)]*16,ro[i][j]-rn[i][j]))
                    basis = [m[i][a]*im[b][j] for a in BANK for b in BANK]
                    if i not in BANK or j not in BANK:
                        equations.append((f"q={q}:exit_support:{i},{j}",basis,Q(0)))
                    if q==-1:
                        p,ip = profiles[1][:2]
                        equations.append((f"q agreement:{i},{j}",
                            [a-p[i][r]*ip[s][j] for a,(r,s) in zip(basis,((r,s) for r in BANK for s in BANK))], Q(0)))
        forms,receipt = solve(equations)
        if forms is None:
            emit(status="EXCLUDED_FIXED_BOUNDARY_WRAPPERS",cases_completed=1,
                 witness=receipt,unresolved=[])
            return
        stage = "nonsingular witness over Q"
        answer = pick_invertible(forms)
        if answer is None:
            emit(status="EXCLUDED_IDENTICALLY_SINGULAR_INNER_WRAPPER",
                 cases_completed=1,system=receipt,unresolved=[])
            return
        assert all(sum(a*b for a,b in zip(row,answer))==rhs for _,row,rhs in equations)
        s = [r.copy() for r in eye]
        for (i,j),v in zip(((i,j) for i in BANK for j in BANK),answer):
            s[i][j] += v
        m,im = profiles[1][:2]
        ti = multiply(multiply(m,s),im)
        entry = [[s[i][j] for j in BANK] for i in BANK]
        exit_wrap = inverse_square([[ti[i][j] for j in BANK] for i in BANK])
        e = [r.copy() for r in eye]
        for i, row in zip(BANK,exit_wrap):
            for j,v in zip(BANK,row):
                e[i][j] = v
        for m,_,_,_,mo,mn in profiles.values():
            assert multiply(multiply(e,m),s)==m
            assert multiply(multiply(e,mn),s)==mo
        emit(status="PASSES_TWO_SECTORS_ONLY",cases_completed=1,system=receipt,
             entrance=entry, exit=exit_wrap, unresolved=[],
             denominators=sorted({v.denominator for row in entry+exit_wrap for v in row}),
             physical_all_bodies_and_paid_replay="pending")
    finally:
        alarm(0)


if __name__ == "__main__":
    assert __debug__
    main()
