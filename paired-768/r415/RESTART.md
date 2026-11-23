# Reproduce the exact ordinary tariff source overlay

Use CPython 3.12 and Git. Set COMPOSED_CHECKOUT to a clean checkout of [exact #8094 c20a08dc0a79a989e3515068560d5da371c0a2a8](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8). From the clean handoff checkout, this command resolves all source inputs from that root and authenticates them against the pinned manifest. It never invokes the runtime bootstrap.

```sh
package="$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage"
python3.12 -IB paired-768/r415/overlay/assemble.py --package-root "$package"
python3.12 -IB paired-768/r415/seam-source/check.py \
  --composed "$package" --archive "$package/peer8057.tar.gz"
```

Match the first output to [ASSEMBLY.json](overlay/ASSEMBLY.json) and the second to [SEAM.json](overlay/SEAM.json). One source preparation and 45 seconds maximum; an optional `--output` must name a new directory. The expected changed signed installation image is 37460b2be0a93ecfe110be25de5a4ea787c2d09973f926f680ea148453dc89e2. The source checks preserve the tested owning routes, selected geometry, tariff and adjacent negative controls. They do not run physical code or produce a completed candidate result. [Exact source inventory](overlay/INPUTS.json) · [Independent signed scalar comparison](../r414/independent-price/README.md)

## First installed test after authorized resume

Check current peer heads, comparable premises, active jobs and the 8 GiB reserve. Replay the strongest pending comparable profile before any weaker comparison. At this seal, the exact #8094 package command in that clean peer checkout was:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-shortcut-word-eta-27bit-5stage
```

Only after admission, prepare the candidate tree from the source above, using a fresh output directory. In that prepared tree the exact first changed runtime gate is:

```sh
peer="$CANDIDATE_TREE/research/frequency-weighted-native-multiplier"
python3.12 -IB "$peer/bootstrap.py" "$CANDIDATE_RUNTIME"
python3.12 -IB "$peer/receipt.py" "$CANDIDATE_RUNTIME" > "$CANDIDATE_PRICE_RECEIPT"
```

Use explicit fresh absolute paths for the three destinations. Verify the candidate installation hash, both tier bounds and all signed price checks against Round 414. The prepared source has no candidate RESULT.json. Preserve a separate new receipt only after the actual installed comparison passes. Reconcile the optional numerical setup cap and its action count independently, including the expanded lookup term. Then run installed price/calendar/raw/exterior/nested/product and setup checks under the guide, including complete signed owners, adjoints, and a truly active paid path. Test the predecessor and a corrupt paid-action control from clean inputs before claiming a κ gain. Review current overlap before opening any eligible focused PR and follow its exact hosted checks.

No further work is scheduled at this seal. The user requested a pause after Rounds 411–415.
