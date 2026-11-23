"""Check weighted child tariff, discrete allocation and complete signed price."""

from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import ceil, floor
from pathlib import Path
import sys

parser = ArgumentParser(description=__doc__)
for option in ("runtime", "signed_source", "primitives", "comparator", "result"):
    parser.add_argument("--" + option.replace("_", "-"), type=Path, required=True)
args = parser.parse_args()

def pin(path, expected):
    assert sha256(path.read_bytes()).hexdigest() == expected, path

pin(args.primitives, "7b06abca74493ca369601c426574e60ef15f5a5c8c76b4cfea2a8387fe32557c")
pin(args.comparator, "0654a74dd2c424ff2e8b26cb9828f451b76bde6f8b35762cb2cb69ba83fdd1ce")
for name, digest in {
    "outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "outer_clock.py": "63363c3da673365f3ac5e1b7e318c6938005f1e9c9896799504cc598efbf96fa",
}.items():
    pin(args.signed_source / name, digest)
pin(args.result, "e37781c0ffcda49b6adc31501cf062d3bbcb6344765440183e96b2572c65411b")
sealed = json.loads(args.comparator.read_bytes())
published = json.loads(args.result.read_bytes())
spec = spec_from_file_location("previous_invoice_primitives", args.primitives)
prev = module_from_spec(spec)
spec.loader.exec_module(prev)
prev.ROOT = args.runtime.resolve()
prev.SIGNED_SOURCE = args.signed_source.resolve()
sys.path.insert(0, str(prev.SIGNED_SOURCE))
from outer_budget import margins
from outer_clock import financial_checks

TRIAL, GAUSSIAN, ETA, GUARD = prev.TRIAL_O, prev.TRIAL_G, prev.ETA, prev.GUARD
LOW, HIGH = 8192, 524288
CAP = 318291911
NEW, PRIOR = Q(11178,8192), Q(11204,8192)
TARIFF, OLD_TARIFF, MEAN = Q(2401,1024), Q(47,20), Q(75,32)
ENTRY = ((3000,3080),1024,Q(".00345"))
OLD = ((8192,117168,524288),501831,Q(".003898219753506"))
NEW_PROFILE = ((8192,111681,524288),509812,Q(".003898223617430"))
EARLY = financial_checks()["early_log2_C_bound"]+1
assert EARLY == 84500001
ROUNDING = Q(1, 2**128)
POWER = prev.power_bounds

def checks_of_bookings():
    # Reopen the actual installed K7 and complex sources and regenerate their
    # original directed word intersections. Reuse the verified all-size
    # interpretation only after authenticating the prior receipt.
    source = prev.transport_and_factors()
    from raw_binary_stage import binary_recipe
    assert all(binary_recipe(height).level_floor == 18960
               for height in sorted(set((*ENTRY[0], *NEW_PROFILE[0]))))
    assert source["k7_cell_sha256"] == sealed["directed_enclosure"]["k7_shares_sha256"]
    assert source["gaussian_cells_sha256"] == sealed["directed_enclosure"]["gaussian_cells_sha256"]
    assert Q(source["k7_fringe"][1]) < 8
    assert source["gaussian_factor"] == [Q(x) for x in sealed["directed_enclosure"]["gaussian_factor"]]
    L = 18960
    common = Q(256,255)*Q(4097,4096)*Q(1028,1024)
    common *= (1+Q(8,L)+ROUNDING)/((1-Q(10,L))*(1-ROUNDING)**3)
    raw = tuple(common*end for end in POWER(1024*134*L,TRIAL))
    old = tuple(OLD_TARIFF*x for x in raw)
    new = tuple(TARIFF*x for x in raw)
    assert prev.enclosure(old) == [Q(x) for x in sealed["directed_enclosure"]["ordinary_factor"]]
    assert POWER(2, NEW-Q(1,8192))[1] < new[0] <= new[1] < POWER(2, NEW)[0]
    assert POWER(2, NEW)[1] < old[0] <= old[1] < POWER(2, PRIOR)[0]
    assert TARIFF / OLD_TARIFF == Q(12005,12032)
    assert MEAN/TARIFF == Q(2400,2401) and MEAN/MEAN == 1
    geometric = 1/(1-MEAN/TARIFF)
    previous_geometric = 1/(1-MEAN/OLD_TARIFF)
    assert geometric == 2401 and previous_geometric == 376 and geometric < 8*previous_geometric
    assert 2**21 < (Q(7,10)*geometric)**2 < 2**22
    assert 2**16 < (Q(7,10)*previous_geometric)**2 < 2**17
    assert all(0 < TRIAL-NEW/h < 1 for h in (*ENTRY[0],*NEW_PROFILE[0]))
    return dict(old_factor=prev.enclosure(old), new_factor=prev.enclosure(new),
                allowance=prev.enclosure(POWER(2,NEW)),
                adjacent_allowance=prev.enclosure(POWER(2,NEW-Q(1,8192))),
                booking_reserve=prev.enclosure((POWER(2,NEW)[0]-new[1],POWER(2,NEW)[1]-new[0])),
                adjacent_shortfall=prev.enclosure((new[0]-POWER(2,NEW-Q(1,8192))[1],new[1]-POWER(2,NEW-Q(1,8192))[0])),
                contraction=MEAN/TARIFF, series=geometric, unit_tariff_control=MEAN/MEAN,
                source_sha256=source["actual_operator_function_source_sha256"],
                k7_share_sha256=source["k7_cell_sha256"], gaussian_share_sha256=source["gaussian_cells_sha256"],
                gaussian_factor=source["gaussian_factor"], gaussian_allowance=source["gaussian_allowance"],
                gaussian_adjacent_shortfall=source["gaussian_one_tick_shortfall_lower"],
                grade_actions=source["setup_grade_actions"])

