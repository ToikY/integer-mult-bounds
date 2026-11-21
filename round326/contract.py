"""Price a common rational frame for both ends of a paid internal crossing."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

PIN = "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
KAPPA = "0.003879928046155"


@cache
def price(rank):
    if rank == 1:
        return Fraction(1), Fraction(1)
    with localcontext() as ctx:
        ctx.prec = 60
        # Decimal.ln and exp round correctly to nearest. Widen each endpoint
        # after each rounded operation; all intermediate factors are positive.
        log = Decimal(rank).ln()
        power = 1 - Decimal(KAPPA)
        lo = (power * log.next_minus()).next_minus().exp().next_minus()
        hi = (power * log.next_plus()).next_plus().exp().next_plus()
        return Fraction(lo), Fraction(hi)


def rank(rows):
    basis = {}
    for row in rows:
        v = list(row)
        for i in sorted(basis):
            coefficient = v[i]
            if coefficient:
                v = [x-coefficient*y for x,y in zip(v,basis[i])]
        i = next((i for i,x in enumerate(v) if x),None)
        if i is not None:
            scale = v[i]
            basis[i] = tuple(x/scale for x in v)
    return len(basis)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("word",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--skip-pairs",type=int,default=0,help="number of previously visited ranked pairs")
    parser.add_argument("--price-first",action="store_true",
                        help="omit frame solving when the exact upper price bound is nonpositive")
    args = parser.parse_args()
    start = monotonic()
    raw = args.word.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    w = json.loads(gzip.decompress(raw))
    charts = {int(c): frame for c,frame in w["frames"].items()}
    dim = {c: frame["dim"] for c,frame in charts.items()}
    body = {c:[tuple(map(Fraction,r)) for r in frame["B"]] for c,frame in charts.items()}
    dual = {c:[tuple(map(Fraction,r)) for r in frame["A"]] for c,frame in charts.items()}
    internal = charts.keys() - set(w["start"] + w["final"])
    incident = defaultdict(Counter)
    for row in w["program"]:
        if row[0] == "MOVE":
            a,b = row[2:]
            assert a != b
            incident[a][b] += 1
            incident[b][a] += 1
    pairs = sorted(((-count,a,b) for a in internal for b,count in incident[a].items()
                    if a < b and b in internal))
    if not 0 <= args.skip_pairs < len(pairs):
        parser.error("offset outside the ranked pair list")
    batch = pairs[args.skip_pairs:args.skip_pairs+64]
    out = dict(word=PIN,kappa=KAPPA,pool=len(pairs),roster=batch,cases=[],witness=None,
               status="sample-exhausted",restart=None,price_scale=10**30)
    @cache
    def contained(a,b):
        return all(sum(x*y for x,y in zip(v,t)) == 0 for v in body[a] for t in dual[b])
    @cache
    def aggregate(ids,perp):
        src = dual if perp else body
        return rank(row for i in ids for row in src[i])
    for minus_count,a,b in batch:
        exterior = incident[a]+incident[b]
        del exterior[a],exterior[b]
        old = Counter({abs(dim[a]-dim[b]):-minus_count})
        for c,other in ((a,b),(b,a)):
            for n,count in incident[c].items():
                if n != other:
                    old[abs(dim[c]-dim[n])] += count
        for d in range(9):
            if monotonic()-start >= 60:
                out.update(status="capped",restart=[a,b,d])
                break
            low = tuple(sorted(n for n in exterior if dim[n]<=d))
            high = tuple(sorted(n for n in exterior if dim[n]>=d))
            def feasible():
                return (aggregate(low,False)<=d<=8-aggregate(high,True)
                        and all(contained(i,j) for i in low for j in high))
            if not args.price_first and not feasible():
                out["cases"].append([a,b,d,"infeasible"])
                continue
            diff = old.copy()
            for n,count in exterior.items():
                if dim[n]!=d:
                    diff[abs(dim[n]-d)] -= count
            hist = sorted((r,n) for r,n in diff.items() if n)
            lo = hi = Fraction()
            for r,n in hist:
                ends = [36*n*p for p in price(r)]
                lo += min(ends)
                hi += max(ends)
            status = "positive" if lo>0 else "negative" if hi<0 else "neutral" if not hist else "uncertain"
            scale = out["price_scale"]
            bounds = [lo*scale//1,-((-hi*scale)//1)]
            if args.price_first and hi<=0:
                out["cases"].append([a,b,d,"excluded-by-price",hist,bounds])
                continue
            if args.price_first and not feasible():
                out["cases"].append([a,b,d,"infeasible"])
                continue
            out["cases"].append([a,b,d,status,hist,bounds])
            if status=="positive":
                out.update(status="witness",witness=[a,b,d])
                break
        if out["status"] != "sample-exhausted":
            break
    out["seconds"] = monotonic()-start
    args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(out["status"],out["pool"],len(out["cases"]),Counter(c[3] for c in out["cases"]),
          out["witness"],out["seconds"])


if __name__ == "__main__":
    main()
