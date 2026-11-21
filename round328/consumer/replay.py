"""Replay the unchanged #7863 rational consumer and expanded outer audit on a supplied cap."""
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import signal
import sys
import tarfile
import tempfile
from time import monotonic
from urllib.request import urlopen

PINS = {
    "replay.tar.gz": ("ac3df5d5c8889f464f575e32dfea43714abf08ca", "p104-round6-independent-proof-replay", "bffb02e833d8253c693ea3e679fdc1a737a5a45f81089255848d9ee9a7d3487d"),
    "source7863.tar.gz": ("b3e4412fe01f07dc58305616fabf96345f49a781", "p104-bit-451-factor-schedule", "5f9d9c378a1bddccb2e42ac6453716fa950f19bd71f6181a9606f5eb68b022b3"),
}
CAP = "0.0038799280438357"
digest = lambda b: hashlib.sha256(b).hexdigest()


def authenticated(args, temp):
    manifest = {}
    for name, (head, package, pin) in PINS.items():
        url = f"https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/{head}/research/{package}/replay.tar.gz"
        raw = (args.archives/name).read_bytes() if args.archives else urlopen(url, timeout=30).read()
        assert digest(raw) == pin
        with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
            members = tar.getmembers()
            assert len({m.name for m in members}) == len(members)
            assert sum(m.size for m in members) < 2**29
            for m in members:
                p = PurePosixPath(m.name)
                assert not p.is_absolute() and '..' not in p.parts and (m.isdir() or m.isfile())
            if name == "replay.tar.gz":
                tar.extractall(temp, filter="data")
                for line in (temp/"SHA256SUMS").read_text().splitlines():
                    key_hash, path = line.split("  ", 1)
                    assert path not in manifest and digest((temp/path).read_bytes()) == key_hash
                    manifest[path] = key_hash
                assert len(manifest) == 253
            else:
                files = [m for m in members if m.isfile()]
                assert len(files) == 204
                for m in files:
                    path = PurePosixPath(m.name).relative_to("package-sanitized")
                    assert (temp/"451-consumer"/path).read_bytes() == tar.extractfile(m).read()
    return manifest


def reject(fn, message):
    try:
        fn()
    except ValueError as exc:
        assert str(exc) == message, str(exc)
    else:
        raise ValueError("missing control rejection")


def main():
    assert sys.version_info[:2] == (3,12) and __debug__
    parser = argparse.ArgumentParser()
    parser.add_argument("--archives", type=Path, help="Directory of two pinned tarballs; otherwise download by exact commit")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    for key in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        os.environ[key] = "1"
    args.out.mkdir(parents=True, exist_ok=False)
    start = monotonic()
    signal.alarm(100)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = authenticated(args, root)
        pkg = root/"451-consumer"
        path = pkg/"source-7830/review/independent.py"
        assert digest(path.read_bytes()) == "a2366b60cb4cd535fbcbce2a834cdf2ed4b9daba3e7025c7403e6abcd598a7ca"
        spec = importlib.util.spec_from_file_location("review_r328", path)
        r = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = r
        spec.loader.exec_module(r)
        work = pkg/"inputs"
        assert r.authenticate(work,False) == (20,127)
        r.ORDINARY = CAP
        app, audit = r.replay_application(work,args.out)
        r.compare_fixed_application(work,app,audit)
        phys = r.rational_orientations(work,app)
        paid, targets, ordinary = r.native_rational(app)
        prices = r.directed_invoice(paid,targets,r.RATIONAL_BRACKET,r.TARGET)
        old_claim = r.Q(json.loads((pkg/"consumer-replay/CONSUMER.json").read_bytes())["claim"])
        claim = app["application"]["claim"]
        tested = r.Q(audit["outer"]["finite_compiler"]["tested"])
        q = r.Q
        gap = q(1,10**14)
        assert q(claim) == (int(q(CAP)/gap)-8)*gap
        assert old_claim < q(claim) and q(claim)+7*gap == tested < q(CAP)
        assert app["caller_census"]["calls"] == 48
        assert audit["compiler_report_sha256"] == digest((args.out/"APPLICATION.json").read_bytes())
        assert q(audit["outer"]["finite_compiler"]["BIT_margin"]) == q(CAP)-tested
        summary = dict(claim=claim,sharp_outer=audit["outer"]["outer_checks"])
        outer = r.rational_outer(app,audit,paid,targets,q(CAP),summary)
        assert audit['outer']['outer_checks']['strict_count']==54 and audit['outer']['outer_checks']['functional_count']==4
        damaged = paid.copy()
        damaged[1] += 1
        reject(lambda:r.directed_invoice(damaged,targets,r.RATIONAL_BRACKET,r.TARGET),"directed signs at raw crossing endpoints")
        reject(lambda:r.outer_margins(q(claim),gap,q(claim)+4*gap-q(1,10**15)),"all strict and functional outer conditions")
        receipt = dict(status="PASS_CONDITIONAL_ON_SUPPLIED_CAP",cap=CAP,claim=claim,tested=str(tested),prior_grid_claim=str(old_claim),
                       controls=["extra_rank_1_charge_rejected","low_cap_rejected"],independent_orientations=phys,
                       directed_rational_raw=prices["raw_crossing"],outer=outer,elapsed_seconds=monotonic()-start,
                       premises=app["premises"],archive_pins=PINS,archive_manifest=manifest,
                       output_sha256={p.relative_to(args.out).as_posix():digest(p.read_bytes()) for p in args.out.rglob("*") if p.is_file()})
        (args.out/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        print("PASS conditional on",CAP,"claim",claim,"tested",tested,"elapsed",receipt["elapsed_seconds"],flush=True)


if __name__=="__main__":
    main()
