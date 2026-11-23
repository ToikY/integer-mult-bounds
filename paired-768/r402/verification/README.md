# Round 402 independent verification

Candidate `9555f2df027f4a182722f736c97e5efafa5382c6`. Predecessor #8070 `7d65b2c6a19941b9922d5e4c86c495aa37073141`. The verifier froze its [plan](PLAN.md) before opening the implementation. It checked the [15 committed paths and modes](CANDIDATE-INPUTS.json), both historical prerequisites and the frozen #8057 archive. A separate cross-check binds all 88 paths to their exact public Git blob IDs. [Archive binding script and results](../peer-source/peer-binding.log)

Use Git and CPython 3.12 from a clean checkout of the exact candidate.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-ordinary-debit-11239
```

To rebuild the independent price and physical image receipts, run the following from this directory. The two arguments point to clean candidate and comparator checkouts pinned to the hashes above. The wrapper validates both heads, restores the archive from the candidate, recreates the signed runtime and compares the new outputs byte for byte to the published receipts. It creates and removes its own temporary directory.

```sh
python3.12 -IB replay_invoice.py ../../../../candidate-checkout ../../../../comparator-checkout
```

## Exact results and controls

The directed upper ordinary factor fits the revised booked debit 11239/8192. Its reserve exceeds 0.000062662376093595. The next tested finer booking 22477/16384 fails by more than 0.000046832527238212 for the same factor. Both signed tiers pass 54 strict and four functional inequalities. The prior ordinary debit at the new heights and the earlier Gaussian height each give exact target shortfalls. The verified conditional rate is 0.00389821412325, exactly 5857/10^16 above the reported #8070 κ. It also clears the prior exact capped-family ceiling, as reconstructed from the literal signed charges. At the new fixed heights Gaussian binds. Other allocations are outside this proof. [Independent exact invoice and negative controls](invoice.json) · [Exact percentage comparisons](comparisons.json)

The literal image comparison finds one installed runtime change, in the profile parameters in `installations.py`. Both typed native schedules, the K7 word, source geometry, paid placement and restoration operators are retained. The full invoice is 318292071 recurring log₂ C, with first terminal header 2^1148456+2, 515-bit entry conversion, maximum height 524288, and fixed serial setup below 2^228. The original five native, ownership, compiler, precision/tape, and analytic-recovery premises are retained. [Exact source image differences](operator-images.json)

The independently run registered package finished all seven modes in **229.50 seconds**, exit 0, and the checkout stayed clean. It executed the raw width-two and width-four fixtures, exterior and actual nonzero nested returns, and the signed product −345550037539 with 157248 native calls and 138 shuttles. The product identity and restored operands are checked in both tiers. The physical coefficient fixture covers entry. Both modulo-3 and modulo-9 controls reject a wrong signed return. Setup passes its full declared scope. [Signed replay log](replay.log) · [Observed stage timings](replay-observed.jsonl)

## Repository checks and time

The screen took 0.028517 s. Literal regeneration, price and calendar took 77.274 s total. The first local onboarding attempt took 111.16 s and failed because the sparse checkout omitted required neighboring fixtures and process inspection was unavailable. The same candidate passed after restoring the fixture set and enabling the child-process check. The repaired onboarding run took 155.93 s and reported 760 tests with 31 skips. The existing historical scope passed its 19 expected rejection controls in 2.35 s and retains its registered partial scope. No scientific source changed during the repair.

Active implementation and source tracing time were not separately timed. The matched #8070 receipt was authenticated and reused. Timings come from different environments and provide no measured speedup or workflow adoption claim. Hosted results are tracked separately. [Build times](build-timings.json) · [Local onboarding](onboarding-summary.log) · [Historical scope](historical.log)
