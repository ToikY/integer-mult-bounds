# Limiting quotient-domain exclusion

**Round 440 · NO VERIFIED GAIN**

[Updated #8098](https://github.com/CrocSwap/integer-mult-bounds/pull/8098) exact release `517eac577bc12a1519eaf346a6816ad91bc9df90` independently certifies κ **0.003900862349161** at its complete signed 28-bit profile. The binding ordinary debit is `1411929/2^20`. This round holds the contraction `2390/2391`, full `256/255` reserve, same clock budget, both suppliers and geometry. It checks one domain-only change to the quotient mean. Latest external #8097 was unchanged at κ 0.003900862325217. [Comparator replay](../r439/REPLAY.md)

For `x=3^(N−2)`, the charged mean `(21x+3)/(9x−1)` exceeds its limit `7/3` by `16/[3(9x−1)]`. The best limiting tariff is therefore `5579/2390` at the same contraction. Its ratio to the current tariff is `18832940/18832941`. The test reconstructs the full literal ordinary periodic factor from 18,906 productive entries, 104,652 paid entries and 24 cells, including all costs and reserves. Even the directed lower charge at the limiting tariff exceeds the directed upper allowance for `1411928/2^20`. The certified difference is at least `7156630525441444964131727669/2^112` and `8651835423648373103335476825563190486418502685541839/2^192` at the two precisions. This excludes every larger finite domain cutoff in this price formula. Other changes to the tariff, contraction or periodic invoice remain open. [Exact signed interval endpoints](SCREEN.json) · [Independent proof](INDEPENDENT.md)

## Clean replay

Use Git, CPython 3.12 with assertions and fresh scratch outside the checkout. Keep 8 GiB free on both volumes. Set `CHECKOUT` to the exact comparator checkout and `HANDOFF` to the checkout containing this receipt. The program authenticates all distinct input paths, both materialized price sources and the installed selector.

```sh
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = 517eac577bc12a1519eaf346a6816ad91bc9df90
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB "$HANDOFF/paired-768/r440/check_floor.py" \
  --package "$CHECKOUT/research/p104-10shortcut-child-tariff" \
  --helper "$HANDOFF/paired-768/r438/check_minimal_debit.py"
```

One fixed profile and one threshold exhausted the declared scope, with both directed reconstructions settling it. The group ran in 0.62 s under a 60-second cap with exit 0. No cases in the declared scope remain open. There was no altered selector, full new scientific replay or gain in this round. [Execution receipt](EXECUTION.log)

The next mechanism uses the separately charged recursion budget of 2401. Keep the finite `N≥16` mean and test the original #8097 contraction `2400/2401` at that budget. Price the whole fixed envelope and adjacent debit before any build.

Credit Ali Romman for #8042’s quotient law and #8057’s signed receiver, SYLforge for the #8097 construction and clock profile, and #8098 and Round 438 for the exact full-reserve envelope and directed reconstruction. OpenAI Codex materially assisted.
