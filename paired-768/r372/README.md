# Fixed compact height excludes a Gaussian-only gain

The exact #8055 compact profile at 7b48187d99525ad59f560de3921ec7e48382484c uses binary heights 35,327 and 559,005. Even with all Gaussian cost forgiven, its signed binary stage ceiling lies below the independently reproduced #8056 κ = 0.0038982016137. The quarter/complement inventory itself passes the whole Gaussian transport at these heights, with 63 cells and the inherited 43/256 Gaussian tariff. It retains the 189,072 extra conditional phase passes of the high copy. There is no gain from this one edit while the binary heights stay fixed.

Use CPython 3.12 and Git. Set `PEER` to the exact #8055 checkout's `research/tiered-native-multiplier` directory. Run from this directory with new outputs.

```sh
python3.12 -IB primary/price.py --peer "$PEER" --out fresh-price.json
python3.12 -IB independent/check.py --package "$PEER" --out fresh-negative.json
```

The independently checked first reopening at the current rate and first binary height needs terminal binary height at least 559,374. At the separately proposed target κ = 0.003898202, the first eligible height is 559,462. A changed profile has to price both tiers, including activation, terminal binary returns, Gaussian phase variations, and the all-input clock. [Independent proof](independent/PROOF.md)

Ali Romman supplied the exact #8055 compact source and phase/clock proof. SYLforge supplied K7. #8056 supplied the exact 1-to-8 rounded packet comparator. OpenAI Codex assisted the pricing and independent exclusion.
