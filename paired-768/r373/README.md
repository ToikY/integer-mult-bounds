# Exact price for one compact two-tier retune

The changed physical Gaussian price is `2143195807/2^39`. Pair it with fixed heights (35,327, 559,462) and Gaussian height 680,000. The candidate keeps the #8055 entry tier and both literal column scales. The terminal target κ = 0.003898202 clears the independently reproduced #8056 value by 0.0000000003863. The ordinary funding margin is greater than 1.2068e−12 and Gaussian funding margin greater than 1.4497e−9. Both tiers pass all 54 strict and four functional inequalities. Actual retimed admission starts at exponent 1,275,308, 457 above the old compact profile, with the conversion premium still 572 bits. The complete recurring coefficient has log₂ upper bound 339,934,211. The largest carrier exponent stays 680,000. The setup accounting retains its 228-bit ceiling.

A literal construction and full replay remain the gate. The measured price identifies one compatible role and paid profile only. No new κ is certified by this pricing.

Use CPython 3.12. From this directory, set `PEER` to the `research/tiered-native-multiplier` directory of exact #8055.

```sh
python3.12 -IB primary/price.py --peer "$PEER" --round372-price ../r372/primary/price.py --round372-receipt ../r372/primary/receipt.json --out fresh-price.json
python3.12 -IB independent/check.py --package "$PEER" --raw-trial 2143195807/549755813888 --out fresh-independent.json
```

[Independent restatement and exact source dependencies](independent/PROOF.md). Credits go to Ali Romman for the 1-to-79 #8055 signed tiers, SYLforge for K7, and the #8056 contributors for the exact rounded transport and comparison. OpenAI Codex assisted the price and cross-check.
