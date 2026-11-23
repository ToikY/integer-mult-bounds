# Identity check at 64 paid K7 chart changes

The fixed 64 cases exhaust the declared early gate. All have nonzero
arbitrary-input normalized fields and non-identity literal chart changes.
Removing the paid call and merely updating the chart metadata corrupts a
live register in each case. The other 2,732 MOVE clocks remain unresolved.
This is a finite restriction on the source's independent-input interface.
It leaves open caller-specific correlations, different charts, batched
moves and replacement programs with new paid paths.

The literal schedule for the ordinary service within #8094 is the
unchanged K7 graph from SYLforge's [#8052] and Ali Romman's [#8057].
Its chart action uses the already charged positive difference of nested
projectors from [#8027] and the physical bank interpretation from [#7914].
The predecessor source and all 36 LOCAL repetitions are preserved.
For an identity call, gross saved raw work would be 36 times
`rank^(1-c_B)` with `c_B=4391986206293/2^50`; there would be no
productive-target change. Every witness requires a repair to restore the
old chart action. One same-rank paid repair consumes the entire gross
saving before overhead. A cheaper repair, if found, must separately
cover routing, ownership, restoration, precision and tape. No change to
the complete recurrence or κ was certified. OpenAI Codex assisted.

## Replay

Use CPython 3.12 with assertions enabled. Use the authenticated
[packed predecessor from #8087] as an explicit input named
`peer8057.tar.gz`. Execute these commands from this handoff directory.

~~~sh
python3.12 -I -B check.py peer8057.tar.gz > checked.json
cmp checked.json RECEIPT.json
python3.12 -I -B replay.py peer8057.tar.gz checked.json > independent.json
cmp independent.json REPLAY.json
~~~

The first test authenticates the archive, its exact nested
`research/tiered-native-multiplier/source/strong-bit-k7.json.gz`,
and the unpacked literal. It computes every chronological support needed
for the fixed cohort using 630 independent basis vectors. It freezes
64 cases by descending rank then zero-based clock, explicitly checking
the exact rational difference of both projectors and outward raw-moment
price intervals. It also checks all terminal logical register maps as the
positive control. The independently implemented replay tests each exact
named input impulse and its address transformation by modular chart
elimination and actual forward composition. Substituting independent
input owner 629 at the first clock yields no live impulse and is rejected.

One rank-7 and 63 rank-6 cases completed. The minimum and maximum
support sizes were 182 and 234. At clock 15415, register 3225 in chart
0 changes to 585. Taking only independent input 4 and placing its impulse
so that the live address has zero head and tail coordinate 0 equal to
one gives a nonzero change in the head. At unit weights this change is
`(3/4,-1/4,-1/4,1/4,0,0,0,0)` modulo 9; the identity rewrite leaves the
head zero. The replay composes with the inverse old chart to construct
this legal input.

The exact gate took 0.201 seconds wall with exit 0. The independent
modular replay took 0.156 seconds wall with exit 0. Script
implementation and proof time were not separately instrumented. Both
reads are bounded at 90 seconds and do not install the native program.
Native caller action, whole-bound pricing and hosted checks were not run
for this finite result. Advance a new candidate only when a named
previously paid path can supply the omitted chart action or can be
composed without any intervening observation.

[#8052]: https://github.com/CrocSwap/integer-mult-bounds/pull/8052
[#8057]: https://github.com/CrocSwap/integer-mult-bounds/pull/8057
[#8027]: https://github.com/CrocSwap/integer-mult-bounds/pull/8027
[#7914]: https://github.com/CrocSwap/integer-mult-bounds/pull/7914
[packed predecessor from #8087]: https://github.com/CrocSwap/integer-mult-bounds/blob/aea1699415250d865f7a635f4df0b76f406c47b4/research/p104-period-debit-25bit/peer8057.tar.gz
