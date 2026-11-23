"""Price one 25-bit profile under the exact #8081 recurring cap."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor, isqrt
from pathlib import Path
import signal
import subprocess
import tarfile
from types import SimpleNamespace

PEER = "510113821774bb27f7ddaad4e8b94837a1c2cf52"
PACKAGE = "research/p104-expanded-budget-25bit"
PINS = {
    "RESULT-460.json": "4e173fd0a9f4b593baf706a00899cc1336dae5eab922c43e6551775256733f63",
    "SETUP-PROOF.md": "e7955f69cdfae30a08a120ebc60c803aa2cc11b8a30c06ace6f29ccbba5fae8f",
    "PROOF.md": "835bd553c6a114c5c6f77cb44a9aaab092383d1764715cd877c4cf0ad8f7521c",
    "prepare.py": "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3",
    "retune.py": "ceb036d4e2c375eea74a7d20e2aca5a99f432814d235372dd6ce4bc1adea7a3e",
    "check_setup_expanded.py": "42ef84680d093bb221b05254f534416515314d0c9adb38ea518c6d90549af3e5",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}
PRIOR_RESULT = "f084851c816440c98c9569ed2d9b5e0b758b35c241edaa17706d031b252f46fb"
FACTOR_RECEIPT = "5f3af25d3d1a9975ae43242efecbd2f5cb066d656566e61a1278946a76f72db0"
REFERENCE_INVOICE = "b6847722fbefe668fc7a9cfab50c665b16bbeb8cfe6fbdb14a25944ab8af5978"
PRIOR = "b72d3fa097d2521939f6b8536029da674648d863"
SIGNED = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
C_B, C_G = Q(4391986206293, 2**50), Q(17145637307, 2**42)
D_B, OLD, NEW = Q(11239, 8192), Q(64939, 524288), Q(64934, 524288)
ETA, GUARD = Q(39, 10000), Q(5, 10**18)
ENTRY_H, ENTRY_G, ENTRY_K = (3000, 3080), 1024, Q(".00345")
OLD_H, OLD_G, OLD_K = (8192,38102,604362), 18845936, Q(".00389846")
H, G, K = (8192,38102,604363), 18845934, Q(".003898460000505")
CAP, PAID = 4354317571, K + GUARD


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, key
        result[key] = value
    return result


def load(body):
    return json.loads(body, object_pairs_hook=unique)


def pin(path, expected):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == expected, path
    return data


def power_interval(debit):
    assert 0 < debit < 1 and debit.denominator.bit_count() == 1
    unit = 2**192
    lo = hi = 2 * unit
    a = b = unit
    for bit in range(debit.denominator.bit_length() - 2, -1, -1):
        lo = isqrt(lo * unit)
        hi = isqrt(hi * unit - 1) + 1
        if debit.numerator >> bit & 1:
            a = a * lo // unit
            b = (b * hi + unit - 1) // unit
    return Q(a, unit), Q(b, unit)


def read_archive(bundle, sources, name):
    data = bundle.extractfile(name).read()
    assert sha256(data).hexdigest() == sources[name], name
    return data


def helper(bundle, sources, module, name):
    path = f"research/tiered-native-multiplier/source/{module}.py"
    scope = {"__name__": module}
    exec(compile(read_archive(bundle,sources,path),path,"exec"),scope)
    return scope[name]


def ordinary(heights):
    booked = Q(0)
    for i, h in enumerate(heights, 1):
        admissible = min(ETA, (249 * (C_B-D_B/h) + booked)/250)
        if i == len(heights):
            return admissible
        booked = Q(floor(admissible*10**21)-1,10**21)


def gaussian(h, debit=NEW):
    return C_G - debit/h


def profile_source(args):
    def git(*command):
        return subprocess.check_output(["git","-C",args.peer,*command])

    assert git("rev-parse","HEAD").decode().strip()==PEER and not git("status","--porcelain")
    package = args.peer/PACKAGE
    files = {name:pin(package/name,digest) for name,digest in PINS.items()}
    for name, data in files.items():
        assert data == git("show",f"{PEER}:{PACKAGE}/{name}")
        entry = git("ls-tree",PEER,"--",f"{PACKAGE}/{name}").decode().split()[0]
        assert bool((package/name).stat().st_mode&0o111)==(entry=="100755")
    old = load(files["RESULT-460.json"])
    prior = load(pin(args.reference8078_price,PRIOR_RESULT))
    previous = load(pin(args.gaussian_receipt,FACTOR_RECEIPT))
    invoice = load(pin(args.reference_invoice,REFERENCE_INVOICE))
    assert old["gaussian"]==prior["gaussian"] and old["ordinary_finite_debit"]==str(D_B)
    assert old["gaussian"]["raw_loss"]==str(OLD)
    assert old["ordinary_child_contraction"]=="375/376" and old["ordinary_floor"]==18960
    fields = old["gaussian"]["finite_loss"]
    assert (fields["upper_scale"],fields["upper_divisor"],fields["lower_band"],fields["debit"])==(263772,1724,1874,str(OLD))
    assert previous["peer_head"]==PRIOR and previous["archive_sha256"]==PINS["peer8057.tar.gz"]
    assert (previous["old_debit"],previous["new_debit"],previous["new_period"])==(str(OLD),str(NEW),"257/256")
    manifest = load(files["PEER-SOURCE.json"])
    assert manifest["head"]==SIGNED and manifest["archive_sha256"]==PINS["peer8057.tar.gz"]
    sources = manifest["files_sha256"]
    calendar = "research/frequency-weighted-native-multiplier/typed_transport.py"
    with tarfile.open(package/"peer8057.tar.gz") as bundle:
        statement = read_archive(bundle,sources,calendar)
        assert b"size = (e - 8) * k" in statement and b"period = 4 * ceil(Q(n, 4 * size))" in statement
        assert b"typed_transport.py" not in files["prepare.py"] and b"typed_transport.py" not in files["retune.py"]
        assert sources[calendar] == previous["calendar_sha256"]
        margins = helper(bundle,sources,"outer_budget","margins")
        stock = helper(bundle,sources,"activation","resource_receipt")
        finance = helper(bundle,sources,"outer_clock","financial_checks")
    # These bin inequalities apply to every x=M/(4s), with s bounded by
    # 258 times the existing upper band. The calendar itself is unchanged.
    minimum = Q(263772,4*258)
    factor = Q(257,256)
    assert 255 < minimum < 256 and 256/minimum < factor < 1+1/minimum
    old_interval = tuple(map(Q,invoice["bookings"]["gaussian_factor"]))
    assert old_interval[0]<=Q(fields["upper_factor"])<=old_interval[1]
    replacement = tuple(end*factor/(1+1/minimum) for end in old_interval)
    assert replacement == tuple(map(Q,previous["factor_interval"]))
    allowance,_ = power_interval(NEW)
    _,below = power_interval(NEW-Q(1,524288))
    assert allowance-replacement[1] == Q(previous["reserve"]) > Q(".000000232515772047")
    assert replacement[0]-below == Q(previous["adjacent_deficit"]) > Q(".000001208067461857")
    return old, margins, stock, finance


def old_stopped_upper(peer):
    term = peer["terminal"]
    assert (tuple(term["ordinary_H"]),term["numerical_H"],Q(term["kappa"]))==(OLD_H,OLD_G,OLD_K)
    assert peer["complete_log2_C"]==CAP and peer["max_native_H"]==OLD_G
    assert ordinary(OLD_H)>OLD_K+GUARD
    assert Q(term["gaussian_rate"])==gaussian(OLD_G,OLD)
    assert gaussian(OLD_G-1,OLD)<OLD_K+GUARD<gaussian(OLD_G,OLD)
    # At any smaller sum, even the relaxed ordinary funding fails. The
    # Gaussian and ordinary required minima then exactly saturate the cap.
    smaller = sum(OLD_H)-1
    root = Q(6324555320336758663997787088865437067439,10**41)
    weight1 = Q(1,62500)
    assert root**2 < Q(1,250) < (root+Q(1,10**41))**2
    assert weight1/(8192**2) < (1+root)**2/(smaller-8192)**2
    loss = weight1/8192+(1+root)**2/(smaller-8192)
    relaxed = C_B*(1-Q(1,250**3))-Q(249,250)*D_B*loss
    assert relaxed < OLD_K+GUARD
    assert 1731+320*sum(OLD_H)+220*OLD_G==CAP
    return gaussian(OLD_G,OLD)-GUARD


def exact_setup(peer):
    heights = (*ENTRY_H,ENTRY_G,*H,G)
    assert len(heights)==7 and all(1024<=h<2**25 for h in heights)
    assert max(heights)==G<peer["max_native_H"]
    assert 92*(2**25-1)<2**32 and 1024*(2**25-1)+3<2**35
    stop_denominator = GUARD.denominator*5
    assert 0<stop_denominator and all(
        value.bit_length()<=128 for rate in (ENTRY_K,K,ETA)
        for value in (rate.numerator,rate.denominator,stop_denominator)
    )
    counted_steps = 2*2048*(2**25+1)+7*2**24
    assert counted_steps==137556398080<2**40
    w,n = 2**38,2**68+2**40
    datum = 2*w+2
    lookup = 8*(4*w*n)*512*128
    local = 2**16*(datum+4)*(7*datum+9)+8*2**16*(datum+4)**2
    full = (n+1)*(lookup+local+2**120)*2**32
    assert full==peer["native_setup_transition_upper"]<2**228
    return full


def price(args):
    peer, margins, resource, finance = profile_source(args)
    old_upper = old_stopped_upper(peer)
    assert OLD_K < old_upper < K < gaussian(G) - GUARD
    assert gaussian(G)-GUARD < K+Q(1,10**15)
    assert gaussian(G,OLD)<PAID and ordinary(OLD_H)<PAID<ordinary(H)
    assert H[:2]==OLD_H[:2] and H[2]==OLD_H[2]+1 and G==OLD_G-2
    assert 1731+320*sum(H)+220*(G+1)>CAP

    signed = {}
    for label, kapp, coordinates, g in [
        ("entry",ENTRY_K,ENTRY_H,ENTRY_G),("terminal",K,H,G),
    ]:
        paid = kapp+GUARD
        strict,functional,margin = margins(kapp,GUARD/5,paid,gaussian(g))
        assert len(strict)==54 and len(functional)==4 and min(*strict,*functional,margin)>0
        assert ordinary(coordinates)>paid
        stock = resource(SimpleNamespace(rank_logs=coordinates,complex_log=g,eta=ETA))
        assert all(cut+2<h for cut,h in zip(stock["binary_cuts"],coordinates[1:]))
        signed[label]={"stock":stock,"strict":54,"functional":4,"minimum_strict":str(min(strict)),
                       "minimum_functional":str(min(functional)),"paid_margin":str(margin)}
    late = signed["terminal"]["stock"]
    exponent = late["public_exponent_A"]
    assert (exponent,late["first_public_offset"])==(19497093,4)
    assert late["binary_cuts"]==[8290,46456,650883]
    assert late["retimed_first_stripe_margin"]>1024 and late["retimed_all_size_margin_floor"]>1024
    assert peer["terminal"]["stock"]==resource(SimpleNamespace(rank_logs=OLD_H,complex_log=OLD_G,eta=ETA))
    finite = 1+finance()["early_log2_C_bound"]
    assert finite==84500001
    entry = max(finite,1602+220*ENTRY_G+40+17+16384*sum(ENTRY_H)+25818582)
    premium = ceil((K-ENTRY_K)*exponent)
    terminal_B = 128+320*sum(H)
    price = 1+max(entry+premium,finite,1602+220*G+terminal_B)
    assert (entry,premium,terminal_B,price)==(125660241,8744,208210368,4354317451)
    assert price==CAP-120 and 17**16*10**(21*16)<2**1182
    fixed = exact_setup(peer)
    print(json.dumps({
        "scope":"exact one-case feasibility; full scientific 25-bit replay still required",
        "peer_head":PEER,"exact_prior_upper":str(old_upper),"exact_kappa":str(K),
        "decimal_kappa":"0.003898460000505","exact_gain":str(K-OLD_K),
        "exact_percent_gain":str(100*(K-OLD_K)/OLD_K),"prior_bound_gap":str(K-old_upper),
        "gaussian_stopped_upper":str(gaussian(G)-GUARD),
        "ordinary_heights":H,"gaussian_height":G,"complete_log2_C":price,"whole_cap":CAP,
        "max_native_height":G,"native_height_bits":G.bit_length(),
        "entry_log2_C":entry,"entry_conversion":premium,"terminal_log2_B":terminal_B,
        "gaussian_debit":str(NEW),"gaussian_period":"257/256","ordinary_debit":str(D_B),
        "setup_transition_upper":fixed,"expanded_added_indexed_actions":2**40,
        "signed":signed,"cases":1,"max_seconds":30,
    },indent=2,sort_keys=True))


def timeout(_sig,_frame):
    raise TimeoutError("One fixed 25-bit price case hit the 30-second cap")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("peer","reference8078-price","gaussian-receipt","reference-invoice"):
        parser.add_argument("--"+option,type=Path,required=True)
    args = parser.parse_args()
    assert __debug__
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(30)
    try:
        price(args)
    except TimeoutError as error:
        parser.exit(124,str(error)+"\n")
    finally:
        signal.alarm(0)


if __name__=="__main__":
    main()
