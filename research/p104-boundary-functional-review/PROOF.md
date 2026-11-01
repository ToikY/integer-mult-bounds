# The #5718 boundary functionals differ, and cleanup order is forced

## Pinned objects

The source word is the `WORD.json.gz` member
`research/p104-temporal-updates/WORD.json.gz` inside
`research/p104-two-boundary-helper-split/inputs/pr5713-source.tar`.
Its canonical JSON SHA256 is
`32adce6656e49aa020d3e6317f1c45c11fccadeeb67a8d506172d101703d2138`.
The published candidate is
`research/p104-two-boundary-helper-split/WORD.json.gz`, canonical SHA256
`a1c8277189a811546bdc7b147d72e6a594504ff9585c9bf59a5681aa873abb01`.
Neither file is modified. The predecessor constructor is not imported.

## Two functionals

Replay the source through event 14330, the pinned move
`MOVE 119 602 -> 684`. Rows start at the identity. Write `a` for row 708
and let `c` be half of row 154. The input carrier is `h = a + c`. It has 88
terms, coefficient 1 on register 708, and its only live main-input terms are
`(x154 + x217) / 4`. The input nuisance is `k = h - e708`, with 87 terms.

On the published word, event 17523 is the unique
`743 += 146/2` at frame 127. Let `t` be row 743 immediately after that
event. The output nuisance is `g = e743 - t`. Direct replay gives
`g = k - c`. The partner covector `c` is nonzero, so `g ≠ k`. The frame-3
prefix of the published word is exactly the instruction list for `-k`,
followed by `126 -= 2·708` and `188 += 2·708`. Thus the input side really
is `k`, while the live 146 correction removes `g`.

## Order

The next three instructions are, in order,
`126 += 2·743`, `188 -= 2·743`, and `743 -= 146/2`.
No later instruction reads 126, 188 or 743. Later writes of 126 and 188 are
ADDs at frame 127, so they commute with the first two restorations. The third
instruction replaces `t` by `e743`, and `t - e743 = -g`.

Doing that replacement first and then adding `±2·e743` instead of `±2·t`
changes the 126 row by `2(t - e743) = -2g` and the 188 row by `2g`. Both
differences are nonzero. The full scalar endpoint walk accepts the published
order on every public and owned row. The same walk on the swapped triple
fails exactly rows 126 and 188. Changing only the last coefficient from
`-1/2` to `+1/2` leaves 126 and 188 corrected, because those restorations
already used `t`, and fails exactly row 743. The order is what couples the
three registers; the sign repairs only the new helper.

## What this does not say

The paid histogram is untouched by this audit, and no new conditional
exponent is computed. Native maps, the physical caller, compiler closure,
precision and the outer ledger stay on the predecessor's obligations.
Unknown costs there are not zero. The selected frontier is unchanged.
