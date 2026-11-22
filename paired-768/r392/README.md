# Complete signed replay of the eight-level ordinary transfer

Exact release `ffa64503646a62a7ac3cd2c47787d670da911f89` certifies conditional **κ = 0.00389821057**. The gain over independently reproduced #8064, exact head `e4fccb224ce5d9bc530a8027d4f617a6a37d4562` at κ = 0.00389821053, is **0.00000000004**, or **(400/389821053)%**. Against external #8057 at κ = 0.00389821, the gain is **0.00000000057**, or **(57/3898210)%**. [#8064](https://github.com/CrocSwap/integer-mult-bounds/pull/8064) · [Exact #8057 science](https://github.com/CrocSwap/integer-mult-bounds/tree/cbe847a953b971f9c6c5a0a6661e2008acd29086/research/frequency-weighted-native-multiplier)

The ordinary profile transfers eight levels from stage two to stage three with total height unchanged. The middle cut moves from 137,768 to 137,760 and the final cut remains 662,227. The candidate keeps the signed caller and Gaussian schedule and charges its larger private control envelope of 536,988,675 in log₂ units. The full recurring log₂ C ≤ 318,293,671 and fixed setup below 2²²⁸ still hold. The exact predecessor falls below the new rate, and transferring seven levels also falls short even with ideal earlier bookings. [Directed signed proof and exact controls](PROOF.md) · [One-case preflight](../r391/README.md)

All seven registered scientific modes passed in 183.74 seconds. The actual direct and compiled stage dispatch matches both seam profiles. The finite signed tape checks compare all 81 records modulo 3 and all 6,561 records modulo 9 with dense oracles, charge three and one exchanges respectively, and reject the wrong return sign. The nested transfer granted 4,507,783,464 axes with both owner returns, and the signed product −345550037539 and input restoration passed. Onboarding passed 760 tests with 31 skips, and the registered historical package passed its declared partial scope. [Scientific replay](scientific.log) · [Onboarding](onboarding.log) · [Historical replay](historical.log) · [Static gates](preflight.log)

Use CPython 3.12 and Git. From the exact release checkout root, run the complete scientific replay.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-ordinary-transfer
```

For detached literal pricing and seam verification, set `CANDIDATE` and `COMPARATOR` to the two exact checkout roots. Run from this handoff directory. Use `--round390-evidence` or `--round391-evidence` if those handoffs are stored separately.

```sh
out=$(mktemp -d)
python3.12 -IB replay.py --candidate "$CANDIDATE" --comparator "$COMPARATOR" --out "$out/verified.json"
cmp "$out/verified.json" public-verified.json
```

The detached check from two independent clean Git roots took 0.116 seconds. It reproduced the original receipt byte for byte after substituting exactly the path-redacted Round 390 onboarding log digest. The current onboarding log also masks one injected-test traceback path. The literal build, original verifier and sealed receipt retain their exact bytes. The public replay SHA-256 is `1bfb222dff908b9cfd73e7eb08a30fb778dbb0c4c03ce2aa4196a311f6a483a5`. [Public replay receipt](public-verified.json) · [Sealed receipt](verified.json) · [Digest substitution](PATH-REDACTION.json)

Ali Romman supplied #8057's signed typed source and ordinary clock, and #8055's native setup accounting. SYLforge supplied the unchanged K7 source. #8059 supplied the directed finite debit, and #8064 supplied the previous complete profile and upper band. OpenAI Codex assisted the proof, implementation and independent replay. [#8055](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) · [#8059](https://github.com/CrocSwap/integer-mult-bounds/pull/8059)
