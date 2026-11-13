# Round 287 staggered owned1547 restoration

**NO VERIFIED GAIN.** The one fixed repair at pre-ADD41950 fails on the exact #7481 word and signed #7113 caller. The primary reverse-row replay and independent literal forward replay passed in 0.13 and 0.17 seconds wall, respectively, with exit code zero and separate 30-second caps. Both agree on the exact early cancellation. The optional CLEAR39897 restore solve was skipped because the mandatory later read already fails.

The edit retains the previous owned1521 direct descent and sends an extra −u on the existing owned1547 return at MOVE30581, where u is the original owned1510 value after ADD30530. It inserts `ADD 1547,1521,4,601` just before that return. The old and edited role402 differ by u, and the early 1547 offset cancels the discrepancy in role1536 at ADD30588. The primary proves equality there for all original input columns. The independent probe also checks the next reads ADD30590 and ADD30594, the unchanged numerical state of role569 and owned1531 at ADD41947, and the original return of role727 after the deleted ADD45355.

The separating input is x2=1, x4=−1 with every other original input zero. It gives u=1. At pre-ADD41950, the complete edited chart761 bank has role402=0 and role569=0, while the original role402=1. The all-zero input has the same edited bank and needs original role402=0. A correction restricted to this bank cannot satisfy both inputs, even with recipient self mixing. The first outward ADD41950 into role569 produces 1 on the original word and 0 on the unrepaired edit. The next other arrival, MOVE41951 of role1164, is after this deadline.

The same probe gives original owned1547=3/4 and edited owned1547=−1/4 at CLEAR39897. This is an observed numeric difference only. The conservative restore solve and physical erasure permission remain untested. The independent normalized replay checks the prior numerical owner/COPY guards, exact local charts and paid delta. The projected paid delta {1:−17,2:−17,3:+17} across 17 native calls gives directed gross [0.11809207775534055, 0.11809207775534056] raw, with productive ranks fixed. A changed role569 encoding, another clock or additional paid route remains outside scope. No physical signed map, complete changed invoice or κ gain was verified.

## Reproduce

From this directory with CPython 3.12, curl and shasum:

```sh
shasum -a 256 -c SHA256
replay_root=$(mktemp -d)
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

The fetch retrieves exact public bytes from fork commit `0d86bd1e4ae98624ef75123b93bb49e93801e872`, adds the included price and row engines, and checks every input by path and SHA-256. Replay works offline with the five declared inputs already in the supplied root. Both deterministic receipts are checked, with only measured elapsed seconds removed from the independent receipt. Expected marker `PASS_R287_OWNED1547_STAGGERED_HANDOFF`.

## Exact sources and credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) head `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b` supplies the complete comparable witness at κ `0.003647081039689`. [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supply its native lineage. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) head `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller. [#7538](https://github.com/CrocSwap/integer-mult-bounds/pull/7538) supplies public copies of the three raw inputs. [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supply exact reverse covectors and directed pricing. The Round 286 fixed-bank experiment supplies the direct descent and its first-deadline control. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Next experiment

The [four-clock B2 relocation test](next-body2/PLAN.md) moves B2 from the rank-56 calls at 1855/1869 to the rank-64 calls at 2324/2337. It leaves other calls and productive outputs fixed. The exact projected gross is 0.12311985005206546–0.12311985005206547 raw across eight ports. First test all 36 columns at port 15 with q=1, B2=−1 and other bodies +1. One candidate and 30 seconds. A mismatch retires the fixed ordinary wrappers. A survivor still needs all-body signed, physical and complete cost replay. The runner is syntax-checked and unrun.

After fetching the inputs above:

```sh
python3.12 -I -B next-body2/check_body2_relocation.py "$replay_root/inputs"
```
