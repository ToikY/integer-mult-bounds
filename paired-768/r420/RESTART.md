# Reproduce the sharper-period source assembly

Use CPython 3.12 with assertions and Git. Set COMPOSED_CHECKOUT to a clean checkout of [exact #8094 c20a08dc0a79a989e3515068560d5da371c0a2a8](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8). From the public handoff checkout:

```sh
package="$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage"
python3.12 -IB paired-768/r420/overlay/assemble.py --package-root "$package"
python3.12 -IB paired-768/r419/cross-price/check.py
```

The first command matches [the assembly receipt](overlay/ASSEMBLY.json). It regenerates and compares the frozen Round 415 source, applies the exact Round 417 setup correction in the new tree, and then changes six tracked source or manifest paths. It does not invoke native bootstrap. A fresh optional `--output` persists the new candidate while leaving the old one untouched. The expected installation image is c5d83f8c6acdab6828185bc6bb67537cf320ba79ab177f9da535edae7b5af72e. The source-only price check and 112-bit/192-bit controls are in [price-source/README.md](price-source/README.md).

## First installed gate after admission

The [exact peer runner request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19842065) has no live job. Recheck the exact stronger pending peer and 8 GiB free. Use the original [Round 418 clean replay route](../r418/RESTART.md) before claiming any improvement. Retain its per-mode exits. The frozen Round 415 assembly is still a distinct comparison and repair input.

After the exact peer is independently reproduced, prepare this candidate in a new destination using the command above with `--output "$CANDIDATE_TREE"`. Under the same native admission, run one cold candidate bootstrap and literal receipt:

```sh
peer="$CANDIDATE_TREE/research/frequency-weighted-native-multiplier"
python3.12 -IB "$peer/bootstrap.py" "$CANDIDATE_RUNTIME"
python3.12 -IB "$peer/receipt.py" "$CANDIDATE_RUNTIME" > "$CANDIDATE_PRICE_RECEIPT"
```

Use fresh absolute output paths and preserve the actual receipt separately. There is no candidate RESULT.json in the source tree. Compare the observed numeric and source fields to the expected assembly and Round 419 exact price before making an expected result file for the registered verifier. The full acceptance still includes the [one-column physical control](../r417/physical/README.md), the [true-helper two-width replay](../r418/typed/README.md), the [nine-recipe census](../r416/setup/README.md), and the actual exercised signed native and product scopes. The source-bound census extension preserves the old controls and pins this exact selector:

```sh
python3.12 -IB paired-768/r420/setup/check_installed.py \
  --profile period --runtime "$CANDIDATE_RUNTIME" \
  --portable "$peer/portable" --scratch "$SETUP_SCRATCH"
```

The prepared tree retains historical #8057 metadata and proof documents as dependency material. They describe prior evidence. The actual runtime receipt and complete candidate runs are required before a ready registered package can be produced.

The unmodified fork workflow remains unavailable unless the route becomes eligible. A request or source receipt is not a live job.

## Verify the source seam from the frozen preimage

Set FROZEN_TREE to a fresh Round 415 assembly. Recreate the new stage verifier from that preimage and check the same 18 arithmetic controls:

```sh
python3.12 -IB paired-768/r420/seam-source/check.py \
  --prepared "$FROZEN_TREE/research/frequency-weighted-native-multiplier" \
  --composed "$package" --archive "$package/peer8057.tar.gz"
```

Match [the seam receipt](seam-source/RECEIPT.json). The derived stage verifier digest must also match the assembled Round 420 file. The test compares the old and new physical helper functions structurally and keeps the prior-rate and adjacent controls.

## Independent review of both prepared trees

With FROZEN_TREE and CANDIDATE_TREE set to the two freshly assembled directories:

```sh
python3.12 -IB paired-768/r420/review/check.py \
  --frozen "$FROZEN_TREE" --candidate "$CANDIDATE_TREE" --composed "$package"
```

Compare [the readback](review/INDEPENDENT.json). This verifies archived files, the exact selector image, period arithmetic and all 18 source seam controls without running installed science.
