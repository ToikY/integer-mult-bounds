# Exact charged-clock signed replay

**Round 442 · VERIFIED IMPROVEMENT**

The exact [preceding #8098 head](https://github.com/CrocSwap/integer-mult-bounds/commit/517eac577bc12a1519eaf346a6816ad91bc9df90) has independently reproduced κ **0.003900862349161**. Both its local and hosted complete registered checks passed. The new exact conditional rate is **0.003900862349168**, with campaign Δκ **0.000000000000007** or **+0.0000000001794475%**. Latest external [#8097](https://github.com/CrocSwap/integer-mult-bounds/commit/e1c251401fe254909ac7e7bf2c773b921a1b6b57) remains κ **0.003900862325217**, with gain **0.000000000023951** or **+0.0000006139924459%** over that exact head. The exact percentages are `700/3900862349161` and `2395100/3900862325217` percent. [Prior #8098 hosted replay](../r439-hosted/REPLAY.md)

The same `N≥16` mean uses contraction `2400/2401`, giving a geometric sum equal to the already charged 2401. The tariff `5024210149/2152336000` funds debit `1411927/2^20`. The preceding tick and the next rate fail their directed controls. The earlier funded and rejected debit pairs `1412105/1412104` and `1411929/1411928` remain predecessor controls. The new rate clears the entire preceding guarded crossing. The word, signed caller, owner returns, routing, precision, tape, full reserve and fixed setup retain their complete charges. Ordinary remains binding at `log₂ C=171810078109`. [Independent price-only comparison](../r441/REPLAY.md) · [Literal invoice](RESULT.json)

## Clean checkout

Check out `fae237c8aee774bb2256d4e394fed9f3934147c2`. Use Git and CPython 3.12 with assertions. Keep at least 8 GiB free on the source and scratch volumes and at least 8 GiB RAM for the registered mode.

```sh
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB scripts/research_package.py --package research/p104-10shortcut-child-tariff
TMPDIR="$scratch" python3.12 -IB research/p104-10shortcut-child-tariff/verify.py census
```

The exact scientific commit `649f8a81b822b743c447416949203e410d8b4a23` authenticated all 26 inputs and executed all seven native and price scopes in 345.78 seconds with exit 0. It signed both tape widths, verified all three native types and exterior and nested owner returns, replayed multiplication and checked the full exact grid and setup. The matched prior-word and signed-output controls retain the inherited physical verifiers. The release commit adds the completed proof and task metadata and keeps all scientific inputs, commands and caps identical. The log's `outcome=partial` suffix reads the earlier frozen task card. The local release passed the separate 2,492,209-record census, all 760 onboarding tests with 31 skips, exact committed source checks, the two-package plan and historical prerequisite. Hosted status is recorded separately.

[Local registered output](LOCAL-REGISTERED.log) · [Installed ten-recipe census](INSTALLED-CENSUS.log) · [Input hashes](INPUTS.log) · [Head and tree receipt](HEAD-TREE.log) · [Timings and exits](LOCAL-EXITS.log)

The conditional result inherits exact native all-column action, ownership and erasure, uniform chronological compilation, fixed-tape movement and precision, and analytic recovery. SYLforge supplied #8097’s word and full-reserve signed resource point. floration supplied the earlier word and profile work. Ali Romman supplied #8042’s quotient rule and #8057’s signed receiver. #8076 and exact #8097 supply the charged contraction and clock. Earlier #8098 heads supplied the booked domain and signed tests. OpenAI Codex materially assisted.

The next source test prices the joint limiting quotient mean and maximum contraction on the fully charged debit grid before changing an ordinary periodic suffix term.
