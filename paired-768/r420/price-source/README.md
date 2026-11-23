# Sharper positive price source checks

The transformer authenticates the exact Round 415 prepared positive and independent price files. It requires the corrected Round 417 receipt as the third preimage. It leaves the ordinary tariff, integer period, weights, charts, roots, signed actions and height allocation in place. The three edited sources compile before the transformer writes any output.

The literal price code bounds the same four-aligned exterior period by 257/256 for both scales and books 1039701/2^23. It tests the smaller adjacent debit and checks that the coarse factor still overflows the new charge. The independent price code retains the coarse predecessor checks. The receipt checks separation from the full prior positive crossing, the exact reported #8094 rate and the adjacent candidate rate. Its funding floors are 134136243 ordinary and 208653 positive. The source scope uses the frozen tariff projection and does not imply independent native execution.

## Replay

Use CPython 3.12 and Git. Prepare a fresh [Round 415 tree](../../r415/RESTART.md) with the exact [#8094 source package](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8). Save the corrected receipt as a separate file through the [Round 417 correction](../../r417/RESTART.md). Set CANDIDATE_TREE, CORRECTED_RECEIPT and COMPOSED_PACKAGE to those explicit, existing paths and run from the handoff root.

~~~sh
python3.12 -IB paired-768/r420/price-source/check.py   --prepared "$CANDIDATE_TREE/research/frequency-weighted-native-multiplier"   --corrected "$CORRECTED_RECEIPT" --package "$COMPOSED_PACKAGE" > price-source.json
cmp price-source.json paired-768/r420/price-source/RECEIPT.json
~~~

The test authenticates the nested exact 112-bit power function and the published coarse receipt inputs, runs the changed source expressions, checks the independent 192-bit expressions, and rejects the adjacent lower debit. It reproduces the original coarse upper factor exactly. The test ran twice with byte-identical results. The first run took 0.08 seconds and exited 0 under the 30-second cap. The signed application, runnable profile geometry, calendar, owner return, fixed setup and registered replay remain separate gates.

Credit the #8085 period proof, floration’s #8094 profile, Ali Romman’s #8057 signed producer and the preceding Round 417 and 419 checks. OpenAI Codex assisted with the transformation and source replay.
