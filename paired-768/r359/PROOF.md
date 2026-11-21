# No nonempty single-chart injection preserves all original outputs

For the frozen #8027 binary word, the output-demand matrix has full column rank on **every one of its 635 source charts**. Its 2,803 paid positions contribute total rank 2,803 and total nullity zero. The largest chart is chart 0, with 516 columns and rank 516. Every possible nonempty subset of departures on an unchanged individual chart changes at least one of the 630 original public outputs. This result includes all subset sizes, beyond the pair-only exclusion in R358.

For a source chart A, enumerate each paid departure at its own original clock. Let bᵢ be its entire GF(2) output perturbation vector. Inject a new independent bit z by a legally cocharted ADD into a chosen subset of those departures, preserving the original graph. The old-output change is (Σᵢ xᵢ bᵢ)z for a selector x. This linear superposition holds even when an earlier injected value reaches a later departing register. Consequently any support preserving every old arbitrary input/output interface must lie in the right kernel of the 630-row matrix with columns bᵢ. Gaussian elimination with least-coordinate pivots checked that each column adds a pivot. Therefore the only selector is zero on every source chart. An empty injection leaves no carried copy of z from which to decode a new higher-grade return in this mechanism.

The test separately reproduced all old forward and transposed endpoints and private lifetimes, the R357 output-demand stream hash, the exact R358 pair exclusion, and the complete 36-call supplier context. Even granting every kernel dimension a productive grade up to 8−dim(A), waiving every decoding/transport cost and counting all 36 real calls, the gross credit is exactly [0,0]. No further physical build is indicated. Scope is one newly injected direction, one unchanged chart, fixed paid graph and fixed old outputs. Changing a frame and its surrounding interfaces, changing the old output map with a proved repair, or injecting across multiple charts would require a separate construction. No claim of global optimality follows.

**Reproduce.** CPython 3.12. All 2,803 positions checked; none unvisited. Cold time 0.244863 seconds under a 30-second discovery cap with ten seconds reserved for verification. Deterministic receipt 5a093254a2244c6289fb13aff19fd18eae5ec7b59d87d1e84a0023adc9a42d1c includes every chart's count, physical rank and nullity. Immutable #8027 head fb9b6a7b0d27da1cf98430893a3016bf811e2aa4, word b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69. R352 remains the independently accepted complete comparator. [Original binary word and signed replay](https://github.com/aliromman/integer-mult-bounds/tree/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain)

```sh
python3.12 -IB audit.py --peer PEER_8027 --accept R352_ACCEPT.json \
  --r354-code R354_INDEPENDENT/audit.py --r357-code R357_INDEPENDENT/audit.py \
  --r358-code R358_INDEPENDENT/audit.py --r357 R357_INDEPENDENT/receipt.json \
  --r358 R358_INDEPENDENT/receipt.json --out fresh.json
```

Ali Romman supplied the native word and signed caller; Clear1nsight and the retained verifier authors supplied the exact literal transpose, chart and pricing rules. R357 supplied the all-position output perturbations and R358 supplied the pair control. OpenAI Codex materially assisted the independent implementation and proof.
