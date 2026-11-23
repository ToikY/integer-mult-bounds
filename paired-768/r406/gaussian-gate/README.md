# One exact Gaussian exterior-period bound

The source is Clear1nsight's [#8078 at b72d3fa](https://github.com/CrocSwap/integer-mult-bounds/commit/b72d3fa097d2521939f6b8536029da674648d863), with κ = 0.00389834, ordinary heights (8192,36220,575705), Gaussian height 978582, and complete recurring log₂ C = 413727211. Its Gaussian receipt matches [#8076 at d502eb2](https://github.com/CrocSwap/integer-mult-bounds/commit/d502eb21637717fe22fc16d4c4e3ede6ec59a106) field for field. Ali Romman's #8057 supplies the archived physical producer and all-size positive clock, SYLforge supplies K7, and #8072 supplies the funded integer weights and exact signed prices used by #8078. Codex assisted the proof and verification.

## Charged mechanism

For exterior size s = (e−8)k, the installed four-aligned physical period is q = 4⌈M/(4s)⌉. The construction retains its exact s and q, all source counts and phases, physical routes, owner allocations and returns. It also retains the existing endpoint, integer, delay-end, round truncation, copy group and fixed setup charges. Only the upper bound on q s/M improves.

With x = M/(4s), the existing scale and largest target grade imply x ≥ 263772/1032 > 255. If x ≤ 256, then ⌈x⌉/x ≤ 256/(263772/1032) < 257/256. If x > 256, then m = ⌈x⌉−1 ≥ 256 and ⌈x⌉/x < (m+1)/m ≤ 257/256. Thus the full proof may replace the old factor 22067/21981 = 1+1032/263772 with 257/256 for every actual exterior field at all admitted heights.

After scaling the independently reconstructed complete Gaussian factor, the exact dyadic price 64934/524288 has reserve greater than 0.000000232515772047. The adjacent 64933/524288 fails by more than 0.000001208067461857 under this envelope. The distinct interval, finite grids and earlier-stage costs all remain in the invoice. For the exact new target at the old Gaussian rank, the minimum reduction from the old 64939/524288 booking lies strictly between one and two grid ticks. The new bound supplies five ticks.

## Reproduce the one-case price

Run with Git and CPython 3.12 from a clean clone of the handoff. Use an exact #8078 detached checkout as `peer-checkout`, an exact #8076 checkout as `prior-checkout`, and #8076's [independent exact invoice](https://github.com/ToikY/integer-mult-bounds/blob/b6c4ffec0f58940a5da4523219614fce3d8409f6/paired-768/r405/verification/independent-invoice.json) as the third dependency.

```sh
python3.12 -IB paired-768/r406/gaussian-gate/check.py \
  --peer peer-checkout \
  --prior-installed prior-checkout/research/p104-weighted-child-tariff/RESULT.json \
  --prior-invoice paired-768/r405/verification/independent-invoice.json
```

One profile solves the same-cap and same-height decision with a 30-second timer. Output replayed byte for byte with exit 0. Moving 180 ordinary height units from H3 to H2 gives (8192,36400,575525) with the same sum. At G = 978582 this prices κ = 0.0038983400039, clearing the entire old Gaussian bound at this maximum rank under the unchanged invoice. Keeping the old Gaussian debit or the old ordinary heights misses the new target. Exact arithmetic and both sets of 54+4 signed margins are in `receipt.json`.

Before the only literal build, the exact positive inequality gives the minimum admissible Gaussian height by flooring 64934 / (524288(c_G−κ−5·10⁻¹⁸)) and adding one. This gives G = 978537, with G−1 rejected. The same ordinary shape then gives complete log₂ C = 413717311, first terminal header 2^1599128+2, maximum native height 978537, entry conversion 717, and the same setup bound below 2^228. Larger changes to the period distribution and other proof terms remain outside this result. This package supplies a price and signed construction candidate. The scientific and hosted replay gates must pass independently before claiming a new κ.
