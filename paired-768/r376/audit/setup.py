"""Check fixed R376 grade/setup count and per-call recurring arithmetic envelopes."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path

PINS = {
    "coupling": "2828f5a208b24b3c556313601d6f05a62fef57509e58dc00d161c9f2d8023553",
    "setup": "6951a98f2f8a0bf73c8d60b16ebbbd66bf87584251df8afbefe4e3a0330bfbf3",
}


def audit(args):
    for key, expected in PINS.items():
        assert sha256(getattr(args,key).read_bytes()).hexdigest()==expected
    book=json.loads(args.coupling.read_bytes())
    rows=book["transport_cells"]
    paid=len({r for r,_,_ in rows})
    productive=len({k for _,k,_ in rows})
    assert (paid,productive,len(rows))==(30,34,63)
    assert 105216+564144<2**20 and paid+productive<2**8
    assert book["largest_reduced_cell_bits"]==263<512
    bound=(2**20*256 + 2**8*256*8 + (paid+productive)**2*32 + 2**10)
    assert bound<2**29<2**32

    word=2**38
    width=2*word+2
    scalar=2**16*(width+4)*(7*width+9)+8*2**16*(width+4)**2
    assert scalar<2**110
    store=4*word*2**68
    lookup=8*store*512*128
    cost=(2**68+1)*(lookup+scalar+2**120)*2**32
    assert store==2**108 and cost<2**228

    H=1024
    per_integral=2**30*(1024*(H+1)+4)**2
    assert per_integral<2**(H//8)
    # Increasing H by one grows the polynomial by less than its exponential
    # allowance, uniformly because the relative increment decreases.
    assert (1024*(H+2)+4)**16 < 2*(1024*(H+1)+4)**16
    return {
        "paid_grade_rows": paid,"productive_grade_rows": productive,
        "whole_changed_fixed_grade_action_upper": bound,
        "prior_grade_action_budget": 2**32,
        "fixed_store_upper": store,"fixed_setup_upper": cost,
        "recurring_integral_arithmetic_upper_at_H1024": per_integral,
        "scope": "inherited exact fixed serial setup and arithmetic envelope, not full replay",
        "pins": PINS,
    }


if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    for key in ("coupling","setup","out"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    with a.out.open("x") as out:
        json.dump(audit(a),out,indent=2,sort_keys=True)
        out.write("\n")
