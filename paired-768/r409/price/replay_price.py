"""Reconstruct one matched-suffix price from authenticated signed receipts."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import product
from math import ceil, floor, isqrt
from pathlib import Path
from subprocess import check_output
from types import SimpleNamespace
import json
import runpy
import signal
import tarfile

HERE = Path(__file__).resolve().parent
HEAD = "aea1699415250d865f7a635f4df0b76f406c47b4"
PACKAGE = "research/p104-period-debit-25bit"
PINS = {
    "R368-RANK-RECEIPT.json": "d26a1f9ea8fd78900f45bf83c29ee2b700d015c231a82eab1cad54283b4aec66",
    "replay_grade_cut.py": "5b7eb70b4258de852a64045a7875fd79d1240ab6119e4c1d11ec8bdcea2f9daf",
    "prepared_native_gate.py": "4c6514ff6143b573ff27e97d7fc96f2bc5d0129a884f7ae80afc4cd5cda387f2",
    "PEER-INTEGRAL.md": "79f4d93bf8b39510c29c8648164c31e6fd730b72b20f5e807cfbd78cdf465683",
    "peer_weighted_suffix.py": "880bbfc11428cadc438722eb9d058f43e06f8990e81214fa20c27ebb628390c8",
    "RESULT-460.json": "8c8b7cebbdea179329d225d828f31e37e2fddfcfd177750803ae81e39726def8",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}
SOURCE = {
    "research/tiered-native-multiplier/source/activation.py": "6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b",
    "research/tiered-native-multiplier/source/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "research/tiered-native-multiplier/source/outer_clock.py": "63363c3da673365f3ac5e1b7e318c6938005f1e9c9896799504cc598efbf96fa",
    "research/frequency-weighted-native-multiplier/typed_transport.py": "b76b9ad3dc0dd91473026c079585f830387eaa3c34c25a7820ee5057d5cbf941",
}
CG = Q(17145637307, 2**42)
CB = Q(4391986206293, 2**50)
DB = Q(11239, 8192)
D0, D1 = Q(64934, 524288), Q(130699669, 2**30)
GUARD, ETA = Q(5, 10**18), Q(39, 10000)
L, SCALE, DELTA = 1874, 263772, Q(1, 2**128)
GRID = 1 << 208


def authenticate(data, digest):
    assert sha256(data).hexdigest() == digest
    return data


def bind_baseline(root):
    assert check_output(["git", "-C", root, "rev-parse", "HEAD"]).decode().strip() == HEAD
    assert not check_output(["git", "-C", root, "status", "--porcelain"])
    folder = root/PACKAGE
    assert json.loads(authenticate((folder/"RESULT-460.json").read_bytes(),
                                    PINS["RESULT-460.json"]))["complete_log2_C"] == 4354317451
    for name in PINS:
        if name not in ("RESULT-460.json", "peer8057.tar.gz"):
            authenticate((HERE/name).read_bytes(), PINS[name])
    authenticate((folder/"peer8057.tar.gz").read_bytes(), PINS["peer8057.tar.gz"])
    modules = {}
    with tarfile.open(folder/"peer8057.tar.gz", "r:gz") as archive:
        for name, digest in SOURCE.items():
            data = authenticate(archive.extractfile(name).read(), digest)
            if not name.endswith("typed_transport.py"):
                namespace = {"__name__": "__signed_source__"}
                exec(compile(data, name, "exec"), namespace)
                modules.update(namespace)
            else:
                for link in (b"size = (e - 8) * k", b"4 * ceil(Q(n, 4 * size))",
                             b"share / len(owners)", b"measure.mass(left_end, right_end)[0]"):
                    assert link in data
    return json.loads((folder/"RESULT-460.json").read_bytes()), modules


def restore_weighted_census(source, stamped):
    target = stamped["unmix"](source["source_targets"])
    paid = stamped["unmix"](source["source_paid"])
    split = paid.copy()
    split[1] -= 1008
    split[Q(1, 2)] = 2016
    targets = (target, {2*r:n for r,n in target.items()})
    payers = (split, {2*r:n for r,n in paid.items()})
    assert [sum(t.values()) for t in targets] == [52608, 52608]
    assert [sum(p.values()) for p in payers] == [282576, 281568]
    return targets, payers, stamped["weighted"](target), stamped["weighted"](paid, 1008)


def allocation(signed, stamped, source):
    targets, payers, target, paid = restore_weighted_census(source, stamped)
    invoice = signed["gaussian"]
    mass = stamped["mass"]
    supply = mass(paid, 1)
    demand = mass(target, 0)
    amount, all_capacity = sum(supply.values()), sum(demand.values())
    assert Q(invoice["directed_margin"]) == 1 - Q(amount, all_capacity) > 0
    assert max(target) == 258 and sum(k*n for k,n in target.items()) == 677246016
    assert sum(paid.values()) == invoice["weighted_loans"] == 128400048
    assert sum(target.values()) == invoice["weighted_targets"] == 23989248
    capacity = {k: Q(value*amount, all_capacity) for k, value in demand.items()}
    remaining = capacity.copy()
    rows = {}
    for r, k in product(sorted(supply, reverse=True), sorted(capacity, reverse=True)):
        if not rows.get(r):
            rows[r] = [supply[r], {}]
        unpaid, shares = rows[r]
        if unpaid and 5*r <= 4*k and remaining[k]:
            funded = min(unpaid, remaining[k])
            rows[r][0] -= funded
            remaining[k] -= funded
            shares[k] = Q(funded, supply[r])
    assert not any(remaining.values()) and not any(row[0] for row in rows.values())
    grade = {(r,k): share for r, (_, shares) in rows.items() for k,share in shares.items()}
    assert len(grade) == invoice["grade_cells"] == 51 and grade[112,258] == 1
    assert all(sum(shares.values()) == 1 for _, shares in rows.values())
    assert all(sum(supply[r]*q for (r,z),q in grade.items() if z == k) == v
               for k,v in capacity.items())

    weights = [5, 451]
    typed = {}
    directed_typed_load = Counter()
    typed_rows = Counter()
    weighted_edges = Counter()
    for (r,k), q in grade.items():
        for a,b in product(range(2), repeat=2):
            if r in payers[a] and k in targets[b]:
                weight = weights[a] * payers[a][r]
                share = q * weights[b] * targets[b][k] / target[k]
                directed_typed_load[b,k] += Q(supply[r]*weight, paid[r])*share/targets[b][k]
                typed[a,r,b,k] = share
                typed_rows[a,r] += share
                weighted_edges[r,k] += weight*share
    assert len(typed) == invoice["typed_cells"] == 88
    assert min(v/targets[b][k] for (_,_,b,k),v in typed.items()) == Q(invoice["min_individual_share"])
    assert set(typed_rows) == {(a,r) for a, census in enumerate(payers) for r in census}
    assert all(value == 1 for value in typed_rows.values())
    assert all(0 < value <= Q(weights[b]*demand[k], target[k])
               for (b,k), value in directed_typed_load.items())
    assert weighted_edges == {key: paid[key[0]]*value for key, value in grade.items()}
    return weighted_edges, grade, typed


@cache
def rooted_power(base, exponent):
    """Evaluate a nonnegative dyadic power on an independent positive grid."""
    base = Q(base)
    assert base >= 1 and 0 < exponent < 1 and exponent.denominator.bit_count() == 1
    lower, upper = floor(base*GRID), ceil(base*GRID)
    lo = hi = GRID
    for bit in range(exponent.denominator.bit_length()-2, -1, -1):
        lower = isqrt(lower*GRID)
        upper = 1 + isqrt(upper*GRID-1)
        if exponent.numerator >> bit & 1:
            lo = lo*lower//GRID
            hi = -(-hi*upper//GRID)
    return Q(lo,GRID), Q(hi,GRID)


def factor(edges, gate, power):
    t = 1 - CG
    phase_intervals = 0
    psi, matched = [Q(0), Q(0)], [Q(0), Q(0)]
    gate["finite_boundaries"]()
    for (r,k), coefficient in edges.items():
        pointwise, count = gate["phases"](r,k)
        phase_intervals += count
        z = k/r
        average_upper = 9*(k-r) + t*r/(2*z*L)
        assert 0 < average_upper <= pointwise
        for i,end in enumerate(power(z,CG)):
            psi[i] += coefficient*r*(end-1)/CG
            matched[i] += coefficient*end/z*average_upper
    assert phase_intervals == 1971 and psi[0] > 1
    exterior = 1+Q(1032,SCALE)
    constant = (1+DELTA)*exterior/(1-DELTA)**4
    x = power(SCALE*L,CG)
    fringe = [matched[i]/(t*psi[1-i]) for i in range(2)]
    bounds = [constant*x[i]*(1+fringe[i]/L+DELTA) for i in range(2)]
    covering = power(2,D1)
    reserve = covering[0]-bounds[1]
    adjacent = bounds[0]-power(2,D1-Q(1,2**30))[1]
    coarse = [constant*x[i]*(1+10*677246016/(t*psi[1-i]*L)+DELTA) for i in range(2)]
    known_good = power(2,D0)[0] - coarse[1]*Q(257,256)/exterior
    assert reserve > 0 and adjacent > 0
    assert coarse[0] > covering[1] and known_good > 0
    return dict(psi=psi, phase_intervals=phase_intervals, fringe=fringe, factor=bounds,
                covering=covering, positive_reserve=reserve, adjacent_shortfall=adjacent,
                old_pointwise_shortfall_at_new_booking=coarse[0]-covering[1],
                predecessor_approved_booking_reserve=known_good, exterior_factor=exterior)


def projected_invoice(result, modules, gate):
    shape = (8192,38102,604363)
    old, new = Q(result["terminal"]["kappa"]), Q(".003898460003746")
    upper = gate["ordinary"](shape)-GUARD
    root = Q(6324555320336758663997787088865437067439,10**41)
    assert root**2 < Q(1,250) < (root+Q(1,10**41))**2
    cost = result["complete_log2_C"]
    lower_sum = 650656
    assert Q(1,62500*8192**2) < (1+root)**2/(lower_sum-1-8192)**2
    bound = CB*(1-Q(1,250**3))-Q(249,250)*DB*(Q(1,62500*8192)+(1+root)**2/(lower_sum-1-8192))
    assert bound < old+GUARD
    prior_max = (cost-1731-320*lower_sum)//220
    stopped = CG-D0/prior_max-GUARD
    h = floor(D1/(CG-new-GUARD))+1
    assert h == 18531230 and prior_max == 18845935 and old < stopped < new < upper
    assert CG-D1/(h-1) <= new+GUARD < CG-D1/h
    tiers = {}
    for name, rate, dims, gaussian in (("entry",Q(".00345"),(3000,3080),1024),("terminal",new,shape,h)):
        options = modules["margins"](rate, GUARD/5, rate+GUARD, CG-D1/gaussian)
        strict, functional, limit = options
        assert len(strict) == 54 and len(functional) == 4 and min(*strict,*functional,limit) > 0
        stock = modules["resource_receipt"](SimpleNamespace(rank_logs=dims,complex_log=gaussian,eta=ETA))
        tiers[name] = dict(minimum_outer_margin=min(*strict,*functional,limit), stock=stock)
    first = tiers["terminal"]["stock"]["public_exponent_A"]
    conversion = ceil((new-Q(".00345"))*first)
    finite = 1 + modules["financial_checks"]()["early_log2_C_bound"]
    entry = max(finite, 1602+220*1024+40+17+16384*(3000+3080)+25818582)
    full = 1 + max(entry + conversion, finite, 1730+320*sum(shape)+220*h)
    assert (first,conversion,finite,full) == (19182389,8603,84500001,4285082571)
    assert max(*shape,h) < 2**25 and 92*h < 2**32 and 1024*h+3 < 2**35
    assert 2*2048*(2**25+1)+7*2**24 < 2**40
    assert all(x.bit_length() <= 128 for x in (new.numerator,new.denominator,10**18))
    jobs, width = 2**68 + 2**40, 2**38
    scalar_size = 2*width+2
    lookup = 8*(4*width*jobs)*512*128
    arithmetic = 2**16*(scalar_size+4)*(7*scalar_size+9) + 8*2**16*(scalar_size+4)**2
    setup = (jobs+1)*(lookup+arithmetic+2**120)*2**32
    assert setup == result["native_setup_transition_upper"] < 2**228
    return dict(projected_kappa=new, benchmark_kappa=old, exact_delta=new-old,
                comparator_stopped_upper=stopped, stopped_separation=new-stopped, ordinary_ceiling=upper,
                paid_gaussian_margin=CG-D1/h-new-GUARD, native_heights=shape, gaussian_height=h,
                complete_log2_C=full, log2_C_saving=cost-full, entry_conversion=conversion,
                setup_transition_bound=setup, fixed_extra_indexed_actions=2**40, tiers=tiers)


def timeout(_signal, _frame):
    raise TimeoutError("The one-case price check reached its wall cap")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    args = parser.parse_args()
    assert __debug__
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    try:
        signed, modules = bind_baseline(args.baseline.resolve())
        gate = runpy.run_path(str(HERE/"prepared_native_gate.py"))
        stamped = runpy.run_path(str(HERE/"replay_grade_cut.py"))
        source = json.loads((HERE/"R368-RANK-RECEIPT.json").read_bytes())
        weighted, grade, typed = allocation(signed,stamped,source)
        independent = factor(weighted,gate,rooted_power)
        repeated = factor(weighted,gate,gate["power"])
        lo,hi = independent["factor"]
        other_lo,other_hi = repeated["factor"]
        assert max(lo,other_lo) <= min(hi,other_hi)
        rows = [[list(map(str,key)),str(v)] for key,v in sorted(grade.items())]
        signs = [[list(map(str,key)),str(v)] for key,v in sorted(typed.items())]
        invoice = projected_invoice(signed,modules,gate)
        print(json.dumps(dict(scope="One exact projected price. No literal profile or signed application executed",
                              baseline=HEAD, guide_proof=gate["SUFFIX_HEAD"], cases=1,
                              wall_seconds_cap=30, debit=D1, grade_rows=rows, typed_rows=signs,
                              directed_rooted=independent, independent_log_series=repeated,
                              complete_projected_invoice=invoice), indent=2, default=str))
    except TimeoutError as exc:
        parser.exit(124, f"{exc}\n")
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
