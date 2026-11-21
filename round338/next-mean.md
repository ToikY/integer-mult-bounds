# Prospective Round 339 paid-mean test and timing trial

One change to the R338 fixed envelope: tighten both uses of the normalized paid log mean bound from 3/4 to 749/1000 on the same tilt, h=1804 and the same 451-factor signed graph. Fix p=20, at most 21 coefficient pairs and 60 seconds. This is a prospective test. No scientific calculation for this case was carried out when preparing this handoff.

From the campaign root, the first command is

```sh
python3.12 -I -B round338/next_mean.py --bit-source round321/benchmark/producer/BIT-451.json --round336-receipt round336/independent/receipt.json --round338-receipt round338/independent/receipt.json --out round339-price.json
```

On a clean PR checkout the BIT source may be research/bit-451-carrier-cover/source7863.tar.gz. Point the script and both historical receipts to their locations in the sealed handoff. The starter resolves the preceding screen relative to itself; use --previous-screen for an explicitly located copy. It authenticates that module's bytes before specializing its degree for its existing price and Newton-coefficient functions. Required runtime is CPython 3.12 on POSIX. Pins are SHA-256 538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749 for the archived BIT JSON, 69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818 for R336, 2c7692f263da6ccaacb7054471aff9d8a693371e8dcb3b83390d70a7bcff4d10 for R338, and 2df053c036c3bf8c3f4f6deccdcdfa3d4821b3c801c6410fe0e377dba6149d23 for round337/next_minimum.py. The p21 comparator has κ=0.00387992804538 and carrier loss 825/H. Refresh the frontier before claiming a gain.

## Frozen decision and prerequisites

1. The literal 14-bin before-splitting paid law at t=1−0.003879928046148 has 0≤Y=log₁₁(r)≤2 and directed raw mean upper 74847592422577689/10^17 from R336. First check that upper bound <749/1000. Independently authenticate ε=10⁻¹⁵ for the full positive original-job split plus completion increment divided by raw paid t-mass. The completed first moment is bounded by (raw_upper+ε)/(1+ε) using the old reference min(X_raw,1) and the actual paid normalizer. This *second* upper must also clear 749/1000. A raw mean alone cannot pay for split/completion.
2. Require the frozen formal limit ( (749/1000)/(23/20) )^20 < η_lower. At or above η_upper, the chosen formal upper polynomial cannot admit the required uniform rate. Inside its enclosure the comparison is unresolved. Both stop the screen before moment expansion. A failure of this comparison gives no impossibility for the true paid law, a tighter source-bound mean or other compiler proofs.
3. Require the sufficient base guard and full directed price with the terminal loss, strict cover, seven charged stages and all seven consumer test ticks. The projected new claim must exceed even raw_upper−825/H−7·10⁻¹⁴. Stop otherwise. These price and capacity gates charge the same physical program, accounting and transfer premises.
4. Only after both price and limit pass, the raw higher moments are bounded by the moments of (2/451)Binomial(451,749/2000). For every increasing convex f, the secant on [0,2] gives E f(Y)≤(1−749/2000)f(0)+(749/2000)f(2). Applying this to one independent raw factor at a time gives upper moments M_k of the raw sum; equality of means is unnecessary. The old clipped-reference kth moment ≤min(1,M_k), hence complete μ_k≤(min(1,M_k)+ε)/(1+ε). The vector need not be realizable by a common distribution. Bell/Newton coefficients have nonnegative dependencies on the individual upper moments. All 21 directed ratios below η_lower provide a uniform all-height result; one interior coefficient failure leaves the formal all-height comparison unresolved. A cap records completed coefficient IDs and leaves the unvisited ones open.

A complete claim requires independent reconstruction of the underlying paid law, all-size bound and signed consumer, and separation against the refreshed comparator. Credit zxv for the increasing-convex, capped reference and paid completion proof on the separated integer compiler, JoyboyBrian for the actual paid moment and leading-coefficient controls on the distinct old 260-factor case, and Clear1nsight for #7863/#7973. Prior campaign receipts supply the actual raw mean, full paid surcharge, predecessor p21 receipt and complete carrier/cover price; the proposed change uses one tighter rational bound on those already paid inputs. [#4480](https://github.com/CrocSwap/integer-mult-bounds/pull/4480) · [#5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042) · [#5070](https://github.com/CrocSwap/integer-mult-bounds/pull/5070) · [#7863](https://github.com/CrocSwap/integer-mult-bounds/pull/7863)

## Three-round review and one reversible measurement

The three primary receipts time the numerical screening command itself. Each consumer/runner.log independently reports its signed consumer runner duration. Neither captures the active time spent tracing the supplier proof, implementing the screen, independently auditing its argument, or reconciling paid normalizers ahead of launch.

| Round | Primary screen seconds | Signed consumer runner seconds |
| --- | ---: | ---: |
| 336 | 0.039405958 | 25.759346750 |
| 337 | 0.010768167 | 26.373406333 |
| 338 | 0.007855083 | 25.808658583 |

Among these measured runners the signed consumer consistently dominates. The greatest *active research* bottleneck is unknown: per-stage active proof and implementation were unmeasured. Chat timestamps, CI elapsed time and intervals between commits do not establish those durations. The present trial is inconclusive for attributing active effort; no faster workflow is established.

For the next comparable task, try one reversible change: at actual boundaries the assignee appends UTC time, worker role, task, event (start/stop) and activity to a handoff-local task log. Categories are source/proof, implementation, numerical solver, independent proof/replay, publication, and waiting. Record the timestamp of the first independently verified build/pivot decision. Keep proof work and replay runner time separate even under one worker; record concurrent worker intervals separately and avoid adding overlapping wall time. Retain the existing runner receipts without changing their scientific commands or controls. The measure succeeds if a subsequent matched task can identify its largest measured active category and its elapsed decision time without reconstructing missing intervals. Keep or reject the instrument after that trial; review separately whether a concrete workflow change actually speeds a matched decision with identical coverage. Missing events remain unknown.
