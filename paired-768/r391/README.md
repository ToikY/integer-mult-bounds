# Eight-level ordinary transfer preflight

One ordinary terminal profile moves eight levels from stage two to stage three, changing `(8192, 129414, 524395)` to `(8192, 129406, 524403)`. The price and independent phase checks pass at prospective κ = 0.00389821057 against the completely replayed Round 390 release `e4fccb224ce5d9bc530a8027d4f617a6a37d4562` at κ = 0.00389821053. The projected increment is 1/25000000000. **No verified κ gain.** Literal binding and the complete independent registered replay remain open. [Exact comparator and seven-mode receipt](../r390/README.md)

The earlier middle cut moves from 137,768 to 137,760. The outer cuts, the numeric recipe, both paid Gaussian fences, and the signed caller stay fixed. The complete recurring price remains log₂ C ≤ 318,293,671 with a 514-bit entry conversion. The absolute private control envelope grows by 8,192 to 536,988,675 in log₂ units and is charged in the preserved linear storage bound. The exact seven-level control `(8192, 129407, 524402)` falls below the proposed rate. This tests one proposed split and its one-level-smaller control. Other splits and supplier changes remain outside scope. [Original exact price receipt](price/receipt.json) · [Independent phase and stage proof](audit/PROOF.md)

Use CPython 3.12 and Git. Set `COMPARATOR` to the clean Git checkout root at the exact Round 390 release. Run from this handoff. If the Round 390 handoff is stored separately, pass `--round390-evidence` with its explicit directory.

```sh
out=$(mktemp -d)
python3.12 -IB replay-price.py --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check_stage_transfer.py \
  --capsule "$COMPARATOR/research/p104-weighted-upper-band" --out "$out/phase.json"
cmp "$out/price.json" price/public-receipt.json
cmp "$out/phase.json" audit/receipt.json
```

The original exact price took 0.150 seconds of its 60-second cap. The independent phase and stage audit took 6.257 seconds of its 90-second cap. The portable price substitutes only the digest for the predecessor onboarding log whose injected test traceback is path-redacted. All other receipt bytes match the original, and the phase receipt matches byte for byte. [Path digest map](PATH-REDACTION.json) · [Portable price receipt](price/public-receipt.json) · [Independent phase receipt](audit/receipt.json)

The next test is to install these exact heights and the target κ, regenerate the signed invoice, and independently run the installed candidate's full registered suite. Ali Romman supplied the signed weighted installation, clock analysis and typed producer from #8057. SYLforge supplied K7 and the original weighted source checks. Round 390 supplied the exact upper-band comparator and preserved calendar evidence. OpenAI Codex assisted the directed price and independent replay. [#8057 typed installation](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
