# Thirty-two binary caller idle fusions

Round 309, 2026-11-20. **NO VERIFIED GAIN.** All 16 twice-used IDLE_ONE roles in the exact [#7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) binary caller were tested. Merge their disjoint stage masks and execute the union at either of the two original clocks, leaving all other events fixed. Each of these 32 edits would have reduced two paid idle jobs to one per port. Every edit creates an off-diagonal polynomial coefficient in the forward map and another in the adjoint. A different diagonal target declaration alone cannot repair that. Other placements, changed ordinary operations and joint caller edits remain unresolved.

The complete 798-event incumbent has 38 independent roles and 111 ports. For example, merging role 2's events 19 and 397 at clock 19 puts a nonzero forward coefficient from input 11 into output 0. All 64 exact monomials and their orientations are in `idle.json`. The 30-second/32-case screen exhausted the declared scope in 0.107 s. An independent single-input implementation checked every saved monomial against both the original and edited caller in 0.05 s. The cost and physical construction gates were unnecessary after formal failure. No hosted job was run for this handoff.

Use CPython 3.12 with assertions enabled. From this directory:

```sh
curl -fLsS -o caller.json.gz https://raw.githubusercontent.com/aliromman/integer-mult-bounds/4f7c67ae387cc91580f469aeda4d508b372b9ec1/research/paired-query-only-bit/EFREE-CALLER.json.gz
curl -fLsS -o binary_operator.py https://raw.githubusercontent.com/Clear1nsight/integer-mult-bounds/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/review/binary_operator.py
python3.12 -IB idle_pairs.py caller.json.gz binary_operator.py fresh.json
python3.12 -IB check_coefficients.py caller.json.gz fresh.json
```

The runner authenticates SHA-256 for both sources, and the single-input checker authenticates the caller independently. Clear1nsight supplied the mixed-supplier comparison and polynomial transfer engine, and Ali Romman's #7776 supplies the pinned paired caller. The caller derives from #6834/#6980/#7001. OpenAI Codex materially assisted. The next mechanism selected for Round 310 exchanges the endpoints of two productive helpers at one shared chart with every paid MOVE retained.
