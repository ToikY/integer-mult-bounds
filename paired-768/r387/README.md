# One lower-band price and calendar test

Round 387 priced one lower band, **1,874**, on #8062's verified (5,451) integer calendar. The physical widths (1,2), raw trial 17145637307/2^42, 51 grade cells and 88 typed cells stay fixed. The lower cutoff funds debit 64982/524288. The same debit fails rigorously at 2,048 even with the real edge-specific fringe. The first actual column widths are 1,866 and 3,732. Independent calculation recovers all eight integer grants at the first band and all four type pairs. Both signed tiers pass at target κ = 0.00389821040 and highest ordinary height 524,369. Round 387 ends with one viable candidate. [Price and negative control](price/PROOF.md) · [Actual calendar and resource audit](audit/PROOF.md) · [Completed Round 388 replay](../r388/README.md)

Use Git and CPython 3.12. Set `PEER` to a checkout of exact #8057 science commit `cbe847a953b971f9c6c5a0a6661e2008acd29086` and `COMPARATOR` to exact #8062 commit `56bd64bed76cadb98e459ed001ccbdf47963ccf6`. The wrapper uses these explicit roots and the supplied immutable evidence. It opens a fresh temporary evidence directory for the original price checker on each run.

```sh
out=$(mktemp -d)
python3.12 -IB replay-price.py --peer "$PEER" --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check.py --research "$PEER/research" --previous evidence/round385/independent/verified.json --previous-price "$COMPARATOR/research/p104-weighted-integer-frequencies-5-451/RESULT.json" --out "$out/audit.json"
cmp "$out/price.json" price/public-receipt.json
cmp "$out/audit.json" audit/receipt.json
```

One machine-generated temporary path in the historical onboarding log is redacted. The public price receipt only changes the hash of that input. The original price receipt SHA-256 is `8128a552127518905bea0799ba2080d6bf6c3026b004a298700eb1394b4702ee` and the calendar receipt SHA-256 is `015ae48db37954f33c7898b1fcaf73fcedabc62e3c1fcfc71df651285cc54e4b`. Ali Romman supplied the typed #8057 producer and #8055 native setup clock. SYLforge supplied K7. #8059 supplied the exact edge-price method and #8062 the previous complete (5,451) calendar. OpenAI Codex assisted the proof and independent reconstruction. [Typed source](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Previous complete profile](https://github.com/CrocSwap/integer-mult-bounds/pull/8062)
