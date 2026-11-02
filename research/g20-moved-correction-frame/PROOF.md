# Moving one G20 correction frame does not lower the paid moment

## Object

The word is the emitted local scalar program in
`research/g20-conjugation-admission/WORD.json.gz`, the output of PR #5708.
Its scalar skeleton is the record list with `Q` and `ZERO_Q` removed.
`ADD(a, b)` means the characteristic-2 update `x_a <- x_a + x_b`. Two such
maps fail to commute when one destination is the other source.

An interval from one `ADD(a, b)` to a later equal `ADD(a, b)` is an **A2
conjugation of length k** when the open interval contains no `ERASE` or
`INIT` of `a` or `b`, contains exactly `k` noncommuting `ADD` records, and
each of those records has an A2 correction:

- `ADD(b, s)` with `s ≠ a` contributes `ADD(a, s)`;
- `ADD(d, a)` with `d ≠ b` contributes `ADD(d, b)`.

`ADD(b, a)` has no correction of this form. There are 765 such intervals
with `k ∈ {1, 2, 3}`. The constructor in #5708 places each contact and its
correction on one common frame `f`. The contact-frame case `f` equal to the
contact's published frame is the census in
`research/g20-short-conjugation-screen`. This proof moves **exactly one**
correction to a different frame and leaves every other correction on its
contact frame.

## Routes and endpoint

`PATHS.json` has 2,369 routes, and every route is one edge whose third
component is an integer rank from 1 through 7. A wire moves from its current
frame `u` to a frame `v` only along that edge. A missing edge means the
candidate does not emit. A nonzero scalar row pays one query of that rank;
a zero row pays nothing and still needs the edge when it moves. The paid
moment at exponent `t` is `Σ_r n_r r^t`.

The scalar endpoint ignores frames. Every non-owned column `i` must finish
as `e_i`, xor `e_{i-111}` when `111 ≤ i < 222`, and every owned column must
finish at zero. The published skeleton meets that identity, and so does
every one of the 765 corrected skeletons, because a frame change does not
alter an ADD's operands.

## Which frames can emit

Fix one correction and a candidate frame `f`. The emitter writes the contact
first and the correction immediately after it, both at `f`. A live ADD,
meaning its source row is nonzero, routes its destination and its source to
`f` before applying the sum. A dead ADD is omitted and does not read `f`.

The contact can change only the frames of its own two operands. Therefore a
correction operand that is not one of those two operands must already be
able to reach `f` from its pre-contact frame, and so must each contact
operand when the contact itself is live. The reachable frames of a wire are
its current frame and the heads of the published edges out of that frame.
Any `f` outside the intersection of those sets fails on the contact pair.
The verifier tests that necessity against an independent two-event replay
on every catalogue frame, for every contact of every interval. It then
replays the whole word, including later routes and the final return, for
every frame inside the intersection.

## Census

The fixed-frame screen reproduces the earlier count: 605 missing edges,
153 losses `2H1 − H2`, one loss `H1 + H2 + H4`, and 6 neutral words.
None of those 160 emitted words has a negative moment change on `(0, 1)`.

The one-move screen examines 28,149 frames in the intersections above.
28,123 do not emit. The other 26 emit, all from length-3 intervals:

| Paid change | Count | Sign on `(0, 1)` |
|---|---:|---|
| `H4` | 2 | `4^t > 0` |
| `5 H2 − 2 H4` | 24 | positive, proved below |

No emitted change is empty or equal to the known saving `H1 − 2H2 + H3`.
On every interval that emits at least one moved frame, a second replay tries
every catalogue frame, not only the intersection, and obtains the same
multiset of changes.

## Sign of `5 H2 − 2 H4`

Let `x = 2^t`. For `0 < t < 1`, the map `t ↦ 2^t` is strictly increasing and
`2^0 = 1`, `2^1 = 2`, so `1 < x < 2`. The change is

```text
5·2^t − 2·4^t = 5x − 2x^2 = x(5 − 2x).
```

Here `x > 1 > 0`. Also `2x < 4`, so `5 − 2x > 1 > 0`. The product is
therefore positive. The same bound at the closed edge `x = 2` is
`2·2 − 5 = −1 < 0` for the factor `2x − 5`, which is the integer check
recorded by the verifier; the open interval stays strictly above that edge.

## What this does not say

The screen does not rebuild the 18-call caller, the adjoint, the moduli
101 and 10201, or the ordinary-admission arithmetic. It does not move two
corrections in the same interval, add a route, or accept a length of four
or more. Length four and above at the original contact frames is the
separate result of PR #6305. Paths through neutral rewrites with correction
frames held fixed are the separate neutral two-step obstruction. The six
neutral one-step neighbors and the 645 common-frame expansions named in the
#5708 README still have no executable definition in that package. No
selected-frontier update follows. The selected conditional exponent remains
`781451/250000000`. Full-history source preflight was not run in this
shallow checkout; the recorded base commit and input hashes are the pins.
