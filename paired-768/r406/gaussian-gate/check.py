"""One priced exterior-period proof for the exact expanded-budget parent."""
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

HEAD = "b72d3fa097d2521939f6b8536029da674648d863"
PACKAGE = "research/p104-expanded-budget-signed"
PEER_FILES = {
    "RESULT-340.json": "f084851c816440c98c9569ed2d9b5e0b758b35c241edaa17706d031b252f46fb",
    "PROOF.md": "8ab735119478f371c5a4b097687832eed6a14b91f9ac0cb6b1a1e416333d47c5",
    "prepare.py": "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3",
    "verify.py": "e5e6523788692376f53176bfebbd6f53eb34c9e83d6f2c860f566632ccf3cac8",
    "retune.py": "0c99c31fc2b3dfea52a7dbf0d636e22b339ed8be81de6b6418333eb46f1e836e",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
}
INVOICE = "b6847722fbefe668fc7a9cfab50c665b16bbeb8cfe6fbdb14a25944ab8af5978"
PREVIOUS = "e37781c0ffcda49b6adc31501cf062d3bbcb6344765440183e96b2572c65411b"
ENTRY_H, ENTRY_G, ENTRY_K = (3000, 3080), 1024, Q(".00345")
H, G, K = (8192, 36400, 575525), 978582, Q(".0038983400039")
OLD, NEW, ORDINARY = Q(64939, 524288), Q(64934, 524288), Q(11239, 8192)
C_B, C_G, GUARD, ETA = Q(4391986206293, 2**50), Q(17145637307, 2**42), Q(5, 10**18), Q(39, 10000)


def pinned(path, expected):
    body = path.read_bytes()
    assert sha256(body).hexdigest() == expected, path.name
    return body


def unique(pairs):
    data = {}
    for key, value in pairs:
        assert key not in data
        data[key] = value
    return data


def load(body):
    return json.loads(body, object_pairs_hook=unique)


