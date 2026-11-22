# Sharpened ordinary transmission debit

Exact head `19e67d1b36210e3047bbf3d04625d1262cba672a` certifies conditional **κ = 0.00389821103** under the same five signed research premises. Against exact #8065 at 0.00389821057 the gain is **0.00000000046**, or **(4600/389821057)%**. The external #8057 difference is **0.00000000103**, or **(103/3898210)%**. The entire physical child charge is 47/20 and the paid finite ordinary factor fits 703/512 with the original 375/376 contraction. The same-height 11/8 control fails even with ideal earlier funding. The new ordinary/Gaussian profiles also reduce the full recurring log₂ ceiling by 640 to 318293031. [Independent cost proof](PROOF.md) · [Exact receipts](verified.json)

The actual rank profile uses H3=523763 and Gaussian H=484799. The literal paid schedule, all owner returns, both ordinary seams, modulus 3 and 9 signed tests, wrong-sign controls, nested Gaussian loan and signed product all passed. The exact maximum descriptor now uses 19 bits under the existing 20-bit bound. Fixed native setup remains conservatively below 2^228. [Literal gate](build.log) · [All seven registered scientific modes](scientific.log)

From the exact current checkout with Git and CPython 3.12:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-ordinary-debit
```

For detached replay, set CURRENT to the exact current checkout, PREVIOUS to #8065 at `ffa64503646a62a7ac3cd2c47787d670da911f89`, and SOURCES to the proof directory from `dfd25d553a843a946ca0b94130a5ff8943e98fdd` containing TRANSFER.md, RECEIVER.md and ORDINARY-CLOCK.md. The verifier authenticates those exact proof files by both blob and SHA-256. [Original proof directory](https://github.com/aliromman/integer-mult-bounds/tree/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier)

```sh
out=$(mktemp -d)
python3.12 -IB replay.py --current "$CURRENT" --previous "$PREVIOUS" --sources "$SOURCES" --out "$out/receipt.json"
cmp "$out/receipt.json" public-receipt.json
```

The portable receipt differs from the sealed exact receipt only in the digest of one redacted temporary fixture pathname in the predecessor onboarding evidence and that log’s enclosing completion manifest. All prices, signed controls and result bytes agree.

Ali Romman supplied the original 47/20 ordinary transmission and tape proof, the #8057 signed typed provider, and #8055 native setup. SYLforge supplied K7, and #8065 supplies the exact prior height assignment. Codex materially assisted proof, implementation and independent verification. [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [#8065](https://github.com/CrocSwap/integer-mult-bounds/pull/8065)
