# First funded debit under two ordinary tariffs

**Round 438 · NO VERIFIED GAIN**

[Round 437](../r437/REPLAY.md) proved that both tariffs fund its one 128-tick test. Here the exact [#8098](https://github.com/CrocSwap/integer-mult-bounds/pull/8098) runtime at `c7d4441c5e4406bff4a79576cf6b2ce0a596390a` reconstructs the complete ordinary envelope from 18,906 productive entries, 104,652 paid entries and 24 certificate cells. Its two precisions independently enclose the same price. The full `256/255` reserve, conservative recursion budget 2401 and all other factors remain charged. [Exact #8098 local replay](../r436/REPLAY.md) · [Hosted replay](../r436-hosted/REPLAY.md)

| Tariff | First funded tick of 2^-20 | Preceding tick rejected | Projected guarded rate |
| --- | ---: | ---: | ---: |
| #8098 `10981863/4703998` | 1412105 | 1412104 | 0.003900862348535 |
| Installed domain `15009853977/6430103800` | 1411929 | 1411928 | 0.003900862349161 |

Both precisions agree. The new domain gives 176 additional debit ticks over the exact fully repriced original tariff. The projected gain is **0.000000000009385** over verified #8098, of which **0.000000000000626** separates it from the strongest rate projected for #8098's older tariff. It strictly clears that stronger exact ordinary crossing. Gaussian is slack and `log₂ C=171810078109`. This establishes a distinct price improvement. The literal selector and complete signed replay remain unrun. Verified campaign Δκ for this round is zero. [Exact screen](SCREEN.json) · [Guarded crossing projection](PROJECTION.json) · [Independent check](INDEPENDENT.md)

## Clean replay and scope

Set `CHECKOUT` to a clean checkout of exact #8098 and `HANDOFF` to the checkout containing this document. Use CPython 3.12 with assertions, Git and 8 GiB of free space on the checkout and scratch volumes. The scripts authenticate the package and their explicit relative input paths. Use fresh scratch outside the checkout.

```sh
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = c7d4441c5e4406bff4a79576cf6b2ce0a596390a
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB "$HANDOFF/paired-768/r438/check_minimal_debit.py" \
  --package "$CHECKOUT/research/p104-10shortcut-child-tariff" \
  --screen "$HANDOFF/paired-768/r437/SCREEN.json"
python3.12 -IB "$HANDOFF/paired-768/r438/check_recurrence.py" \
  --package "$CHECKOUT/research/p104-10shortcut-child-tariff" \
  --handoff-root "$HANDOFF/paired-768"
```

The two tariffs took 28 directed endpoint or bisection probes per precision under the declared 32-probe cap. The group replay exited 0 in 0.48 seconds under the remaining 59-second budget. An earlier 0.51-second run stopped before any search probes when its 112-bit reconstruction reduced rational bases before rounding. The corrected reconstruction rounds the original numerator and denominator powers first and matches the literal source upper bound exactly. Independent cold replay reproduced the corrected screen byte for byte. The tested tariff scope exhausted. [Execution receipts](EXECUTION.log)

## First build step

Update the funded ordinary debit to `1411929/2^20` and install the `N≥16` child bound and provisional selector in a single overlay of exact #8098. Authenticate the new installation image. Test the unchanged #8098 price and the strongest existing-tariff guard at the proposed rate. Require the `1411928` debit and adjacent rate controls to fail. Replay the exact signed package and full costs before any κ claim. Refresh the comparator and check overlap before opening or updating a PR.

Credit Ali Romman for the #8042 quotient law and #8057 signed receiver, SYLforge for the #8097 full-reserve profile, and #8098 for the installed factor and separate directed implementation. OpenAI Codex materially assisted.
