# Fixed-height seam verification overlay

The overlay authenticates the original `check_stage_seam.py` from [exact #8094](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8) before editing the ordinary debit and κ used by the verification. The height-drop and near-neighbour controls continue to use the old debit and booking. The new price must exceed the old guarded ordinary crossing, satisfy the full signed arithmetic, and fail at the adjacent higher displayed rate and the preceding Gaussian height.

Use CPython 3.12 at the root of the Round 415 handoff. Set `COMPOSED_CHECKOUT` to exact #8094 and `K7_ARCHIVE` to the [#8073 copy of the #8057 source archive](https://github.com/CrocSwap/integer-mult-bounds/blob/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e/research/p104-weighted-k7-suffix/peer8057.tar.gz), SHA-256 `0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c`. From the directory that contains `seam-source` and `overlay`:

```sh
python3.12 -IB seam-source/check.py \
  --composed "$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage" \
  --archive "$K7_ARCHIVE"
```

The check reads the archive in memory, patches a temporary authenticated source copy, and rejects an altered source without changing it. It checks the arithmetic portion of the resulting verifier using pinned geometry and signed budget functions and a declared profile fixture. The two physical test functions are identical by AST comparison. The run exercised 17 negative arithmetic controls in 0.07 seconds and exited 0. It does not execute installed physical dispatch, native action, signed tape, or setup. Those tests remain required.

Credit floration for the exact #8094 seam checks, Ali Romman for the retained geometry and signed budget, and the Round 414 independent price calculation. OpenAI Codex assisted with the overlay and source replay.
