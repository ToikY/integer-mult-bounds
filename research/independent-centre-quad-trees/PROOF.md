# Sharp obstruction for independent four-contact trees

This is a scoped proof, with an exact source-specific finite certificate.
It concerns the retained 640-input centre-contact graph of Chris R's PR4867
and PR4888, built on Cinna Davis's retained-centre interface and Cao Yifan's
PR4610 word. The three-contact theorem in Nick Petalas's PR6306,
`research/independent-centre-triples`, prices every induced rank-zero path of
length two and leaves induced four-vertex trees open. This note prices those
trees. It does not re-audit the three-contact proof.

## Statement

Freeze every source chart except the four contacts of one connected block whose
induced internal subgraph is a tree. The internal graph on the 176 empty-chart
variable contacts has 256 rank-zero edges. In that graph every connected
induced subgraph on four vertices is one of 716 paths, 160 claws, or 62
four-cycles, and these three families are disjoint. The theorem covers the
716 paths and 160 claws.

Replace each of the four charts independently by any nontrivial one-transvection
neighbour of the empty chart. Keep every incident edge charge, every native
map, every boundary and all 408 productive helper targets unchanged. For every
such block and every `0<theta<1`, the complete paid-moment change satisfies

    Delta(theta) >= 3 - 2^theta + 7^theta - 8^theta > 0.

The bound is sharp for every such theta at once. In the graph's zero-based
node numbering, the induced path `(11013,11014,11015,11016)` with neighbour
label `59` at all four nodes has rank-histogram change

    delta_0 = -2, delta_1 = 3, delta_2 = -1, delta_7 = 1, delta_8 = -1,

and every other delta zero. Rank-zero edges have cost zero, so this histogram
attains the displayed bound. Label 59 is normal 30, tag 1, transvection axis
1054. The same numerical histogram is the three-contact witness on the first
three nodes. The fourth contact changes the histogram by zero, through the
explicit four-edge cancellation recorded below. That cancellation is a property
of this witness, not an identity for an arbitrary fourth label.

Every induced claw has capped-rank prefix vector at least

    (4,3,3,3,3,3,3,2,2),

strictly above `(2,1,1,1,1,1,1,0,0)` in every coordinate. No claw attains the
path bound. The claw floor is attained by centre `11014` with leaves
`10945,11013,11015`, again at label 59 on every contact. Its histogram is

    delta_0 = -4, delta_1 = 5, delta_2 = -1, delta_7 = 1, delta_8 = -1.

The 62 induced four-cycles are not priced.

The argument is an exact reduction over the whole independent label domain,
followed by finite integer minimization. It does not sample label tuples or
screen a list of theta values.

## Four-vertex trees and the source census

A tree on four vertices has three edges, so its degree sum is 6, and every
degree is a positive integer. Maximum degree at least 4 forces degree sum at
least 7. Maximum degree 3 forces the degrees `3,1,1,1`: the claw, with the
centre joined to every leaf and with no leaf-leaf edge. Maximum degree at most
2 forces the degrees `1,2,2,1`: the path. Thus every four-vertex tree is a
path or a claw.

On the source internal graph the constructive enumerations and a radius-3 ball
census agree:

- an induced path is recovered once from its unique middle edge, oriented from
  the smaller endpoint to the larger, and again by extending every induced
  three-vertex path one step at either end;
- an induced claw is every centre together with three neighbours and no edge
  among those neighbours;
- an induced four-cycle is recovered once per vertex set by using each edge as
  a side, and again from its two pairs of nonadjacent opposite corners;
- every connected four-vertex subset appears in the radius-3 ball of its
  smallest vertex, and the induced degree sequences are exactly
  `(1,1,2,2)` for 716 sets, `(1,1,1,3)` for 160 sets and `(2,2,2,2)` for 62
  sets.

A connected graph with degree sequence `(2,2,2,2)` is a four-cycle. No other
connected induced four-contact block exists in this graph. Sixteen empty
contacts have internal degree 2 and 160 have internal degree 3, so each claw
uses the entire neighbourhood of its centre. Every empty contact still has
four incident edges in the full graph, counting edges that leave the empty
set. The paid histogram of the whole source is

    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8},

