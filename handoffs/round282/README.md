# Round 282 paired incoming transfer census

**NO VERIFIED GAIN.** Both exact inventories exhausted the fixed paired incoming transfer model on the #7481 word with its signed #7113 caller. They found 264 single-incoming MOVE windows, six consecutive pairs within stable source versions and zero eligible funded orientations. All 12 orientations were screened. No direction reached the price-ranked list, so no ranked keys were tested or left unresolved. Each run finished within its 30-second cap, with a limit of 64 price-ranked keys. Primary wall time was 0.14 seconds and independent wall time was 0.25 seconds. Both exited zero on CPython 3.12.14.

The fixed edit requires two distinct unprotected public recipients with one incoming ADD each on their paid visit to the same chart. They must use the same source version, enter on the same exact paid chart pair, and have nested high charts for a funded decode that restores both independent original values. A donor's version is the clock of its last write or chart transition. The independent checker walks these histories in source-first order and treats any ADD, COPY, SCALE, MOVE, INIT or CLEAR targeting the donor as a new version. Intervening reads leave it unchanged. It checks the original chart and owned activity metadata across all 76,475 events and excludes the 400 protected roles, owned roles, and ten named active or funded roles.

| Source at version clock | Original ADD clocks | Recipients | First rejection in both orientations |
| --- | --- | --- | --- |
| 258 at 31615 | 31618, 31651 | 259, 61 | Same entry 3→2, with incomparable departure charts 293 and 304. |
| 924 at 42533 | 42534, 43012 | 1362, 1335 | Exact lower charts 1088 and 1026 differ before entry into170. |
| 994 at 36630 | 36631, 38402 | 991, 1346 | Exact lower charts 75 and 599 differ before entry into261. |
| 1020 at 37919 | 37920, 38011 | 1066, 1051 | Exact lower charts 235 and 234 differ before entry into518. |
| 1020 at 37919 | 38011, 38800 | 1051, 1176 | Exact lower charts 234 and 498 differ before entry into518. |
| 1020 at 37919 | 38800, 38868 | 1176, 1351 | Exact lower charts 498 and 516 differ before entry into518. |

The independent replay verifies the normalized shear identity on three independent input coordinates, rejects an altered decode sign, and reproduces the positive directed price of the known funded rank pattern (4,2,1). These controls exercise the algebra and tariff. No literal nomination reached physical signed action, adjoint, phase, restoration or full signed cost verification. Nonconsecutive eligible pairs, different donor versions, changed lower charts, alternative repair and paid itineraries remain open.

## Reproduce

From this directory with CPython 3.12, curl and shasum:

```sh
shasum -a 256 -c SHA256
replay_root=$(mktemp -d)
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

The fetch command retrieves exact public source bytes from fork commit `0d86bd1e4ae98624ef75123b93bb49e93801e872` and authenticates the four input files by path and SHA-256. Replay also works offline with an explicitly supplied root containing the four paths in `INPUT-SHA256`. It compares deterministic primary and independent receipts, excluding only the independent elapsed time. The expected marker is `PASS_R282_PAIRED_INCOMING_HANDOFF`.

## Exact sources and credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) head `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b` supplies the native word, exact application and funded two-field detour. The unchanged benchmark is κ `0.003647081039689`. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) head `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller. [#7538](https://github.com/CrocSwap/integer-mult-bounds/pull/7538) supplies public copies of the three authenticated source files.

[#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) and [#7494](https://github.com/CrocSwap/integer-mult-bounds/pull/7494) supply chronology and contact-slide precedents. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed tariffs. The preceding [Round 281 paired-outward handoff](https://github.com/ToikY/integer-mult-bounds/tree/bb1b80a7916f6fa35b10323601660436c8d82009/handoffs/round281) supplies the transposed fixed two-field screen. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Next incremental test

The [Type B stage-7 seam plan](next-stage7/PLAN.md) tests whether the completed paid B7 stage already isolates the old arbitrary input on rail50 at pre-event1215. It changes the source of potential savings to productive credit. The proposed rank-17 split into ranks 8 and 9 has projected gross 0.33985048763130562–0.33985048763130563 raw across all eight Type B ports, with fixed paid counts. The first test checks both row and column isolation in both signed sectors, then the fresh suffix on a survivor. One role, one cut, 30 seconds. Physical exposure of the old result, legal admission of a fresh arbitrary input and complete cost and signed replay remain required. The test is syntax-checked and unrun.

From this directory after the source fetch above:

```sh
python3.12 -I -B next-stage7/check_stage7_isolation.py "$replay_root/inputs"
```
