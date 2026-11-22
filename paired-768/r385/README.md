# Complete 5-to-451 signed integer birth replay

Exact `56bd64bed76cadb98e459ed001ccbdf47963ccf6` verifies conditional **κ = 0.00389821035** under the five inherited signed assumptions. The exact gain over reproduced #8061 at 0.00389821034 is **0.00000000001**, or **(50/194910517)%**. The change over external #8057 at 0.00389821 is **0.00000000035**, or **(35/3898210)%**. The real `(5,451)` birth counts fund all 51/88 cells and keep both signed widths, phases and owner returns. The old `(6,541)` counts fail at the new tariff, and the one-too-short ordinary height fails funding. The actual recurring log₂ C≤318282151 and fixed native setup ≤2^228 include the whole revised price. [Independent proof and controls](PROOF.md) · [R384 pinnings and physical checks](../r384/README.md)

All seven registered scopes passed in 156.05 seconds. At ordinal 3418 the actual nonzero cross-type loan grant was **4,507,783,464**. Both signed return paths, exterior owners, the exact product −345550037539 and restored inputs passed. Onboarding passed 760 tests with 31 skips, and the declared historical scope passed. [Exact signed log](scientific.log) · [Detached verified receipt](verified.json)

From the exact candidate checkout run Git and CPython 3.12:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-integer-frequencies-5-451
```

For detached replay set `CAPSULE` to the package directory from that checkout. From this handoff directory:

```sh
out=$(mktemp -d)
python3.12 -IB accept.py --inputs evidence --capsule "$CAPSULE" --out "$out/accept.json"
cmp "$out/accept.json" verified.json
```

Ali Romman supplied the exact typed #8057 work and #8055 native clock. SYLforge supplied K7. #8059 supplied the exact debit and #8061 the previous fully replayed two-type integer profile. OpenAI Codex assisted the exact proof, implementation and independent verification. [Typed predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Prior reproduced comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/8061)
