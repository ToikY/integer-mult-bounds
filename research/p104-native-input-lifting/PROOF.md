# Native helper input lifting

## Claim and source

Under the five inherited framework assumptions, the emitted supplier and
the unchanged p16/a7 caller give kappa `0.003129111`. The comparison is
PR6167's complete claim `0.003128645`. The direct word is PR6314's scalar
compression of PR6167. The source has 17,445 events. The new word has 17,452.

Write `Z` for the zero subspace, frame ID 3, and `Omega` for the full
nine-dimensional space, frame ID 127. Frame ID 0 is not `Z`.
All frame labels below are literal IDs in the emitted word.
Let `H_r = r^(1-kappa)` and `H_0 = 0`.

## Basis identity

Let `A` be the source preparation map from the inputs in `Z` to their scalar
values at their first departures. A helper direction `h` has support only on
helpers that start in `Z` and finish in `Omega`. Choose a primary helper `p`
with `h_p = 1`. In each construction, the preparation never writes to `p`.
Let `a = A h`. Suppose the first destination frame for each nonzero component
of `a` contains one subspace `F`.

Define

```text
B = I + (h - e_p) e_p^T.
B^-1 = I - (h - e_p) e_p^T.
```

The square of `(h - e_p) e_p^T` is zero. Thus `B` is invertible and has
determinant one. It changes only helper inputs. The source endpoint is the
identity on these helpers, so it commutes with `B`.

Start the existing independent input `x_p` in frame `F`. Omit its uses in the
initial preparation. This gives the response `A(x - e_p x_p)`. Deliver the
response `a x_p` at the stated later common frames. The sum is `A B x`.
Apply `B^-1` at the full output frame. This restores the source endpoint for
every input. No helper input is set to zero or replaced by a copy.

This identity alone does not establish a legal schedule. The constructor
states every delivery, move and output correction. The replay checks the
actual source frame of every operand and all independent input columns.

## Four directions and schedules

The four supports of `h` are disjoint. Their basis matrices commute.
Every coefficient is dyadic.

| Primary | New initial frame and basis | Input direction `h` | Departure response `a` |
| --- | --- | --- | --- |
| 496 | 595, `[52]` | `e496 - e639 - e643/2` | `h` |
| 649 | 597, `[82]` | `e649 - e648` | `h + e198` |
| 663 | 105, `[51]` | `e663 - e665` | `h + e179/2` |
| 508 | 1093, `[30,42,384]` | `e508 - e631 - e635/2` | `h` |

The verifier computes each response from the full scalar chronology.
It does not accept the displayed responses without a check.
Frame 1093 is the intersection of frames 118 and 733. It has dimension three.
Each other listed common frame has dimension one.

For primary 496, roles 639 and 643 first move from `Z` to frame 1027.
Role 496 first reaches frame 595 in the source. Replace these movements by:

```text
at Z:     639 -= 2 * 643
          move 639 from Z to 1027
          move 643 from Z to 595
at 595:   643 -= 496 / 2
          move 643 from 595 to 1027
at 1027:  639 += 2 * 643
```

Role 496 now starts at 595, so its old `Z -> 595` move is removed.
If roles 639 and 643 hold arbitrary values `v` and `z`, the displayed block
leaves `v - x496` and `z - x496/2`. The subtraction at `Z` removes the
carrier's old value from the later delivery. That value is not assumed zero.

Use the same block for primary 508 with roles `(631,635)`, destination 118
and intermediate frame 1093. Role 508 starts at 1093 and then moves to its
old first destination 733. No new owned field is used.

For primary 649, add its value to role 198 when role 198 reaches frame 597.
Move role 648 to frame 120 before role 649 arrives there. Move 649 from 597
to 120 and subtract it from 648. The original later move of 648 is removed.
The value of 649 is still its independent input at this subtraction.

For primary 663, move role 179 to frame 105 before role 663 leaves it and
add half of 663 to 179. Move role 665 to frame 1051, then move 663 from 105
to 1051 and subtract it from 665. Remove the two original later moves.
All later reads of roles 179 and 665 remain in their source order.

At frame 127, emit the six inverse-basis additions:

```text
639 += 496; 643 += 496/2; 648 += 649;
665 += 663; 631 += 508; 635 += 508/2.
```

`construct.py` guards all source event indices and all ten omitted initial
uses. It changes four initial frame declarations, appends frame 1093,
replaces twelve movement sites and appends the six output additions.
Every other event is copied. Protected contact events and frames 1091/1092
remain fixed.

## Exact scalar and native checks

The unchanged checker replays all 770 arbitrary public inputs and all 29 owned
columns. Each helper has its required independent output. Each main output
has its required input and shear contribution. Every owned lifetime is
initialized and cleared at its declared frame. Peak ownership is 13.

