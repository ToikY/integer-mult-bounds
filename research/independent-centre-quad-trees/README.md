# Independent four-contact trees keep a sharp positive paid cost

Every induced four-contact tree in the fixed retained 640-input centre graph
raises the complete paid moment by at least

    3 - 2^theta + 7^theta - 8^theta > 0,   0<theta<1,

when its four empty charts move independently to nontrivial one-transvection
neighbours and every helper target stays fixed. One induced path and one label
assignment attain the bound for every such theta. The internal graph's only
connected four-vertex blocks are 716 paths, 160 claws and 62 four-cycles. This
certificate prices the paths and the claws.

This is a **scoped proof with an exact finite certificate**. The selected
frontier remains κ = 781451/250000000 from PR6030. No supplier is admitted.

## Result and predecessors

[PR6306](https://github.com/CrocSwap/integer-mult-bounds/pull/6306), by Nick
Petalas, proves the same lower bound for every induced three-contact path and
asks for a declared four-vertex tree as the next paired-label test. Its package
is `research/independent-centre-triples`. The present certificate answers that
question for every induced four-vertex tree on the same graph. The 62 induced
four-cycles are counted and left unpriced. PR6306 is consumed as a published
predecessor; its checker is not imported and its files are unchanged.

The question PR6306 answered was posed by unpaidmoon's
[PR6289](https://github.com/CrocSwap/integer-mult-bounds/pull/6289). Chris R /
Clear1nsight's [PR4867](https://github.com/CrocSwap/integer-mult-bounds/pull/4867)
and [PR4888](https://github.com/CrocSwap/integer-mult-bounds/pull/4888) supply
the retained graph and the earlier coherent and pair ceilings. The four-contact
argument uses a new min-plus chain for a path of three edges and a three-leaf
claw reduction. Both are equalities on the full 1,022-label domain. See
[PROOF.md](PROOF.md).

The fixed-contact floor in
[PR5590](https://github.com/CrocSwap/integer-mult-bounds/pull/5590) and the
projection floor in
[PR5324](https://github.com/CrocSwap/integer-mult-bounds/pull/5324) hold the
data this experiment changes. The bounded star in
[PR5161](https://github.com/CrocSwap/integer-mult-bounds/pull/5161) has two
prescribed leaf alternatives and fixed owned-centre boundaries. Schematic
four-contact questions in other graphs, including length-9 numerator splits and
G20 conjugation words, are different objects.

The certificate visits all 716 induced paths, all 160 induced claws and all
nine capped-rank tariffs. Componentwise path minima are
`(2,1,1,1,1,1,1,0,0)`. Claw minima are `(4,3,3,3,3,3,3,2,2)`, attained by
centre `11014` and leaves `10945,11013,11015` at label 59, with histogram
change `{0:-4,1:5,2:-1,7:1,8:-1}`. Node path
`(11013,11014,11015,11016)`, with label 59 at each node, attains the path
vector. Its paid-histogram change is `{0:-2,1:3,2:-1,7:1,8:-1}`. Moving the
fourth node to that same label cancels: the edge into node 11015 stays at rank
0, two empty-chart edges rise from 0 to 1, and the edge into node 11209 falls
from 1 to 0. All 408 helper targets and the zero independent centre reward stay
fixed.

Family status, revision 7, treats a local geometry obstruction as a place to
stop unless a changed producer still has a fully charged consumer. This package
stops at induced four-vertex trees.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -W error -B research/independent-centre-quad-trees/verify.py
python3 -W error -O -B research/independent-centre-quad-trees/verify.py
python3 -B scripts/research_package.py --package research/independent-centre-quad-trees
python3 -B scripts/check_research_commit.py --package research/independent-centre-quad-trees --check-source-history
```

Expected markers are `PASS_INDEPENDENT_CENTRE_QUAD_TREES`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
`VERIFY.json` registers both complete normal and optimized checks with
120-second limits. Set `TMPDIR` to an existing scratch directory to place the
temporary graph and source-control files there. Optional
`--output /absolute/external/path.json` writes a generated receipt containing
package-file hashes, every minimum class and the literal attaining witnesses.
Writing that receipt inside the checkout is rejected.

The direct checker compares every label pair in widths 1 through 5 with the
paired geometry, 99 transforms with full independent-label oracles, and 24
path products and 24 claw products with exhaustive four-factor minimization.
Census fixtures cover an induced path, an induced claw, a chordal path, an
induced four-cycle and a duplicate edge. Five invalid transform inputs, three
changed graph contracts and four source-byte mutations are rejected. Proof
checks use explicit exceptions and remain active under `-O`. The
selected-binding orientation passed at the pinned base.

[SOURCES.json](SOURCES.json) pins base
`626e936ce4d61f2584316914fc71baf96940c512`, catalogue revision 8 and every
runtime source. [TASK.json](TASK.json) records the changed task premise.
Generated evidence stays outside the checkout.

## Limits

The optimistic paid moment of this chart contract is strictly higher while the
408 productive targets stay fixed. Unknown native, delivery and restoration
costs are not given a zero price; they are outside the priced bill, and the
paid side is already strictly worse. The result is specific to this retained
graph. Cycles, blocks of five or more contacts, changed routes and changed
helper targets remain open. No native amplitudes, physical caller, restoration
schedule, rounding, precision or tape proof, compiler closure, selected cold
replay, Lean proof or outer theorem was run. All five selected framework
assumptions remain. Independent human and formal proof-kernel review are
unclaimed.

## Open next questions

1. Can one of the 62 induced four-cycles improve the same fixed-graph invoice
   under independent one-transvection charts? The tree transform does not apply
   to a chord. The smallest useful step is a joint elimination for one
   four-cycle, with every incident edge still charged and every helper target
   fixed. No cycle identity or favourable cycle candidate is supplied here.
2. Can a five-contact tree, or a changed route or helper target, produce a
   favourable complete bill on this graph? Internal degree is at most 3, so
   the next tree is a longer path or a claw with one extra edge. A changed
   physical mechanism still needs its own endpoints and a complete
   paid/productive bill. Neither object is enumerated here.

## Implementation bounds

New loops have finite domains: widths at most nine, 18 binary coordinates,
1,022 labels, 176 empty-chart contacts, 716 paths, 160 claws, 62 cycles, nine
prefixes and the 34,830-edge source graph. Radius-3 balls are rejected above
40 vertices, and ball combinations are rejected above 24 other vertices. No
recursion is used. Source-byte hashes are checked before import. The original
builder and its two pinned imports are unchanged. Each transform retains a
minimizing label. Direct incident-edge walks check every source minimizer, and
one full edge scan checks the sharp witness.

Power-of-Ten rule 3 deviation: CPython and its standard library allocate during
execution. Live collections are bounded by the domains above, with at most
`176*9*1022` unary entries and one transform table of that width per prefix
evaluation. Temporary outputs have one context-managed lifetime. Fixed memory
pools would require a different runtime. If this checker becomes a service or
accepts a larger graph, add an enforced input capacity and a separate measured
memory budget before widening these bounds.

Rule 8/9 deviation: one authenticated graph builder is loaded through Python's
module loader. The target is a fixed pinned file and its two pinned imports.
There is no plugin dispatch. Generic source-bound replay is the reason for
retaining this boundary. Warning-strict normal and optimized checks, together
with the source and graph mutations, cover it. No repository-wide tooling
change is included.

## Credit

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Credit Nick Petalas / PR6306 for the three-contact theorem, the paired
transform and the four-vertex question; unpaidmoon / PR6289 for the independent
chart question; Chris R / Clear1nsight / PR4867 and PR4888 for the retained
graph and coherent/pair ceilings; Cinna Davis / PR4694, PR4698 and PR4690 for
the retained-centre interface; Cao Yifan / PR4610 for the native word; David
Ganz / Dugongue / PR4841 for the chart-neighbour framework; and the retained
PR4470, scalar, E8, Clifford, helper, precision, compiler and caller lineage.
Binary Lagrangian geometry, min-plus elimination and concave summation by parts
are classical. The new contribution is the four-contact census and the sharp
tree certificate. Predecessor files and notices remain unchanged.
