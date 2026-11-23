# First eligible Round 402 test

Refresh the peer frontier and reproduce or authenticate #8070 at `7d65b2c6a19941b9922d5e4c86c495aa37073141` before testing. If a stronger comparable result has appeared, reprice the lead against it. The Round 401 screen excluded the 684/707 fusion under the actual first-read, recipient and restoration contract. A different legal first-read schedule and a legal recipient for the combined grade are required to reopen that specific fusion. The current directed Gaussian factor also fails one tick below 64939/524288.

The next narrow lead charges the independently reconstructed ordinary finite factor at one finer grid point, `11239/8192` in place of `1405/1024`. Price one funded allocation only. Move a single height level from the second ordinary stage to the Gaussian stage, leaving the ordinary heights at `(8192,124863,524288)` and the Gaussian height at `490639`. Candidate target `0.00389821412325`. The test is a 30-second, one-case exact screen, including the full recurring coefficient and entry conversion. Run it from this file's sibling `verification` directory after authenticating or replaying its invoice receipt.

```sh
python3.12 -IB - <<'PY'
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
PY
```

A pass would justify checking both signed callers and building one literal branch in the next round. It would leave the complete proof, placement, ownership and restoration, fixed setup, precision and tape checks, fault controls and independent signed replay pending. An assertion failure rules out the tested booking or allocation and identifies which inequality blocks it. A timeout leaves that single case unresolved. This screen is saved for the next round and has not been launched.
