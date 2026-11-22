# One actual integer birth profile passed both early gates

Round 380 adds no verified κ gain. Exact #8059 at `c34c958114297cdbd1f493666342b8859531d40d` reproduces 0.00389821030. The next literal candidate uses real weights `(8,721)`, widths `(1,2)`, exact tariff `17145637231/2^42`, numerical height 483,871 and old finite debit 65000/524288. The full direct controls reproduce the old `(1,90)` failure at this dyadic, every one of the 51 grade and 88 typed cells, both first exterior placements and positive all-depth finite debit. The actual integer calendar on reduced signed types opens 9,647 and 869,369 replicas at band 20 and exercises all four route types. The original third binary height is excluded by an exact `2.5752e−11` shortfall even with ideal Gaussian funding. Its smallest permitted change to 524,355 gives a funded provisional rate of 0.00389821033. No nearby frequencies or heights enter this result. [Price proof](price/PROOF.md) · [Physical calendar audit](calendar/PROOF.md)

Use CPython 3.12 and Git. Set `PEER` to exact #8057 scientific checkout `cbe847a953b971f9c6c5a0a6661e2008acd29086`. Run from this directory with the pinned evidence tree. The primary case used 0.11 s within a 60 s cap. The separate physical calendar audit used 5.024 s within 90 s. Both runners authenticate their inputs.

```sh
out=$(mktemp -d)
python3.12 -IB price/price.py --root evidence --peer "$PEER" --out "$out/price.json"
python3.12 -IB calendar/check.py --research "$PEER/research" --previous evidence/round378/audit/receipt.json --out "$out/calendar.json"
cmp "$out/price.json" price/receipt.json
cmp "$out/calendar.json" calendar/receipt.json
```

This changes the next round by giving the sole `(8,721)` build priority because actual integer openings and paid counts cleared the independent calendar, and the single higher ordinary height pays the whole signed invoice. All changed ownership checks, nested signed returns and the independent registered replay remain the gate for claiming a gain at this checkpoint.

Ali Romman supplies the actual typed #8057 calendar and compact proof, SYLforge the K7 precursor, and #8059 the exact edge debit and comparator. OpenAI Codex assisted the independent price and physical audit. [Weighted signed source](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Verified comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/8059)
