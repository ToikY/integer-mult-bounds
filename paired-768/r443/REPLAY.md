# Joint limit of the charged child tariff

**Round 443 · NO VERIFIED GAIN**

The exact [#8098 release fae237c8](https://github.com/CrocSwap/integer-mult-bounds/commit/fae237c8aee774bb2256d4e394fed9f3934147c2) uses debit `1411927/2^20` at verified κ **0.003900862349168**. Keep the same complete signed profile, periodic factor with full `256/255` reserve, and paid geometric budget 2401. Round 440 closed improving only the quotient domain at the older contraction. This test closes the combined choice of quotient domain and contraction inside the same clock budget and debit grid. [Exact comparator replay](../r442/REPLAY.md) · [Prior fixed-contraction exclusion](../r440/REPLAY.md)

The quotient mean exceeds `7/3` for every finite (N) by `16/[3(9x−1)]`, where `x=3^(N−2)`. The paid budget implies `1/(1−ρ)≤2401` and so `ρ≤2400/2401`. Combining both optimistic endpoints gives the limiting tariff `16807/7200`, with ratio `18832940/18832941` to the verified tariff. The whole periodic factor is positive. Scaling the authenticated bounds at that tariff preserves their direction and retains every other charged factor. [Source intervals](../r441/SCREEN.json)

The optimistic lower charge still exceeds the upper allowance for `1411926/2^20`. The certified gaps are `1603406067093625745325706603/2^112` and `1938398993836230601583996245824334124942068204949971/2^192`. Any larger tariff in this family costs more, and smaller debits allow less. The combined family therefore cannot gain another tick at the fixed invoice. The exclusion concerns this price formula, paid clock and `2^−20` debit grid. [Exact directed result](SCREEN.json) · [Independent proof and replay](INDEPENDENT.md)

## Clean replay

Use Git and CPython 3.12 with assertions. Set `CHECKOUT` to an exact #8098 checkout and `HANDOFF` to the checkout containing this document. The program authenticates both input paths. It needs no previous scratch or installed calendar.

```sh
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = fae237c8aee774bb2256d4e394fed9f3934147c2
python3.12 -IB "$HANDOFF/paired-768/r443/check_joint_limit.py" \
  --package "$CHECKOUT/research/p104-10shortcut-child-tariff" \
  --screen "$HANDOFF/paired-768/r441/SCREEN.json"
```

One fixed profile and one threshold exhausted the declared scope at both precisions, with exit 0 and 0.08 seconds wall in the 45-second cap. Other ordinary cost mechanisms remain open. There is no new verified campaign Δκ. [Execution receipt](EXECUTION.log)

The next decision targets a distinct priced term in the periodic ordinary suffix formula. Compute a total optimistic bound on the literal transport cells before considering any new physical construction. [Next source test](NEXT.md)

Credit Ali Romman for the #8042 quotient law and #8057 signed receiver, #8076 and SYLforge’s #8097 for the paid clock, and #8098 and Round 441 for the exact full-reserve price and directed bounds. OpenAI Codex materially assisted.
