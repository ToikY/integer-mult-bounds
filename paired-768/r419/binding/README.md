# Sharper Gaussian exterior price at the frozen #8094 heights

One source and arithmetic screen. Exact [#8094 c20a08dc](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8) is ordinary-bound at its recorded 0.003900857267786. The [Round 415 tariff candidate](../../r415/RESTART.md) transfers the binding inequality to Gaussian at projected 0.003900857269150. Keep ordinary heights (3000, 3080) and (31808, 502922, 7951907, 125730703, 134217727) and Gaussian heights 1024 and 208653. The only tested mechanism is substituting the sharper, previously verified exterior period factor from [#8085](https://github.com/CrocSwap/integer-mult-bounds/pull/8085) in the Gaussian debit.

The literal typed producer has exterior size s = (e−8)k, upper band U = 2 floor(M/(2S)), S = 263772, k ≤ 258 and four-aligned period q = 4 ceil(M/(4s)). It charges floor(M²/q) full cycles per birth. Therefore x = M/(4s) ≥ S/1032 > 255. For x ≤ 256, ceil(x)/x ≤ 256·1032/S < 257/256. For x > 256, put m = ceil(x)−1 ≥ 256 and use ceil(x)/x < (m+1)/m ≤ 257/256. This preserves the literal period, both band endpoints, weighted shares, phase and owner routes and every other charge. Only the proof upper multiplier changes, from 22067/21981 to 257/256.

The independent integer-grid check retains #8094's precise lower share sum and bounds the powers on a directed 192-bit grid. The revised factor fits debit 1039701/2^23 with reserve greater than 1.7952279789×10⁻⁸. Its immediately smaller debit fails the revised upper envelope, and the old coarse envelope fails at the new debit. This gives a 75-tick decrease at the same Gaussian heights. Reconstructing the ordinary stage recurrences, 54 strict and four functional bounds per tier, and complete recurring maximum gives a new **projection κ = 0.003900857312000** at unchanged **log₂ C = 85945126846** and entry surcharge 121121. The signed budget rejects the proposed rate with the old debit and the adjacent higher grid rate even with the sharpened debit. The projection strictly clears the entire frozen Gaussian crossing, by 0.000000000042850 over the frozen booked projection and 0.000000000044214 over #8094's reported κ. Applying the new factor to #8094 alone leaves the old ordinary ceiling in place.

The arithmetic is conditional on the retained funded transport and signed hypotheses. The source binding authenticates the typed period, cut and predecessor price code that will supply the finite bound. No new source package was built, and no native, fixed-setup or complete comparative replay ran. This screen does not certify a κ gain. Preserve the frozen Round 415 comparison and record this as an alternate binding mechanism.

## Replay

Use CPython 3.12, the clean handoff at its repository root and a source-only [Round 415 assembly](../../r415/RESTART.md) at a fresh output path. Set CANDIDATE_TREE to that path.

```sh
python3.12 -IB paired-768/r419/binding/check.py \
  --prepared "$CANDIDATE_TREE/research/frequency-weighted-native-multiplier"
```

One profile, 30-second runner cap, 0.04 seconds and exit 0. A fresh run reproduced the [exact receipt](RECEIPT.json) byte for byte. Credit floration for the exact #8094 recipe and Ali Romman for the signed typed producer, and the #8085 authors for the exterior-period proof. OpenAI Codex assisted with the independent source and rational reprice.
