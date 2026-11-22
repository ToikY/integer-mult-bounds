# Complete signed replay at lower band 1,874

Exact release `682fd9512ccbf3035089d7e5f9cb4dedf9f746b4` certifies conditional **κ = 0.00389821040**. The gain over independently reproduced #8062 at 0.00389821035 is **0.00000000005**, or **(100/77964207)%**. The gain over external #8057 at 0.00389821 is **0.00000000040**, or **(4/389821)%**. The change uses a lower Gaussian band of 1,874, debit 64982/524288 and terminal ordinary height 524,369. It charges the same 456 integer openings and all 51 grade and 88 typed transport cells. Its recurring log₂ C≤318285351 and fixed native setup below 2^228 are fully charged. [Scope and costs](PROOF.md) · [R387 arithmetic and calendar evidence](../r387/README.md)

All seven registered scientific modes passed in 167.38 seconds on the scientific commit. The release changes a single proof line. The new cutoff verifies all eight transfers into the first band and 523,324,250,322 paid leaf axes in the reduced fixture. The genuine nonzero loan at ordinal 3418 grants 4,507,783,464 axes on the unchanged physical word. Both signed owner returns, the exact product −345550037539 and input restoration passed. Onboarding passed 760 tests with 31 skips, and the registered historical scope passed. [Exact scientific log](scientific.log) · [Detached check receipt](verified.json)

For the complete replay, check out the exact release with Git and run CPython 3.12 from the checkout root.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-lower-band
```

For detached replay, set `CAPSULE` to that checkout's package directory. Use the evidence supplied here with explicit roots.

```sh
out=$(mktemp -d)
python3.12 -IB accept.py --inputs evidence --capsule "$CAPSULE" --out "$out/accept.json"
cmp "$out/accept.json" verified.json
```

Expected detached SHA-256 is `a795a3fd9e4812d5bba4f46ab1a6c403bf83180fc1247b2196beae756c58693c`. Ali Romman supplied the typed #8057 producer, its finite-loss proof, and the #8055 native setup clock. SYLforge supplied K7. #8059 supplied the exact edge method and #8062 the reproduced (5,451) baseline. OpenAI Codex assisted the construction, proof and independent replay. [Typed predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Exact prior comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/8062)
