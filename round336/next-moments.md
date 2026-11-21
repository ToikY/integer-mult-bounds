# Prospective Round 337 paid tensor moment test

Freeze one case: p=23, h=1804, the original #7863 physical paid cutoff 11^451, the same signed caller and seven-stage schedule, 60 seconds, 24 coefficient ratios checked in order 0,23,1,…,22. No test or price for this candidate was executed when writing this handoff. The Round 336 local comparator is conditional κ=0.00387992804518, p=27, terminal loss 1061/H. Refresh it before publication. The previous comparison law rounded completed ranks to sixteenths. This proposal avoids those round-ups by controlling each of the first 23 moments directly. It cannot deduce an entire interval of rejected powers from those bounds.

Run from the saved campaign root with CPython 3.12:

```sh
python3.12 -I -B round336/next_moments.py --bit-source round321/benchmark/producer/BIT-451.json --round336-receipt round336/independent/receipt.json --out round337-price.json
```

The first argument may instead be research/bit-451-carrier-cover/source7863.tar.gz from the prior clean submission. The command authenticates the exact JSON member (SHA-256 538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749) and the independent Round 336 receipt (69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818). Existing outputs are preserved. Before computing the 23 raw moment bounds it checks the fixed base guard and limiting ratio. It also computes the strict terminal loss, charged cover, seven ordinary stages, consumer reserve and separation from the old relaxed complete ceiling. A failed directed price stops the case.

## Proof and scope

For each of the 451 *raw* independent tensor factors, Y=log₁₁(r) has 0≤Y≤2 because max raw paid rank is 56≤121. Its probability law is the signed-word paid t-tilt at t=1−0.003879928046148, with all positive multiplicities. Round 336 independently directs its mean below 3/4. For increasing convex f on [0,2], the secant at 0 and 2 gives E[f(Y)]≤(1−3/8)f(0)+(3/8)f(2). This is increasing-convex domination; equality of means, a requirement of the usual convex order, was never assumed. Applying this inequality one coordinate at a time to the positive integer power of the nonnegative raw average gives, for k≥1,

    M_k = (2/451)^k sum_{j=1}^k S(k,j) (451)_j (3/8)^j.

This is the exact kth moment of a rescaled binomial and an upper bound on the raw kth moment. The kth moment of the *capped* old reference is ≤min(1,M_k), since min(X_raw,1)^k≤X_raw^k and is at most one. The clipped power need not be convex. Every old call above the cutoff carries unit reference value, so its replacement can increase the weighted numerator by at most its additional paid mass. Every completion contributes at most its **entire positive paid mass**. The exact split and completion increment as a fraction of raw mass is x; its certified upper bound is ε. Division by the actual total mass and monotonicity in x give

    E[X^k] ≤ (min(1,M_k)+ε)/(1+ε).

The R336 independently proved raw mean bound and positive uplift also imply E[X]≤3/4, used to tighten the k=1 bound. The fresh run must authenticate those inequalities. No independence of split pieces, fractional dispatch, net productive credit or change in physical tape and ownership is introduced.

The inherited #4480 Bell and shift polynomials have nonnegative coefficients in all individual μ_k. Apply them to these upper bounds without supposing a single probability law realizes every μ_k. All 24 certified coefficient ratios below the directed η lower bound yield a uniform contraction for every integer height. A failed coefficient excludes only this sufficient coefficient comparison. A failed upper-base or lower-η guard similarly excludes only that sufficient test. These outcomes do not exclude the true distribution or all-height polynomial. On a cap, retain the last recorded coefficient IDs and the specific missing inequalities. A fresh allocation requires a new output path. No independent consumer or full theorem is supplied by this command. A surviving construction needs an independent source-to-profile reconstruction, all-height proof, full signed consumer, and current comparator check.

## Priority and sources

zxv's #4480 at 4cf054a50c5718616594ec4ca2c9114278120a8b already proves this raw chord, capped full paid-excess bound, and higher-moment coefficient method. JoyboyBrian's #5042 at 7d09263f63f8a05537a659045dbd7e98ae7237c6 used *actual* raw moments through order 24 and independent EGF reconstruction on the older 260-factor witness. #5070 at fd2d388093e3a471c81dbb7ca90c36fd9d1b6dd2 bounded clipping from its first two raw moments and excluded its fixed degree-23 law. Their conditional exclusion depends on that supplier's mean, scale, capacity and paid excess. It does not carry to the literal 451-factor inventory. A publication should credit their priority and describe only the new source-specific instance, complete price and independently replayed result. Ali Romman's #5351 supplies the rational-law decision background, the submitted test uses #4480's direct sufficient coefficient bound. Clear1nsight's #7863 and #7973 supply the original schedule and independent audit. Earlier #8026 and R336 carry the charged cover, physical transfer, previous price and independent raw-mean bounds. [#4480 exact source](https://github.com/CrocSwap/integer-mult-bounds/blob/4cf054a50c5718616594ec4ca2c9114278120a8b/research/net-tax-rank-compiler/LOG-MOMENTS.md) · [#5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042) · [#5070](https://github.com/CrocSwap/integer-mult-bounds/pull/5070) · [#5351](https://github.com/CrocSwap/integer-mult-bounds/pull/5351) · [#7863](https://github.com/CrocSwap/integer-mult-bounds/pull/7863)
