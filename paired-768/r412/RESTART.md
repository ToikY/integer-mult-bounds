# Reproduce and resume Round 412

Use CPython 3.12. The following commands assume a clean checkout of this handoff at its repository root. Dependencies are authenticated before use. No prior temporary state is needed.

```sh
python3.12 -IB paired-768/r412/tick/check.py
python3.12 -IB paired-768/r412/reserve/check.py \
  --proof-root "$TRANSFER_CHECKOUT/research/retimed-native-multiplier" \
  --prepare "$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage/prepare.py"
```

The first check uses the sealed Round 410 and 411 exact inputs already in this branch. The second expects ordinary proof checkout [dfd25d553a843a946ca0b94130a5ff8943e98fdd](https://github.com/aliromman/integer-mult-bounds/commit/dfd25d553a843a946ca0b94130a5ff8943e98fdd) and composed checkout [c20a08dc0a79a989e3515068560d5da371c0a2a8](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8). See [the argument and four exact source digests](reserve/README.md).

For the 64 K7 cases, set `K7_ARCHIVE` to the exact public [#8073 copy of #8057’s archive](https://github.com/CrocSwap/integer-mult-bounds/blob/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e/research/p104-weighted-k7-suffix/peer8057.tar.gz). SHA-256 is `0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c`.

```sh
python3.12 -IB paired-768/r412/k7/check.py "$K7_ARCHIVE" > k7-screen.json
cmp k7-screen.json paired-768/r412/k7/RECEIPT.json
python3.12 -IB paired-768/r412/k7/replay.py "$K7_ARCHIVE" k7-screen.json
```

## Next bounded physical obligation

Refresh exact peer heads and the local 8 GiB admission first. The narrow next test is whether the written [#8084 η-lift](https://github.com/CrocSwap/integer-mult-bounds/pull/8084) at af73b476d5fdeaa763e0bff2dd87b2ecaf097c49 establishes the ordinary proof domain when transplanted to #8094's five terminal heights and floor 4474. The first concrete step is to pin the exact #8084 changed files, find the written source replacing the inherited η≤0.0039 assumption in the physical clock, and extract the exact width, local coefficient work and two-moment cutoff inequalities. Check both entry and terminal floors/transition seams. Cover the seven frozen ordinary recipes only. A source-exact inequality pass advances the single 1420717/2^20 assembly. An unchanged stricter inequality, missing charge, or unproved interface stops that transplant until repaired. If admission returns first, run the existing strongest pending #8094 package in its exact checkout and preserve any mismatched proof or skipped gate.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-shortcut-word-eta-27bit-5stage
```

The stronger pending profile and one-tick claimant must be replayed separately. The complete gate includes signed forward and adjoint custody, actual raw and nested calls, registered setup with the nine expanded recipes, reproduced complete cost, active signed product path and both independent controls. Keep the K7 exclusion scoped to these selected clocks. A distinct route needs a named legal action, for example the exact quotient receiver's smaller frame-averaged child charge, and a full directed invoice before any native construction.
