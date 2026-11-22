"""Price the single R373 compact tiered profile on the rebuilt quarter roster."""
from argparse import ArgumentParser
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile
import time

PINS = {
    "round372_price": "cd827bc3298a2ad9dae03df19c1c7e034a029fb787979759dae58bf1870d266e",
    "round372_receipt": "33854dce220483454d08bf242b4fec99424758ffd2ea21070ea21fda297a26f0",
}
PEER_PINS = {
    "source/ordinary_clock.py": "91dcf0ef72dddbde998b80f3d8b30c8036de9ce97e06e2bbd9c4159bf292020d",
    "check_serial_setup.py": "11d1c3209cb523a360ab9abaefb3122507fdf5cb469169890fe2dac636812c47",
    "serial_setup.py": "61b5058d394ed74e943303e4bdbf21d58ccf5d8bb39fc4b02e97bc135d7bdbbc",
    "MEASUREMENTS.json": "a1083bc55178baf0015ef83ef169f45df61475fcc648f487e03c852c871f1f00",
}
KAPPA = Q(".003898202")
REFERENCE_C = Q(".0038982016137")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def ceil(q):
    return -(-q.numerator//q.denominator)


def examine(a, work):
    for n,pin in PINS.items():
        assert digest(getattr(a,n))==pin,n
    for n,pin in PEER_PINS.items():
        assert digest(a.peer/n)==pin,n
    old_price=runpy.run_path(str(a.round372_price))
    quarter=old_price["evaluate"](a.peer,work/"installed")
    assert json.loads(json.dumps(quarter)) == json.loads(a.round372_receipt.read_bytes())
    assert quarter["canonical_cells"]==63 and Q(quarter["maximum_k_over_r"])==9
    assert quarter["canonical_reserve_factor_millionths"]==1121328
    assert quarter["phase_qualifying_large_copy_passes"]==189072
    assert quarter["phase_equivalent_field_extents"]==1134432

    import installations as original
    from linear_geometry import entrance_geometry
    gaussian=Q(quarter["gaussian_candidate_c"])
    assert gaussian==Q(2143195807,2**39)
    assert gaussian>Q(quarter["gaussian_old_crossing"][1])
    entry=original.ENTRY
    terminal=replace(original.TERMINAL,rank_logs=(35327,559462),kappa=KAPPA)
    assert terminal.complex_log==680000 and entry.complex_log==1024
    assert len(terminal.rank_logs)==2 and min(terminal.rank_logs)>=8192
    assert 1008*(Q(1,4)+Q(3,4))==1008
    assert 40764<32*2066  # Enlarged candidates before empty support cells are dropped.
    assert 2**80*(2**1024)**93 < (2**1024)**96
    assert (2**1024)**96 * (2**1024)**92 * 2**25 < (2**1024)**193

    source=a.peer/"source"
    outer=runpy.run_path(str(source/"outer_budget.py"))
    activation=runpy.run_path(str(source/"activation.py"))
    ordinary=runpy.run_path(str(source/"ordinary_clock.py"))
    receipt={}

    for name,p in (("entry",entry),("terminal",terminal)):
        inner=Q(0)
        history=[]
        for index,h in enumerate(p.rank_logs):
            limit=min(p.eta,(249*(original.BINARY_C-Q(11,8*h))+inner)/250)
            rate=Q(int(limit*10**21)-1,10**21) if index==0 else p.ordinary
            assert inner<rate<limit
            history.append((str(rate),str(limit-rate)))
            inner=rate
        g=Q(1,p.positive_stop_denominator)
        assert g==Q(1,10**18)
        cap=gaussian-Q(43,256*p.complex_log)
        signed=outer["qualify"](p.kappa,g,p.ordinary,cap)
        stock=activation["resource_receipt"](p)
        A=original.activation(p)
        assert stock["public_exponent_A"]==A
        assert 68+83*p.complex_log<92*p.complex_log<448*p.complex_log
        assert (872*(4*p.complex_log+1)).bit_length()<=p.complex_log
        if min(p.rank_logs)>=8192:
            assert 2660000*32<2**30
            B=128+320*sum(p.rank_logs)
        else:
            overhead=ordinary["first_stage_bound"](p.eta),ordinary["polynomial_to_fibre_bound"]()
            assert Q(376*7,10)**len(p.rank_logs)<2**17
            B=40+17+16384*sum(p.rank_logs)+sum(max(0,e-944*h)
                                               for e,h in zip(overhead,p.rank_logs,strict=True))
        recurring=max(84500001,1602+220*p.complex_log+B)
        receipt[name]={"kappa":str(p.kappa),"rank_logs":p.rank_logs,"complex_log":p.complex_log,
                       "ordinary_history_rates_and_strict_gaps":history,"signed":signed,
                       "stock":stock,"geometry":entrance_geometry(A),
                       "log2_B":B,"log2_C":recurring,
                       "positive_rate_before_gap":str(cap)}
    assert receipt["entry"]["log2_C"]==125660241
    A=receipt["terminal"]["stock"]["public_exponent_A"]
    edge=2**A
    external=edge+(-edge)%6
    previous=original.TERMINAL
    original.TERMINAL=terminal
    try:
        assert original.at_public(edge-1) is entry and original.at_public(edge) is terminal
        assert original.at_public(external-6) is entry and original.at_public(external) is terminal
    finally:
        original.TERMINAL=previous
    assert A>activation["full_entrance"](594603,680000)
    premium=ceil((terminal.kappa-entry.kappa)*A)
    clock=1+max(receipt["entry"]["log2_C"]+premium,receipt["terminal"]["log2_C"])
    w=2**38
    h=2*w+2
    scalar=2**16*(h+4)*(7*h+9)+8*2**16*(h+4)**2
    store=4*w*2**68
    lookup=8*store*512*128
    setup=(2**68+1)*(lookup+scalar+2**120)*2**32
    assert setup<2**228 and store==2**108
    assert max(terminal.rank_logs).bit_length()<w

    return {
        "scope":"one fixed ordinal trial, no physical construction or complete replay",
        "comparator":quarter["comparator"],"old_kappa":str(REFERENCE_C),
        "peer":quarter["peer"],"kappa":str(KAPPA),"delta_vs_8056":str(KAPPA-REFERENCE_C),
        "gaussian_dyadic":str(gaussian),"ordinary_signed_and_resource_books":receipt,
        "prefix_entry_fee_bits":premium,
        "complete_log2_clock_upper":clock,
        "changed_first_public_offset":external-edge,
        "fixed_installation_funded_action_envelope":"2^228 (literal new recipe compiler replay pending)",
        "directed_paid_label_family":{"productive":105216,"paid":564144,"transport_cells":63,
                                      "max_routing_ratio_k_over_r":9,
                                      "phase_passes":quarter["phase_qualifying_large_copy_passes"],
                                      "phase_extents":quarter["phase_equivalent_field_extents"]},
        "decision":"VIABLE_FULL_PRICE_ONLY",
        "next_gate":"literal shared compact tiers and signed supplier, installation and all six scientific modes",
        "pins":PINS,"peer_pins":PEER_PINS,
    }


if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    for n in ("peer","round372_price","round372_receipt","out"):
        parser.add_argument("--"+n.replace("_","-"),type=Path,required=True)
    parser.add_argument("--child",action="store_true")
    a=parser.parse_args()
    if a.child:
        a.peer=a.peer.resolve()
        with tempfile.TemporaryDirectory(prefix="tier-book-") as root:
            result=examine(a,Path(root))
        with a.out.open("x") as out:
            json.dump(result,out,sort_keys=True,indent=2)
            out.write("\n")
    else:
        t=time.perf_counter()
        r=subprocess.run([sys.executable,"-IB",__file__,"--child",*sys.argv[1:]],timeout=45)
        print(f"exit={r.returncode} seconds={time.perf_counter()-t:.3f}")
        raise SystemExit(r.returncode)
