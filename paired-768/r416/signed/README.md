# Exact signed Gaussian columns for one direct relay

This source check selects node 104493 from the literal five-relay word in [exact #8094](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8). It replaces charts 365 → 1028 → 529 by 365 → 529 with paid grade five. The new chart-local row has exactly donor 94870 with coefficient one.

The checker extracts the retained Clifford compiler and independent Gaussian-dyadic verifier from the pinned #8057 archive. It uses the original `phase_atlas.catalogue` inner lowering and selects one case before its complete pair and port loops. The independent verifier evaluates each of the 512 basis columns. The installed factorization agrees with the two-edge chart product and the direct canonical frame action. The compiled factor's conjugate transpose agrees on all 512 columns with the swapped canonical frames. The controls reject a quarter-turn global phase with the same Pauli tableau and reject leaving the forward Fourier inside the adjoint wrapper. All arithmetic is exact. This checks the isolated chart operator; Round 411 already checked the surrounding five-relay forward rational mixing.

## Physical path and remaining gate

The composed source binds the chart factors via [the exact #8094 prepare patch](https://github.com/CrocSwap/integer-mult-bounds/blob/c20a08dc0a79a989e3515068560d5da371c0a2a8/research/p104-shortcut-word-eta-27bit-5stage/prepare.py). The signed positive supplier passes them from `strong_complex.artifacts` through `grades.numerical_source` to `retimed_supplier.Positive`, which constructs `ComplexRaw` and `TypedRaw`. In the retained [raw48.py](https://github.com/CrocSwap/integer-mult-bounds/blob/46783fbbfc219a3faffbea76f60a2810b85ab75a/research/native-stock-activation/raw48.py), `ComplexRaw.graph` forms a fresh zero field for node 104493, applies its right chart, publishes a scratch token with rank-five axis groups, pops the returning token and applies the left chart. It stages the terminal fields before replacement and retires the residual fields. `TypedRaw.native` rejects shared productive owners and a paid tag or width mismatch. The symbolic adjoint corresponds to the inverse left monomial, inverse Fourier and inverse right monomial; the retained `chart(..., inverse=True)` reverses the monomial instructions and negates the relevant phase exponents. No physical field or typed calendar was executed in this source-only check.

At the next admitted installed check, exercise this exact direct pair in the physical child probe using the generated factor record, both directions, and owner/field restoration; follow the same label through the registered signed raw and nested calls. The other four relay roles, multi-column and spectator behavior, the signed caller and the complete native replay remain open. A finite pass gives no overall κ claim.

## Replay

Use CPython 3.12 with assertions. Point `COMPOSED_PACKAGE` at `research/p104-shortcut-word-eta-27bit-5stage` in a clean checkout of the exact #8094 head. The two file pins and all extracted code pins are authenticated. The replay reads the archives in memory, selects one case, and caps time at 30 seconds.

```sh
python3.12 -IB check.py \
  --word "$COMPOSED_PACKAGE/w5669_shortcut5.json.gz" \
  --archive "$COMPOSED_PACKAGE/peer8057.tar.gz" > reproduced.json
cmp reproduced.json RECEIPT.json
```

The check took 0.55 seconds and exited 0. Credit floration for the five-relay word, Ali Romman for the #8057 signed source and archived receiver chain, and the retained Clifford and independent native review authors credited in the archive. OpenAI Codex assisted with the bounded independent audit.
