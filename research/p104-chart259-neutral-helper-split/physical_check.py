"""Portable native precision and physical replay for chart259.

Reuse the authenticated #7120 source chain and its attributed native verifiers.
Chart compiler and exact interpreter credit the retained CrocSwap reviewers.
Chart120 adapter and integration used OpenAI Codex assistance.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import gzip
from importlib.util import module_from_spec, spec_from_file_location
import json
import re
from types import ModuleType
from pathlib import Path
import subprocess
import sys

OLD = "4f19c6ee57b74d7c3ea1863df0b33fe275a3a7511f77084f05726ee216ebdc34"
NEW = "0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc"
PACKAGE_PINS = {
    "source.py": "5d9173af18fe8cece93243a8c04d850001ef03082b3a565d25c6bd9037c0fcde",
    "derive_grid.py": "ceb7a44ef19d72a16db7b43c65c85910d965499d1715436011de32af5d39dbb0",
}
FROZEN_PINS = {
    "physical.py": "4e995d1158033d83bf69b671f23dc7924d66edbbe07623ba063ba7421234ea20",
    "clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "verify_host3_odd.py": "e75ad2096ba2587d1dc9c8982b2c2eb7c6fd2636a80adcd943314ef2cf6fd258",
}


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_pins(path, pins):
    for name, digest in pins.items():
        assert sha256((path / name).read_bytes()).hexdigest() == digest, name


def word(path, pin):
    data = gzip.decompress(path.read_bytes())
    assert sha256(data).hexdigest() == pin
    return json.loads(data)


def pairs(word):
    hosted = word["hosted"]
    mains = set(word["live"]) | {i+112 for i in word["live"]}
    mains |= set(hosted["X2"]) | set(hosted["Y2"])
    return ({tuple(e[2:4]) for e in word["program"] if e[0]=="MOVE"} |
            {(a,b) for i,(a,b) in enumerate(zip(word["initial"],word["final"])) if i not in mains})


def chart_maps(vendor, baseline, changed):
    C = load("chart259_clifford", vendor / "frozen/clifford_exact.py")
    V = load("chart259_exact_interpreter", vendor / "frozen/native_verify.py")
    delta = pairs(changed)-pairs(baseline)
    required = delta | {(3,259),(259,246),(3,246)}
    verify = {}
    source = {}
    summary = []
    for a, b in sorted(required):
        frames = [changed["frames"][i] for i in (a,b)]
        ca, cb = [C.canonical_frame(9, tuple(x)) for x in frames]
        record, _ = C.lower_child(ca.adjoint().then(cb))
        expect = V.adjoint(V.frame(frames[0],9)) + V.frame(frames[1],9)
        actual = V.recipe(record)
        V.equal(actual, expect, "signed tableau and Gaussian phase")
        assert record["rank"] == abs(len(frames[1])-len(frames[0]))
        assert all(V.state(actual,i)==V.state(expect,i) for i in range(512))
        bad = deepcopy(record)
        bad["left"]["phase"] = (bad["left"]["phase"]+1) % 4
        try:
            V.equal(V.recipe(bad),expect,"mutated global phase")
        except ValueError:
            pass
        else:
            raise AssertionError("Wrong global phase accepted")
        verify[a,b] = actual
        source[a,b] = expect
        summary.append({"pair":[a,b],"rank":record["rank"],"exact_columns":512,"phase_control_rejected":True})
        print("PASS_EXACT_PAIR",a,b,record["rank"],flush=True)
    split = verify[3,259]+verify[259,246]
    expected = source[3,246]
    V.equal(split,expected,"coherent factorization through chart259")
    assert all(V.state(split,i)==V.state(expected,i) for i in range(512))
    print("PASS_COHERENT_SPLIT",246,flush=True)
    return {"status":"PASS_EXACT_CHANGED_CHART_MAPS_AND_COMPOSITION",
            "new_ordered_pairs":sorted(delta),"checked":summary,"composition_exact_columns":512}


def delta(a,b):
    answer=Counter(a)
    answer.subtract(b)
    return {k:v for k,v in sorted(answer.items()) if v}


def native(vendor, archive, baseline, changed, derive, candidate):
    I=load("chart259_source_independent",vendor/"independent.py")
    n0,n1=map(I.native,(baseline,changed))
    assert not n0["bad_inputs"] and not n1["bad_inputs"]
    assert not delta(n1["paid"],n0["paid"])
    assert delta(n1["helpers"],n0["helpers"])=={3:1,5:1,8:-1}
    assert all(n0[k]==n1[k] for k in ("rises","owned_peak","lifetimes"))
    mutant=deepcopy(changed)
    assert mutant["program"].pop(31854)==["ADD",231,448,"1",259]
    assert I.native(mutant)["bad_inputs"]
    print("PASS_NATIVE_ADJOINT_AND_MUTATION",flush=True)
    derived, rows = derive(changed)
    odd, height = derived["odd_scale"], derived["fractional_bits"]
    print("DERIVED_NATIVE_GRID", odd, height, flush=True)
    n=changed["public"]
    target=[{i:Fraction(1)} if i<n else {} for i in range(n+changed["owned_fields"])]
    H=changed["hosted"]
    D=set(H["Dports"])
    for i,a in enumerate(changed["live"]):
        b=a+112
        if i in D:
            target[b][a]=Fraction(1)
        else:
            target[a][b]=Fraction(-1)
            target[b]={a:Fraction(1,2),b:Fraction(1,2)}
    for a,b in zip(H["X2"],H["Y2"]):
        target[a][b]=Fraction(-1)
    assert rows==target
    print("PASS_EXACT_RATIONAL_FORWARD_AND_PREPRODUCT_GRID",flush=True)
    forward_path=archive/"audit_native.py"
    if height == 24:
        A=load("chart259_forward_grid",forward_path)
    else:
        code=forward_path.read_text()
        old='word["public"], word["owned_fields"], 2**24'
        assert code.count(old)==1
        A=ModuleType("chart259_forward_grid")
        A.__file__=str(forward_path)
        sys.modules[A.__name__]=A
        exec(compile(code.replace(old,f'word["public"], word["owned_fields"], 2**{height}'),
                     str(forward_path),"exec"),A.__dict__)
    forward,grid=A.replay(changed,list(enumerate(changed["program"])),set(),grid=odd)
    unit=odd*2**height
    assert forward[0]==[{k:v*unit for k,v in row.items()} for row in target]
    assert grid["odd_grid_lcm"]==odd and grid["dyadic_height"]==height and grid["owned_rise_mass"]==56
    print("PASS_INDEPENDENT_INTEGER_FORWARD_AND_OWNED_GRID",flush=True)
    host = subprocess.run([sys.executable, "-I", "-B", str(vendor/"frozen/verify_host3_odd.py"),
                           str(candidate), str(odd)], check=True, capture_output=True, text=True)
    assert f"endpoint bad rows 0 odd certificate S {odd}" in host.stdout
    assert "PASS_HOST3 decoupled ports 96 hosted ports 8" in host.stdout
    print("PASS_NATIVE_HOST3_ODD", flush=True)
    return {"status":"PASS_FULL_NATIVE_ADJOINT_FORWARD_AND_PRECISION_GRID",
            "native":n1,"derived_grid":derived,"integer_grid":grid,"grid_axes":len(target),
            "grid_coefficient_positions":len(target)**2,"wrong_cut_add_rejected":True}


def physical_width(vendor, candidate):
    frozen = vendor / "frozen"
    result = subprocess.run([
        sys.executable, "-I", "-B", str(frozen / "physical.py"), str(candidate),
        str(frozen / "clifford_exact.py"), "1000000009", "11",
    ], check=True, capture_output=True, text=True)
    expected = (
        "gate interpreter agrees with the library on 4 exact state vectors",
        "replayed 73698 events, ",
        "prime 1000000009 seed 11: helper rows bad 0 (of 1090), X rows bad 0, "
        "Y rows bad 0, X2 rows bad 0, Y2 rows bad 0 (of 104 ports; 96 with second mains)",
        "tableau on 104 ports: XX!=D 0 YY!=D 0 YX!=Q^-1D 0 XY!=QD 0 | "
        "controls matching (must be 0): 0 0",
        "PASS_PHYSICAL ",
    )
    assert all(marker in result.stdout for marker in expected), result.stdout
    match=re.search(r"replayed 73698 events, (\d+) chart pairs",result.stdout)
    assert match is not None
    chart_pairs=int(match[1])
    print("PASS_WIDTH512_PHYSICAL", flush=True)
    return {
        "status": "PASS_WIDTH512_PHYSICAL",
        "width": 512, "prime": 1000000009, "seed": 11,
        "events": 73698, "chart_pairs": chart_pairs, "exact_vector_controls": 4,
        "helpers": 1090, "main_ports": 104, "second_main_ports": 96,
        "helper_bad": 0, "main_bad": 0, "tableau_bad": 0, "wrong_sign_controls_matching": 0,
    }


def run(native_package: Path, candidate: Path) -> dict:
    """Run finite native gates from authenticated #7120 source and candidate."""
    if not __debug__:
        raise RuntimeError("Run without -O: source verifiers use assertions.")
    native_package, candidate = Path(native_package).resolve(), Path(candidate).resolve()
    check_pins(native_package, PACKAGE_PINS)
    baseline = word(native_package / "WORD.json.gz", OLD)
    changed = word(candidate, NEW)
    source = load("chart259_portable_source", native_package / "source.py")
    grid = load("chart259_portable_derive_grid", native_package / "derive_grid.py")
    with source.sources() as (vendor, archive, rank9, bundle, parent, original):
        check_pins(vendor / "frozen", FROZEN_PINS)
        exact = native(vendor, archive, baseline, changed, grid.derive, candidate)
        maps = chart_maps(vendor, baseline, changed)
        width = physical_width(vendor, candidate)
    return {"status": "PASS_CHART259_PORTABLE_NATIVE_PHYSICAL",
            "source": OLD, "word": NEW, "native": exact, "maps": maps, "width": width}


def main(mode, package, candidate, receipt):
    package, candidate = Path(package).resolve(), Path(candidate).resolve()
    check_pins(package, PACKAGE_PINS)
    baseline=word(package/"WORD.json.gz",OLD)
    changed=word(candidate,NEW)
    source=load("chart259_cli_source",package/"source.py")
    grid=load("chart259_cli_grid",package/"derive_grid.py")
    print("START",mode,NEW,flush=True)
    with source.sources() as (vendor,archive,rank9,bundle,parent,old):
        check_pins(vendor/"frozen",FROZEN_PINS)
        print("PASS_AUTHENTICATED_SOURCE_CHAIN",flush=True)
        if mode=="maps":
            out=chart_maps(vendor,baseline,changed)
        else:
            assert mode=="native"
            out=native(vendor,archive,baseline,changed,grid.derive,candidate)
    out.update(source=OLD,word=NEW)
    Path(receipt).write_text(json.dumps(out,indent=2,sort_keys=True,default=str)+chr(10))
    print(out["status"],flush=True)


if __name__=="__main__":
    main(*sys.argv[1:])
