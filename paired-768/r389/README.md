# Directed upper-band divisor preflight

This round tested exactly one wider upper band, U=2⌊M/(1724·306)⌋, on the signed (5,451) schedule at exact #8063 release 682fd9512ccbf3035089d7e5f9cb4dedf9f746b4, κ=0.00389821040. The original word is #8057 science cbe847a953b971f9c6c5a0a6661e2008acd29086. The full finite factor is below 1.08964667430503, with at least 0.0000078874159 headroom at debit 64944/524288. The prior divisor exceeds the new allowance by at least 0.000051649827. The physical period is 1364 with tickets (0,272,545), exact first swap 1→272, and true root grant at both relevant heights. The first sufficient ordinary H3 is 524395 at prospective κ=0.00389821053. This is a viable candidate preflight. The literal full registered replay remains a separate gate. All other divisors, words, and resource envelopes are outside this one-case scope. [Directed assumptions and proof](price/PROOF.md) · [Independent physical proof](audit/PROOF.md)

Use CPython 3.12 and Git. Set PEER to an exact detached checkout of the stated #8057 commit and COMPARATOR to the exact #8063 release checkout.

```sh
out=$(mktemp -d)
python3.12 -IB replay-price.py --peer "$PEER" --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check.py --research "$PEER/research" \
  --previous ../r388/verified.json \
  --previous-price "$COMPARATOR/research/p104-weighted-lower-band/RESULT.json" \
  --out "$out/physical.json"
cmp "$out/price.json" price/public-receipt.json
cmp "$out/physical.json" audit/receipt.json
```

The 60-second one-price and 90-second one-physical scopes finished in 0.11 and 12.789 seconds respectively. The portable price copy redacts a single temporary pathname from the prior onboarding log and pins the redacted bytes. All arithmetic fields match the original sealed receipt. The price receipt hash field for that onboarding path necessarily differs. The actual signed physical audit is unchanged. Build one literal upper divisor only when both gates pass.

Ali Romman supplied the #8057 signed native multiplier, tape bounds and original transport proof. SYLforge supplied K7. #8059 supplies the directed finite debit method and #8063 the verified lower band. OpenAI Codex materially assisted research and independent verification. [Exact signed peer source](https://github.com/CrocSwap/integer-mult-bounds/tree/cbe847a953b971f9c6c5a0a6661e2008acd29086/research/frequency-weighted-native-multiplier) · [Current comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/8063)
