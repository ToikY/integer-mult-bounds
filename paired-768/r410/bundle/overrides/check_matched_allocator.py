"""Bind the matched offset-eight price to the actual installed paid calendar."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
GRADES_SHA = "1aadcc6753aa20eb39bf28608ed54c71035f308312349e31f608d5cc05edc7e0"
TYPED_SHA = "cc015f155ce80f751656547f7937631df3cbd36e948f83c5e17924f3d3e6c520"
MARGIN = Q(50803612971593099397385261823, 24054211488961849122338563785759685737032)
MIN_SHARE = Q(13201304847172927608845459442008190307185393429462992684270298788700245,
              446899527904170582754959784023300718037811994769910427909046367785638460030016)


def digest(rows):
    canonical = [[list(map(str, key)), str(value)] for key, value in sorted(rows.items())]
    return sha256(json.dumps(canonical, separators=(",", ":")).encode()).hexdigest()


def paid_edges(recipe, intervals):
    sources = recipe.types()
    weights = [part.multiplicity for part in sources]
    paid = [Counter(part.paid) for part in sources]
    targets = [Counter(part.targets) for part in sources]
    assert weights == [5, 451]
    assert [sum(counts.values()) for counts in paid] == [282576, 281568]
    assert [sum(counts.values()) for counts in targets] == [52608, 52608]
    paid_counts = Counter()
    target_counts = Counter()
    for i, w in enumerate(weights):
        paid_counts.update({r:w*n for r,n in paid[i].items()})
        target_counts.update({k:w*n for k,n in targets[i].items()})
    assert paid_counts == recipe.paid.histogram and target_counts == recipe.targets.histogram
    assert sum(paid_counts.values()) == 128400048 and sum(target_counts.values()) == 23989248
    assert sum(k*n for k,n in target_counts.items()) == 677246016

    grade, actual = recipe.cells, recipe.typed_cells()
    assert len(grade) == 51 and len(actual) == 88 and grade[112,258] == 1
    assert digest(grade) == GRADES_SHA and digest(actual) == TYPED_SHA
    supply = {r:n*intervals(r,1-recipe.trial)[1] for r,n in paid_counts.items()}
    demand = {k:n*intervals(k,1-recipe.trial)[0] for k,n in target_counts.items()}
    scale = Q(sum(supply.values()), sum(demand.values()))
    assert 1-scale == MARGIN
    assert all(sum(share for (p,_),share in grade.items() if p==r)==1 for r in paid_counts)
    assert all(sum(supply[r]*share for (r,z),share in grade.items() if z==k)==value*scale
               for k,value in demand.items())

    independently_typed = {}
    weighted_edges, rows, loads = Counter(), Counter(), Counter()
    for (r,k), share in grade.items():
        assert share > 0 and 5*r <= 4*k
        for a,b in product(range(2), repeat=2):
            if r in paid[a] and k in targets[b]:
                paired = share * weights[b] * targets[b][k] / target_counts[k]
                origin = weights[a]*paid[a][r]
                independently_typed[a,r,b,k] = paired
                weighted_edges[r,k] += origin*paired
                rows[a,r] += paired
                loads[b,k] += Q(supply[r]*origin, paid_counts[r])*paired/targets[b][k]
    assert independently_typed == actual
    assert min(v/targets[b][k] for (_,_,b,k),v in actual.items()) == MIN_SHARE
    assert set(rows) == {(a,r) for a,counts in enumerate(paid) for r in counts}
    assert all(value==1 for value in rows.values())
    assert set(loads) == {(b,k) for b,counts in enumerate(targets) for k in counts}
    assert all(0 < value <= Q(weights[b]*demand[k], target_counts[k])
               for (b,k),value in loads.items())
    assert weighted_edges == {key:paid_counts[key[0]]*value for key,value in grade.items()}
    return weighted_edges


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    args = parser.parse_args()
    assert __debug__
    sys.path[:0] = [str(args.runtime.resolve()),str(HERE)]
    from upstream import install
    install()
    from grades import numerical_recipe, LOWER, UPPER_DIVISOR
    from installations import TERMINAL
    from matched_price_support import CG, D1, factor, rooted_power, series_power
    from positive_debit import certify_loss
    from unpowered_price import intervals

    assert (TERMINAL.kappa, TERMINAL.rank_logs, TERMINAL.complex_log) == (
        Q(".003898460003746"),(8192,38102,604363),18531230)
    recipe = numerical_recipe(TERMINAL.complex_log)
    assert (recipe.trial, recipe.ambient, LOWER, UPPER_DIVISOR) == (CG,306,1874,1724)
    edges = paid_edges(recipe,intervals)
    root = factor(edges,rooted_power)
    series = factor(edges,series_power)
    assert max(root["factor"][0],series["factor"][0]) <= min(root["factor"][1],series["factor"][1])
    installed = certify_loss(recipe,LOWER)
    assert Q(installed["debit"]) == D1
    assert Q(installed["exterior_period_factor"]) == Q(22067,21981)
    assert root["factor"][0] <= Q(installed["upper_factor"]) < root["covering"][0]
    print("PASS_MATCHED_LIVE_ALLOCATOR", json.dumps({
        "grade_cells":51, "typed_cells":88, "phase_intervals":root["phase_intervals"],
        "debit":str(D1), "factor_reserve":str(root["positive_reserve"]),
        "adjacent_shortfall":str(root["adjacent_shortfall"]),
        "grade_sha256":GRADES_SHA,"typed_sha256":TYPED_SHA,
    }), flush=True)


if __name__ == "__main__":
    main()
