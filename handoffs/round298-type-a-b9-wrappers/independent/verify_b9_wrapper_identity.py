"""Check the fixed Type A B9 four-role wrapper contradiction by reverse covectors."""
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
CERTIFICATE = "b247c56795c2089a3eb9f06276922a23805f5a4d587ac95d3f2e4bf14d112da7"
START, STOP, CAP = 1448, 1746, 30
ROLES = range(36)
BANK = (0,1,10,11)
VARIABLES = tuple((a,b) for a in BANK for b in BANK)


def emit(**fields):
    print(dumps(fields, sort_keys=True, default=str),flush=True)


def unique(pairs):
    x=dict(pairs)
    assert len(x)==len(pairs),"duplicate JSON key"
    return x


def pull(tape, row, q, b9, inverse=False):
    out=row.copy()
    for k,op,r,*a in tape if inverse else reversed(tape):
        assert k=="A" and r in ROLES
        if op in ("QUERY","ADD"):
            src,v=a
            assert src in ROLES and src!=r
            if op=="QUERY":
                assert v in (-1,1)
                v=Q(q)**v
            else:
                v=Q(v)
            out[src]+=(-v if inverse else v)*out[r]
        elif op=="SWAP":
            src,=a
            assert src in ROLES and src!=r
            out[r],out[src]=out[src],out[r]
        elif op=="LAMBDA":
            sign,=a
            # The two Gaussian terms (1+i*sign)/2 and (1-i*sign)q²/2 sum to 1.
            assert sign in (-1,1) and q*q==1
        else:
            assert op=="IDLE_ONE" and len(a)==1
            mask,=a
            assert mask and len(mask)==len(set(mask)) and all(1<=j<=17 for j in mask)
            if 9 in mask:
                out[r]*=b9
    return out


def body_geometry(word,caller):
    p=caller["types"]["A"]["ports"][0]
    assert p==0 and p in word["hosted"]["Dports"]
    vector=word["ports"][p]
    assert vector==11 and 0<vector<512
    first=(vector&-vector).bit_length()-1
    assert first<9 and caller["ambient_rank"]==9+8*caller["stages"]==145
    body_axes=[tuple(range(9+8*i,17+8*i)) for i in range(17)]
    assert body_axes[8]==tuple(range(73,81))
    details=[]
    for q in (1,-1):
        for b in (1,-1):
            axes=([first] if q<0 else [])+([73,74] if b<0 else [])
            marks=sum(1<<j for j in axes)
            actual_q=(-1)**((marks&vector).bit_count()&1)
            exponents=[sum(1 for j in group if marks>>j&1)%4 for group in body_axes]
            # On a marked body axis C_f has eigenvalue i, on an unmarked one +1.
            assert exponents==[0]*8+[0 if b>0 else 2]+[0]*8 and q==actual_q
            details.append({"q":q,"B9":b,"minus_walsh_axes":axes,"q_squared":q*q,"lambda":1})
    return {"port":p,"central_vector":vector,"B9_axes":list(body_axes[8]),"width":1,"fibres":details}


def profiles(old,new,q):
    eye=[[Q(i==j) for j in ROLES] for i in ROLES]
    result={name:[] for name in ("m","inv","po","pn","ro","rn")}
    for unit in eye:
        m=pull(old,unit,q,1)
        inv=pull(old,unit,q,1,inverse=True)
        assert m==pull(new,unit,q,1)
        assert pull(old,m,q,1,inverse=True)==pull(old,inv,q,1)==unit
        for k,v in (("m",m),("inv",inv),("po",pull(old,unit,q,-1)),("pn",pull(new,unit,q,-1)),
                    ("ro",pull(old,inv,q,-1)),("rn",pull(new,inv,q,-1))):
            result[k].append(v)
    return result


def equation(id_, book):
    parts=id_.split(":")
    i,j=map(int,parts[-1].split(","))
    assert i in ROLES and j in ROLES

    def transport(P,a,b):
        return P["m"][i][a]*P["inv"][b][j]

    if parts[0]=="q agreement":
        assert len(parts)==2
        return [transport(book[-1],a,b)-transport(book[1],a,b) for a,b in VARIABLES],Q(0)
    assert len(parts)==3 and parts[0] in ("q=1","q=-1")
    P=book[int(parts[0][2:])]
    if parts[1]=="exit_support":
        assert i not in BANK or j not in BANK,"exit support is checked only outside the bank block"
        return [transport(P,a,b) for a,b in VARIABLES],Q(0)
    assert parts[1]=="intertwine"
    old,new=P["ro"],P["rn"]
    return [new[i][a]*(j==b)-(i==a)*old[b][j] for a,b in VARIABLES],old[i][j]-new[i][j]


