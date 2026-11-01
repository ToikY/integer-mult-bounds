# Idle registers do not lower the span-(m+1) line bound

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
This is a written scoped proof. The finite checks in `verify.py` corroborate
algebraic steps; they are not a substitute for the argument and they are not
proof-kernel verification.

## 1. Model

Fix an address dimension `m >= 1`, a data-register count `t >= 1` and a helper
count `r >= 0`. Set `n = t + r`. Work in the group algebra `R = F_2[M_m(Q)]`
of the additive group of rational `m x m` matrices, with `[A][B] = [A+B]`.
The identity element is `[0]`. A paid call is

    D_N([A]) = I_n + ([A] - 1) N,    rank_Q(A) = 1,    N = x y^T,    y^T x = 1,

with `x, y` in `F_2^n`. A word of `k` paid calls is required to satisfy

    prod_j D_{N_j}([A_j]) = diag([C_1], ..., [C_t], [H_1], ..., [H_r]),   (1)

where every `C_s` is invertible and every helper exponent `H_j` is an
arbitrary single matrix. A clean helper has `H_j = 0`. A dirty helper may
carry any monomial `[H_j]`. Equality is of every formal coefficient. There
is no free address map between calls.

This is the scalar-idempotent model of eumemic's PR #288, section 1.2, as
used by Ali Romman's PR #468 and by Nick Petalas's
`research/span-lemma-every-dimension`. Those statements take `r = 0` and
require every diagonal entry to be invertible. The one-relation theorem in
`research/bit-one-relation-any-registers` already allows arbitrary `n` when
the frames have at most one rational relation. It is not reused as a lemma
here; the span window below is the complementary small-span regime.

Let `S` be the rational span of the paid frames. As in PR #468, section 3,
every exponent that survives in (1) lies in `S`, because a diagonal entry is
an `F_2`-combination of subset sums of frames and the surviving symbol is a
single group element.

## 2. Statement

**Theorem.** Suppose `dim S <= m + 1`, and write the normalized extra frame
of `research/span-lemma-every-dimension`, section 3, as `u v^T` with
`K = supp(u) ∩ supp(v)`.

1. If `dim S <= m`, or `dim S = m + 1` and `|K| != 2`, then `k >= m t`.
2. The same word with `r` clean helpers attains `k = m t`.

Identity helpers and arbitrary dirty monomial helpers therefore do not lower
the call bound in every case that the predecessor reduces to its Lemma A
(the line projection) or to the triangular diagonal projection. The
`|K| = 2` flag bound is not extended.

No new κ follows. The selected record stays the value pinned in
`certificates/selected-result.json`.

## 3. Rank of a rank-one product

**Lemma R.** Over a commutative ring, let `a_j` be scalars and let
`x_j, y_j` be column vectors. Then

    P = prod_{j=1}^{k} (I + a_j x_j y_j^T)

satisfies `rank(P - I) <= k` whenever the scalar ring is an integral domain
and the rank is computed over its fraction field. Idempotence of the
updates is not required.

*Proof.* Proceed by induction on the column space. The case `k = 0` is
`P = I`. If the columns of `P_{j-1} - I` lie in `span{x_1, ..., x_{j-1}}`,
then

    P_j - I = (P_{j-1} - I) + a_j x_j (y_j^T P_{j-1}).

The row `y_j^T P_{j-1}` is a coordinate row, so the second summand has
columns in `span{x_j}`. The columns of `P_j - I` lie in
`span{x_1, ..., x_j}`. ∎

PR #468, section 2, records the sharper triangular factorization
`P = I + X T Y^T` for the idempotent case. Lemma R is the only rank input
used below.

## 4. Line projection with helpers

**Lemma A'.** Let `b_0, ..., b_s` be a basis of `S` made of rank-one
matrices, and suppose every paid frame is a rational multiple of one
`b_i`. Then

    k >= sum_{s=1}^{t} nnz(C_s) >= m t,

where `nnz` is the number of nonzero coordinates in this basis. Helper
exponents do not appear on the right-hand side.

*Proof.* Let `phi_i` be the `i`th coordinate functional on `S`. The rule
`[A] -> [phi_i(A)]` is a ring homomorphism from `F_2[S]` onto its image in
`F_2[Q]`. Apply it entrywise to (1). A call whose frame lies on another
line has `phi_i(A_j) = 0`, so that call maps to `I`. Let `k_i` be the
number of calls on line `i`. Lemma R, applied over the fraction field of a
Laurent polynomial domain, gives rank at most `k_i` for the image of the
product minus `I`.

The image of the right-hand side minus `I` is the diagonal matrix with
entries `[phi_i(C_s)] - 1` and `[phi_i(H_j)] - 1`. In that fraction field,
`t^c - 1 = 0` if and only if `c = 0`. The rank of a diagonal matrix equals
the number of nonzero diagonal entries, so the rank is at least the number
of data indices with `phi_i(C_s) != 0`. A helper can add a nonzero entry.
It cannot cancel a data entry, because the output is diagonal. Therefore
`k_i >= #{s : phi_i(C_s) != 0}`.

