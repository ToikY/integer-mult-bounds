"""Portable native precision and physical replay for chart120.

Reuse the authenticated #7115 source chain and its attributed native verifiers.
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
from pathlib import Path
import subprocess
import sys

OLD = "ae30929ff3b5f6b49a5edac78e2164acfbf809113d0b9f03249ef940dd7b2491"
NEW = "ff51fcc949bc50a31230a784822ab6f0d079c9102abf22c75746b2b5cdd09553"
PACKAGE_PINS = {
    "source.py": "9e0c5e7d08f5a3d40ef50ffa80228169f889bf6cd78b3ee0420de6f401d351a4",
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
    C = load("chart120_clifford", vendor / "frozen/clifford_exact.py")
    V = load("chart120_exact_interpreter", vendor / "frozen/native_verify.py")
    delta = pairs(changed)-pairs(baseline)
    required = delta | {(597,120),(120,127),(120,207),(597,127),(597,207)}
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
    for end in (127,207):
        split = verify[597,120]+verify[120,end]
        expected = source[597,end]
        V.equal(split,expected,"coherent factorization through chart120")
        assert all(V.state(split,i)==V.state(expected,i) for i in range(512))
        print("PASS_COHERENT_SPLIT",end,flush=True)
    return {"status":"PASS_EXACT_CHANGED_CHART_MAPS_AND_COMPOSITIONS",
            "new_ordered_pairs":sorted(delta),"checked":summary,"both_compositions_exact_columns":512}


def delta(a,b):
    answer=Counter(a)
    answer.subtract(b)
    return {k:v for k,v in sorted(answer.items()) if v}


def native(vendor, archive, baseline, changed, derive, candidate):
    I=load("chart120_source_independent",vendor/"independent.py")
    n0,n1=map(I.native,(baseline,changed))
    assert not n0["bad_inputs"] and not n1["bad_inputs"]
    assert delta(n1["paid"],n0["paid"])=={3:1,4:1,7:-1}
    assert delta(n1["helpers"],n0["helpers"])=={4:2,8:-1}
    assert all(n0[k]==n1[k] for k in ("rises","owned_peak","lifetimes"))
    mutant=deepcopy(changed)
    assert mutant["program"].pop(38670)==["ADD",1302,1447,"-1",120]
    assert I.native(mutant)["bad_inputs"]
    print("PASS_NATIVE_ADJOINT_AND_MUTATION",flush=True)
    derived, rows = derive(changed)
    assert derived["odd_scale"]==1125 and derived["fractional_bits"]==24
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
    A=load("chart120_forward_grid",archive/"audit_native.py")
    forward,grid=A.replay(changed,list(enumerate(changed["program"])),set())
    unit=1125*2**24
    assert forward[0]==[{k:v*unit for k,v in row.items()} for row in target]
    assert grid["odd_grid_lcm"]==1125 and grid["owned_rise_mass"]==56
    print("PASS_INDEPENDENT_INTEGER_FORWARD_AND_OWNED_GRID",flush=True)
    host = subprocess.run([sys.executable, "-I", "-B", str(vendor/"frozen/verify_host3_odd.py"),
                           str(candidate), "1125"], check=True, capture_output=True, text=True)
    assert "endpoint bad rows 0 odd certificate S 1125" in host.stdout
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
        "replayed 72844 events, 2963 chart pairs",
        "prime 1000000009 seed 11: helper rows bad 0 (of 1086), X rows bad 0, "
        "Y rows bad 0, X2 rows bad 0, Y2 rows bad 0 (of 104 ports; 96 with second mains)",
        "tableau on 104 ports: XX!=D 0 YY!=D 0 YX!=Q^-1D 0 XY!=QD 0 | "
        "controls matching (must be 0): 0 0",
        "PASS_PHYSICAL ",
    )
    assert all(marker in result.stdout for marker in expected), result.stdout
    print("PASS_WIDTH512_PHYSICAL", flush=True)
    return {
        "status": "PASS_WIDTH512_PHYSICAL",
        "width": 512, "prime": 1000000009, "seed": 11,
        "events": 72844, "chart_pairs": 2963, "exact_vector_controls": 4,
        "helpers": 1086, "main_ports": 104, "second_main_ports": 96,
        "helper_bad": 0, "main_bad": 0, "tableau_bad": 0, "wrong_sign_controls_matching": 0,
    }


def run(native_package: Path, candidate: Path) -> dict:
    """Run finite native gates from authenticated #7115 source and candidate."""
    if not __debug__:
        raise RuntimeError("Run without -O: source verifiers use assertions.")
    native_package, candidate = Path(native_package).resolve(), Path(candidate).resolve()
    check_pins(native_package, PACKAGE_PINS)
    baseline = word(native_package / "WORD.json.gz", OLD)
    changed = word(candidate, NEW)
    source = load("chart120_portable_source", native_package / "source.py")
    grid = load("chart120_portable_derive_grid", native_package / "derive_grid.py")
    with source.sources() as (vendor, archive, rank9, bundle, parent, original):
        check_pins(vendor / "frozen", FROZEN_PINS)
        exact = native(vendor, archive, baseline, changed, grid.derive, candidate)
        maps = chart_maps(vendor, baseline, changed)
        width = physical_width(vendor, candidate)
    return {"status": "PASS_CHART120_PORTABLE_NATIVE_PHYSICAL",
            "source": OLD, "word": NEW, "native": exact, "maps": maps, "width": width}
