# Exact offset-eight projected price on #8087

The one fixed, independently calculated case supports building the trial profile below. The incumbent is [#8087 at aea16994](https://github.com/CrocSwap/integer-mult-bounds/commit/aea1699415250d865f7a635f4df0b76f406c47b4), κ **0.003898460000505**. The trial prices κ **0.003898460003746**, an exact projected increase of **3241/10^15**. The increase remains provisional pending installation and complete independent signed replay.

| Full projected charge | #8087 | Offset-eight trial |
|---|---:|---:|
| Complete recurring log₂ C | 4354317451 | 4285082571 |
| Maximum native height | 18845934 | 18531230 |
| First terminal header | 2^19497093+4 | 2^19182389+4 |
| Entry rate conversion | 8744 | 8603 |
| Fixed native setup | below 2^228 | below 2^228 |

The capped check reconstructed and funded all 51 grade cells and 88 typed shares, matched the recorded weighted census, exact raw margin and minimum individual share, and traversed the 1,971 phase intervals. Two outward methods, repeated square roots at 208 bits and an atanh/Taylor enclosure at 224 bits, give overlapping bounds and certify the same booking **130699669/2^30**. The first method has a positive reserve greater than 2.1591e−10. The immediately lower booking falls below the directed accounting factor by more than 4.8645e−10. Using the predecessor pointwise interior term with the new debit fails. The exact #8087 pointwise term with its actually charged exterior factor and old debit passes its positive control. The new price keeps the original conservative exterior multiplier 22067/21981 and takes no stacking credit.

The ordinary contraction remains 375/376. Charging the smallest possible ordinary height sum allowed by the relaxed comparison bounds the old Gaussian height at 18845935 under #8087's recurring cap. Its stopped upper is exactly `49304965441196404811631259733/12647292888678400000000000000`. The trial clears that upper by `40977549613358026667/12647292888678400000000000000`. The projected Gaussian guard is positive at height 18531230 and fails at 18531229. Both tiers pass the 54 strict and four functional scalar inequalities. The full price includes the same seven fixed installation recipes, all prior signed routing and returns, finite startup, entry conversion, and the extra 2^40 indexed setup actions.

## Clean arithmetic replay

Use Git and CPython 3.12 on POSIX. From this directory supply a clean detached [#8087 checkout](https://github.com/CrocSwap/integer-mult-bounds/commit/aea1699415250d865f7a635f4df0b76f406c47b4).

```sh
python3.12 -IB replay_price.py ./inputs/peer8087 > price-result.json
```

The command authenticates every used input by path, reads the needed archived sources with no file extraction, and caps the single case at 30 seconds. Exit 124 leaves the case unresolved. The recorded run took 0.42 seconds and exited zero. [Exact receipt](PRICE.json) · [Input manifest](../INPUTS-SHA256.json)

The calculation reads the unchanged [Round 368 literal rank receipt](https://github.com/ToikY/integer-mult-bounds/blob/a636a3892e7036b782168bbba260419c6b2be309/paired-768/r368/primary/receipt-final.json) and the prior [#8087 signed scientific evidence](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45121099547/job/137516069048). The pure scalar functions and typed calendar from Ali Romman’s #8057 archive retain their exact digests. [#8083 at dd2e2ff](https://github.com/CrocSwap/integer-mult-bounds/pull/8083) supplied the phase-averaged interior bound and its complete finite error decomposition, and [#8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072) the original signed offset-eight calendar. Clear1nsight supplied the #8081 charged setup, SYLforge supplied K7, and OpenAI Codex materially assisted the independent price and source preparation.

The live native allocator, retuned installation, exact endpoint precision and signed release candidate remain outside this run. [Two-file source preview](../source-preview/README.md) · [Full build and verification gates](../BUILD-READINESS.md)
