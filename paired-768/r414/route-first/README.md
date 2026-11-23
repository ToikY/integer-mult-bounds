# Route-first workflow, exact #8094 direct and quotient

The fixed case IDs are DIRECT and QUOTIENT on #8094 at
c20a08dc0a79a989e3515068560d5da371c0a2a8. The stop was two useful exact
source decisions or 180 seconds, whichever came first. This trial pins the
retained caller, receiver and its patch chain before comparing the proof.
The checked route anchors covered both cases. No scientific package or
native loop was launched.

The signed ordinary call goes through patched ordinary_carrier.py and its
profile-preserving stage body. The latter selects the direct threshold
at ceil(e/w) ≤ N^8 and retains maximum stage−1 for earlier service.
triangular_ordinary.py:root_body passes its true coarse c to the binary
receiver. SameOrderBody.weighted determines f and the remainder with
divmod(c,N). Its remainder uses weighted_pair with previous_swap only.
The compiler receives f and keeps the trimmed remainder as spectator
factors. The K7 machine leaf issues serve_line and installs the returned
field into its original owner before continuing.

- DIRECT. Physical Receiver.serve_line uses one weighted callback at
  atoms=f for the coordinate case. The alternative direct_line uses its
  single weighted callback at atoms=f between actual forward and inverse
  basis routes. The basis routes only call earlier service on the complete
  field. The late small-child switch still takes the canonical direct path
  with the same rank, layout and prior service.
- QUOTIENT. Physical Receiver.serve_line visits each canonical_lows output
  once. Its fixed packet length is unused × high × older × atom^(2Nf)
  × gap × suffix. All complete low packets have the same true high
  cardinality and are disjoint. same_order_line chooses its corner pairs
  from the fixed low's pivot and issues 1+2|pairs| weighted callbacks at
  atoms=f, uncomputing the preliminary actions and both shear sweeps.
  Callback spectators multiply to exactly that low packet's full volume.
  Pending storage checks an empty return and the inverse split restores
  the original field layout.

The pinned receiver and ordinary clock prove, for each fixed incoming
rank-one frame, quotient mean at most (21x+3)/(9x−1), x=3^(N−2).
Both cases use f=floor(c/N). The ratio for each required width moment
s∈{1−(c_B−d/H),1} is at most N^(−s), with fixed paid normalized leaf
count F(N). Each installed rank has N≥9, so the quotient mean is at
most 2390/1024 and direct cost is at most one. The two moments therefore
use the same 2390/1024·F(N)·N^(−s) upper bound. The original local
movement and earlier-service bills still carry shears, staging, basis
changes, parked banks, and returns. Static inspection found no further
same-rank path in these two cases. Physical replay and next-threshold
admission remain open independently of these route anchors. [Exact receiver](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/RECEIVER.md) · [Two-moment clock](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/ORDINARY-CLOCK.md)

Use CPython 3.12 with the exact [#8094 source](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8)
and the [existing #8057 archive](https://github.com/CrocSwap/integer-mult-bounds/blob/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e/research/p104-weighted-k7-suffix/peer8057.tar.gz).
The command reads the relevant nested archive members in memory, validates
the physical patch anchors and requires neither a prior installer nor
untracked source paths.

```sh
python3.12 -IB check.py --archive "$K7_ARCHIVE" \
  --prepare "$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage/prepare.py" > reproduced.json
cmp reproduced.json RECEIPT.json
```

Elapsed time to first validated static route receipt was 131 seconds
including pinning, source review, implementation and wrapper overhead. The
runner took 0.06 seconds. Source proof and implementation were interleaved
and active subintervals were not captured reliably. Independent
verification is separate and not included in the 131 seconds. Treat
any comparison requiring matched active timings as inconclusive.

Credit Ali Romman for #8042's exact quotient receiver and #8057's retained
K7 stack, SYLforge for K7, floration for the composed profile, and the
Round 413 tariff analysis. OpenAI Codex assisted with this trace.