productive helper targets remain `{4:28,7:7,8:47,9:326}`, and the independent
centre reward remains zero. Edges incident to a variable contact use the
identity native map.

## Paired neighbour geometry

Write the ambient space as `F_2^n x F_2^n` with coordinates `(x,z)`, and the
empty Lagrangian as `L_0={(0,z)}`. For each nonzero normal `x`, let `j` be its
least nonzero coordinate. The two transvections with axes `(x,0)` and `(x,e_j)`
are exactly the two Lagrangian neighbours whose intersection with `L_0` is the
hyperplane `H_x={(0,z): x dot z=0}`. A distance-one neighbour meets `L_0` in
some `H_x`. Every vector in its other coset has first coordinate `x`, because
isotropy makes that coordinate annihilate `H_x`. Modulo `H_x` the second
coordinate has two possibilities, distinguished by its dot product with `x`.
Both transvections occur. Every nontrivial transvection image has distance
one from `L_0`, so this is the full one-transvection domain. It contains
`2(2^n-1)` charts.

Zero-based labels place the two images of normal `x` at `2(x-1)` and
`2(x-1)+1`, in the axis order above. Partners are therefore `k xor 1`. Here
`n=9`, so there are 1,022 labels. Two labels have Lagrangian distance 0 when
they agree, 1 when they are partners, and 2 otherwise. Partners intersect in
`H_x`. Distinct normals `x,y` intersect in `H_x intersect H_y`, of dimension
`n-2`. This is the three-valued distance used by the elimination. The checker
also compares it with literal frame ranks for every pair in widths 1 through 5.

## Exact elimination on a tree

For `j=1,...,9` write `h_j(r)=min(r,j)` and `h_j(0)=0`. Let `U_v^j(k)` be the
sum of the changes of `h_j` over edges incident to `v`, when only `v` moves to
label `k` and every other endpoint keeps its source chart. These unaries are
recomputed from the source frame bases by binary elimination. No stored
single-contact or pair receipt supplies them.

Every one-transvection chart meets the empty chart in codimension 1. On an old
rank-zero internal edge whose other end stays empty, one unary therefore adds
`1` for every `j>=1`. If both ends move, the two unaries contribute `2`, while
the true capped change on that edge is `min(d(i,k),j)`. The correction is

    C_j(i,k) = min(d(i,k),j) - 2.

Edges with neither end in the block cancel. An edge with only one end in the
block is already exact inside that end's unary, because the other chart is the
unchanged source chart. The only edges with two ends in an induced tree are
the tree edges. The path and claw formulas below count each of those once.