A separate reverse-chronology checker uses dense integer rows with binary
denominators. It checks all 799 columns and 638,401 endpoint coefficients.
The source and dense checks use different representations and directions.
Both are author checks made with credited predecessor code.

The native checker lowers every distinct chart change to a signed Clifford
recipe. A separate exact phase representation checks its signed Pauli images
and global phase. The 2,930 distinct maps include the changed helper
normalizers. It also checks 208 free main adapters and 1,124 helper
normalizers. Its tensor argument applies at each positive tensor width.
No free native transition is inferred from scalar endpoint equality.

Negative controls omit a carrier subtraction, reverse an injection, omit an
output correction, use the wrong input chart or intersection, or omit a
carrier move. Each fails the scalar or frame check. Native phase, caller
translation, missing price, missing target debit and damaged source controls
also fail. Explicit checks remain active with Python `-O`.

## Paid and productive profiles

Each of the three one-dimensional lifts has paid change `H4 - H5` and
target change `H8 - H9`. Its signed margin gain is

```text
H5 + H8 - H4 - H9.
```

This is positive for `0 < kappa < 1`: strict concavity gives
`H5 - H4 > H9 - H8`.

The three-dimensional lift has paid change
`H1 + H2 + H3 - H4 - H5` and target change `H6 - H9`.
Its signed margin gain is

```text
H4 + H5 + H6 - H1 - H2 - H3 - H9.
```

The exact complete price establishes the required total gain at the tested
kappa. No claim of positivity for this last expression at every kappa is needed.

The combined local paid change is
`H1 + H2 + H3 + 2 H4 - 4 H5`. The target change is
`H6 + 3 H8 - 4 H9`. Both rank totals decrease by six.
The general concave-order preflight is inconclusive for the complete bill:
its paid-minus-target hinge change is 18 at cap 1 and -108 at cap 5.
The claim therefore uses the exact power-moment checks below.

| Rank | Local paid jobs | Local productive targets |
| --- | ---: | ---: |
| 1 | 2217 | 14 |
| 2 | 457 | 8 |
| 3 | 497 | 4 |
| 4 | 100 | 107 |
| 5 | 161 | 14 |
| 6 | 8 | 3 |
| 7 | 9 | 9 |
| 8 | 1 | 22 |
| 9 | 0 | 381 |

The paid rank total is 5946. The scalar allowance is 127088. There are
770 independent public inputs, 29 owned labels and 32 owned lifetimes.

## Complete caller and price

The source p16/a7 caller is unchanged. Its literal Laurent replay checks all
boundary programs and all 18 forward local calls. The physical replay checks
7,488 contacts, all 53,248 central-square columns, main target phases and
every whole idle. Let `P_local` and `T_local` denote the table above. The
complete invoice is

```text
P = 18 P_local + 1560 H1
    + 208 sum_(l in {7,8}) sum_(j=1..l) H_(8(j+1)),
T = 18 T_local + 208 H145
    + 208 sum_(l in {7,8}) sum_(j=1..l) H_(1+8(j+1)).
```

It has 66,780 paid calls and 13,444 productive fields. Its rank surplus is
760. The maximum paid and productive ranks are 72 and 145. Two independent
censuses agree with the emitted caller. The target debit is included in both.

The strict raw crossing is in
`(0.00312911821812, 0.00312911821813)`. A rational derivative bound gives
uniqueness below the retained BIT cap `0.0034`. Two rational moment engines
give compatible intervals and a strict positive margin at
`TESTED = 0.003129116`. The old complete profile has a negative margin at
`KAPPA = 0.003129111`.

The inherited strictification uses power 1024, cutoff 16, floor 17, tail
offset `1/7`, reserve `10^-12` and decay `125/128`. All completion, tail,
splitting and rounding inequalities pass with the new invoice. The compiler
gap is `1/1400000000`. The integer threshold exponent is 47005 and
`H = 65807000000000`, so its declared uniform threshold is `N = 2^H`.
The predecessor integer threshold fails the same test. No such large word
is materialized.

The local scalar allowance plus the route and adapter allowance is below
`10^7`. The complete nonrecursive bound is 184647552, below the funded
budget `10^9`. It includes native helpers, adapters, routes, owned operations,
queries and caller boundaries. All 54 strict and four functional outer
predicates pass with the retained BIT admission.

`pricing.py` is the exact PR6167 price program with four declared text edits:
the two new kappa constants, the previous claim, the paid call count and the
result labels. `PRICING-EDITS.json` binds these edits. The verifier rejects
any other price-program change.

## Remaining obligations

The five framework assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. Native replay verifies
this finite construction inside that framework. It does not remove those
assumptions. The rounded integer multiplier is not constructed or benchmarked.
No independent scientific review or selected-frontier change is claimed.

The small gain does not establish that this mechanism scales to a large gain.
The published word and exact checks are the contribution. Finite discovery
screens are not lower bounds or proofs that other lifts are impossible.
