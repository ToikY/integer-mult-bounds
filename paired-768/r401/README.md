# Round 401 Gaussian screens

The baseline is [#8069](https://github.com/CrocSwap/integer-mult-bounds/pull/8069) at `2d0d7d378929269b00dcabfac1099b2bb23b3b3b`, conditional κ 0.0038982141167032. A fresh exact-checkout [registered replay](baseline.log) passed all seven modes in 244.35 seconds. The maintainer-selected record is #7000 at 0.00363005817. The latest comparable external proposal remains [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) at 0.00389821. The [Round 399 proof](../r399/README.md) closes the old heights-only family for the fixed paid invoice and declared resource caps.

| Lead | Before screen, by potential upside | After screen, by signed feasibility |
|---|---|---|
| Direct-sum fusion of type-one paid calls at 684 and 707 | 1 | Excluded in the unchanged recipient and restoration interface |
| Book Gaussian debit 64939/524288 | 2 | 1, one funded literal construction to verify |

## Paid schedule

The source installs the owner at root 4080 for paid call 684 before the exact ADD at 691 reads it as its destination. The separate root 4095 issues at 707. Delaying the first owner return fails the native caller at 684. The fused grade 224 needs a recipient of grade at least 280 under the exact admission rule, while the installed maximum is 258. Splitting back into the two grade-112 actions restores the original invoice and its existing installed ceiling. This one case leaves alternative return and recipient interfaces outside scope. The screen was separate from the two type-zero unsplits, rank-two splits, and weight changes in [Round 377](../r377/README.md), [Round 379](../r379/README.md), and [Round 386](../r386/README.md). [Scope and cap](schedule/PLAN.md) · [Exact receipt](schedule/receipt.json)

## Gaussian debit

The unchanged full outward factor is below 1.089646674305021264. Directed arithmetic gives the tighter debit a positive reserve above 0.000000684423610889. The strict minimum required reduction from the old debit is about 4.7706898495e−7 at the actual #8069 clock cap, one tick on this debit grid. The single case tested changes the debit numerator from 64944 to 64939. It funds prospective κ 0.0038982141226643 with ordinary heights (8192,124864,524288), Gaussian height 490638, and recurring log₂ C 318292171. This is 280 units below #8069's actual bound. The ordinary inequality binds at the new crossing. Actual placement retains share 1/624, period 1364, and the first signed slot exchange 1→272. This books a tighter proved debit while charging the same native work and restoration. Full signed replay is the next gate. The screen does not certify a gain. [Scope and cap](debit/PLAN.md) · [Exact receipt](debit/receipt.json)

## Clean checkout replay

Use Git and CPython 3.12. Set `BASELINE` to the exact #8069 checkout above and run from this directory. The scripts authenticate committed files and reject duplicate source keys before replaying the isolated witnesses.

```sh
out=$(mktemp -d)
python3.12 -IB debit/screen.py --baseline "$BASELINE" --out "$out/debit.json"
python3.12 -IB schedule/screen.py --baseline "$BASELINE" --out "$out/schedule.json"
cmp "$out/debit.json" debit/receipt.json
cmp "$out/schedule.json" schedule/receipt.json
```

The successful debit run took 6.95 seconds. The two earlier runner-path corrections brought its total to 14.73 seconds. The schedule run took 6.27 seconds. The candidate build is restricted to the one new debit and allocation, with an independent verifier and all seven modes required before publication of a gain. #8058 remains a separate hosted runner issue. [Maintainer handoff on #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19821920)

## Predecessor credit

Ali Romman's [#8057 signed supplier](https://github.com/CrocSwap/integer-mult-bounds/tree/cbe847a953b971f9c6c5a0a6661e2008acd29086/research/frequency-weighted-native-multiplier) supplies the native compiler and ownership interface. SYLforge's [K7 construction](https://github.com/CrocSwap/integer-mult-bounds/pull/8052) supplies the ordinary word. [#8059](https://github.com/CrocSwap/integer-mult-bounds/pull/8059), [#8063](https://github.com/CrocSwap/integer-mult-bounds/pull/8063), and [#8064](https://github.com/CrocSwap/integer-mult-bounds/pull/8064) supply the charged factor and literal Gaussian bands. [#8066](https://github.com/CrocSwap/integer-mult-bounds/pull/8066), [#8067](https://github.com/CrocSwap/integer-mult-bounds/pull/8067), [#8068](https://github.com/CrocSwap/integer-mult-bounds/pull/8068), and [#8069](https://github.com/CrocSwap/integer-mult-bounds/pull/8069) supply the ordinary invoice, literal floor, capped allocation, and exact baseline. Round 401 adds a new debit screen and a distinct paid-fusion exclusion. OpenAI Codex materially assisted both checks.
