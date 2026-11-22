# Complete signed replay at upper divisor 1,724

Release `e4fccb224ce5d9bc530a8027d4f617a6a37d4562` certifies conditional **κ = 0.00389821053**. The gain over independently reproduced [#8063](https://github.com/CrocSwap/integer-mult-bounds/pull/8063) at `682fd9512ccbf3035089d7e5f9cb4dedf9f746b4`, κ = 0.00389821040, is **0.00000000013**, or **(65/19491052)%** (about **+0.0000033349%**). The gain over [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) at κ = 0.00389821 is **0.00000000053**, or **(53/3898210)%**.

The physical edit changes the paid upper fence from `2 floor(M / (2048 × 306))` to `2 floor(M / (1724 × 306))`, retaining lower fence 1,874. Its exact Gaussian debit is 64,944/524,288 and terminal ordinary height is 524,395. All 456 openings, 51 grade links and 88 directed owner links remain charged. The full recurring bound is log₂ C ≤ 318,293,671, with fixed native setup below 2²²⁸. [All-size proof and controls](PROOF.md) · [Presolve evidence and exact scope](../r389/README.md)

All seven registered scientific modes passed in 176.99 seconds. The installed boundary ran at both native heights, all eight lower-cutoff grants passed, and the real nested transfer returned both owners and granted 4,507,783,464 axes. The signed product was −345550037539 with input restoration. Onboarding passed 760 tests with 31 skips and the registered historical package passed its declared partial scope. The earlier literal build returned exit 1 at the historical #8056 gain fixture. Correcting that fixture's exact gain arithmetic gave a passing price and calendar replay. [Scientific log](scientific.log) · [Onboarding log](onboarding.log) · [Historical log](historical.log) · [Static gates](preflight.log) · [Literal build log](build.log)

Use CPython 3.12 and Git. In a checked-out copy of the exact release, run the complete scientific replay from the repository root.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-upper-band
```

For the detached exact check, set `CANDIDATE` and `COMPARATOR` to the roots of clean Git checkouts at the exact release and #8063 commits above, respectively. Run from this handoff directory.

```sh
out=$(mktemp -d)
python3.12 -IB replay.py --candidate "$CANDIDATE" --comparator "$COMPARATOR" --out "$out/verified.json"
cmp "$out/verified.json" public-verified.json
```

Expected SHA-256 is `c621a5063bdebba3fb37473f28421cb70979239b11dfcaf33fe50dcd4e9e975b`. The public adapter replaces traceback path digests at exactly two named receipt keys, then checks byte equality with the sealed receipt modulo those keys. The original sealed receipt remains available at SHA-256 `d3725f1e0133c3111322ad9ef4f6381aa3d1c7d7173eecc6129874ce30e43980`. [Path digest map](PATH-REDACTIONS.json) · [Sealed receipt](verified.json)

Ali Romman's #8057 provided the typed Gaussian producer and #8055 provided the native setup clock. SYLforge provided K7. #8059 supplied the exact edge price, #8062 supplied the deployed 5:451 frequency, and #8063 supplied the active lower cutoff and signed comparison. OpenAI Codex assisted the construction, proof and independent replay. [#8055](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) · [#8059](https://github.com/CrocSwap/integer-mult-bounds/pull/8059) · [#8062](https://github.com/CrocSwap/integer-mult-bounds/pull/8062)
