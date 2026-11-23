"""Check the supported debit grid for the K7 matched-interval suffix envelope."""

from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_bytes()
assert sha256(source).hexdigest() == "d8b6844b4b10abdfe43cae6b37494b541006d0f194aa991647d337fe762409aa"
prior = json.loads(source)["factors"]
assert prior["k7_floor"] == 18960
assert Q(prior["k7_fringe"][1]) < 8
lower, upper = map(Q, prior["ordinary_factor"])
L = prior["k7_floor"]
delta = Q(1, 2**128)
ratio = (1 + Q(8, L) + delta) / (1 + Q(64, L) + delta)
grid = 10**18
new_lower = Q(floor(grid * lower * ratio), grid)
new_upper = Q(ceil(grid * upper * ratio), grid)
assert new_upper**8192 < 2**11204
assert new_lower**8192 > 2**11203
assert lower**8192 > 2**11204
print(json.dumps({
    "factor_lower": str(new_lower),
    "factor_upper": str(new_upper),
    "booking_grid": 8192,
    "last_supported_booking": 11204,
    "rejected_adjacent_booking": 11203,
    "old_suffix_envelope_rejects_new_booking": True,
}, indent=2))
