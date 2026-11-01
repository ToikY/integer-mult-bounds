# Two-round stock for the typed actual-width return

This note shows that one fixed tape collection carries two rounds of the
typed actual-width physical `H` on the ell=2 layouts already checked by
`research/typed-actual-width-physical-h`. It does not retain both outputs,
attach the PR #3617 diagonal, or change a multiplication exponent.

## Inventory

Fix precision `p >= 1`, record count `M`, coefficient count `r = 2^ell`,
packet width `w = p + 2` and work width `W = p + g + 2` for a round that
selects `g` address bits. One round of the predecessor, while its butterfly
is in progress, holds seven tapes:

| Buffer | Cells |
|---|---:|
| source, root, consumer | `M r 2 w` each |
| scratch, paired | `M r 2 W` each |
| low, high | `(M/2) r 2 W` each |

The total is

```text
F = 3(M r 2 w) + 2(M r 2 W) + 2((M/2) r 2 W) = 6 M r (w + W).
```

Those seven lengths are exactly the allocation order inside
`TypedActualWidthH.run` and `_butterfly` when `g` is the work width used to
size the inventory. A second retained copy of the same seven tapes would hold
`2F` cells.

## Schedule

The schedule constructs those seven tapes once. Each round creates a fresh
`TypedActualWidthH` object and runs the unchanged `run` method, with the
module's `Tape` constructor redirected onto the inventory in the order
above. The redirect refuses an eighth tape and refuses a length other than
the inventory length. Between rounds, `_blank_tape` clears root and consumer
and returns their heads to cell 0. That is the previous-output reset: the
next round's output occupies the same cells. Scratch and the three
auxiliaries are already blank at the end of `run`. Counters are zeroed after
the reset is recorded, so each round's read, write, move and gate ledger is
comparable to a fresh one-shot call.

For a tape of length `n` whose head is already at cell 0, `_blank_tape`
writes `n` zeros and moves `2(n - 1)` cells: one step forward across the
tape and a return to cell 0. Root and consumer each have length
`n = M r 2 w`.

## The ell=2 witness

The predecessor's two-record witness is `ell = 2`, `flags = (False,)`,
`k = 1`, `p = 4`. It has one layout height, `h = 0`, with selected bit
`(0,)`, so `g = 1`, `M = 2`, `r = 4`, `w = 6` and `W = 7`. Then
`F = 6 · 2 · 4 · (6 + 7) = 624`. The two schedule rounds are two admissible
presentations of that same height. Each presentation's tensor and ledger
equal a fresh one-shot call. The common ledger is 768 reads, 1200 writes,
3890 moves and 620 gates, the same closed bill as the one-round package.
Each output tape's reset is 96 writes and 190 moves. The first consumer
image is not blank, and it is blank after the reset, before the second
presentation. A second `run` on one predecessor object still raises
`one-shot physical H`.

## Two heights at ell=2

`flags = (True,)` is the next ell=2 row in the same cube list. Its heights
are `h = 1` then `h = 0`, with selected bits `(1,)` and `(0,)`. Both have
`g = 1`, and `M = 4`, so `F = 1248 = 2 · 624`. The same redirect carries
both heights of one cube. The two tensors differ, and each matches its own
one-shot call. This is still one footprint, not two.

## What is not claimed

The redirect asks for the exact length of each buffer. A later round whose
`g` is smaller or larger than the inventory's `g` is rejected rather than
packed into a wider scratch. `ell = 3`, `flags = (True, False)`, `k = 1`
has a height of `g = 1` followed by heights of `g = 2`, so it is outside
this certificate. Both outputs are not live together. No diagonal factor,
descriptor update, production-width cube, selected cold replay, or change
to κ is included. The five selected framework assumptions remain.
