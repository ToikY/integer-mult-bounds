# Round 404 charged K7 suffix screen

Exact comparator [#8072 at 75f7e1c4](https://github.com/CrocSwap/integer-mult-bounds/commit/75f7e1c44f48c43983016bcf8878c4d9e5e87c62), κ 0.003898214283192, with matching complete local and hosted evidence. Latest external #8057 remains 0.00389821. The maintainer-selected #7000 remains separate.

The installed K7 edge census bounds the matched-interval suffix coefficient below 8 at the historical floor L=18960. The additive term from the integer birth count is separated from the leading term, and the four small additive, integer, grid and delay errors remain covered by the existing 2^-128 reserve. The ordinary exterior-width loss and all other child, routing, precision, and restoration costs stay charged. [Authenticated exact K7 proof check](fringe-audit/result.json)

From this handoff checkout with Git and CPython 3.12, run the saved one-case test and the directed factor check.

```sh
python3.12 -IB paired-768/r404/next_fringe_gate.py paired-768/r402/verification/invoice.json
python3.12 -IB paired-768/r404/directed_factor.py paired-768/r402/verification/invoice.json
```

The single saved gate passed in 0.110208 s, below its 30 s cap. The exact 8/L factor supports 11204/8192. The prior 64/L envelope and the adjacent lower 11203/8192 booking fail these directed comparisons. A bounded 11205 allocation search was followed by three neighboring prices at the tighter proven 11204 booking. The latter exact gate used 0.288 s and established the single winning G501831 profile with ordinary heights (8192,117168,524288). Gaussian height 501830 misses on Gaussian and height 501832 on ordinary. The whole proposed clock is 318291911, 100 below #8072, with first header 2^1151953+4 and 517-bit entry conversion. The whole price and both signed inequalities passed. [Exact profiles and invoice](price-audit/receipt.json)

The two supplementary reproductions take explicit roots. Use exact clean checkouts of #8072 and #8067, and the exact original [#8042 TRANSFER.md](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/TRANSFER.md) with SHA-256 7164831a5dd9f5c6231bf4c3f4b2061d91cbfab559071a0a5d68966e3f7ac55c.

```sh
python3.12 -IB paired-768/r404/fringe-audit/check_suffix.py comparator-checkout floor-checkout TRANSFER.md paired-768/r402/verification/invoice.json
python3.12 -IB paired-768/r404/price-audit/check_allocation.py comparator-checkout paired-768/r403/verification/REPLAY-RECEIPT.json
```

Ali Romman supplied the #8042 complete suffix and timing proof, #8057 signed caller and compiled sources, and #8055 native setup. SYLforge supplied K7. #8067 supplies the directed K7 edge bound and actual paid floor; #8072 supplies the verified allocation comparison and the unchanged inherited charges. Codex materially assisted the directed calculation and proof review. The price evidence above by itself is provisional until independent literal replay.
