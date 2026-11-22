# Exact denial of fractional packets and a bounded repair candidate

The exact current comparator is [#8054](https://github.com/CrocSwap/integer-mult-bounds/pull/8054) at `f6f4ecd5dd717ce2b155dd564469e9693ac90f6d` with conditional κ = 0.0038981730255. Round 369 replaces all 1,006 half-rank pairs in its fixed Gaussian word by nominal quarter and three-quarter ranks. The complete invoice admits 55 cells. The literal plan rejects the proposal at production band 32,770 because its 32,762 columns give noninteger lengths 16,381/2 and 49,143/2. The 39/256 debit proof separately requires revision for the smaller rank. This is a scoped exact exclusion. [Full price](../r369/primary/PROOF.md) · [Independent literal obstruction](../r369/interface/PROOF.md)

Round 370 changes the admitted lengths to the integer floor of one quarter and its complement, with both pieces ordered on one original owner. Across the two permitted column residues, the prototype reconciles every named axis with the event decoder and leaf count, rejecting a corrupted paid size. Separate exact proofs bound the per-edge fringe, lower-end reserve, inverse-power intervals, unchanged precision and signed tariff. They fund κ = 0.0038982016137 at fixed heights and 40-bit Gaussian dyadic 4286126377/2^40. The prospective absolute gain over #8054 is 0.0000000285882. The complete native emitter, returned owners, repeated caller, and all eight signed modes remain gates. [Price proof](price/PROOF.md) · [All-size rounded proof](proof/PROOF.md) · [Event and decoder fixture](prototype.json)

## Replay

Use CPython 3.12 and Git on PATH from a clean checkout. Set `UNSPLIT` to the exact #8054 checkout's `research/p104-gaussian-unsplit-returns` directory. Run from this directory with fresh outputs.

```sh
python3.12 -IB ../r369/primary/quarter.py --unsplit-package "$UNSPLIT" --out fresh-quarter.json
python3.12 -IB prototype.py --unsplit-package "$UNSPLIT" --out fresh-prototype.json
python3.12 -IB proof/check.py --receipt fresh-quarter.json --out fresh-proof.json
```

The original `outer_budget.py` can be obtained from the underlying archived #8052 package. After preparing the #8054 variant through the [R368 command](../r368/README.md), set `NATIVE` to that unpacked directory.

```sh
python3.12 -IB ../r369/interface/check.py --package "$NATIVE" --out fresh-rejected.json
python3.12 -IB price/parity_price.py --quarter fresh-quarter.json --split ../r368/primary/receipt-final.json --transfer ../r369/TRANSFER-8042.md --outer-budget "$NATIVE/outer_budget.py" --out fresh-rounding-price.json
```

The pinned `TRANSFER-8042.md` is from [Ali Romman’s exact #8042](https://github.com/CrocSwap/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/TRANSFER.md). That proof supplies the original source geometry and signed 48-call compiler. SYLforge’s #8052 supplies the stronger binary provider and retained installation. #8053 and #8054 supply the fixed-carrier price and current paid counts. OpenAI Codex assisted the bounds, implementation, and independent replay.