def charged_invoice(profile, debit, new):
    result = prev.invoice(profile, margins, debit)
    heights, g, _ = profile
    surcharge = (5 if len(heights) == 2 else 3*len(heights)) if new else 0
    result["ordinary_log2_B"] += surcharge
    result["log2_C_before_entry_and_selector"] = max(EARLY, 1602 + 220*g + result["ordinary_log2_B"])
    return result

def discrete_slice(g, debit, charge):
    # Use exact one-step discrete differences instead of candidate tangents.
    heights_total = (CAP-charge-220*g)//320
    first, last = LOW, HIGH
    middle = heights_total-first-last
    heights = (first, middle, last)
    assert first < middle < last
    invoice = charge + 320*heights_total + 220*g
    assert invoice <= CAP < invoice + 320
    weights = (Q(1,250**2),Q(1,250),Q(1))
    max_add = max(w/(h*(h+1)) for w,h in zip(weights, heights) if h < HIGH)
    min_drop = min(w/(h*(h-1)) for w,h in zip(weights, heights) if h > LOW)
    cost_of_deviation = Q(249,250)*debit*min(min_drop-max_add,min_drop)
    eligible = Q(249,250)*sum(w*(TRIAL-debit/h) for w,h in zip(weights, heights))
    actual, floors = prev.ordinary_rates(heights, debit)
    assert max(*floors,actual) < ETA
    assert 0 < eligible-actual < cost_of_deviation
    return dict(heights=heights, charge=invoice, exact_ordinary=actual,
                exact_gaussian=prev.gaussian_rate(g), floors=floors,
                actual_floor_loss=eligible-actual, discrete_deviation_loss_floor=cost_of_deviation)

def stopped_cap(profile, debit, charge, signed, entry):
    g = profile[1]
    below, at, above = (discrete_slice(h,debit,charge) for h in (g-1,g,g+1))
    assert at["heights"] == profile[0]
    ceiling = min(at["exact_ordinary"],at["exact_gaussian"])-GUARD
    assert below["exact_gaussian"] < profile[-1]+GUARD
    assert above["exact_ordinary"] < profile[-1]+GUARD
    assert profile[-1] < ceiling
    strict,functional,paid = margins(ceiling,GUARD/5,ceiling+GUARD,at["exact_gaussian"])
    assert len(strict) == 54 and len(functional) == 4 and min(*strict,*functional)>0 and paid>=0
    assert at["floors"][-1] < ceiling+GUARD
    assert signed["complete_log2_C"] <= CAP
    assert ceil((ceiling-entry["kappa"])*signed["activation_exponent"]) == signed["entry_conversion_bits"]
    return dict(supremum=ceiling, guard=GUARD, slices=[below,at,above],
                binding="ordinary" if ceiling+GUARD == at["exact_ordinary"] else "Gaussian",
                installed_reserve=ceiling-profile[-1],
                lower_shortfall=profile[-1]+GUARD-below["exact_gaussian"],
                upper_shortfall=profile[-1]+GUARD-above["exact_ordinary"])

