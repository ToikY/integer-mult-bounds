"""Screen one Gaussian debit booking on the exact #8069 signed producer."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

HEAD = "2d0d7d378929269b00dcabfac1099b2bb23b3b3b"
PACKAGE = "research/p104-weighted-optimal-allocation"
PINS = {
    "RESULT.json": "03eb56a8c62976a10cd37718fbb77a849db0620196514a5fb2ae2318de0e450b",
    "prepare.py": "f45daf92a2459de76a0a091c0fb53fa3c893edd157dd9f7d2d29df1e75f47b57",
    "verify.py": "a30cf62aa1a9ca1dd25972135a97751c73af12e2de2c3ba64775acb000c51544",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}
BINARY, GAUSSIAN = Q(4391986206293, 2**50), Q(17145637307, 2**42)
D, D_OLD, D_NEW = Q(1405, 1024), Q(64944, 524288), Q(64939, 524288)
G, ETA, M = Q(1, 10**18), Q(".0039"), Q(249, 250)
WEIGHTS = (Q(1, 62500), Q(1, 250), Q(1))
H_MIN, H_MAX = 8192, 524288
CAPS = (318292451, 318292711)
OLD_H, OLD_G, K_OLD = (8192, 124847, 524288), 490664, Q(".0038982141167032")
OLD_CEILING = Q(104641888400286240891629336349, 26843545600000000000000000000000)


def unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"Repeated key {key}")
        result[key] = value
    return result


def authenticate(repo):
    def git(*argv):
        return subprocess.check_output(["git", "-C", str(repo), *argv], timeout=8)

    assert git("rev-parse", "HEAD").decode().strip() == HEAD
    package = repo / PACKAGE
    for name, expected in PINS.items():
        data = (package / name).read_bytes()
        assert sha256(data).hexdigest() == expected, name
        assert data == git("show", f"{HEAD}:{PACKAGE}/{name}"), name
    return package, json.loads((package/"RESULT.json").read_bytes(), object_pairs_hook=unique)


def interval18(q):
    scale = 10**18
    return Q((q*scale).__floor__(),scale), Q((q*scale).__ceil__(),scale)


def power_two(q):
    terms = 28
    u = Q(1,3)
    log2lo = 2*sum(u**(2*i+1)/(2*i+1) for i in range(terms))
    log2hi = log2lo + 2*u**(2*terms+1)/((2*terms+1)*(1-u*u))
    lo,hi=q*log2lo,q*log2hi

    def partial(x):
        acc=part=Q(1)
        for i in range(1,terms+1):
            part=part*x/i
            acc+=part
        return acc, part*x/(terms+1)

    low = partial(lo)[0]
    high,remainder = partial(hi)
    high += remainder/(1-hi/(terms+2))
    return interval18(low)[0], interval18(high)[1]


def ordinary(heights):
    rates=[]
    preceding=Q()
    for height in heights:
        current=M*(BINARY-D/height)+preceding/250
        assert current<ETA
        if len(rates)==2:
            return current, rates
        # Use the precise preceding tick used by the registered invoice.
        preceding=Q((current*10**21).__floor__()-1,10**21)
        rates.append(preceding)


def funding(cap, height, debit):
    ordinary_sum=(cap-1731-220*height)//320
    heights=(H_MIN,ordinary_sum-H_MIN-H_MAX,H_MAX)
    assert all(H_MIN<=h<=H_MAX for h in heights)
    slopes=[w/h**2 for w,h in zip(WEIGHTS,heights,strict=True)]
    assert slopes[0]<slopes[1]<slopes[2]
    raw=ordinary(heights)[0]
    ideal=BINARY*(1-Q(1,250**3))-M*D*sum(w/h for w,h in zip(WEIGHTS,heights,strict=True))
    slack=M*D*min(WEIGHTS)/H_MAX**3
    assert 0<=ideal-raw<Q(2,10**21)*(Q(1,250)+Q(1,250**2))<slack
    numerical=GAUSSIAN-debit/height
    return {"gaussian_height":height,"ordinary_heights":heights,"ordinary_ceiling":raw-5*G,
            "gaussian_ceiling":numerical-5*G,"installed_ceiling":min(raw,numerical)-5*G}


def crossing(cap):
    # A 256-wide predeclared bracket around the incumbent, with monotone global tails.
    lo,hi=OLD_G-128,OLD_G+128
    evaluations={}

    def evaluate(height):
        if height not in evaluations:
            assert len(evaluations)<10,"Scalar family evaluation cap"
            evaluations[height]=funding(cap,height,D_NEW)
        return evaluations[height]

    left,right=evaluate(lo),evaluate(hi)
    assert left["gaussian_ceiling"]<=left["ordinary_ceiling"]
    assert right["gaussian_ceiling"]>=right["ordinary_ceiling"]
    outside=(left["gaussian_ceiling"],right["ordinary_ceiling"])
    while hi-lo>1:
        middle=(lo+hi)//2
        row=evaluate(middle)
        if row["gaussian_ceiling"]<=row["ordinary_ceiling"]:
            lo=middle
        else:
            hi=middle
    left,right=evaluate(lo),evaluate(hi)
    best=max((left,right),key=lambda r:r["installed_ceiling"])
    assert max(outside)<best["installed_ceiling"]
    assert best["installed_ceiling"]>OLD_CEILING
    return dict(best, crossing=[left,right], evaluations=len(evaluations),
                outside_upper_bounds=outside, max_log2_c=cap)


def verify_placement(package, destination, height):
    restored=runpy.run_path(str(package/"verify.py"))["restore"](destination)
    runpy.run_path(str(package/"prepare.py"))["materialize"](restored)
    runtime=destination/"runtime"
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(destination)}
    subprocess.run([sys.executable,"-IB",str(restored/"bootstrap.py"),str(runtime)],
                   timeout=18,env=env,stdout=subprocess.DEVNULL,check=True)
    placement=restored/"check_placement.py"
    text=placement.read_text()
    for before,after in (
        ("recipe = numerical_recipe(TERMINAL.complex_log)",
         "recipe = numerical_recipe(int(sys.argv[2]))"),
        ("for H in (ENTRY.complex_log, TERMINAL.complex_log):",
         "for H in (ENTRY.complex_log, int(sys.argv[2])):"),
        ("print(json.dumps(out, indent=2))",
         "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
         "from positive_debit import certify_loss\n"
         "import positive_debit\n"
         "positive_debit.POSITIVE_DEBIT = Q(64939,524288)\n"
         "print(json.dumps(dict(placement=out, finite_loss=certify_loss(recipe, LOWER))))"),
    ):
        assert text.count(before)==1,before
        text=text.replace(before,after)
    placement.write_text(text)
    result=subprocess.run([sys.executable,"-IB",str(placement),str(runtime),str(height)],
                          check=True,timeout=18,stdout=subprocess.PIPE,env=env)
    return json.loads(result.stdout, object_pairs_hook=unique)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    signal.alarm(60)
    package,old=authenticate(args.baseline.resolve())
    assert Q(old["gaussian"]["raw_loss"])==D_OLD and Q(old["gaussian"]["trial"])==GAUSSIAN
    assert Q(old["ordinary_finite_debit"])==D and old["ordinary_floor"]==18960
    assert old["gaussian"]["weights"]==[5,451] and old["max_native_H"]==H_MAX
    assert tuple(old["terminal"]["ordinary_H"])==OLD_H and old["terminal"]["numerical_H"]==OLD_G
    assert Q(old["terminal"]["kappa"])==K_OLD and old["complete_log2_C"]==CAPS[0]
    assert ordinary(OLD_H)[0]-5*G==OLD_CEILING
    factor=Q(old["gaussian"]["finite_loss"]["upper_factor"])
    limit=power_two(D_NEW)
    assert factor<limit[0]
    frontier=[]
    for cap in CAPS:
        threshold=(cap-1731-320*(sum(OLD_H)+1))//220
        longer=funding(cap,threshold,D_OLD)
        shorter=funding(cap,threshold+1,D_OLD)
        assert longer["ordinary_ceiling"]>OLD_CEILING==shorter["ordinary_ceiling"]
        reduction=D_OLD-threshold*(GAUSSIAN-OLD_CEILING-5*G)
        assert 0<reduction<D_OLD-D_NEW
        frontier.append(dict(crossing(cap),largest_g_to_beat_old_ordinary=threshold,
                             required_strict_debit_reduction=reduction,
                             smallest_grid_tick_count=(reduction*524288).__floor__()+1))
    best=frontier[0]
    height=best["gaussian_height"]
    hs=best["ordinary_heights"]
    k=Q((best["installed_ceiling"]*10**16).__ceil__()-1,10**16)
    assert OLD_CEILING<k<best["installed_ceiling"] and GAUSSIAN-D_OLD/height<k+5*G
    with TemporaryDirectory(prefix="signed-placement-",dir=args.out.resolve().parent) as tmp:
        tree=Path(tmp)
        witness=verify_placement(package,tree,height)
        assert [r["H"] for r in witness["placement"]]==[1024,height]
        assert Q(witness["finite_loss"]["upper_factor"])==factor
        archive=tree/"research/tiered-native-multiplier/source"
        stock=runpy.run_path(str(archive/"activation.py"))["resource_receipt"](
            SimpleNamespace(rank_logs=hs,complex_log=height,eta=ETA))
        qualify=runpy.run_path(str(archive/"outer_budget.py"))["qualify"]
        entry=old["entry"]
        first=qualify(Q(entry["kappa"]),G,Q(entry["ordinary_rates"][-1]),GAUSSIAN-D_NEW/entry["numerical_H"])
        terminal=qualify(k,G,k+5*G,GAUSSIAN-D_NEW/height)
    prefix=((k-Q(old["entry"]["kappa"]))*stock["public_exponent_A"]).__ceil__()
    ordinary_log=128+320*sum(hs)
    complete=1+max(84500001,1602+220*height+ordinary_log,old["entry"]["log2_C"]+prefix)
    assert complete<=CAPS[0] and prefix<=old["entry_price_surcharge"]
    record={"status":"VIABLE_DEBIT_AND_LITERAL_PLACEMENT_ONLY","baseline":HEAD,"payer_files":PINS,
            "candidate_debit":D_NEW,"candidate_debit_power_interval":limit,
            "old_factor_interval":interval18(factor),"certified_factor_reserve":limit[0]-interval18(factor)[1],
            "old_debit":D_OLD,"frontier":frontier,"candidate_kappa":k,"old_installed_ceiling":OLD_CEILING,
            "gain_reported":k-K_OLD,"gain_over_installed":k-OLD_CEILING,
            "entry_signed":first,"terminal_signed":terminal,"stock":stock,"entry_conversion":prefix,
            "complete_log2_C":complete,"log2_B":ordinary_log,"max_native_height":max(*hs,height),
            "literal_placement":witness["placement"]}
    args.out.write_text(json.dumps(record,default=str,indent=2,sort_keys=True)+"\n")
    signal.alarm(0)


if __name__=="__main__":
    main()
