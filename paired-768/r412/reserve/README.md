# The ordinary reserve and the paid child contraction

One exact profile tested in Round 412. The local ordinary clock permits the #8082 reserve removal at the #8094 tariff, given the inherited paid-leaf inequality and physical child-volume bound. The five-stage #8094 invoice already pays the resulting larger child sum. This settles the reserve question in the Round 411 one-tick calculation. Full signed replay and the other changed interfaces remain required before claiming any exponent gain.

## Written argument

Write `c_B` for the binary trial, `N=2^H`, `F=P(N)/N^92` for paid singleton volume normalized by the exact productive width, and `U` for the complete finite bound on `F/N^(1−c_B)`. The common transfer inequality bounds `(256/255)F/N^(1−c_B)` by `(256/255)U`, giving the bare bound by cancellation. The positive numerical clock explicitly uses its geometric reserve. The ordinary clock has a different sum and starts from its nonchild tape bill and the native child-volume bound. The tighter K7 suffix replaces only the weighted interior term inside `U`. Padding, integer error, routing and the nonchild clock remain charged. [Transfer and numerical reserve](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/TRANSFER.md) · [Ordinary sweeps and contraction](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/ORDINARY-CLOCK.md)

At debit `d` and tariff `τ`, set `s₀=1−(c_B−d/H)`. If `τU<2^d`, then `τF<N^s₀`. For each of the two required moments `s∈{s₀,1}`, the normalized child mass is bounded by `(75/32)F N^(−s)`. The width floor on child sizes can only lower this bound. The exponent `s₀≤1` and the directed tariff inequality give the common bound `(75/32)/τ`. The factor `75/32` pays the entire actual low-chart average per charged owner and bounds direct frames, which use one child. The disjoint child volumes, basis routing and restoration belong to the inherited ordinary proof. This estimate does not depend on a Gaussian word or its control chronology. [Child-volume proof](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/RECEIVER.md)

At τ = 2401/1024 the two moment ratios are at most 2400/2401. Induction on remaining recursion depth bounds their total by 2401. The predecessor τ = 47/20 had ratio 375/376 and total 376. Replacing 376 by 2401 costs fewer than three extra bits per terminal stage because `2401 < 8·376`. The two-stage entry coefficient `(7·2401/10)^2` is below `2^22`, in place of `(7·376/10)^2 < 2^17`. The #8094 source charges the terminal `3·len(heights)` and raises the entry exponent by 5. The argument leaves the separate `249/250` stage funding constraint and the local nonchild tape envelope unchanged. A tariff equal to 75/32 has ratio one, so this finite geometric bound would fail. [#8082 reserve proposal](https://github.com/CrocSwap/integer-mult-bounds/pull/8082) · [Exact #8094 price wiring](https://github.com/CrocSwap/integer-mult-bounds/blob/c20a08dc0a79a989e3515068560d5da371c0a2a8/research/p104-shortcut-word-eta-27bit-5stage/prepare.py)

The published #8094 `PROOF.md` still shows old profile arithmetic with the reserve. This audit uses its exact `prepare.py` and the written predecessor clock. Applying the clock to all its new physical stages still requires the η, setup and signed source checks listed in Round 411. #8089 had a different conservative debit and its actual hosted replay does not establish #8094’s physical source.

## Replay

Use CPython 3.12 and clean checkouts of the exact commits. From this directory run the read-only check with the two explicit dependency roots. The first root is headed by `dfd25d553a843a946ca0b94130a5ff8943e98fdd`, the second by `c20a08dc0a79a989e3515068560d5da371c0a2a8`. SHA-256 authenticates each input before inspection.

```sh
python3.12 -IB check.py \
  --proof-root "$TRANSFER_CHECKOUT/research/retimed-native-multiplier" \
  --prepare "$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage/prepare.py"
```

The arithmetic and source-anchor replay exhausted the one profile in 0.03 seconds and exited 0 on the final script. It tests the two moment ratios, both charged clock terms and rejection of the unit-ratio control. The all-size inequality above is a written argument. No native job or hosted job was launched. The next price step can reuse the matched 24-cell receipt once the remaining exact comparator gaps are resolved.

Ali Romman supplied the transfer and two-moment clock with the physical receiver bound. Floration proposed the exact reserve removal and composed it into #8094. SYLforge supplied the native K7 graph. The campaign's #8076 tariff and the Round 411 matched phase calculation supplied the numeric inputs. OpenAI Codex materially assisted the independent source audit and replay.
