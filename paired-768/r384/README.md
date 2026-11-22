# One precise 5-to-451 physical calendar screen

Round 384 adds no verified κ gain. It priced one `(5,451)` integer birth pair with physical widths `(1,2)` at `17145637307/2^42`, Gaussian H=483,871 and debit 65000/524288. The old `(6,541)` invoice from #8061 is strictly negative at the new tariff. The real planner funds all 51/88 cells, each type, both forced first placements and the actual 456-birth schedule. Both strict signed budgets pass at one selected third ordinary height 524,359 for target κ = 0.00389821035. Neither the old height nor one extra unit alone reaches that target. Other ratios, heights and portable setup bounds lie outside the one test. [Exact price](price/PROOF.md) · [Actual calendar and setup](audit/PROOF.md)

Use Git and CPython 3.12. Set `PEER` to exact #8057 science `cbe847a953b971f9c6c5a0a6661e2008acd29086` and `COMPARATOR` to exact #8061 `a29697b04f8f07ac44aeb2dd34803ee6de9423c4`. From this directory, the supplied path-keyed evidence and pinned checkouts reproduce the exact receipts.

```sh
out=$(mktemp -d)
python3.12 -IB price/price.py --root evidence --peer "$PEER" --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check.py --research "$PEER/research" --previous evidence/round383/independent/verified.json --previous-price evidence/round383/publish/research/p104-weighted-integer-frequencies-6-541/RESULT.json --out "$out/audit.json"
cmp "$out/price.json" price/receipt.json
cmp "$out/audit.json" audit/receipt.json
```

The directed test took 0.10 seconds within 60 seconds. The real physical and resource audit took 5.116 seconds within 90 seconds. Both establish this single candidate can proceed to literal signed replay. Ali Romman supplied the weighted #8057 source and #8055 setup. SYLforge supplied K7. #8059 supplied the exact finite debit and #8061 the previous fully replayed schedule. OpenAI Codex assisted both proofs. [Pinned predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Current comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/8061)
