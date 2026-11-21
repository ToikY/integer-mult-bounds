# Round 336 complete grid proof and next bounded test

The 16-bin law on the unchanged 451-factor word certifies conditional κ = 0.00387992804518. The exact gain over the preceding #8026 proof is 0.00000000000013. Against independently reproduced peer #7863 the cumulative gain is 0.00000000000172, approximately 0.0000000443307190426%. All 28 coefficient bounds pass for power 27. The limiting ratio at power 26 exceeds the true capacity upper endpoint. This settles integer powers for this single comparison law. [Signed scientific package](https://github.com/CrocSwap/integer-mult-bounds/tree/18718411ece1481c79d317c9ee9e1445dcf8ef28/research/bit-451-carrier-cover/grid) · [Source and proof credit](https://github.com/CrocSwap/integer-mult-bounds/blob/18718411ece1481c79d317c9ee9e1445dcf8ef28/research/bit-451-carrier-cover/grid/PROOF.md)

Use CPython 3.12. From the pinned #8026 checkout the first command replays the complete result. The second is a prospective single-case arithmetic test at power 23. It assumes this handoff checkout is in a sibling directory named `handoff`.

```sh
python3.12 -IB scripts/research_package.py --package research/bit-451-carrier-cover
python3.12 -IB ../handoff/round336/next_moments.py --bit-source research/bit-451-carrier-cover/source7863.tar.gz --round336-receipt research/bit-451-carrier-cover/grid/RESULT.json --out round337-price.json
```

The prospective test has a 60-second cap. An all-height price pass earns independent proof and full signed replay. [Prior art and peer coverage](frontier.md) · [First test and stop conditions](next-moments.md)
