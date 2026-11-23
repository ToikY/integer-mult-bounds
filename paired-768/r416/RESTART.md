# Reproduce and advance Round 416

Use CPython 3.12 and Git. Set COMPOSED_CHECKOUT to a clean checkout of [#8094 c20a08dc0a79a989e3515068560d5da371c0a2a8](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8). From the handoff repository root, the exact source checks are:

```sh
package="$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage"
python3.12 -IB paired-768/r416/setup/check.py --package-root "$package"
python3.12 -IB paired-768/r416/signed/check.py \
  --word "$package/w5669_shortcut5.json.gz" --archive "$package/peer8057.tar.gz"
```

Both commands authenticate exact local dependencies from that public checkout. Their expected results are [setup/RECEIPT.json](setup/RECEIPT.json) and [signed/RECEIPT.json](signed/RECEIPT.json). Neither command bootstraps a native runtime.

## Open next questions

Refresh the strongest comparable witness and actual resources. Start the native peer replay if the 8 GiB reserve is met. Reuse the frozen [Round 415 overlay](../r415/RESTART.md) for the separate candidate. The next setup command, after native bootstrap, is the [nine-recipe installed census](setup/README.md). It requires an explicit matching runtime, portable dependency and scratch root. Compare the receipt generator's numeric setup field with the checked expanded total. Preserve the older arithmetic and report its scope independently.

The immediate distinct signed question is whether the installed typed call for node 104493 actually visits charts 365 → 529 with its generated rank-five factor, arbitrary legal spectator payloads, inverse phase and complete owner return. The first concrete step is to adapt the pinned physical child fixture to that exact tag and chart pair rather than using the inherited archived pair selection. Inspect `strong_complex.artifacts`, `retimed_supplier.Positive` and `raw48.py` as identified in [the signed trace](signed/README.md). Cap the first physical probe at one pair. A signed phase, tag or owner mismatch stops this candidate profile. An exact successful installed probe earns the remaining four relay scopes and complete signed package replay. Keep the 8 GiB disk reserve and the independent predecessor and negative controls.

No κ gain is certified. The active goal continues from the exact frozen overlay and the stronger pending peer, with unrun installation and signed gates explicit.
