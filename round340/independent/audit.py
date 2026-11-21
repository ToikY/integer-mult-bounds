# SPDX-License-Identifier: Apache-2.0
"""Independent fixed-shift family exclusion on the measured-mean envelope."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import signal

BIT = "538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749"
MEAN = "41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e"


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def read(path, expected):
    data = path.read_bytes()
    require(sha256(data).hexdigest() == expected, f"source digest for {path.name}")
    return json.loads(data)


def audit(bit, mean):
    h, p, v, q = 2700, 20, 451, F(749, 1000)
    require((mean["p"], mean["h"], mean["uniform_J"], F(mean["mean"])) == (p, 1804, 786, q),
            "preceding result")
    mu = [F(value) for value in mean["moments"]]
    require(len(mu) == p+1 and mu[:2] == [1, q] and all(mu[k] >= q**k for k in range(p+1)),
            "all positive formal moments dominate the Jensen powers")
    # a >= 17/10 and c <= 41/20, proved by cross-multiplying their logarithms.
    require(2**(10*h) >= 11**(v*17) and 134**20 <= 11**41, "integer logarithm bounds")
    lo, hi = F(17,10), F(41,20)
    require(hi > q, "positive derivative of (a+q)/(a+hi)")
    ratio = ((lo+q)/(lo+hi))**p
    eta = F(bit["uniform"]["eta"][1])
    require(ratio > eta, "strict high-half-line obstruction")

    H, end = bit["uniform"]["H"], h-1
    # floor(r).bit_length() is the least J with r<2^J for every r>=1,
    # including r a power of two. Decreasing h increases (1+H/h)^p.
    terminal = (1 + F(H,end))**p
    J = (terminal.numerator//terminal.denominator).bit_length()
    require(2**(J-1) <= terminal < 2**J and J == 774, "strict integer terminal interval")
    H_loss = F(J,H)
    cover = F(1,H*2**44)
    C = F(bit["separation"]["trial"])-H_loss-cover
    rho, seed = (F(bit["cover_and_stock"][k]) for k in ("rho","seed"))
    require(seed < C and 0 < rho < 1, "stage monotonicity")
    # Unrounded stage map z -> rho*z + (1-rho)*C composed seven times.
    cap = (1-rho**7)*C + rho**7*seed
    tick = F(1,10**14)
    upper = cap-7*tick
    grid = (-(-upper//tick)-1)*tick
    require(grid < upper <= grid+tick, "greatest grid point strictly below bound")
    prior = F(mean["candidate_grid_claim"])
    ceiling = F(bit["raw_crossing"][1])-F(mean["uniform_loss"])-7*tick
    require(F(mean["uniform_loss"]) == F(786,H) and prior < grid < ceiling < upper,
            "scope of preceding relaxed-ceiling exclusion")
    return {
        "pins":{"BIT-451.json":BIT,"tensor/MEAN.json":MEAN},
        "power":p, "mean":str(q), "large_h_min":h, "small_h_range":[1,end],
        "height_zero_lower":str(ratio), "capacity_upper":str(eta),
        "high_margin":str(ratio-eta), "minimum_integer_J":J, "high_stage_cap":str(cap),
        "continuous_upper":str(upper), "strict_grid_upper":str(grid),
        "previous_grid_claim":str(prior), "old_relaxed_ceiling":str(ceiling),
        "old_ceiling_minus_grid_upper":str(ceiling-grid), "continuous_surplus":str(upper-ceiling),
        "grid_upper_minus_prior_claim":str(grid-prior),
        "scope":"fixed p20 formal moments, all integer h>=1, current grid and relaxed separation gate",
    }


if __name__ == "__main__":
    signal.alarm(60)
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("bit","mean","out"):
        cli.add_argument(name,type=Path)
    args = cli.parse_args()
    receipt = audit(read(args.bit,BIT),read(args.mean,MEAN))
    with args.out.open("x") as out:
        json.dump(receipt,out,indent=2)
        out.write("\n")
    print("PASS_FIXED_P20_SHIFT_EXCLUSION",receipt["minimum_integer_J"],receipt["strict_grid_upper"])
