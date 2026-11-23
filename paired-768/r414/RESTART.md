# Reproduce and resume Round 414

Use CPython 3.12. From the clean public handoff checkout, no installer or prior temporary state is needed for these checks.

```sh
python3.12 -IB paired-768/r414/price/check.py
python3.12 -IB paired-768/r414/independent-price/check.py
```

The two route checks authenticate exact #8094 c20a08dc0a79a989e3515068560d5da371c0a2a8 and the exact [#8073 copy of #8057's source archive](https://github.com/CrocSwap/integer-mult-bounds/blob/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e/research/p104-weighted-k7-suffix/peer8057.tar.gz), SHA-256 0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c. The variables name explicit portable dependency roots.

```sh
for method in proof-first route-first; do
    python3.12 -IB "paired-768/r414/$method/check.py" \
      --archive "$K7_ARCHIVE" \
      --prepare "$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage/prepare.py"
done
```

## Final round of the pause window

Refresh the live comparator and disk admission. Freeze one source overlay on exact #8094. The first concrete step is to authenticate its prepare.py, stage-seam checker, result, native source archive and signed installation patch. In the overlay replace the paid ordinary tariff with 2391/1024 and debit with 1414404/2^20, update the admitted terminal booking to 0.003900857269150 and retain the original fringe, calendar and physical calls. The native receiver and previously charged entry and terminal clocks must retain the verified bounds. Keep old tariff and parameter controls scoped to their own baseline; at the new price the positive supplier binds, so the old binding-side assertions need replacing with the exact adjacent positive control and old crossing check. Recompute the installation digest from literal source and confirm the changed price reaches the actual caller, or stop on the first unavailable source edge. Do not manufacture a complete result record from scalar evidence.

With local admission, run the strongest pending comparator and the installed changed package separately. The #8094 command is:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-shortcut-word-eta-27bit-5stage
```

The actual native adjoint and signed owner checks, active product path, finite setup accounting, clean independent replay and hosted exact-head checks remain required for a gain claim. Preserve the source assembly, its exact remaining gate and unrun scope if capacity stays below the limit. Seal Round 415 and pause the goal at the requested boundary.