def power_interval(debit):
    assert 0 < debit < 1 and debit.denominator.bit_count() == 1
    unit = 2**192
    low = high = 2 * unit
    left = right = unit
    for bit in range(debit.denominator.bit_length() - 2, -1, -1):
        low = isqrt(low * unit)
        high = isqrt(high * unit - 1) + 1
        if debit.numerator >> bit & 1:
            left = left * low // unit
            right = -(-right * high // unit)
    return Q(left, unit), Q(right, unit)


def ordinary(heights):
    prior = Q(0)
    for index, height in enumerate(heights):
        limit = min(ETA, (249 * (C_B - ORDINARY / height) + prior) / 250)
        if index + 1 == len(heights):
            return limit
        prior = Q(floor(limit * 10**21) - 1, 10**21)


def archive_member(bundle, sources, name):
    body = bundle.extractfile(name).read()
    assert sha256(body).hexdigest() == sources[name]
    return body


def function(bundle, sources, module, name):
    path = f"research/tiered-native-multiplier/source/{module}.py"
    ns = {"__name__": module}
    exec(compile(archive_member(bundle, sources, path), path, "exec"), ns)
    return ns[name]


def main(args):
    def git(*command):
        return subprocess.check_output(["git", "-C", args.peer, *command])

    assert git("rev-parse", "HEAD").decode().strip() == HEAD
    assert not git("status", "--porcelain")
    package = args.peer / PACKAGE
    paths = {name: pinned(package / name, digest) for name, digest in PEER_FILES.items()}
    assert all(body == git("show", f"{HEAD}:{PACKAGE}/{name}") for name, body in paths.items())
    peer = load(paths["RESULT-340.json"])
    previous = load(pinned(args.prior_installed, PREVIOUS))
    invoice = load(pinned(args.prior_invoice, INVOICE))
    assert peer["gaussian"] == previous["gaussian"]
    terminal_peer = peer["terminal"]
    assert (terminal_peer["ordinary_H"], terminal_peer["numerical_H"]) == ([8192, 36220, 575705], G)
    assert peer["ordinary_finite_debit"] == str(ORDINARY) and peer["complete_log2_C"] == 413727211
    assert peer["max_native_H"] == G and peer["log2_fixed_setup_upper"] == 228
    assert peer["native_setup_transition_upper"] < 2**228
    terms = peer["gaussian"]["finite_loss"]
    assert [terms[key] for key in ("upper_scale", "upper_divisor", "lower_band", "debit")] == [
        263772, 1724, 1874, str(OLD)
    ]
    sources = load(paths["PEER-SOURCE.json"])["files_sha256"]
    with tarfile.open(package / "peer8057.tar.gz") as bundle:
        calendar = "research/frequency-weighted-native-multiplier/typed_transport.py"
        raw = archive_member(bundle, sources, calendar)
        assert b"size = (e - 8) * k" in raw and b"period = 4 * ceil(Q(n, 4 * size))" in raw
        assert b"typed_transport.py" not in paths["prepare.py"] and b"typed_transport.py" not in paths["retune.py"]
        margins = function(bundle, sources, "outer_budget", "margins")
        resources = function(bundle, sources, "activation", "resource_receipt")
        finite = 1 + function(bundle, sources, "outer_clock", "financial_checks")()["early_log2_C_bound"]

    # x=M/(4s'), where every physical exterior size s'=(e-8)k<=258U.
    x_min, period = Q(263772, 4*258), Q(257, 256)
    assert 255 < x_min < 256
    assert Q(256, 1) / x_min < period < 1 + 1/x_min
    # For x<=256: ceil(x)/x<=256/x_min.
    # For x>256: m=ceil(x)-1>=256 and ceil(x)/x<(m+1)/m<=257/256.
    inherited = tuple(map(Q, invoice["bookings"]["gaussian_factor"]))
    assert inherited[0] <= Q(terms["upper_factor"]) <= inherited[1]
    factor = tuple(end * period / (1 + 1/x_min) for end in inherited)
    allowance, _ = power_interval(NEW)
    _, adjacent = power_interval(NEW - Q(1, 524288))
    assert allowance - factor[1] > Q("0.000000232515772047")
    assert factor[0] - adjacent > Q("0.000001208067461857")

    old_rate = Q(terminal_peer["kappa"])
    old_ceiling = C_G - OLD/G - GUARD
    assert Q(terminal_peer["gaussian_rate"]) == old_ceiling + GUARD
    assert old_rate < old_ceiling < K
    assert ordinary(tuple(terminal_peer["ordinary_H"])) < K + GUARD
    needed = OLD - G*(C_G - K - GUARD)
    assert Q(1,524288) < needed < Q(2,524288) < OLD-NEW
    assert sum(H) == sum(terminal_peer["ordinary_H"]) and min(H) >= 8192
    assert max(*H,G) == G and all(v.bit_length() <= 20 for v in (*H, G, *ENTRY_H, ENTRY_G))
    assert len(H) + len(ENTRY_H) + 2 == 7

    checks = {}
    for label, heights, height, rate in (("entry", ENTRY_H, ENTRY_G, ENTRY_K), ("terminal", H, G, K)):
        gaussian_rate = C_G - NEW/height
        assert ordinary(heights) > rate + GUARD and gaussian_rate > rate + GUARD
        strict, functional, paid = margins(rate, GUARD/5, rate+GUARD, gaussian_rate)
        assert len(strict)==54 and len(functional)==4 and min(*strict,*functional,paid)>0
        stock = resources(SimpleNamespace(rank_logs=heights, complex_log=height, eta=ETA))
        assert all(x+2 < h for x,h in zip(stock["binary_cuts"],heights[1:]))
        checks[label] = dict(stock=stock, gaussian_slack=str(gaussian_rate-rate-GUARD),
                             ordinary_slack=str(ordinary(heights)-rate-GUARD), signed=[54,4])
    entry = max(finite,1602 + 220*ENTRY_G + 125433359)
    premium = ceil((K-ENTRY_K) * checks["terminal"]["stock"]["public_exponent_A"])
    terminal_ordinary = 128 + 320*sum(H)
    terminal = max(finite,1602 + 220*G + terminal_ordinary)
    cost = 1+max(entry+premium,terminal)
    assert cost==413727211 and entry==125660241 and terminal_ordinary==198437568
    funding = (ceil(ORDINARY/(C_B-K-GUARD)),ceil(NEW/(C_G-K-GUARD)))
    print(json.dumps({
        "status":"ONE_PERIOD_PROFILE_PRICE_PASSED", "peer_head":HEAD,
        "calendar_sha256":sources[calendar], "archive_sha256":PEER_FILES["peer8057.tar.gz"],
        "resource":{"C_log2":cost,"max_native_height":G,"entry_conversion":premium,
                    "fixed_setup_log2":228,"terminal_ordinary_log2":terminal_ordinary,"funding_floors":funding},
        "old_period":str(1+1/x_min), "new_period":str(period),
        "factor_interval":[str(x) for x in factor], "old_debit":str(OLD), "new_debit":str(NEW),
        "reserve":str(allowance-factor[1]), "adjacent_deficit":str(factor[0]-adjacent),
        "minimum_strict_debit_reduction":str(needed),
        "candidate":{"ordinary":H,"gaussian":G,"kappa":str(K),"checks":checks},
        "exact_peer_gaussian_cap":str(old_ceiling),
        "gain_over_reported_peer":str(K-old_rate),"gain_over_peer_gaussian_cap":str(K-old_ceiling),
        "percent_over_peer":str(100*(K-old_rate)/old_rate),
        "excluded":["old debit at fixed max Gaussian height","unchanged ordinary shape at new rate",
                    "next lower grid debit under this factor envelope"],
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--peer",required=True,type=Path)
    parser.add_argument("--prior-installed",required=True,type=Path)
    parser.add_argument("--prior-invoice",required=True,type=Path)
    if not __debug__:
        parser.error("Run with assertions enabled")
    def timeout(*unused):
        raise TimeoutError("The one-profile price reached its 30 second cap")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(30)
    try:
        main(parser.parse_args())
    except TimeoutError as error:
        parser.exit(124,f"{error}\n")
    finally:
        signal.alarm(0)
