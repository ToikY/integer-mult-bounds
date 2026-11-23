"""Extract exact ordinary K7 rank counts and 24 funding cells without installation."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from math import isqrt
from pathlib import Path
import ast
import gzip
import json
import tarfile

ARCHIVE_SHA = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
WORD_SHA = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
PAYLOAD_SHA = "f4a43e4e36ac734dea10a73dca496bf4a4f4a9804b903ea379483d0513d7abc3"
CB = Q(4391986206293, 2**50)
UNIT = 1 << 112


def member(raw, name, pins, key):
    with tarfile.open(fileobj=BytesIO(raw)) as t:
        m=t.getmember(name)
        assert m.isfile()
        data=t.extractfile(m).read()
    pins[key]=sha256(data).hexdigest()
    return data


def power_interval(rank, exponent):
    k,d=exponent.numerator,exponent.denominator
    assert rank>0 and k>=0 and not d&(d-1)
    whole,residue=divmod(k,d)
    low=high=rank**whole*UNIT
    lo_root=hi_root=rank*UNIT
    while d>1:
        d//=2
        lo_root=isqrt(lo_root*UNIT)
        hi_root=1+isqrt(hi_root*UNIT-1)
        if residue & d:
            low=low*lo_root//UNIT
            high=-(-high*hi_root//UNIT)
    return low,high


def run(path):
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==ARCHIVE_SHA
    pins={"peer8057.tar.gz":ARCHIVE_SHA}
    gz=member(raw,"research/tiered-native-multiplier/source/strong-bit-k7.json.gz",pins,"k7.gz")
    assert pins["k7.gz"]==WORD_SHA
    payload=gzip.decompress(gz)
    assert sha256(payload).hexdigest()==PAYLOAD_SHA
    pins["k7.payload"]=PAYLOAD_SHA
    word=json.loads(payload)
    check=member(raw,"research/tiered-native-multiplier/source/check_binary_k7.py",pins,"check_binary_k7.py")
    nested=member(raw,"research/tiered-native-multiplier/source/installer.tar.gz",pins,"installer.tar.gz")
    nested=member(nested,"retimed-source.tar.gz",pins,"installer.tar.gz::retimed-source.tar.gz")
    price=member(nested,"unpowered_price.py",pins,"retimed-source.tar.gz::unpowered_price.py")
    ancestor=member(nested,"predecessor/predecessor-8030.tar.gz",pins,"retimed-source.tar.gz::predecessor-8030.tar.gz")
    strict=member(ancestor,"strict_moment.py",pins,"predecessor-8030.tar.gz::strict_moment.py")

    # Execute only the exact self-contained integer power function, then
    # compare it against the independent transcription above for all ranks.
    tree=ast.parse(strict)
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="power_interval")
    namespace={"isqrt":isqrt,"UNIT":UNIT,"ceiling":lambda a,b:-(-a//b)}
    exec(compile(ast.Module(body=[function],type_ignores=[]),"strict_moment.py","exec"),namespace)
    for r in range(1,135):
        for exponent in (CB,1-CB):
            assert namespace["power_interval"](r,exponent)==power_interval(r,exponent)

    # The frozen source asserts this exact signed complete K7 invoice.
    text=check.decode()
    start=text.index("    expected_signed = ")
    end=text.index("    assert signed == expected_signed",start)
    statements=text[start:end]
    namespace={"dict":dict,"enumerate":enumerate,"range":range}
    exec(compile("\n".join(line[4:] for line in statements.splitlines()),
                 "check_binary_k7.py::expected_signed","exec"),namespace)
    signed=namespace["expected_signed"]
    dims={int(k):v["dim"] for k,v in word["frames"].items()}
    native=Counter(abs(dims[e[2]]-dims[e[3]]) for e in word["program"] if e[0]=="MOVE")
    assert sum(native.values())==2796
    paid=Counter({r:36*n for r,n in native.items()})
    caller_paid={1:444,**{r:444 for r in range(7,57,7)}}
    paid.update(caller_paid)
    native_target=Counter(abs(dims[b]-dims[a])
                          for a,b in zip(word["start"][222:],word["final"][222:],strict=True))
    assert sum(native_target.values())==word["public"]-222==408
    caller_targets={**{r:444 for r in range(8,65,7)},127:222}
    targets=Counter({r:36*n for r,n in native_target.items()})
    targets.update(caller_targets)
    assert sum(targets.values())==18906 and sum(paid.values())==104652
    assert sum(r*n for r,n in targets.items())==286098
    assert sum(r*n for r,n in paid.items())==284592
    assert {r:targets[r]-paid[r] for r in targets.keys()|paid.keys() if targets[r]!=paid[r]}==signed

    # Match frozen certify(C, census) without importing its installer.
    source=ast.parse(price)
    certify=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=="certify")
    namespace={"F":Q,"intervals":power_interval}
    exec(compile(ast.Module(body=[certify],type_ignores=[]),"unpowered_price.py","exec"),namespace)
    margin,cells=namespace["certify"](CB,(targets,paid))
    assert margin>0 and len(cells)==24
    assert all(5*r<=4*k for r,k in cells)
    psi=sum(paid[r]*share*r*(Q(power_interval(k,CB)[0],power_interval(r,CB)[1])-1)/CB
            for (r,k),share in cells.items())
    fringe=10*sum(k*n for k,n in targets.items())/((1-CB)*psi)
    assert 0<fringe<Q(186,25)
    return {"status":"PASS_EXACT_K7_24_CELL_INPUTS","peer":"8094",
            "head":"c20a08dc0a79a989e3515068560d5da371c0a2a8","binary_trial":str(CB),
            "power_unit":UNIT,"pins":pins,
            "native_paid":dict(sorted(native.items())),"native_copies":36,
            "caller_paid":caller_paid,"native_targets":dict(sorted(native_target.items())),"caller_targets":caller_targets,"targets":dict(sorted(targets.items())),"paid":dict(sorted(paid.items())),
            "signed":dict(sorted(signed.items())),"cells":[{"r":r,"k":k,"share":str(v)} for (r,k),v in cells.items()],
            "raw_margin":str(margin),"psi_lower":str(psi),"pointwise_suffix_upper":str(fringe),
            "floor":4474,"ordinary_debit":"710359/524288","child_tariff":"2401/1024",
            "signed_source_extraction":statements,
            "scope":"Rank counts reconstructed from literal native MOVE/helper boundaries and fixed root ranks, cross-checked against frozen source asserted signed invoice; funding cells regenerated by exact frozen certify. No native action or caller proof rerun."}


if __name__=="__main__":
    assert __debug__
    p=ArgumentParser(description=__doc__)
    p.add_argument("archive",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    data=(json.dumps(run(a.archive),sort_keys=True,indent=2)+"\n").encode()
    if a.output:
        with a.output.open("xb") as f:f.write(data)
    else:
        print(data.decode(),end="")
