# Round 283 literal Type B stage-7 seam

**NO VERIFIED GAIN.** One literal coordinate and cut were tested on the exact #7113 signed caller. Type B rail50 cannot give an isolated rank-eight B7 return immediately before event1215 under the fixed chronology. The primary and independent checks passed in 0.33 and 0.12 seconds wall respectively, with exit code zero and separate 30-second caps. The one declared case was resolved.

Both sectors q²=+1 and q²=−1 have 14 nonzero off-diagonal terms in the rail50 output row and 24 nonzero off-diagonal terms in the rail50 input column at that cut. In each sector, input48 contributes +B6B7 to output50 and input50 contributes −2B7 to output36. Both witnesses have even parity. The full original rail50 row and column nevertheless give exactly the prescribed q³B7B8 diagonal at the end of the 4,783-event caller. The primary reconstructs the row by forwarding all 36 Type B inputs. The independent checker uses a reverse algebraic row pullback and a separately oriented forward column. Its nonsymmetric ADD control rejects a mistaken row orientation, and its odd-phase control distinguishes the two sectors. The algebraic row pullback is a coefficient check.

The fixed one-rail separation would have credited +8 rank-eight, +8 rank-nine and −8 rank-seventeen productive returns across the eight Type B ports, with paid work unchanged. Its directed gross opening was between 0.33985048763130562 and 0.33985048763130563 raw at the pinned crossing. The literal cut fails the necessary prefix gate, so no suffix build or complete reprice was applicable. Grouped input bases, different rails or clocks, changed caller schedules, or another physical exposure mechanism remain outside scope.

## Reproduce

From this directory with CPython 3.12, curl and shasum:

```sh
shasum -a 256 -c SHA256
replay_root=$(mktemp -d)
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

The fetch command retrieves exact public source bytes from fork commit `0d86bd1e4ae98624ef75123b93bb49e93801e872` and verifies every input by relative path and SHA-256. The replay command works offline given a root with the paths in `INPUT-SHA256`. The manifest includes the exact comparator word for source closure even though neither Laurent checker imports it. Both replay receipts are compared deterministically, excluding independent elapsed time only. Expected marker `PASS_R283_TYPE_B_STAGE7_HANDOFF`.

## Exact sources and credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) head `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b` supplies the complete comparator at κ `0.003647081039689` and its exact application. The application names the exact [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) predecessor at `58a9d052143f5d85295ed2d0163591c47f89a331`. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) head `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller. [#7538](https://github.com/CrocSwap/integer-mult-bounds/pull/7538) supplies the public copies used by the fetch.

[#7536](https://github.com/CrocSwap/integer-mult-bounds/pull/7536) supplies the Type B signed propagation model and preceding fixed-root scope. [#7398](https://github.com/CrocSwap/integer-mult-bounds/pull/7398) supplies the retained Gaussian Laurent arithmetic, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed tariffs. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Next incremental test

The [paired Type B seam plan](next-stage7-pair/PLAN.md) grants an input basis on old rails 50 and 51 and a corresponding seam decoder on the same two rails. Test both even B7 and odd q B7. The first gate asks for a nonzero ingress vector with no forbidden body or parity term in either sector. A survivor needs a dual decoder and nonzero pairing before physical admission. One cut, two parity classes and 30 seconds. Any fully charged additional rank-one job per port consumes the projected gross. The test is syntax-checked and unrun.

After the source fetch above:

```sh
python3.12 -I -B next-stage7-pair/check_stage7_bilateral.py "$replay_root/inputs"
```
