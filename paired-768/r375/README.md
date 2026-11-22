# Two exact limits on the compact quarter schedule

**No verified κ gain in Rounds 374–375.** Round 374 reproduced the 1-to-79 schedule on actual signed nonzero columns, then became weaker than the new #8057 peer proposal. At its installed heights, the ordinary ceiling is about 0.003898202001206843 and the Gaussian ceiling about 0.003898203449789259. Even the best Gaussian raw endpoint with the old Gaussian debit misses 0.00389821 by more than 3.3297654977e−9. The fixed two-tier construction is therefore retired as a frontier candidate. [Exact bounds and distinct successor test](PROOF.md) · [Frontier and assumptions audit](FRONTIER.md)

## Reproduce the exclusion and the next price

Use CPython 3.12 from this directory. The evidence tree holds the exact independently authenticated inputs, including both predecessor controls. No temporary pointer or external interpreter path is needed.

```sh
out=$(mktemp -d)
python3.12 -IB check.py --inputs evidence --out "$out/verified.json"
cmp "$out/verified.json" evidence/round375/independent/verified.json
python3.12 -IB coupling.py --inputs evidence --out "$out/coupling.json"
cmp "$out/coupling.json" coupling.json
```

The exact Round 374 checkout is `28f9516bbd758831650efd2f9fc3ed5a586f0eb5`. From the root of that checkout, run both registered packages. Onboarding also passed locally with 760 tests and 31 skips. No hosted checks were run for Round 374.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-compact-rounded-partitions
python3.12 -IB scripts/research_package.py --package research/p104-compact-rounded-partitions-numerical-replay
```

The signed numerical run traverses 564,144 paid cuts, 105,216 independent owners and 358,410,240 output axes at widths 6 and 474. The signed multiply returns −345550037539 with restoration, 138 bank shuttles and 157,248 H calls. [Exact literal source](https://github.com/ToikY/integer-mult-bounds/tree/28f9516bbd758831650efd2f9fc3ed5a586f0eb5/research/p104-compact-rounded-partitions) · [Main replay](main-replay.log) · [Numerical replay](numerical-replay.log)

The sole surviving next test replaces the Gaussian debit with 339/2048 and retunes the terminal binary height. Both signed prices and all 63 transport cells clear the exact arithmetic screen. Fifty-one shares change, so a fresh calendar and complete signed replay are required. No other debit, height, or physical width was tested. [Next test and exact obligations](PROOF.md)

Ali Romman supplied #8055's compact native tiers, along with #8057's distinct weighted chronology. SYLforge supplied K7. Reused #8056 work includes the integer quarter and complement and phase accounting. OpenAI Codex assisted the constructions and independent checks. [Compact tiers](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) · [Integer partitions](https://github.com/CrocSwap/integer-mult-bounds/pull/8056) · [Weighted peer](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
