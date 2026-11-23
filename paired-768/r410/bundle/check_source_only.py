"""Check exact overlays and the price checks on the frozen arithmetic roster."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import runpy

PACKAGE = Path("research/p104-matched-suffix-25bit")
EXPECTED = ("price", "calendar", "raw", "exterior", "nested", "product", "setup", "source-pins")


def verified(path, digest):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == digest, path.name
    return data


def source_overlay(root, package):
    manifest = json.loads((root/"SOURCE-ASSEMBLY.json").read_bytes())
    for path, pin in manifest["files"].items():
        verified(root/path, pin)
    assert not (package/"RESULT-460.json").exists()
    checks = json.loads((package/"VERIFY.json").read_bytes())
    actual = tuple(cmd["argv"][-1] if cmd["argv"][-1] != "{package}/check_parent_pins.py"
                   else "source-pins" for cmd in checks["commands"])
    assert actual == EXPECTED
    for file in ("verify.py", "verify_setup.py"):
        runpy.run_path(str(package/file))["authenticate"]()
    runpy.run_path(str(package/"check_parent_pins.py"), run_name="__main__")
    with TemporaryDirectory(prefix="offset8-source-check-") as temp:
        source = runpy.run_path(str(package/"upstream_verify.py"))["restore"](Path(temp))
        runpy.run_path(str(package/"prepare.py"))["materialize"](source)
        names = ("typed_transport.py", "grades.py", "check_exterior.py", "check_nested.py", "runtime.patch")
        old = {name:(source/name).read_bytes() for name in names}
        profile = runpy.run_path(str(package/"retune.py"))
        profile["install"](source,"460")
        assert all((source/name).read_bytes()==data for name,data in old.items() if name!="runtime.patch")
        assert (source/"runtime.patch").read_bytes() == old["runtime.patch"].replace(
            profile["PARENT_INSTALLATION"].encode(),
            b'TERMINAL = Profile((8192, 38102, 604363), 18531230, Q(".003898460003746"))',
        )
        prov = json.loads((source/"SOURCES.json").read_bytes())
        assert prov["runtime_images"]["installations.py"]["after"] == profile["PROFILES"]["460"]["image_sha"]
        for src, dst in (
            ("matched_positive_debit.py","positive_debit.py"),
            ("check_matched_allocator.py","check_matched_allocator.py"),
            ("matched_price_support.py","matched_price_support.py"),
        ):
            assert (package/src).read_bytes() == (source/dst).read_bytes()
        for path in source.glob("*.py"):
            compile(path.read_bytes(),path.name,"exec")
        inner = (source/"verify.py").read_text()
        assert '"price": ("check_matched_allocator.py", "receipt.py", "independent_price.py", "check_placement.py")' in inner
        assert '"check_scaled.py", "check_ordinary_floor.py"' in inner and "fcntl.flock" in inner
    print("PASS_EXACT_SOURCE_OVERLAY 8 planned modes, frozen archive, one profile, same signed calendar and lock")


def receipt_controls(package, evidence):
    data = json.loads(verified(evidence/"PRICE.json",
                               "9c06021a01749f560cc0d8b14167fa8b07f5d6771695939bd20e56f0d99bf4e6"))
    source = json.loads(verified(evidence/"R368-RANK-RECEIPT.json",
                                 "d26a1f9ea8fd78900f45bf83c29ee2b700d015c231a82eab1cad54283b4aec66"))
    verified(evidence/"replay_grade_cut.py","5b7eb70b4258de852a64045a7875fd79d1240ab6119e4c1d11ec8bdcea2f9daf")
    grade = runpy.run_path(str(evidence/"replay_grade_cut.py"))
    live_check = runpy.run_path(str(package/"check_matched_allocator.py"))

    def rank(text):
        value = Q(text)
        return value.numerator if value.denominator == 1 else value

    def cells(rows):
        return {tuple(map(rank,key)):Q(value) for key,value in rows}

    def labels(counts):
        return tuple(x for grade,count in counts.items() for x in (rank(grade),)*count)

    old_t, old_p = (grade["unmix"](source[name]) for name in ("source_targets","source_paid"))
    split_paid = old_p.copy()
    split_paid[1] -= 1008
    split_paid[Q(1,2)] = 2016
    typed = cells(data["typed_rows"])
    parts = tuple(SimpleNamespace(multiplicity=w, paid=p, targets=t) for w,p,t in (
        (5,labels(split_paid),labels(old_t)),
        (451,labels({2*r:n for r,n in old_p.items()}),labels({2*r:n for r,n in old_t.items()})),
    ))
    recipe = SimpleNamespace(
        types=lambda:parts,
        paid=SimpleNamespace(histogram=grade["weighted"](old_p,1008)),
        targets=SimpleNamespace(histogram=grade["weighted"](old_t)),
        cells=cells(data["grade_rows"]), typed_cells=lambda:typed, trial=Q(17145637307,2**42),
    )

    def intervals(r, exponent):
        assert exponent == 1-recipe.trial
        return grade["outward"](Q(r))

    edges = live_check["paid_edges"](recipe,intervals)
    price = runpy.run_path(str(package/"matched_price_support.py"))
    first = price["factor"](edges, price["rooted_power"])
    other = price["factor"](edges, price["series_power"])
    assert all(str(first[key])==data["directed_rooted"][key]
               for key in ("positive_reserve","adjacent_shortfall","old_pointwise_shortfall_at_new_booking"))
    assert str(other["positive_reserve"])==data["independent_log_series"]["positive_reserve"]
    typed[next(iter(typed))] += Q(1,2**112)
    try:
        live_check["paid_edges"](recipe,intervals)
    except AssertionError:
        print("PASS_SOURCE_ROSTER_MUTATION_CONTROL")
    else:
        raise ValueError("A corrupted allocation unexpectedly passed")
    print("PASS_FROZEN_ROSTER_PRICE 51 grade cells, 88 typed shares, 1971 intervals, exact factors")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("assembly",type=Path)
    parser.add_argument("price_evidence",type=Path)
    args = parser.parse_args()
    assert __debug__
    root = args.assembly.resolve()
    package = root/PACKAGE
    source_overlay(root, package)
    receipt_controls(package,args.price_evidence.resolve())


if __name__ == "__main__":
    main()
