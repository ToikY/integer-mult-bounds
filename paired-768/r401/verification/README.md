# Round 401 independent verification

Frozen head `7d65b2c6a19941b9922d5e4c86c495aa37073141`.
See [committed input hashes and modes](CANDIDATE-INPUTS.json), [cold preflight](preflight.log), and the [independent plan](PLAN.md) frozen before opening the builder's proof.

Run with Git and CPython 3.12. The full signed package can be run from a clean checkout of the frozen head.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-gaussian-debit
```

Run the separate invoice check from this evidence directory with the clean candidate checkout as the explicit dependency root. It authenticates and restores all 88 archived source files, installs the archived signed supplier into a fresh temporary directory, and checks both reconstructed receipts byte for byte.

```sh
python3.12 -IB replay_invoice.py ../../../../candidate-checkout
```

The dependency argument points to the candidate checkout. Any other clean relative path to that same exact checkout works. The temporary directory is created and removed by this command. No previous runner state is needed.

## Results

The independent invoice reconstructs ordinary productive/paid counts of 18,906/104,652 across 24 grade cells, both Gaussian types at 52,608 productive operations, 282,576 and 281,568 paid operations, and the weighted totals 23,989,248/128,400,048. It checks all 54 strict and four functional signed margins on each tier. The full outward factor leaves a strictly positive reserve above 0.000000684423610889 at debit 64939/524288. The adjacent 64938 booking fails with that upper-bound method. The previous 64944 debit fails when used at the new Gaussian height and rate. The reconstructed recurring bound is 318292171, with 515-bit entry conversion, private capacity 536870915 and first terminal header 2^1148456+2. The conservative serial setup bound is below 2^228.

The independent cold candidate replay passed all seven modes in **257.99 seconds**, with exit 0 (user 180.76 s, system 70.90 s). The predecessor replay ran the same seven modes in 244.35 seconds. Both signed raw modes passed, as did exterior and actual nonzero nested owner returns. The full signed product is −345550037539, with 157248 native calls and 138 shuttles. Watcher stage times are observations, sampled separately from solver times. Both modulus-3 and modulus-9 controls rejected deliberately corrupted signed returns. The local onboarding suite reported 760 cases with 31 skips and the historical replay passed its declared partial scope with 19 rejection controls. [Independent invoice](reconstruction.json) · [Charged census and controls](charges.json) · [Exact science log](replay.log) · [Observed stage timings](replay-observed.jsonl)

The literal build took 83.553 seconds. Local onboarding took 152.432 seconds on its own clock and overlapped the verification work. The separate historical replay took 2.48 seconds. Preparation and source tracing were not independently timed. The Gaussian debit screen took 14.73 seconds including two corrections to runner paths (6.95 seconds on the successful pass). The excluded fusion screen took 6.24 seconds. No workflow change was adopted on these unmatched measurements. Hosted evidence is recorded separately.
