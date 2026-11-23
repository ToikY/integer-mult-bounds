# Reproduce and resume Round 417

Use CPython 3.12. From the handoff root, set COMPOSED_CHECKOUT to [exact #8094 c20a08dc](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8), then run:

```sh
package="$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage"
python3.12 -IB paired-768/r417/seed/check.py
python3.12 -IB paired-768/r417/owner/check.py \
  --package "$package" --signed-receipt paired-768/r416/signed/RECEIPT.json
```

The first command authenticates the sealed graph and exact layout-building inputs in Round 411 and evaluates one normalized row. The second uses a literal source transaction and synthetic physical field. Their outputs match [seed receipt](seed/RECEIPT.json) and [owner receipt](owner/RECEIPT.json). One selected relay, with 30 seconds per command. [Hosted comparison](hosted-note.md)

## First tests after admission

Refresh the exact comparable witness and the 8 GiB availability. Use the [Round 415 clean source assembly](../r415/RESTART.md) to make a fresh candidate tree; retain the original sealed tree. Before producing the candidate receipt, create the checked setup correction as a new file within that fresh tree:

```sh
peer="$CANDIDATE_TREE/research/frequency-weighted-native-multiplier"
python3.12 -IB paired-768/r417/setup-receipt/check_patch.py \
  "$peer/receipt.py" --output "$peer/receipt.corrected.py"
```

The exact output SHA-256 is in [the correction receipt](setup-receipt/RECEIPT.json). Use the corrected script for candidate receipt generation, with its adjacent authenticated price modules. Bind any official price replays to the same corrected source in the fresh isolated copy. The actual fixed directory measurement still needs the [guarded nine-recipe census](../r416/setup/README.md).

After native admission and the exact #8094 bootstrap, run the [installed one-column chart fixture](physical/README.md). One pair, 90 seconds, with actual signed forward and inverse operations, distinct scratch owner and dirty spectator data. A phase, tag or owner mismatch stops this branch. On a pass, use the first-native legal helper tag at source label 164 in the full typed parent test, checking that node 104493 actually receives its occupied rank-five payload. Preserve physically independent owners over both requested widths and use the proven zero seeds as negative scope controls. A second true owner must remain independent across the physical return. Match actual adjoints, precision and retained charges before running the full mode suite and claiming any κ gain.

The full native baseline and candidate were not launched. Goal remains active.
