# Two-round cube stock for the typed actual-width H

**Scoped tape-stock certificate. No new κ.**

One fixed collection of seven tapes carries two rounds of the typed
actual-width physical `H` on the ell=2 layouts from
`research/typed-actual-width-physical-h`. Previous-output reset blanks the
root and consumer tapes between rounds. The live cell count stays one
round's footprint, `F = 6Mr(w+W)`, which is half of two retained one-shot
inventories.

## Result

The predecessor's two-record witness is `ell = 2`, one short axis
`flags = (False,)`, `k = 1` and `p = 4`. It has a single layout height, so
the two-round schedule is two admissible presentations of height `h = 0`.
The shared inventory has 624 cells. Each presentation matches a fresh
one-shot tensor and the one-round bill of 768 reads, 1200 writes, 3890 moves
and 620 gates. Each reset of an output tape writes 96 bits and moves 190
cells. The first consumer image is nonempty and is blank after the reset.
The predecessor object still rejects a second `run` with `one-shot physical H`.

The same contract on `flags = (True,)`, the smallest ell=2 layout with two
heights, carries `h = 1` and then `h = 0` in 1248 cells. The selected bits
are `(1,)` and `(0,)`. The tensors differ and each matches its one-shot call.

[PROOF.md](PROOF.md) derives `F` and the reset bill. The checker compares
both schedules with the unmodified `physical_h.py` machine.

## Scope

This is the first open question of `research/typed-actual-width-physical-h`,
left by discussion #1166 comment 19016699 after the one-round return was
supplied. It is not a proof of any of the five selected framework
assumptions, not a PR #3617 diagonal join, and not a production-width cube.
Rounds whose selected-bit counts differ do not fit this exact-length
inventory. Both outputs are not retained at once. Selected κ stays
`781451/250000000`.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/two-round-cube-stock/verify.py
python3 -B -O research/two-round-cube-stock/verify.py
python3 -B scripts/research_package.py --package research/two-round-cube-stock --check-only
python3 -B scripts/research_package.py --package research/two-round-cube-stock
```

Both direct runs print `PASS_TWO_ROUND_CUBE_STOCK`. On this host each took
well under a second. The selected-record binding check
`python3 -B scripts/research_selected_baseline.py` printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` and was not a scientific replay.

Not run: `make frontier6030-verify`, Lean, Docker, a production `ell`, and
the PR #3617 diagonal.

## Open next questions

1. Can one inventory carry a layout whose rounds have different `g`? The
   ell=3 row `flags = (True, False)`, `k = 1` selects one bit and then two.
   A wider scratch would have to accept the shorter round's exact allocation,
   which this redirect rejects. First step: pad or window the `g = 2` tapes
   so the `g = 1` round is a prefix, and check both tensors.
2. What stock is required when the caller keeps both round outputs? Reset
   is what keeps `F` from becoming `2F`. First step: add a second
   root/consumer pair and price the retained pair against `F`.
3. Can the reset output sit under PR #3617's framed diagonal without a new
   stage object per round? That is still the predecessor's second question.
   First step: feed one rounded packet into the unchanged diagonal consumer
   and price the framing.

## Credit

The matched layout, one-round machine, tensor and toward-zero return are
Clear1nsight's PR #3623, incorporating Sagar Thakrar's PR #3617 diagonal
contract and the PR #3493 / #3593 / #3599 / #3611 sources credited there.
The one-round tape bill is unpaidmoon's `research/typed-actual-width-physical-h`.
The handoff is discussion #1166 comment 19016699. The two-round inventory,
reset bill and checks are new.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No
independent human or formal-kernel acceptance is claimed. Apache-2.0.
