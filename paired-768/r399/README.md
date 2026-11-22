# Exact fixed-clock height allocation bound

The exact comparator is #8068 at `8c800e1b6458526e1ce7a59150bba8a0d29d0027` with reported κ = 0.00389821380. Its independently reproduced installed ceiling is exactly `6415371643634932109531074617/1645720738201600000000000000000`. Its seven scientific modes, repository checks and historical replay passed on that same head. [#8068](https://github.com/CrocSwap/integer-mult-bounds/pull/8068) · [Complete comparator and replay](../r398/README.md)

The two exact adjacent crossing heights are 490,663 and 490,664. The global optimum for this family uses ordinary heights `(8192, 124847, 524288)` and Gaussian height 490,664, giving a true installed ceiling of `104641888400286240891629336349/26843545600000000000000000000000`. It funds prospective κ = 0.0038982141167032, exactly `170173756287357890503/1645720738201600000000000000000` above the old installed ceiling. The charged log₂ C decreases by 260 to 318,292,451 with 515 bits of entry conversion, maximum native height 524,288 and live tape bound 297.6n bits. **No verified κ gain.** The final literal construction and its full independent replay remain open. [Whole-family proof](price/PROOF.md) · [Independent derivation](audit/PROOF.md)

This bound covers all three-stage ordinary height allocations in [8,192, 524,288] and Gaussian heights in [1,024, 524,288] under the same signed K7 and Gaussian words, debits and recurring clock ceiling 318,292,711. It prices the actual prior ticks and both signed tiers. The primary search used 14 evaluations in 0.10 seconds, and the independent audit used four in 0.083 seconds. The 18 evaluations cover 14 distinct heights. Other signed words, debit changes and larger resource limits remain outside scope. [Sealed primary receipt](price/receipt.json) · [Sealed independent receipt](audit/receipt.json)

Use CPython 3.12 and Git. Set `COMPARATOR` to the clean exact #8068 checkout root. Run from this handoff directory.

```sh
out=$(mktemp -d)
python3.12 -IB replay.py --comparator "$COMPARATOR" --out "$out"
cmp "$out/price.json" price/public-receipt.json
cmp "$out/audit.json" audit/public-receipt.json
```

The wrapper runs both original checker programs. It reproduces both receipts from the exact checkout, allowing changes only to the predecessor onboarding traceback digest and the derived receipt and manifest hashes. All original sealed receipts are included. A replay from isolated exact Git objects used 0.189 seconds. [Public price receipt](price/public-receipt.json) · [Public audit receipt](audit/public-receipt.json) · [Sealed log manifest](price/COMPLETE.json) · [Public log manifest](price/COMPLETE-public.json)

The next test is to bind the one optimum profile and exact rate, then run the complete signed science and repository checks. Ali Romman supplied the original weighted signed provider, caller and storage proof. SYLforge supplied K7. #8068 supplied the complete signed comparator and actual resource envelope. OpenAI Codex assisted the primary and independent checks. [Weighted provider #8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
