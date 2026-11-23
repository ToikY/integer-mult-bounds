# Fully charged Round 405 allocation

The one-case opening gate used (H=(8192,117167,524288)) and (G=501832). It passed in 0.095296 s. The ensuing search checked 17 distinct Gaussian slices in 0.59 s, under a cap of 24 profiles and 30 s. It proved the fixed-booking capped optimum at (H=(8192,111681,524288)), (G=509812). The left slice misses on Gaussian rate and the right slice on the best ordinary rate. A weighted reciprocal tangent and the exact two intermediate floors certify the ordinary bounds. All explored slices and signed checks are in the [exact receipt](receipt.json). Other budgets, stage counts and tariffs stay open.

The tariff changes from 47/20 to 2401/1024, keeping the coarse physical mean ≤75/32 at both normalized moments. Charge the entire geometric sum 2401 and five entry and nine terminal clock bits. The full profile has recurring log₂ C 318291900, first terminal header 2^1154447+4, 518 entry conversion units, and maximum native height 524288. The conditional target is 0.003898223617430 under the same five hypotheses. This arithmetic reconstruction is distinct from the registered signed scientific replay.

Run from a clean checkout of this handoff with CPython 3.12, using an exact clean detached #8073 checkout at `comparator-checkout`:

```sh
python3.12 -IB paired-768/r405/price-audit/check_allocation.py \
  comparator-checkout \
  paired-768/r404/verification/REPLAY-RECEIPT.json \
  paired-768/r404/price-audit/receipt.json \
  paired-768/r404/fringe-audit/result.json
```

The source pins key by full archive path. Ali Romman's #8042 derives the actual fixed-frame mean and full ordinary clock, #8057 supplies the signed provider, and SYLforge supplies K7. #8073 supplies the exact comparator and its K7 suffix proof. Codex materially assisted the check.
