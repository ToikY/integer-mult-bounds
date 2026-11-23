from fractions import Fraction as Q
from importlib.util import spec_from_file_location, module_from_spec
import json
from math import ceil
from pathlib import Path

receipt = json.loads(Path("charges.json").read_bytes())
factor = Q(receipt["ordinary_factor_outward_12_places"][1])
debit = Q(11239, 8192)
assert factor**8192 < 2**11239, "ordinary outward bound misses the finer booking"
spec = spec_from_file_location("reconstruct", "reconstruct.py")
invoice = module_from_spec(spec)
spec.loader.exec_module(invoice)
heights, gauss, kappa = (8192, 124863, 524288), 490639, Q("0.00389821412325")
assert kappa > invoice.CANDIDATE[-1]
ordinary, _ = invoice.ordinary(heights, debit=debit)
gaussian = invoice.GAUSSIAN_TRIAL - invoice.NEW_DEBIT / gauss
assert min(ordinary, gaussian) > kappa + invoice.STOP, "one or both signed rate ceilings fail"
cuts, head, offset = invoice.connected(heights, gauss)
premium = ceil((kappa - invoice.ENTRY[-1]) * head)
entry = invoice.recurring(invoice.ENTRY)[1] + premium
terminal = invoice.recurring((heights, gauss, kappa))[1]
bill = 1 + max(entry, terminal)
assert bill <= 318292171 and premium <= 515 and max(*heights, gauss) <= 524288
print(dict(kappa=str(kappa), ordinary=str(ordinary), gaussian=str(gaussian),
           recurring_log2_C=bill, entry_bits=premium, terminal_cuts=cuts,
           activation_exponent=head, activation_offset=offset))
