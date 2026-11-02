# Idle helpers do not lower the span-(m+1) line bound

**Scoped negative result; no new kappa.** In the abelian scalar-idempotent
register model, `t` invertible `m x m` rational targets plus any number of
clean or dirty monomial helper registers still need at least `m t` paid
calls when the paid-frame span has dimension at most `m + 1`, except in the
normalized `|K| = 2` block. The direct coordinate word attains `m t` and
leaves every clean helper at the group identity.

This answers open question 3 of
[`research/span-lemma-every-dimension`](../span-lemma-every-dimension/README.md):
Lemma A's line projection survives identity helper targets. Extra registers
do not escape that part of the three-register obstruction.

The selected frontier is unchanged. On this base,
`certificates/selected-result.json` records
`781451/250000000`.

## Result

Let `S` be the rational span of the paid frames and let `K` be the support
intersection of the normalized extra frame `u v^T`.

| Hypothesis | Bound | Helpers |
| --- | --- | --- |
| `dim S <= m` | `k >= m t` | clean or arbitrary monomials |
| `dim S = m + 1` and `|K| >= 3` | `k >= m t` | clean or arbitrary monomials |
| `dim S = m + 1` and `|K| <= 1` | `k >= m t` | clean or arbitrary monomials |
| `dim S = m + 1` and `|K| = 2` | not extended | flag bound still assumes invertible blocks |
| direct word | `k = m t` | any number of untouched clean helpers |

[PROOF.md](PROOF.md) gives Lemma R (rank of a rank-one product) and Lemma A'
(line projection with helper outputs), then invokes the address normalization
from the predecessor. That normalization does not depend on the register
count.

## What was compared before the proof

The card's first experiment names the #1974 GL3 census and the #2027
mixed-root tariff.

- `#1974`, as recorded in `research/bit-gl3-mixed-targets-length10`, is a
  two-register census in `F_2[GL_3(F_2)]` with coordinate-CNOT labels and
  free `GL_2(F_2)` mixing. It is not the rational matrix group used here.
- `#2027` is a UT4 mixed-root tariff. It does not convert these rational
  frames.
- `research/bit-one-relation-any-registers` already allows every register
  count when the frames have at most one rational relation. This note does
  not reprove that regime. The small-span window is the complementary case.
- `research/three-data-aux-direct` checks eight coordinate projectors on
  four roles. Lemma A' is the projection those assignments instantiate; it
  is not a classification of the 120 four-register projectors.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 -I -W error -B research/span-lemma-idle-helpers/verify.py
python3 -I -O -W error -B research/span-lemma-idle-helpers/verify.py
python3 scripts/research_package.py --package research/span-lemma-idle-helpers
```

Both verifier commands print `PASS_SPAN_LEMMA_IDLE_HELPERS`. The package
command prints `PASS_REGISTERED_RESEARCH_PACKAGE`. A passing run reports
28 and 120 idempotents, 14400 pair products, a diagonal one-line grid,
direct words for 0, 1 and 2 clean helpers, the `(3,3,2,0)` rank-2 failure,
a three-coordinate block call that is not the direct word, and zero
eight-call covers of three lines.

The pair check evaluates every `3 x 3` minor of `(I + a N)(I + b M) - I`
at `a, b in {1, 2, 3, 5}`. Each minor has degree at most 3 in each scalar,
so those four values certify that the minor polynomial is identically zero.
The grid is a control for Lemma R. The induction in PROOF.md is the proof.

## Limitations

- `|K| = 2` with helper registers is open. The predecessor's off-line
  example shows that frames need not lie on the diagonal-plus-`B` lines.
- Span `m + 2` and two or more frame relations are open. One idle register
  does not remove the two-relation hypothesis already stated in
  `research/bit-one-relation-any-registers`.
- No native schedule, hosting bill, precision bill, or selected-frontier
  change is claimed. Unknown physical costs are not zero; they are outside
  this formal identity.

## Open next questions

1. Does the `|K| = 2` flag bound still give `k >= m t` for clean identity
   helpers? The cited `2W` count assumes every diagonal block is invertible,
   and a clean helper has zero blocks. First step: recompute the
   dimension-two flag inequalities at `m = 3` with `t` invertible targets
   and `r` zero targets. Blocker: Lemma C fails at `|K| = 2`.
2. Can one idle register together with two independent frame relations
   realize three invertible targets in fewer than `m t` calls? First step:
   fix `m = 3`, `t = 3`, `r = 1` and one explicit span-5 frame list, and
   decide whether any eight-call word exists. Blocker: the two-relation
   Laurent kernel is not principal.

## Credit

The model is eumemic's PR #288, section 1.2. The low-span lemma, the `m = 3`
span-four argument and the block flag bound are Ali Romman's PR #468
(`research/bit-three-register-lower-bound`). The all-dimension span lemma
and its open question 3 are Nick Petalas's
`research/span-lemma-every-dimension`. The arbitrary-register one-relation
theorem is `research/bit-one-relation-any-registers`. The coordinate
auxiliary check is `research/three-data-aux-direct`. The GL3 census
comparison uses Hanson Sun's seed and the length-10 closure in
`research/bit-gl3-mixed-targets-length10`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
