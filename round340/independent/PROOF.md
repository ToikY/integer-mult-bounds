# Fixed power-20 scalar shifts under the measured-mean estimate

Every positive integer shift fails the existing requirement to beat the power-20 predecessor's relaxed complete ceiling on the existing comparison grid. The claim of the preceding head is 0.00387992804541. A claim inside the prior enclosure, a different grid, a different moment estimate or a different word remains open. The multiplier's actual costs are constrained here only through the frozen formal estimate. [Predecessor and exact source references](https://github.com/CrocSwap/integer-mult-bounds/blob/c2a4868b057898710a586d58e068189071d8ac45/research/bit-451-carrier-cover/tensor/MEAN.md)

For h≥2700 set a=h log(2)/(451 log(11)) and c=log(134)/log(11). At G=0 the positive coefficients and 21 exact moment bounds μₖ≥(749/1000)ᵏ give a lower bound of ((a+749/1000)/(a+c))²⁰ on the **formal** ratio. The inequalities 2²⁷⁰⁰⁰≥11⁷⁶⁶⁷ and 134²⁰≤11⁴¹ imply a≥17/10 and c≤41/20. Replacing c by 41/20 decreases the ratio. The ratio then increases with a because 41/20>749/1000. At the lower bound a=17/10 its twentieth power exceeds the upper endpoint of the directed capacity by more than 0.000010249. Thus the formal height-zero guard excludes the upper half-line before pricing.

For 1≤h≤2699, (1+H/h)²⁰ is minimized at 2699. At that endpoint it lies in [2⁷⁷³,2⁷⁷⁴), forcing J≥774 for every such h. Set C to the proved trial less 774/H and the full cover debit 1/(H·2⁴⁴). Composing the seven unrounded stages gives the upper service rate (1−ρ⁷)C+ρ⁷s, where s and ρ are the authenticated seed and contraction. Subtracting the seven mandatory test ticks gives a continuous upper **above** the old relaxed ceiling. Its largest strictly admissible grid point is 0.00387992804543, which falls **below** that ceiling by exactly 131/100200000000000000. That grid upper exceeds the predecessor's displayed claim by 0.00000000000002. No individual small shift was constructed. [Exact original seven-stage supplier](https://github.com/CrocSwap/integer-mult-bounds/tree/b3e4412fe01f07dc58305616fabf96345f49a781/research/p104-bit-451-factor-schedule)

**Independent replay.** From the exact predecessor checkout, put this handoff's standalone `audit.py` in the current directory and run the following with CPython 3.12 and two new temporary output paths. The verifier checks the exact source and proof hashes and uses its own integer and rational arithmetic. A 60-second alarm bounds execution.

```sh
pkg=research/bit-451-carrier-cover
tmp=$(mktemp -d)
tar -xOzf "$pkg/source7863.tar.gz" package-sanitized/BIT-451.json > "$tmp/BIT-451.json"
python3.12 -IB audit.py "$tmp/BIT-451.json" "$pkg/tensor/MEAN.json" "$tmp/exclusion.json"
```

The output must report `PASS_FIXED_P20_SHIFT_EXCLUSION 774 387992804543/100000000000000`. Its deterministic receipt has SHA-256 `f9d0c62f1d0912d8f4d433f54128fb04ee0b8d4219b11bef4bc54fa11afb4b06`. Changing one supplied input byte must fail the source check.

Clear1nsight supplied the #7863 word and #7973 consumer. zxv supplied the positive tensor comparison, JoyboyBrian the earlier paid mean and clipping controls, and Ali Romman the all-height criterion. The preceding #8026 certificate supplied the measured moments, existing seven-stage procedure, and source pins. OpenAI Codex assisted this independent proof and replay. [#4480](https://github.com/CrocSwap/integer-mult-bounds/pull/4480) · [#5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042) · [#5070](https://github.com/CrocSwap/integer-mult-bounds/pull/5070) · [#5351](https://github.com/CrocSwap/integer-mult-bounds/pull/5351) · [#8026](https://github.com/CrocSwap/integer-mult-bounds/pull/8026)
