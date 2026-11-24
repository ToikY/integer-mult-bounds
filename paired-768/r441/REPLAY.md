# Ordinary pricing at the charged recursion budget

**Round 441 · NO VERIFIED GAIN**

The exact [current #8098](https://github.com/CrocSwap/integer-mult-bounds/commit/517eac577bc12a1519eaf346a6816ad91bc9df90) independently certifies κ **0.003900862349161** with ordinary debit `1411929/2^20`. The [Round 440 exclusion](../r440/REPLAY.md) closes domain-only tightening with fixed contraction. This round holds the same installed `N≥16` mean `6277647/2690420` and uses more of the recursion budget already included in the full invoice.

Changing contraction from `2390/2391` to `2400/2401` gives geometric sum 2401, the existing charged budget at both moments. The latter contraction and its entry and terminal clocks were already used on the exact #8097 profile, including both signed suppliers, physical restoration and full reserve. At the same mean the tariff becomes `5024210149/2152336000`. The whole-factor ratio to #8098 is `573839/573840`. Price directly by rescaling the authenticated Round 440 intervals, with exact ratio `171540889373/171541179200` from its limiting tariff to the new one. All remaining clock, precision, tape and setup factors retain their full charges. [Exact source and #8097 precedent](INDEPENDENT.md)

Both precisions fund `1411927/2^20` and reject `1411926/2^20`. Five of seven permitted threshold probes per precision resolve the first admissible tick. The other two are above that tick and the allowance is increasing. The guarded rate projects **0.003900862349168**, exactly `7/10^15` above the verified #8098 rate and above its full ordinary crossing. At fixed geometry Gaussian is slack. The activation exponent, entry premium and `log₂ C=171810078109` retain their original values. This is a verified scoped price calculation. The literal selector and the complete independent signed suite are open, so the verified campaign Δκ this round is zero. [Directed thresholds and crossings](SCREEN.json)

## Clean replay

Use CPython 3.12 with assertions. Set `CHECKOUT` to a clean exact #8098 checkout, `PEER` to a clean exact #8097 checkout, and `HANDOFF` to the checkout containing this document. The screen authenticates the distinct source paths and reconstructs the arithmetic from scoped inputs without prior temporary state.

```sh
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = 517eac577bc12a1519eaf346a6816ad91bc9df90
test "$(git -C "$PEER" rev-parse HEAD)" = e1c251401fe254909ac7e7bf2c773b921a1b6b57
python3.12 -IB "$HANDOFF/paired-768/r441/check_paid_contraction.py" \
  --package "$CHECKOUT/research/p104-10shortcut-child-tariff" \
  --peer-package "$PEER/research/p104-10shortcut-3type-28bit-6stage" \
  --screen "$HANDOFF/paired-768/r440/SCREEN.json" \
  --handoff-root "$HANDOFF/paired-768"
```

The scope exhausted with exit 0 in 0.10 seconds under the 45-second process cap. No mathematical comparison remains unresolved for its declared tariff and thresholds. [Measured execution](EXECUTION.log)

Start the next build by substituting the new tariff, contraction and debit in the source proof and changing only the installed rate selector. Keep the exact #8098 debit and guarded crossing as controls. The preceding debit and immediately higher rate must fail. Require complete clean signed replay before reporting any gain.

Credit Ali Romman for the #8042 quotient law and #8057 receiver, #8076 and SYLforge’s #8097 for the exact contraction and charged recursion clock, and the earlier #8098 heads for the signed caller and fixed price profile. OpenAI Codex materially assisted.
