# Independent fixed-height price for the smaller ordinary child tariff

Scope is one profile, exact #8094 at c20a08dc0a79a989e3515068560d5da371c0a2a8. The only experimental substitution is the proposed ordinary tariff 2391/1024, using debit 1414404/2^20 on the earlier suffix 186/25 and floor 4474. Its receiver inequality and directed finite price are the pinned Round 413 receipt. This check holds the Gaussian height at 208653 and bills both ordinary clocks with their existing bounds.

The largest admitted 10^-15 grid result is 0.003900857269150, above the reported #8094 value 0.003900857267786 by 341/250000000000000. It exceeds the exact old guarded ordinary crossing. The new ordinary crossing has positive room and the Gaussian inequality binds. The next display tick and the unchanged candidate rate at Gaussian height 208652 both fail the Gaussian inequality. Both tiers pass the inherited 54 strict and four functional signed scalar checks. The entry conversion surcharge remains 121121 and the complete recurring log₂ C remains 85945126846.

The checker independently reconstructs all ordinary stage bookings, both tier charges and the whole recurring maximum. It authenticates and then reuses the outer-budget inequality implementation, and treats the earlier literal tariff bound as an input. The predecessor control reconstructs all published rates and signed margin records exactly. The logical and physical signed dispatch, candidate package installation, setup metering and native replay remain separate gates. There is no verified gain at this stage. [Exact #8094 profile](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) · [Inherited ordinary receiver and clock](https://github.com/CrocSwap/integer-mult-bounds/pull/8042)

## Replay

From a clean handoff checkout containing the pinned Round 411 and Round 413 inputs and this directory, use CPython 3.12:

```sh
python3.12 -IB paired-768/r414/independent-price/check.py > independent-price.json
cmp independent-price.json paired-768/r414/independent-price/RECEIPT.json
```

An explicit `--root` can instead point to the checkout's `paired-768` directory. The checker enforces a 30-second cap and rejects mismatched input hashes, duplicate receipt keys and disabled assertions. The scoped runner took 0.03 seconds and exited 0.

Credit floration for the #8094 profile, Ali Romman for the inherited ordinary receiver and clock, SYLforge for the K7 supplier, Clear1nsight for the wider-η control, and the Round 411 and Round 413 independent receipts. OpenAI Codex assisted with this independent priced comparison.