A frame lies on at most one line: it is a multiple of a single basis
matrix. Summing over lines gives `k >= sum_s nnz(C_s)`. Each `C_s` is a
sum of `nnz(C_s)` rank-one matrices, so `m = rank(C_s) <= nnz(C_s)`. ∎

The clean case `H_j = 0` has `phi_i(H_j) = 0` on every line, so those
diagonal entries contribute nothing. That is the identity-helper case asked
for by the predecessor's open question.

## 5. The three address cases that reduce to a projection

The normalization in `research/span-lemma-every-dimension`, section 3, is a
change of address coordinates `A -> P A Q`. It is an automorphism of the
additive group, preserves rank, and does not depend on `n` or on which
diagonal entries are invertible. Invertible targets remain invertible, and
the zero matrix remains zero. After that normalization the predecessor's
address lemmas apply verbatim. They never mention the register count.

**Dimension at most `m`.** An invertible `m x m` matrix cannot lie in a
rational matrix space of dimension less than `m`. Thus `dim S = m`. PR #468's
low-span lemma puts `S` on `m` diagonal lines `E_ii`, and every paid frame
in that diagonal space is a multiple of one `E_ii`. An invertible diagonal
matrix has every diagonal entry nonzero, so `nnz(C_s) = m`. Lemma A' gives
`k >= m t`.

**`|K| >= 3`.** Lemma C of the predecessor says every rank-one matrix of
`S` lies on one of the `m + 1` lines spanned by `E_00, ..., E_{m-1,m-1}` and
`B = u v^T`. The minor identity used there is an address calculation. Lemma
A' again gives `k >= m t` for arbitrary invertible data targets.

**`|K| <= 1`.** The predecessor's Lemma D makes `S` triangular after a
permutation. Each transformed data target is invertible and triangular, so
all `m` diagonal entries are nonzero. A rank-one triangular matrix has at
most one nonzero diagonal entry: two nonzero diagonal entries `i` and `j`
would force both off-diagonal entries of that `2 x 2` block to be nonzero,
because a rank-one matrix is an outer product. Projecting onto that
diagonal coordinate, as in Lemma A', assigns each paid call to at most one
coordinate and shows that each coordinate is hit by at least `t` calls.
Hence `k >= m t`.

## 6. What stays open at `|K| = 2`

The predecessor's `|K| = 2` case cites PR #468's block flag bound: `2W`
calls on the `2 x 2` block and `W` calls on each `1 x 1` block, using that
every one of the `W` targets has invertible diagonal blocks. A clean helper
has exponent `0`, whose diagonal blocks are zero, not invertible. Lemma A'
does not apply, because Lemma C fails at `|K| = 2` (the predecessor's
explicit off-line example `u = v = (1, 1, 0)`, `D = diag(2, 2, 0)`,
`t = -1`). This note does not claim `k >= m t` for that case.

## 7. The bound is attained with any number of clean helpers

Write each invertible `C_s` as a sum of `m` rank-one matrices and apply
those `m` frames with the coordinate projector `E_{ss}`. No call touches a
helper register, so each helper stays at `[0]`. The product is (1), the
frame span has dimension at most `m`, and `k = m t`. Adding clean helpers
does not create a shorter word in the regimes of section 5, and it does
not increase the direct cost.

## 8. Neighbouring results that do not already contain this statement

- PR #468 proves `k >= m W` when `r = 0` and `m = 3` for span at most 4.
  Its statement excludes extra registers.
- `research/span-lemma-every-dimension` extends that span bound to every
  `m`, still with `r = 0`. Its open question 3 asks whether Lemma A
  survives identity helper targets. Sections 4 and 5 answer that question
  for every case the predecessor reduces to a line or diagonal projection.
- `research/three-data-aux-direct` checks one direct nine-call word and the
  pigeonhole for eight coordinate projectors on four roles. It does not
  treat a general frame on a line, and it leaves the 120 four-register
  projectors unclassified. Lemma A' is the projection those coordinate
  assignments instantiate.
- `research/bit-one-relation-any-registers` removes the register-count
  restriction when `dim S >= k - 1`. Two or more relations remain open
  there. This note does not re-prove the one-relation regime.
- The GL3 census behind PR #1974, recorded in
  `research/bit-gl3-mixed-targets-length10`, uses two registers, the
  finite alphabet of coordinate CNOTs in `F_2[GL_3(F_2)]`, and free
  `GL_2(F_2)` mixing. PR #2027's mixed-root tariff is a UT4 quotient.
  Neither alphabet is the rational matrix group used here, so neither
  census is a special case of Lemma A' or a counterexample to it.

## 9. Scope

This is a formal group-algebra bound. It gives no native schedule, no
hosting or precision bill, and no change to the selected frontier. It does
not cover frame span `m + 2` or more, free address maps between calls, or
the `|K| = 2` block with helper registers.