For a vector `f` define `T_j f(k)=min_i[f(i)+C_j(i,k)]`. The paired geometry
gives

    T_j f(k) = min(
        f(k)-2,
        f(k xor 1)-1,
        min_{i outside k's pair} f(i) + min(2,j)-2
    ).

The outside minimum is the better of the two smallest pair-minima after the
current pair has been excluded, even when the global minimum lies in the
current pair. Each alternative is attained by a label, and the implementation
keeps one minimizing label.

On an induced path `a-b-c-d` the exact prefix change at labels `(i,k,l,m)` is

    U_a(i)+U_b(k)+U_c(l)+U_d(m)+C(i,k)+C(k,l)+C(l,m).

Group the expression from the left. Set `g(k)=U_b(k)+T U_a(k)`, then
`h(l)=U_c(l)+T g(l)`. The minimum is `min_m U_d(m)+T h(m)`. For each fixed
right-hand label the transform attains its left-hand minimum, and that choice
does not depend on any label further to the right. The domain is finite, so
the three successive minima equal the minimum over all four labels. This is
the same equality for a path of three edges that PR6306 records for a path of
two edges. It is not the sum of two separately optimized pair invoices.

On an induced claw with centre `b` and leaves `a,c,d`, there is no leaf-leaf
edge. At a fixed centre label `k` the three leaf corrections are independent,
and the exact minimum is

    min_k [U_b(k) + T U_a(k) + T U_c(k) + T U_d(k)].

A chord would add another correction and would identify two leaves, so neither
formula applies to a cycle or to a non-induced path.

## Source certificate

The pinned builder regenerates the graph with 19,197 nodes, 4,429 frames and
34,830 positive paid edges. The checker solves nine prefix problems on each of
the 716 paths and 160 claws: 7,884 integer minimizations. For every minimizing
label tuple it recomputes the incident-edge rank histogram and requires the
corresponding prefix coordinate to equal the reduction. One full-edge scan of
the sharp witness matches the incident index. Across the paths the
componentwise minima are `(2,1,1,1,1,1,1,0,0)`. Across the claws they are
`(4,3,3,3,3,3,3,2,2)`. One claw assignment, named above, meets that vector in
every coordinate at once.

The named sharp assignment was evaluated directly, not inferred from the
per-prefix argmin. Its histogram is the vector displayed in the statement, and
its nine prefixes equal the path floor. The receipt's per-coordinate witnesses
are the first minimizing block in path order. For prefixes 8 and 9 that block
is `(10944,11013,11014,11015)`, whose own earlier prefixes lie above the floor.
The named assignment still meets every coordinate, including those two zeros. Relative to the same three labels on
`(11013,11014,11015)`, moving node `11016` to label 59 makes exactly these
rank changes:

- edge `(11015,11016)` no longer rises from rank 0 to rank 1, because both
  ends carry label 59 and the Lagrangian distance is 0;
- edges `(10947,11016)` and `(11016,11017)` rise from rank 0 to rank 1;
- edge `(11016,11209)` falls from rank 1 to rank 0.

The added changes contribute `delta_0=-1-1+1` and `delta_1=+1+1-1` before
accounting for the removed rise, and the removed rise contributes
`delta_0=+1`, `delta_1=-1`. The marginal histogram is zero. The four-contact
witness therefore has the same paid-moment change as the three-contact witness
on its first three nodes.

Small controls, separate from the source minimum, compare the transform with
the full label product, compare both tree reductions with the full four-label
product on domains of 4 and 6 labels, and reject a chordal path, a duplicate
edge, an invalid transform input, a negative charge, a changed contact map, an
invalid rank and each altered source file.

## From prefixes to every concave power

For a histogram change `delta` define

    S_j = sum_{r=1}^9 delta_r min(r,j),
    q_j = j^theta - (j-1)^theta.

Summation by parts gives

    Delta(theta) = sum_{j=1}^8 S_j (q_j-q_{j+1}) + S_9 q_9.

Every coefficient is positive for `0<theta<1`. Every tree assignment has
`S_j >= m_j` for `m=(2,1,1,1,1,1,1,0,0)`, whether or not the minimizing labels
of the nine prefixes coincide. Hence

    Delta(theta) >= 2(q_1-q_2) + sum_{j=2}^7 (q_j-q_{j+1})
                 = 3 - 2^theta + 7^theta - 8^theta.

The right-hand side is `(2-2^theta)+(1+7^theta-8^theta)`. The first summand is
positive for `theta<1`. The second is positive because `t |-> t^theta` is
strictly subadditive at `8=1+7` when `0<theta<1`. The sharp histogram has
`S=m`, so equality holds for every theta in the interval. The claw floor is
recorded because it is exact. It is not needed for this lower bound: the path
floor already covers every claw, and the claw expression
`4-2^theta-8^theta` changes sign on `(0,1)`.

## Boundary

The identities and the finite census prove the obstruction for every induced
four-contact tree in this fixed graph, for the whole interval `0<theta<1`.
They do not prove a source-independent floor. The 62 induced four-cycles,
every block of five or more contacts, nonempty original charts, second-step
neighbours, changed operations, routes, native maps, helper targets and
endpoints remain outside the priced contract. No new paid improvement, native
construction, physical restoration, rounded implementation, compiler closure,
supplier admission or multiplication theorem is established. The selected
frontier stays the PR6030 conditional record.
