# Round 281 paired outward-read census

**NO VERIFIED GAIN.** On exact #7481 with the signed #7113 caller, both inventories exhaust the fixed model with 260 single-outward MOVE windows, four consecutive same-receiver pairs, and zero eligible funded orientations. The 64-case cap applies to already eligible directions. None reached that gate, so zero were priced and zero identified directions remain unresolved. Each run had a 30-second cap. The original primary and independent wall times were 0.16 and 0.25 seconds, with exit code zero.

The test requires one outward ADD per producer, the same receiver with consecutive writes, a common exact low and middle chart, no changed intervening scalar contacts, and both independent values restored through one fully charged return detour. It omits protected and already reserved roles. The first exact failure in either orientation of each pair is:

| Receiver | Old ADD clocks | Producer roles | Exclusion for both orientations |
| --- | --- | --- | --- |
| 230 | 32729, 40817 | 227, 719 | Exact entry charts differ |
| 256 | 36316, 36318 | 416, 735 | Exact entry charts differ |
| 256 | 36318, 36320 | 735, 288 | Exact entry charts differ |
| 1022 | 32436, 36385 | 1023, 831 | A producer leaves before the second read |

The independent receiver-first inventory checks literal chart, activity and ownership guards and the known positive #7481 price shape (4,2,1). The positive control checks pricing only. No build or complete application was run. Multi-read windows, distinct paid itineraries, receiver chronology changes and alternative restorations remain open.

## Reproduce

From this directory with CPython 3.12, `curl`, and `shasum`:

```sh
shasum -a 256 -c SHA256
replay_root=$(mktemp -d)
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

The first command authenticates this handoff's files. The fetch command downloads exact public source bytes from fork commit `0d86bd1e4ae98624ef75123b93bb49e93801e872` and checks every input. The replay command works offline with an explicitly supplied directory containing the four paths in `INPUT-SHA256`. It compares both deterministic receipts, excluding only measured elapsed time from the independent result. Exact expected marker `PASS_R281_PAIRED_OUTWARD_HANDOFF`.

## Exact sources and credit

Comparator [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) at `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b` supplies the native word, exact application and funded two-producer construction. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller. [#7538](https://github.com/CrocSwap/integer-mult-bounds/pull/7538) supplies exact public copies of the three source files. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) and [#7494](https://github.com/CrocSwap/integer-mult-bounds/pull/7494) supply chronology and fixed-peer outward retiming precedents. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed tariffs.

The [peer triangular producer investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19586314) supplies the shared encoding and charged detour algebra for its explicitly multi-read domain. This handoff checks the one-read-each model. OpenAI Codex and subagents materially assisted design, implementation and independent replay. Apache-2.0.

## Next incremental test

Use [the paired incoming-update plan](next-incoming/PLAN.md). Two public destinations receive a value from the same unchanged source. The exact normalized construction pre-encodes their independent input values on a common chart, keeps one old incoming ADD, and restores both old outputs through a fully charged return. This tests shared incoming reads and leaves the source's value and itinerary fixed. The cap is one metadata pass, 64 qualifying price-ranked orientations and 30 seconds. Stop at one positive directed gross bound or exhaustion. A nominated route needs exact signed action and complete charges. The test is syntax-checked and unrun.

From this directory after the source fetch above:

```sh
python3.12 -I -B next-incoming/check_paired_incoming.py "$replay_root/inputs"
```