def main():
    assert __debug__ and version_info[:2]==(3,12)
    p=ArgumentParser(description=__doc__)
    p.add_argument("inputs",type=Path)
    p.add_argument("certificate",type=Path,help="pinned primary RESULT.jsonl")
    args=p.parse_args()
    t=perf_counter()
    stage="authentication"

    def timeout(_sig,_frame):
        emit(status="CAP_UNRESOLVED",cap_seconds=CAP,stage=stage,seconds=perf_counter()-t)
        raise SystemExit(124)

    signal(SIGALRM,timeout)
    alarm(CAP)
    raw={k:(args.inputs/k).read_bytes() for k in PINS}
    assert {k:sha256(v).hexdigest() for k,v in raw.items()}==PINS
    word=decompress(raw["ROLE902-WORD.json.gz"])
    assert sha256(word).hexdigest()==WORD
    word,app,caller=(loads(v,object_pairs_hook=unique) for v in (word,raw["ROLE902-APPLICATION.json"],raw["7113-CALLER.json"]))
    assert app["status"]=="PASS_ROLE902_FINAL_APPLICATION" and app["candidate_canonical_sha256"]==WORD
    assert app["caller_sha256"]==PINS["7113-CALLER.json"] and Q(app["claim"])==Q("0.003648411294790")
    cert=args.certificate.read_bytes()
    assert sha256(cert).hexdigest()==CERTIFICATE
    launch,receipt=(loads(line,object_pairs_hook=unique) for line in cert.splitlines())
    assert launch["bank"]==list(BANK) and launch["cap_seconds"]==CAP and launch["case_cap"]==1
    assert receipt["status"]=="EXCLUDED_FIXED_BOUNDARY_WRAPPERS" and receipt["cases_completed"]==1
    witness=receipt["witness"]
    assert len(witness["identity"])==10 and Q(witness["contradiction"])==4
    geometry=body_geometry(word,caller)
    tape=caller["events"]
    assert len(tape)==4783 and caller["types"]["A"]["roles"]==36 and caller["types"]["A"]["offset"]==0
    old=tape[START:STOP]
    assert old[0]==["A","IDLE_ONE",1,[2,3,4,5,6,7,8]] and old[-1]==["A","IDLE_ONE",11,[9,10]]
    assert tape[1742]==["A","IDLE_ONE",10,[9]]
    assert Counter(e[1] for e in old)=={"ADD":262,"IDLE_ONE":16,"SWAP":8,"LAMBDA":8,"QUERY":4}
    new=[["A","IDLE_ONE",1,[2,3,4,5,6,7,8,9]],*old[1:-1],["A","IDLE_ONE",11,[10]]]
    stage="reverse exact signed and inverse unit rows"
    book={q:profiles(old,new,q) for q in [1,-1]}
    assert book[1]["po"][11][0]==-2 and book[1]["pn"][11][0]==2
    stage="literal ten-row rational certificate"
    lhs=[Q(0)]*len(VARIABLES)
    rhs=Q(0)
    audit={}
    controls=[]
    for name,w in witness["identity"].items():
        m=Q(w)
        coefficients,constant=equation(name,book)
        audit[name]={"weight":m,"coefficients":coefficients,"constant":constant}
        lhs=[a+m*b for a,b in zip(lhs,coefficients,strict=True)]
        rhs+=m*constant
        if name=="q=-1:exit_support:0,2":
            controls=[m*v for v in coefficients]
    assert not any(lhs) and rhs==4 and any(controls)
    alarm(0)
    emit(status="PASS_INDEPENDENT_B9_BOUNDARY_CONTRADICTION",cases_completed=1,unresolved=[],
         bank=BANK,interval=[START,STOP],variables=VARIABLES,physical=geometry,
         equations=audit,weighted_left_coefficients=lhs,weighted_right_constant=rhs,
         omitting_exit_support_causes_nonzero_left=controls,
         comparator_head=HEAD,caller_head=CALLER,word_canonical_sha256=WORD,
         input_pins=PINS,certificate_sha256=CERTIFICATE,cap_seconds=CAP,seconds=perf_counter()-t)


if __name__=="__main__":
    main()
