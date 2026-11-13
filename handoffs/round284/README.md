# Round 284 two-rail Type B stage-7 seam

**NO VERIFIED GAIN.** At the single fixed cut before event1215, both candidate B7 parities are excluded for an input direction encoded only in the original Type B rails50 and51 on the exact #7113 paid schedule. The primary and independent replays finished in 0.06 and 0.16 seconds wall respectively, with exit code zero and a 30-second cap each. Both classes and both sectors were resolved.

For each parity, allow arbitrary body-independent Gaussian rational input weights independently in both central-even sectors q²=±1. All coefficient rows outside the chosen B7 parity are forbidden. A nonzero determinant on two such rows already prevents any nonzero input combination from producing the desired support. The independent replay reconstructs the columns with a separate sparse local matrix engine, checks the exact primary minors at roles36 and37, and computes the Gram determinant of the complete forbidden coefficient matrix. Each matrix has 16 coefficient rows.

| Intended first return | Forbidden B7 parity on rows36 and37 | Minor in q²=+1 | Minor in q²=−1 | Full forbidden Gram determinant in each sector |
| --- | --- | --- | --- | --- |
| B7 | Odd | −1 | +1 | 23177/256 |
| q B7 | Even | −1 | −1 | 28553/256 |

The original endpoint row and column of each input rail replay exactly to the prescribed q³B7B8 diagonal after all 4,783 events, in both sectors. The controls reject a wrong row orientation and distinguish an odd phase from its other sector value. The failed ingress is independent of which decoder is allowed, so no fixed two-rail decoder, dual pairing, or suffix branch was tested. The exclusion covers this exact cut, original pair, unchanged paid chronology and body-independent encoding. Wider input groups, other cuts and different paid chronology are outside scope. The calculation is a normalized Gaussian Laurent support test, with signed physical exposure and the all-size operator contract separate.

The projected productive delta would replace eight rank-17 credits with eight rank-eight and eight rank-nine credits, without paid changes. Its directed gross interval is [0.33985048763130562, 0.33985048763130563] raw at the pinned crossing. The failed ingress prevents any literal split or complete reprice.

## Reproduce

From this directory with CPython 3.12, curl and shasum:

```sh
shasum -a 256 -c SHA256
replay_root=$(mktemp -d)
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

The fetch command retrieves exact source bytes from public fork commit `0d86bd1e4ae98624ef75123b93bb49e93801e872` and authenticates every input by relative path and SHA-256. Replay works offline with the paths in `INPUT-SHA256` already available at the explicit root. The manifest includes the comparator word for source closure. The wrapper compares both deterministic receipts, excluding only independent elapsed time. Expected marker `PASS_R284_TYPE_B_STAGE7_PAIR_HANDOFF`.

## Exact sources and credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) head `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b` supplies the complete comparator at κ `0.003647081039689` and exact application. The application names the [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) predecessor at `58a9d052143f5d85295ed2d0163591c47f89a331`. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) head `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller. [#7538](https://github.com/CrocSwap/integer-mult-bounds/pull/7538) supplies public copies of the pinned raw inputs.

[#7536](https://github.com/CrocSwap/integer-mult-bounds/pull/7536), [#7519](https://github.com/CrocSwap/integer-mult-bounds/pull/7519) and [#7398](https://github.com/CrocSwap/integer-mult-bounds/pull/7398) supply the signed-sector support and exact Laurent precedents. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed tariffs. The [Round 283 handoff](https://github.com/ToikY/integer-mult-bounds/tree/d0647837c539bccc66437a5af75a91ad0118300d/handoffs/round283) supplies the literal rail50 failure, exact cut and independent sector matrix engine. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Next incremental test

The overlap check retired the four-to-three Type A QUERY idea under the unchanged J blocks by [#7309's defect-rank bound](https://github.com/CrocSwap/integer-mult-bounds/blob/0de5abc36b4a17c7da4f29e1c3e78f956bf33de5/research/p104-signed-caller-relative-defect-bound/PROOF.md). No duplicate solve ran. Prior [#7486](https://github.com/CrocSwap/integer-mult-bounds/pull/7486) and [#7397](https://github.com/CrocSwap/integer-mult-bounds/pull/7397) also block the canonical one-core rank-18 idea for Type B events 1339/1340 in the fixed-fibre even-erasure model.

The [rank-13 partial-fibre plan](next-rank13/PLAN.md) instead tests the physical compiler's one-job volume contract. Pin one port, the two independent old returns, and a rank-13 proposal at 11/8 old field volume. The optimistic gross is 1.18214082242914628–1.18214082242914629 raw across eight ports, conditional on the unproved volume-linear admission. Follow the pinned binder, tape and invoice sources for up to 30 seconds. Stop on an exact typed obstruction or an explicit witness. A timeout leaves the geometry unresolved. No replacement supplier has been built.
