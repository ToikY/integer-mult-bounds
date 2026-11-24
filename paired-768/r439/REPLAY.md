# Exact tighter-domain tariff replay

**Round 439 · VERIFIED IMPROVEMENT**

The preceding [#8098 head c7d4441c5e4406bff4a79576cf6b2ce0a596390a](https://github.com/CrocSwap/integer-mult-bounds/commit/c7d4441c5e4406bff4a79576cf6b2ce0a596390a) remains the exact prior reproduced witness at κ **0.003900862339776**. Its seven registered modes passed locally and hosted. The new signed selector certifies **0.003900862349161**, with exact gain **0.000000000009385** (`9385/10^15`) and relative gain **+0.0000002405878286%**. Compared with latest external [#8097 at e1c25140](https://github.com/CrocSwap/integer-mult-bounds/commit/e1c251401fe254909ac7e7bf2c773b921a1b6b57), κ **0.003900862325217**, the gain is **0.000000000023944**, or **+0.0000006138129984%**. The exact percentages are `234625/975215584944` and `2394400/3900862325217` percent. Peer benchmark movement during the round was zero. [Predecessor hosted evidence](../r436-hosted/REPLAY.md)

Ordinary price binds. The installed domain gives the child mean bound `6277647/2690420` at `N≥16` and tariff `15009853977/6430103800` at contraction `2390/2391`. The priced stage minimum is `H=3000`. The full `256/255` reserve, geometric budget 2401 and fixed signed caller are retained. Both 112-bit and 192-bit checks find first funded debit ticks `1412105` under the prior tariff and `1411929` with the tighter domain, each divided by `2^20`. The preceding ticks fail the exact fixed-profile price formula. The additional 176 ticks give a gain of `0.000000000000626` beyond the price-only repriced previous tariff. The signed rate strictly clears its complete guarded crossing and the next rate tick fails. Maximum native height 268435455, activation 536923552, recurring `log₂ C=171810078109` and fixed setup below `2^228` all retain their original charged proofs. [Price comparison inherited from Round 438](../r438/REPLAY.md) · [New literal invoice](RESULT.json)

## Clean checkout

Use Git and CPython 3.12 with assertions. Keep at least 8 GiB free on the source and scratch volumes and at least 8 GiB RAM. Check out release commit `517eac577bc12a1519eaf346a6816ad91bc9df90`.

```sh
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB scripts/research_package.py --package research/p104-10shortcut-child-tariff
TMPDIR="$scratch" python3.12 -IB research/p104-10shortcut-child-tariff/verify.py census
```

The full independent local registered run on scientific commit `e5ab435e62b6072d936ef336c743a33c1948f5f6` passed seven modes in 337.33 seconds. It authenticated the 25 packaged inputs, reconstructed both source overlays, replayed signed product and both tape widths, and exercised the three types plus exterior and nested owner returns. The signed calendar rejects the prior booked and first-funded earlier-tariff debits at the candidate rate. The exact serial setup and w5664 word catalogue complete the registered suite. The final log shows the original task-card status `outcome=partial`. The release commit updates the proof documents and task outcome and has identical scientific bytes, command vectors and caps. The exact release head passed the installed ten-recipe census with 2,492,209 records, 760 onboarding tests with 31 skips, committed source checks, the unchanged two-package plan and the historical prerequisite. Hosted status is tracked separately.

[All modes and exact outputs](LOCAL-REGISTERED.log) · [Path-hash inputs](INPUTS.log) · [Source and installation changes](SOURCE-INTEGRITY.json) · [Release heads and trees](HEAD-TREE.log) · [Timings and exits](LOCAL-EXITS.log)

The theorem retains the five signed premises for native action, ownership and erasure, chronological compilation, precision and tape movement, and analytic recovery. SYLforge supplied the #8097 word, producer and resource profile. floration supplied the antecedent #8088/#8090/#8094 construction work. Ali Romman supplied the #8042 quotient law and #8057 signed receiver. #8076 supplied the conservative clock proof. The prior #8098 and Round 438 work supply the exact rate and repriced tariff comparisons. OpenAI Codex materially assisted.

The next bounded test uses the limiting child mean `7/3` in the fixed profile and same contraction to decide whether the immediately preceding debit tick is reachable by any further domain-only tightening.
