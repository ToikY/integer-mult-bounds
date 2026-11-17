# Two scoped paid-stop exclusions on the original #7605 word

**NO VERIFIED GAIN.** Rounds 301 and 302 exclude two ways to remove a paid stop under the original #7605 erasure contract. The results retire the closed two-role exchange screen and one fixed-prefix swap-then-delete splice. Both preserve the existing #7605 benchmark.

## Exact source and replay

Use [#7605](https://github.com/CrocSwap/integer-mult-bounds/pull/7605) at `e1d2756eecf03e146338239fee81772a99ba8d4c` and the signed [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The native word has 76,636 events. Its canonical SHA-256 is `e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd`. The replay authenticates the compressed word, application receipt, signed caller and applicable verifier inputs by their explicit file names and hashes.

From this handoff directory, use a POSIX environment and CPython 3.12 with assertions enabled. Fetch the pinned source checkout if it is absent.

```sh
git init ../source-7605
git -C ../source-7605 sparse-checkout set research/p104-timed-helper757
git -C ../source-7605 fetch --depth=1 https://github.com/CrocSwap/integer-mult-bounds.git e1d2756eecf03e146338239fee81772a99ba8d4c
git -C ../source-7605 checkout --detach e1d2756eecf03e146338239fee81772a99ba8d4c
python3.12 -I -B replay.py --source-checkout ../source-7605
```

The replay stages authenticated inputs in its own temporary directory. It recomputes the census, sample matrices, structural exclusion, reverse row-span test, and independent forward probe, then compares their outputs to the receipts in [receipts](receipts/). The recorded clean-input run completed in 0.70 seconds with exit 0. The source checkout can also be supplied from another location through the same argument.

## Round 301 · Closed two-role blocks

Enumerate public non-main pairs with the same initial and final charts and a coframed ADD/SCALE block of at most 24 event clocks and 12 contacts. A priced orientation also requires an already-paid entrance and exit linked by proper chart inclusions, with the entrance and exit on distinct roles. The complete census covers 25,973 windows and 710 positively priced orientations. One additional rank-one native MOVE would cost 17 units in the full caller and exceed every directed gross upper bound.

The initial exact matrix loop was capped at eight cases and 30 seconds. It evaluated eight matrices and found zero antidiagonal exchanges. Its 702 uncomputed matrices remain individually unevaluated. The independent structural replay covered all 710 orientations. Every block has one or two mutual ADDs, with counts 403 and 307 respectively. Interleaved nonzero diagonal SCALEs can be moved to the ends by rescaling the shear coefficients. A product of two same-direction shears stays triangular, and a product of two opposed shears has one diagonal entry equal to one before the external scales. Thus the required invertible antidiagonal is impossible throughout the declared scope, including the 702 without explicit matrix multiplication. The finite family is exhausted. A block with at least three mutual ADDs, an earlier encoding or an extra legal operand would be a different test.

See [exact matrix sample](receipts/MATRIX.json), [structural coverage](receipts/SHEAR.json) and [enumerated cases](receipts/EXCHANGE.jsonl.gz).

## Round 302 · Fixed-prefix C1 return

Port only the C1 candidate involving helpers 396 and 564 from [#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636) at `7e68d8dd62d9a38c0f3c942262a7a85ca7125b75`. The trial preserves #7605's original 74 CLEAR contents. It replaces rank 3 plus rank 3 by rank 6, provisionally saving about 0.256732185 raw units across the signed caller, and retimes the earlier observer of 564 into chart 844. The first return must reproduce the old `504 += 564` at ADD42449 in chart 895. At that cut, the legal trial bank is exactly roles 396 and 504. Role 1396 arrives at the next event.

The trial bank has exact rank two. Adding old role 564 raises the rank to three. The separating probe has only input 230 set, to `−1/2`. Both trial bank rows are zero while the original role 564 is one. An independent forward replay verifies the entire trial bank on the probe and zero control. This excludes the proposed first return using these two rows. The later chart-844 return and other C1 prefixes, bank expansions and swap layouts remain untested. The original #7636 hub re-settlement under its own erasure premises falls outside this exclusion.

See the [reverse span result](receipts/RESULT.json) and the [independent forward probe](receipts/PROBE.json).

## Benchmark, provenance and next decision

A fresh local execution at the exact #7605 head passed all six registered stages in 411.39 seconds and reproduced signed conditional κ `0.003650444244716` under the five inherited assumptions. See the [local research package receipt](receipts/7605-local.log). The corresponding [hosted onboarding job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/43632689871/job/132562565239) stopped at the selected-record/CI-guide mismatch. The [hosted scientific replay job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/43632689871/job/132563641085) was skipped.

The #7605 construction and signed #7113 application supply the word, caller, cost boundary and erasure contract. [#7498](https://github.com/CrocSwap/integer-mult-bounds/pull/7498) at `f69879a7dc7e633151e582dae11f4480290405c9` supplies the earlier two-role window and fixed-paid endpoint exchange formulation. The Round 301 census applies it to paid-stop removal and adds the structural exclusion. #7636 supplies the C1 swap-then-delete mechanism and original source schedules. Round 302 tests its fixed-prefix transfer under the older erasure contract. OpenAI Codex and subagents materially assisted the search, proof and independent replays. The inherited premises are `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape` and `analytic_recovery`.

The next bounded check is a separate transplant of DreamingOfClouds's [#7610 terminal main-46 repair](https://github.com/CrocSwap/integer-mult-bounds/pull/7610) onto exact #7605. [#7611](https://github.com/CrocSwap/integer-mult-bounds/pull/7611) is the larger overlapping four-drop composition on #7608. Apply #7610's eleven premix ADDs at the start, use the existing role 818 arrival at MOVE45376 for the two chart-245 corrections, and replace role 46's rank-one hops through chart 245 by the direct rank-two MOVE at clock 47958. The first decision is exact equality of the original #7605 CLEAR44 row at clock 42713. A match earns all-row, phase and complete signed verification, including ordinary, precision and tape costs. This handoff makes no claim for that separate round.
