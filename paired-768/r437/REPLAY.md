# Installed ordinary quotient domain

**Round 437 · NO VERIFIED GAIN**

One exact price screen on [#8098 at c7d4441c5e4406bff4a79576cf6b2ce0a596390a](https://github.com/CrocSwap/integer-mult-bounds/commit/c7d4441c5e4406bff4a79576cf6b2ce0a596390a), κ 0.003900862339776. The complete local Round 436 replay is the baseline. The latest external headline remains #8097 at κ 0.003900862325217 in the latest verified publication refresh. [Baseline reply](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19845139) · [Baseline independent replay](../r436/REPLAY.md)

The eight priced ordinary heights have minimum H=3000. The installed guard H≥4 supports N≥16, so the existing decreasing mean `(21x+3)/(9x−1)`, x=`3^(N−2)`, has uniform upper bound `6277647/2690420`. Test only this bound. Keeping contraction `2390/2391` gives tariff `15009853977/6430103800`, and the whole ordinary factor falls by ratio `20592774709/20595165100`. Retain the original recursive budget of 2401, full `256/255` reserve, all other clock factors and the Gaussian price. No additional operations or routing were proposed.

The one-profile 112-bit and 192-bit directed screen passed with debit `1414441/2^20`, a 128-tick decrease. It gives provisional κ **0.003900862340231**. This clears the old guarded ordinary crossing, while Gaussian retains headroom. The projected increment is exactly `91/200000000000000`, or 0.000000000000455, with the same recurring `log₂ C=171810078109`. The independent control proves #8098’s existing tariff also funds this debit. Its ratio relative to #8097 times the convex upper bound `1+4224/2^20` is `12903689025/12907770512<1`. A tariff change adds no benefit at the tested debit. The full signed replay for a higher selector remains open, and the verified campaign Δκ for this round is zero. [Exact directed receipt](SCREEN.json) · [Independent readback](INDEPENDENT.md)

## Reproduce and continue

Use CPython 3.12 with assertions. Set `CHECKOUT` to a clean checkout of exact #8098 and `HANDOFF` to the checkout containing this document. The script validates the five distinct input paths and needs no prior temporary state.

```sh
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = c7d4441c5e4406bff4a79576cf6b2ce0a596390a
python3.12 -IB "$HANDOFF/paired-768/r437/check_domain_tariff.py" \
  --package "$CHECKOUT/research/p104-10shortcut-child-tariff" \
  --handoff-root "$HANDOFF/paired-768"
```

The 45-second cap is in the command. One case and its existing-tariff control ran under CPython 3.12.14 on macOS without exhausting the cap. No cases remain unvisited in this price scope. The lowest funded debit for each of the two tariffs remains open.

Start the next round by exposing the complete ordinary factor bounds in #8098’s `independent_price.py`. At both directed precisions, find the lowest funded debit for each tariff at the same fixed profile and reserve. Test the preceding debit as a price control. Use the tighter domain proof in a literal candidate only if it funds a stronger guard than the best existing-tariff price and clears the actual verified comparator. Run the complete signed registry before claiming a gain.

Credit Ali Romman for the #8042 canonical quotient bound and the #8057 signed receiver, SYLforge for the #8097 construction and full-reserve profile, and #8098 for the complete tariff comparison and exact replay. OpenAI Codex materially assisted.