factor = checks_of_bookings()
known_entry = charged_invoice(ENTRY,PRIOR,False)
known_late = charged_invoice(OLD,PRIOR,False)
prev.add_entry_and_selector(known_entry,known_late)
assert json.loads(json.dumps(known_entry,default=str)) == sealed["entry"]
assert json.loads(json.dumps(known_late,default=str)) == sealed["terminal"]
entry, late = charged_invoice(ENTRY,NEW,True), charged_invoice(NEW_PROFILE,NEW,True)
prev.add_entry_and_selector(entry,late)
assert entry["entry_ordinary_surcharges"] == [0,25818582]
assert entry["ordinary_log2_B"] == 125433364
assert late["ordinary_log2_B"] == 206131657 and late["gaussian_height_log_charge"] == 112158640
assert late["complete_log2_C"] == 318291900 and late["entry_conversion_bits"] == 518
assert late["select_entry_after_conversion"] == 125660764
assert late["first_header_precision_and_tape"]["absolute_log2_private_control_envelope"] == 536870915
old_stopped = stopped_cap(OLD,PRIOR,1731,known_late,known_entry)
new_stopped = stopped_cap(NEW_PROFILE,NEW,1740,late,entry)
assert old_stopped["supremum"] == Q(sealed["new_family_ceiling"])
assert old_stopped["binding"] == "ordinary" and new_stopped["binding"] == "Gaussian"
assert new_stopped["supremum"] == Q(1667119388378402860472786027,427661302169600000000000000000)
assert new_stopped["installed_reserve"] == Q(441096658027,427661302169600000000000000000)
gain = NEW_PROFILE[-1]-old_stopped["supremum"]
assert gain == Q(518607092213701021150319,134217728000000000000000000000000)

from band_product import precision
from installations import ENTRY as installed_entry, TERMINAL as installed_late, activation, at_public
from linear_geometry import public_shape
from staged_carriers import entrance_logs

for invoice, installation, literals in ((entry, installed_entry, published["entry"]), (late, installed_late,published["terminal"])):
    exponent, offset = invoice["activation_exponent"],invoice["activation_offset"]
    header = (1<<exponent)+offset
    assert activation(installation) == exponent
    assert invoice["cuts"] == list(entrance_logs(installation.rank_logs))
    assert invoice["max_native_height"] == max(*installation.rank_logs,installation.complex_log)
    assert invoice["kappa"] == installation.kappa
    assert invoice["heights"] == installation.rank_logs
    assert invoice["gaussian_height"] == installation.complex_log
    assert invoice["ordinary_log2_B"] == literals["log2_B"]
    assert invoice["log2_C_before_entry_and_selector"] == literals["log2_C"]
    tape = invoice["first_header_precision_and_tape"]
    for i, shift in enumerate((4,5)):
        extent = header//6+shift-exponent
        shape = public_shape(header,extent)
        recovered = precision(header,extent,shape.count)
        assert shape.count.bit_length()-1 == tape["log2_axis_count"]
        assert prev.value_hash(recovered) == tape["coefficient_precision_endpoints_sha256"][i]
        assert recovered.bit_length() == tape["coefficient_precision_bit_lengths"][i]
exponent, nice = late["activation_exponent"], late["activation_offset"]
first_header = (1<<exponent)+nice
assert (exponent,nice) == (1154447,4)
assert at_public(first_header) == installed_late and at_public(first_header-6) == installed_entry

width = 1<<38
register = 2*width+2
arithmetic = 2**16*(register+4)*(7*register+9) + 8*2**16*(register+4)**2
lookup = 4*width*2**68*8*512*128
all_setup = 2**21*2**68*512*register**2 + arithmetic + lookup
# The source's bound uses separate conservative highest-exponent domination.
assert (arithmetic,lookup) == (sealed["serial_setup"]["local_arithmetic"],sealed["serial_setup"]["lookup"])
assert all_setup < 2**228 and published["native_setup_transition_upper"] == sealed["serial_setup"]["all_setup"]
assert published["native_setup_transition_upper"] < 2**228
assert len(ENTRY[0])+len(NEW_PROFILE[0])+2 == 7
assert factor["grade_actions"] == published["native_setup_grade_actions"] < 2**32
setup_source = prev.SIGNED_SOURCE.parent / "check_serial_setup.py"
sys.path.insert(0, str(setup_source.parent))
from check_serial_setup import clock as setup_clock
setup = setup_clock()
assert setup["max_datum_bits"] == width and setup["setup_exponent"] == 228
assert setup["all_setup"] == published["native_setup_transition_upper"]
print(json.dumps(dict(bookings=factor, entry=entry, terminal=late,
                      known_good_entry=known_entry, known_good_terminal=known_late,
                      stopped_cap_prior=old_stopped, stopped_cap_candidate=new_stopped,
                      gain_over_prior_exact_cap=gain, fixed_setup=setup), indent=2,default=str))
