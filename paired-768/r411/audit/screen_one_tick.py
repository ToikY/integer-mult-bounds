"""Bound one matched ordinary booking and its dependence on the reserve."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import runpy
import signal

POWER_SHA = "4964fb80e4f2a449decbd35044808b3cc235c44405bfa926f6b12f95e9213c33"


def stop(_signal,_frame):
    raise TimeoutError("One-case directed gate reached the 30-second cap")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("rooted_power_source",type=Path)
    parser.add_argument("roster", type=Path)
    args = parser.parse_args()
    assert __debug__
    assert sha256(args.rooted_power_source.read_bytes()).hexdigest()==POWER_SHA
    signal.signal(signal.SIGALRM,stop)
    signal.alarm(30)
    try:
        proof = runpy.run_path(str(args.rooted_power_source))
        power = proof["rooted_power"]
        raw = args.roster.read_bytes()
        assert sha256(raw).hexdigest() == "93258711e7903b962a2327a8dd4560b6efd8313bfd743f059c3faf59cc8af935"
        roster = json.loads(raw)
        assert roster["head"] == "c20a08dc0a79a989e3515068560d5da371c0a2a8"
        assert Q(roster["pointwise_suffix_upper"]) < Q(186,25)
        targets = {int(k):n for k,n in roster["targets"].items()}
        paid = {int(r):n for r,n in roster["paid"].items()}
        edges = {(x["r"],x["k"]):Q(x["share"]) for x in roster["cells"]}
        assert len(edges) == 24 and sum(targets.values()) == 18906 and sum(paid.values()) == 104652
        assert sum(k*n for k,n in targets.items()) == 286098
        c=Q(4391986206293,2**50)
        t=1-c
        assert all(5*r<=4*k and share>0 for (r,k),share in edges.items())
        assert all(sum(share for (x,k),share in edges.items() if x==r)==1 for r in paid)
        supply={r:n*power(r,t)[1] for r,n in paid.items()}
        capacity={k:n*power(k,t)[0] for k,n in targets.items()}
        assert all(0<sum(supply[r]*share for (r,k),share in edges.items() if k==j)<=v
                   for j,v in capacity.items())

        def matched_fringe(powers):
            intervals = 0
            psi = [Q(0),Q(0)]
            suffix = [Q(0),Q(0)]
            for (r,k),share in edges.items():
                pointwise, pieces = proof["phases"](r,k)
                intervals += pieces
                z=Q(k,r)
                mean=9*(k-r)+t*r/(2*z*4474)
                assert 0<mean<=pointwise and mean<9*k
                for index, v in enumerate(powers(z,c)):
                    psi[index] += paid[r]*share*r*(v-1)/c
                    suffix[index] += paid[r]*share*v/z*mean
            assert psi[0]>1
            return (suffix[0]/(t*psi[1]),suffix[1]/(t*psi[0])), intervals

        fringe, intervals = matched_fringe(power)
        redundant, phases = matched_fringe(proof["series_power"])
        assert phases==intervals and max(fringe[0],redundant[0]) <= min(fringe[1],redundant[1])
        h=4474
        cost=Q(2401,1024)*Q(4097,4096)*Q(1028,1024)
        delta=Q(1,2**128)
        outer=cost/((1-Q(10,h))*(1-delta)**3)
        lower,upper=power(1024*134*h,Q(4391986206293,2**50))
        funded_old=(Q(186,25),1420718)
        proposed_debit=1420717
        # The matched mean is strictly below 9k on each positive edge, versus
        # the former 10k. The funded marginal dominates the summed z^-t.
        proven_fringe_limit=Q(9,10)*funded_old[0]
        old_cover=2*power(2,Q(funded_old[1],2**20)-1)[0]
        cover_lo,cover_hi=(2*x for x in power(2,Q(proposed_debit,2**20)-1))
        old_hi=outer*upper*(1+funded_old[0]/h+delta)
        old_lo=outer*lower*(1+funded_old[0]/h+delta)
        assert fringe[1]<proven_fringe_limit
        new_hi=outer*upper*(1+fringe[1]/h+delta)
        retained_lower=Q(256,255)*outer*lower*(1+delta)
        threshold=h*(cover_lo/(outer*upper)-1-delta)
        assert old_hi<old_cover and old_lo>cover_hi
        assert new_hi<cover_lo<cover_hi<retained_lower
        assert 0<proven_fringe_limit<threshold<funded_old[0]
        print(json.dumps(dict(
            scope="One fixed ordinary factor; uses #8094's reserve treatment and the inherited funded calendar",
            cap_seconds=30,cases=1,floor=h,old_debit=f"{funded_old[1]}/2^20",
            tested_debit=f"{proposed_debit}/2^20",matched_fringe_upper=proven_fringe_limit,
            exact_matched_interval=fringe,phase_intervals=intervals,grade_cells=24,
            sufficient_fringe_threshold=threshold,positive_reserve=cover_lo-new_hi,
            old_expression_shortfall_at_new_tick=old_lo-cover_hi,
            retained_full_reserve_shortfall_even_at_zero_fringe=retained_lower-cover_hi,
            original_book_positive_control=old_cover-old_hi,
        ),indent=2,default=str))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
