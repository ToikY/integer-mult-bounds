# Round 405 one-case price screen

The independently reproduced comparator is [#8073 at cf4c4b7](https://github.com/CrocSwap/integer-mult-bounds/commit/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e), κ 0.003898219753506. Its exact stopped ceiling is 523210198560303585338978849681/134217728000000000000000000000000. The latest comparable external peer remains [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057), κ 0.00389821. Selected #7000 is separate.

Run from a clean checkout of this handoff with CPython 3.12 and the exact #8073 candidate checkout available at an explicit path.

```sh
python3.12 -IB paired-768/r405/next_child_tariff.py   paired-768/r404/fringe-audit/result.json   paired-768/r404/price-audit/receipt.json   candidate-checkout/research/p104-weighted-k7-suffix/peer8057.tar.gz
```

The script authenticates all three inputs by SHA-256. One fixed profile took 0.095296 s, exit 0, within the 30 s cap. It finished its declared one-case scope. All other heights were outside that scope. Charge the ordinary child tariff 2401/1024 against exact upper mean volume 75/32. This changes the geometric sum from 376 to 2401. Add five entry and nine terminal clock bits before the full selector. The directed envelope funds debit 11178/8192 and rejects 11177/8192. At ordinary heights (8192,117167,524288) and Gaussian height 501832, the complete quoted recurring log₂ C is 318291820, first terminal header 2^1151953+4, entry conversion 517, and maximum height 524288. The quoted target .003898219754 clears #8073’s exact ceiling at this profile. This is prospective pricing. A complete signed replay remains pending.

Ali Romman’s [#8042](https://github.com/CrocSwap/integer-mult-bounds/pull/8042) supplies the receiver-volume proof and [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) the signed supplier. SYLforge supplies the K7 construction. [#8073](https://github.com/CrocSwap/integer-mult-bounds/pull/8073) supplies the directed K7 suffix and exact baseline. Material AI assistance from OpenAI Codex.

Next: check the capped crossing under this charged model in at most 24 profiles and 30 s, check the all-size clock proof at both moments, and freeze at most one winning profile for clean independent signed replay.
