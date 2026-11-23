from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import sys
raw = Path(sys.argv[1]).read_bytes()
assert sha256(raw).hexdigest() == "d8b6844b4b10abdfe43cae6b37494b541006d0f194aa991647d337fe762409aa"
data = json.loads(raw)
f = data["factors"]
assert (f["k7_floor"], Q(f["k7_fringe"][1]) < 8) == (18960, True)
L, delta = 18960, Q(1, 2**128)
new_upper = Q(f["ordinary_factor"][1]) * (1 + Q(8,L) + delta) / (1 + Q(64,L) + delta)
assert new_upper ** 8192 < 2**11205
debit, heights, G = Q(11205,8192), (8192,124648,524288), 490951
target, guard = Q("0.0038982142837"), Q(5,10**18)
old_cap = Q(523209464347189355219919950737,134217728000000000000000000000000)
c_O, c_G = Q(4391986206293,2**50), Q(17145637307,2**42)
def ordinary(hs):
    prior = Q(0)
    for i, h in enumerate(hs, 1):
        top = min(Q(39,10000), (249*(c_O-debit/h)+prior)/250)
        if i == len(hs):
            return top
        prior = Q(floor(top*10**21)-1,10**21)
entry_rate = Q(".00345")
assert ordinary((3000,3080)) > entry_rate + guard
ordinary_rate, gaussian_rate = ordinary(heights), c_G - Q(64939,524288*G)
assert target > old_cap and min(ordinary_rate,gaussian_rate) > target + guard
cuts = []
for h in heights:
    cuts.append(max(ceil(Q(250*(h+64),249)), cuts[-1]+h+64 if cuts else 0))
required = cuts[-1] + G + 102
s = next(width for width in range(required, required+500) if width-7*(width-1).bit_length() >= required)
A = s-1
offset = (-pow(2,A,6)) % 6
premium = ceil((target-entry_rate)*A)
entry_clock = data["arithmetic"]["entry_new"]["log2_C_before_entry_and_selector"]
price = 1 + max(entry_clock+premium, 1602+128+320*sum(heights)+220*G)
assert (cuts,A,offset,premium,price)==([8290,133002,657354],1148553,4,515,318291911)
assert max(*heights,G)==524288
print("PASS one scoped fringe price", target, "margin", min(ordinary_rate,gaussian_rate)-target-guard,
      "complete clock", price, "activation", (A,offset), "premium", premium)
