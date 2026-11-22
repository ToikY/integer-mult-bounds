# Directed ordinary finite-debit preflight

One tested candidate keeps the signed K7 recipe and its 32,768 opening floor. The completely charged ordinary factor has a directed upper bound below 2^(703/512), allowing the debit to fall from 11/8 to 703/512 with the same child volume factor 47/20 and contraction 375/376. The original conservative upper bound at 702/512 fails. At proposed heights `(8192, 129406, 523763)` and Gaussian height 484,799, keeping the old 11/8 debit fails even with ideal intermediate bookings. The Gaussian debit remains 64,944/524,288. [Directed price and exact controls](audit/PROOF.md) · [Sealed exact price](price/receipt.json)

The comparator is independently reproduced #8065 at `ffa64503646a62a7ac3cd2c47787d670da911f89`, κ = 0.00389821057. Both signed tiers price the proposed κ = 0.00389821103, a projected difference of 23/50000000000. The complete recurring log₂ clock falls by 640 to 318,293,031. The maximum candidate height descriptor needs 19 bits and fits the existing at-most-20-bit setup bound. The literal install must update the active guard from exactly 20 to at most 20 while retaining the historical fixtures' original invoices. **No verified κ gain.** Only this profile and the stated controls were tested. [#8065](https://github.com/CrocSwap/integer-mult-bounds/pull/8065) · [Exact comparator replay](../r392/README.md)

The independent phase audit reconstructs both signed profiles and checks the genuine Gaussian exterior placement at both heights. It tests the actual ordinary direct and compiled seams, replaying 81 records modulo 3 and 6,561 modulo 9 against dense signed oracles and rejecting the wrong return sign. This preflight clears the candidate to build one literal installed profile. The next gate is that header and full registered independent replay under the retained five premises. [Exact independent receipt](audit/receipt.json)

Use CPython 3.12 and Git. Set `COMPARATOR` to the root of a clean checkout at the exact #8065 head. Run from this handoff directory with the earlier handoffs adjacent. If the `paired-768` evidence directory is elsewhere, pass it as `--evidence-root` and set `BASELINE_EVIDENCE` below to its `r392` directory.

```sh
out=$(mktemp -d)
BASELINE_EVIDENCE=../r392
python3.12 -IB replay-price.py --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check.py \
  --capsule "$COMPARATOR/research/p104-weighted-ordinary-transfer" \
  --baseline-receipt "$BASELINE_EVIDENCE/verified.json" \
  --baseline-log "$BASELINE_EVIDENCE/scientific.log" --out "$out/audit.json"
cmp "$out/price.json" price/public-receipt.json
cmp "$out/audit.json" audit/receipt.json
```

The portable price replay passed from a fresh Git root in 0.097 seconds under its 60-second cap. Its only difference from the sealed receipt is the pinned digest of the path-redacted Round 392 onboarding traceback. The original independent audit ran in 6.528 seconds under a 90-second cap and its public replay reproduces the same bytes. [Sealed completed-log pins](price/COMPLETE.json) · [Portable completed-log pins](price/COMPLETE-public.json) · [Portable price receipt](price/public-receipt.json)

Ali Romman supplied the #8057 signed installation and finite tape factor and the unchanged physical contraction and tape proof. SYLforge supplied K7. #8065 supplied the fully reproduced profile and decisive predecessor controls. OpenAI Codex assisted this pricing and independent replay. [Signed installation](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
