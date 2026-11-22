# Exact weighted fringe and complete signed replay

The weighted finite-debit retune at `c34c958114297cdbd1f493666342b8859531d40d` passes all seven local scientific modes at conditional **κ = 0.00389821030**. Relative to independently reproduced #8058 at 0.00389821005 the exact gain is **0.00000000025**, or **(500/77964201)%**. Relative to the external #8057 claim and reproduced 0.00389821, it is **0.00000000030**, or **(3/389821)%**. The weighted 51-cell/88-share calendar retains physical widths 1 and 2, birth counts 1 and 90, all signed paid calls, and all owners. The tighter finite debit 65000/524288 uses an outward directed integral at each edge. The third binary height is 524,349. The 514-bit entry conversion, actual first terminal header, cofinal and setup costs are fully charged. [Exact proof and price](price/PROOF.md) · [Native setup, stock and activation audit](audit/PROOF.md) · [Independent proof and negative controls](PROOF.md)

## Clean replay

Run CPython 3.12 with Git. From the exact candidate repository root:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-finite-edge
```

The science runner finished in 176.64 seconds. It checked both real job types, actual exterior births, the nonzero cross-type loan at paid ordinal 3418, both owner returns through complete signed words, the independent product −345550037539, and 4,071 integer plus 7,396 rational serial controls. The exactly matching K7 source, ledger and verifier pins reuse the earlier 630-role independent binary evidence. All actual work and repayment counts remain in the registered receipt. [Seven-mode replay](scientific.log) · [Earlier K7 receipt](../r376/main-replay.log)

From this handoff directory set `PEER` to exact #8057 scientific checkout `cbe847a953b971f9c6c5a0a6661e2008acd29086`. Set `CAPSULE` to `research/p104-weighted-finite-edge` in the candidate checkout. Use the supplied relative evidence root. This reproduces the receipts without prior temporary state.

```sh
out=$(mktemp -d)
python3.12 -IB price/price.py --root evidence --peer "$PEER" --out "$out/price.json"
python3.12 -IB audit/check.py --research "$PEER/research" --out "$out/audit.json"
python3.12 -IB accept.py --evidence . --capsule "$CAPSULE" --out "$out/verified.json"
cmp "$out/price.json" price/receipt.json
cmp "$out/audit.json" audit/receipt.json
cmp "$out/verified.json" verified.json
```

The exact active-edge negative control rejects pricing the new debit with the earlier three-term sum. A second rejects the older debit at the proposed booked rate. The five inherited research premises remain necessary for the all-size statement. The fixed native setup uses 2^228 and the recurring coefficient has log₂ bound 318,278,951. Regenerating a sharper fixed bound for the changed portable image remains open. [Scientific comparison #8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Independent prior frontier #8058](https://github.com/CrocSwap/integer-mult-bounds/pull/8058)

Ali Romman supplied the weighted signed source, exact-edge proof and native setup route. SYLforge supplied the K7 ordinary edit. #8058 supplied the preceding replayed frontier. OpenAI Codex assisted the exact retained-proof comparison, implementation and independent replays. [Weight and chronology source](https://github.com/CrocSwap/integer-mult-bounds/tree/cbe847a953b971f9c6c5a0a6661e2008acd29086/research/frequency-weighted-native-multiplier) · [Native setup predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/8055)
