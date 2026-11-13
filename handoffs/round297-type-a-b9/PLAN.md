# Next incremental gate · one paid Type A B9 body transfer

Pin [#7546](https://github.com/CrocSwap/integer-mult-bounds/pull/7546) at `99438c43df7aac1e5dbcc43c1578fcd886c119ec`, κ `0.003648411294790`, canonical native `bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745` and complete application SHA256 `a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f`. The exact unchanged signed caller is [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d` and SHA256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`. Pin `pricing.py` SHA256 `f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182`. Refresh exact live peer claims before launch.

## One edit, named paid path, and price

Move B9 (eight axes) from IDLE_ONE1745 on Type A role11, old mask {9,10}, to IDLE_ONE1448 on role1, old mask {2,3,4,5,6,7,8}. New masks are {10} and {2,3,4,5,6,7,8,9}, respectively. Both jobs already have their original owners and physical routes. Their ranks change 16,56→8,64. All scalar wrappers, other idles, QUERYs, output owners, J hosts and clocks stay fixed. There is no added call or free rescue assumption.

Compare all 36 roles at the exact left and right boundaries of [1448,1746). The role1 earliest subsequent ADD1449 uses its new normalized value on the original receiver. The role11 prior ADD1744 feeds the late paid slot and ADD1746 begins its unchanged following path. These existing paths carry the same scalar chronological data only if the interval maps agree. Retain the independent original role10 B9 at IDLE1742. The intervening block has 262 Type A ADDs, 16 IDLE_ONEs, eight SWAPs, eight LAMBDAs and four QUERYs. No J or Type B events are in the interval. The fixed ordinary prefix and suffix are cancellable when testing exact interface equality. A proposed changed wrapper or extra phase-dependent routing is outside the test.

The whole signed invoice has ΔP=`{8:+96,16:-96,56:-96,64:+96}`, ΔT empty, across 96 Type A ports. Strict concavity gives positive pre-repair gross `96(H16+H56−H8−H64)`, with equal paid rank mass. Emit an exact directed enclosure at the comparator crossing before looking at columns. Its whole upper is below 96 raw, so one rank-one paid repair per affected port eliminates the gain. Count every physical basis, typed whole-field remap, routing, restoration, precision and tape delta before construction.

## One case, 30 seconds, and restart

Take width one with q=+1, B9=−1 and all other bodies +1. The two zero-based B9 Walsh axes 73 and 74 carry minus labels, so their two C eigenvalues multiply to −1. Each fixed QUERY contributes the usual off-diagonal ADD and each LAMBDA is identity in this specialization. Compare old and modified exactly on all 36 independent boundary inputs, with the unit-body equality as a control. A single mismatch excludes this fixed-mask edit on the signed word. A pass merely calls for arbitrary-body signed forward and adjoint, including physical geometry of the new rank64 job and original old returns. Formally signed action, stock, precision, ordinary bill and complete independent application need to pass before a claim. A cap records all completed columns and remaining scope. Changed wrappers, other clocks and other body masks remain open.

Stage this directory as `next-type-a-b9/` in a clean replay root containing the three pinned files `inputs/ROLE902-APPLICATION.json`, `inputs/7113-CALLER.json` and `inputs/pricing.py`. Use CPython 3.12 with assertions enabled.

```sh
python3.12 -I -B next-type-a-b9/check_type_a_b9_transfer.py inputs
```

Exact clocks, masks and syntax checked. The experiment is unrun. [#7541](https://github.com/CrocSwap/integer-mult-bounds/pull/7541) supplies a distinct Type B B2 transfer and directed scope precedent. [#7402](https://github.com/CrocSwap/integer-mult-bounds/pull/7402) supplies the body-transfer method. [#7309](https://github.com/CrocSwap/integer-mult-bounds/pull/7309) fixes all bodies at +1 and targets the central-phase rank budget; this screen instead changes one real body incidence. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed price. No exact matching peer evidence surfaced in the bounded search. OpenAI Codex materially assisted.
