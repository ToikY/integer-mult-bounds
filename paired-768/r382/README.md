# Exact 6-to-541 price and physical scope

Round 382 adds no verified κ gain. The independently reproduced #8060 comparator has κ = 0.00389821033 on exact `efde300bd2902be5bf967533871487b2624240c3`. We priced and independently constructed one actual `(6,541)` calendar at widths `(1,2)` and tariff `17145637263/2^42`, with Gaussian H=483,871 and debit 65000/524288. The old `(8,721)` raw moment is negative at the new point. The new true integer planner funds all 51 grade and 88 typed cells, retains both real first exterior placements, exercises all four type directions, and fits the full 547-birth upper charge. Only terminal ordinary height 524,357 was screened. Both signed supplier prices and all activation, conversion and setup costs pass for provisional κ = 0.00389821034. This gate covers one ratio and one exact price and earns a literal build. [Directed arithmetic](price/PROOF.md) · [Actual calendar and tape audit](audit/PROOF.md)

Use Git and CPython 3.12. Set `PEER` to the clean exact #8057 scientific checkout `cbe847a953b971f9c6c5a0a6661e2008acd29086`. Set `COMPARATOR` to exact #8060 checkout `efde300bd2902be5bf967533871487b2624240c3`. Use the supplied evidence root. Primary ran in 0.12 s within 60 s. Independent calendar and price ran in 5.054 s within 90 s.

```sh
out=$(mktemp -d)
python3.12 -IB price/price.py --root evidence --peer "$PEER" --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check.py --research "$PEER/research" --previous evidence/round381/independent/verified.json --previous-price evidence/round381/publish/research/p104-weighted-integer-frequencies/RESULT.json --out "$out/audit.json"
cmp "$out/price.json" price/receipt.json
cmp "$out/audit.json" audit/receipt.json
```

This changes the next round by building the one exact frequency profile because the whole signed price, actual integer counts and stable forced placement check out. The next registered replay must exercise all changed owner counts and exact nonzero restoration on the literal installation. Other ratios and all portable setup variants remain open.

Ali Romman supplied the weighted #8057 physical source and #8055 native setup. SYLforge supplied K7. #8059 supplies the exact directed finite-debit proof, and #8060 serves as the signed baseline. OpenAI Codex assisted these independent proofs. [Weighted predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Verified comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/8060)
