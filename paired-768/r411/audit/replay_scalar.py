"""Reconstruct exact scalar invoices across the published shortcut profiles."""
from fractions import Fraction as Q
from hashlib import sha256
from math import ceil, floor
from pathlib import Path
import json
import runpy
import signal

HERE = Path(__file__).resolve().parent
PINS = {
    "inputs/8089-RESULT.json": "abef5f5070bd3c3bc154fd9fef8d32b048c1b6df7e906b8e5a8a2e7a10284c2c",
    "inputs/8090-RESULT.json": "db037099a65c79389d9813fb86d6dd757e23c9fc80f0fd21eec88305a0456d8e",
    "inputs/8094-RESULT.json": "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
    "inputs/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
}
CB = Q(4391986206293, 2**50)
CG = Q(17158764376, 2**42)
DG = Q(1039776, 2**23)
ETA = Q(1, 256)
G = Q(1, 10**18)


def unique(pairs):
    if len(dict(pairs)) != len(pairs):
        raise ValueError("Duplicate receipt key")
    return dict(pairs)


def ordinary(heights, debit, booking=None):
    previous = Q(0)
    result = []
    for i,h in enumerate(heights,1):
        upper = min(ETA, Q(249,250)*(CB - debit/h) + previous/250)
        if i < len(heights):
            booked = Q(floor(upper*10**21)-1,10**21)
        else:
            booked = upper if booking is None else booking
        assert previous < booked <= upper
        result.append(booked)
        previous = booked
    return result


def entry_stock(heights, gaussian):
    cuts = []
    for h in heights:
        native = ceil(Q(250*(h+64),249))
        cuts.append(max(native,(cuts[-1] if cuts else 0)+h+64))
    required = cuts[-1]+gaussian+102
    initial = required+7*(required-1).bit_length()
    while initial-7*(initial-1).bit_length() < required:
        initial = required+7*(initial-1).bit_length()
    after_next_boundary = required+7*((initial-1).bit_length()+1)
    if (1<<(initial-1).bit_length())+1 < after_next_boundary:
        initial = after_next_boundary
    power = initial-1
    offset = 6-(4 if power%2==0 else 2)
    return cuts,power,offset


def charge_setup(extra):
    w = 2**38
    n = 2**68+extra
    h = 2*w+2
    lookup = 8*(4*w*n)*512*128
    work = 2**16*(h+4)*(7*h+9) + 8*2**16*(h+4)**2
    return (n+1)*(lookup+work+2**120)*2**32


def check(pr,record,qualify):
    debit = Q(record.get("ordinary_finite_debit",record.get("ordinary_debit")))
    assert Q(record.get("gaussian",{}).get("trial",record.get("gaussian_raw"))) == CG
    assert Q(record.get("gaussian",{}).get("raw_loss",record.get("gaussian_debit"))) == DG
    each = []
    for label in ("entry","terminal"):
        t = record[label]
        rate = Q(t["kappa"])
        h = t["ordinary_H"]
        g = t["numerical_H"]
        paid = rate+5*G
        book = ordinary(h,debit,paid)
        assert book == list(map(Q,t["ordinary_rates"]))
        gaussian = CG-DG/g
        assert gaussian == Q(t["gaussian_rate"])
        assert qualify(rate,G,paid,gaussian) == t["signed"]
        cuts,power,offset = entry_stock(h,g)
        stock = t["stock"]
        assert (cuts,power,offset) == (stock["binary_cuts"],stock["public_exponent_A"],stock["first_public_offset"])
        assert all(a+2 < b for a,b in zip(cuts,h[1:]))
        log_b=128+3*len(h)+320*sum(h) if label=="terminal" else 62+16384*sum(h)+25818582
        assert log_b == t["log2_B"]
        log_c = max(84500001, 1602+220*g+log_b)
        assert log_c == t["log2_C"]
        assert book[-1] < ordinary(h,debit)[-1]
        each.append(dict(kappa=str(rate),gaussian_height=g,log2_B=log_b,log2_C=log_c,
                         ordinary_guarded_ceiling=ordinary(h,debit)[-1]-5*G,
                         positive_margin=gaussian-paid,public_A=power,public_offset=offset))
    start,end=each
    rate=Q(end["kappa"])
    paid=rate+5*G
    g=end["gaussian_height"]
    assert CG-DG/(g-1)<=paid<CG-DG/g
    conversion=ceil((rate-Q(start["kappa"]))*end["public_A"])
    assert conversion==record.get("entry_price_surcharge",record.get("entry_conversion_bits"))
    complete=1+max(start["log2_C"]+conversion,end["log2_C"])
    assert complete==record["complete_log2_C"]

    output=dict(pr=pr,tier_rows=each,entry_conversion=conversion,complete_log2_C=complete,
                negative_G_minus_one=CG-DG/(g-1)-paid)
    if pr in (8090,8094):
        assert rate <= end["ordinary_guarded_ceiling"] < rate+Q(1,10**15)
        frozen=record["native_setup_transition_upper"]
        old,new=charge_setup(0),charge_setup(2**40)
        assert frozen==old<new<2**228
        count=len(record["entry"]["ordinary_H"])+len(record["terminal"]["ordinary_H"])+2
        structural=2*2048*(2**25+1)+count*2**24
        assert structural<2**40
        output.update(native_setup_receipt=frozen,written_expanded_setup=new,
                      extra_charge_omitted_from_receipt=new-old,recipe_count=count)
        # A price sensitivity only. No claim that the lower allowance is proved.
        smaller=debit-Q(1,2**20)
        candidate=Q(floor((ordinary(record["terminal"]["ordinary_H"],smaller)[-1]-5*G)*10**15),10**15)
        new_paid=candidate+5*G
        assert candidate>rate and new_paid<CG-DG/g
        output.update(projected_kappa_at_one_smaller_ordinary_tick=candidate,
                      projected_delta_at_one_smaller_ordinary_tick=candidate-rate,
                      projected_same_G_positive_margin=CG-DG/g-new_paid,
                      projected_same_G_complete_log2_C=1+max(
                          start["log2_C"]+ceil((candidate-Q(start["kappa"]))*end["public_A"]),
                          end["log2_C"]))
    return output


def timeout(_signal,_frame):
    raise TimeoutError("The three-scalar-case check reached its 30-second cap")


def main():
    assert __debug__
    for name,h in PINS.items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==h
    qualify=runpy.run_path(str(HERE/"inputs/outer_budget.py"))["qualify"]
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(30)
    try:
        rows=[check(n,json.loads((HERE/f"inputs/{n}-RESULT.json").read_bytes(),
                                 object_pairs_hook=unique),qualify) for n in (8089,8090,8094)]
        print(json.dumps({"scope":"Exact scalar invoices only; no native setup, signed source or theorem admission",
                          "cases":len(rows),"results":rows},indent=2,default=str))
    finally:
        signal.alarm(0)


if __name__=="__main__":
    main()
