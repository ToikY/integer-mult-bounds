# Two-chart corrections for profitable helper transpositions

**NO VERIFIED GAIN.** On the unchanged binary word shared by #7830 and #7863, none of #8022’s 3,112 favorable helper destination transpositions can be implemented by independently preparing local linear corrections at two charts and applying them through the frozen future sends. This covers a common-cut schedule with arbitrary local XOR work. The all-clock relaxation already excludes every member. Each transposition would strictly improve the productive rank moment at equal total rank while retaining the paid packet invoice. No physical edit reached the build stage.

The exact ordered candidate list has SHA-256 `429a5704dfc0f60d290d5441adaccf2440425502222a9a2becd151e929a182dc`. The original word has 680 public owners, 2,874 paid packets and 636 charts. For pair i,j define t=e_i+e_j. Its required public change before relabeling is the rank-one operator t tᵀ. In forward orientation, 3,088 pairs have no chart that can read t; 24 pairs have one chart each. In adjoint orientation, all 3,112 pairs have no reader. The saved result gives the chart for each of the 24 positive single-reader cases. No pair was readable at two distinct charts. No legal common-cut or downstream pulse combination survived for construction. Both orientations together required 3,958,464 per-chart membership decisions. No part of the declared scope remains unresolved.

## Proof for two different local corrections

Let R_c be the original read space and S_c the space of output responses to pulses at chart c. The adjoint read space is S_c. Preparations precede all injections. Under the unchanged linear background, chart c contributes a linear map whose row space is contained in R_c and whose image lies in S_c. The proof grants unlimited free combinations of those rows and responses. It also grants every clock for the impossibility test.

In forward orientation, at most one chart reads t and no chart can unilaterally deliver response t. Given two distinct charts, pick a chart a at which t is unreadable, and call the other b. There is an input x that annihilates R_a while tᵀx=1. The correction from a then vanishes. The required response on x is t, which is outside S_b. Thus even two arbitrary different locally precomputed corrections cannot sum to t tᵀ. The same argument applies in reverse by choosing b among the charts whose response space omits t; neither chart can read t. A single-chart correction was independently excluded in #8022.

For any number of charts under the narrower mechanism where *each* acting chart must first store t itself, the forward direction has at most one eligible chart and the reverse has none. This does not establish a ceiling for three arbitrary different local forms. Sequential feedback that changes later read spaces, an additional paid path, a changed word or a different terminal map remains open. A subsequent test could name a third actual chart and check whether t lies in the image of the sum of the three local map spaces before attempting a construction.

## Clean replay

With CPython 3.12, download the exact public package files from the #8022 head. The two scripts check source bytes, regenerate the ordered candidate pool, and compare it against its pinned digest.

```sh
set -eu
base=https://raw.githubusercontent.com/ToikY/integer-mult-bounds/8bd02daca9f4e7a227f6c552905930eed9498655/research/bit-helper-exchange-obstruction
mkdir -p pinned/sources
for f in verify.py EXPECTED.json crosscheck.py sources/WORD.json.gz sources/bit_native.py sources/binary_operator.py; do
  curl -fLsS "$base/$f" -o "pinned/$f"
done
python3.12 -IB exchange.py pinned result-fresh.json
python3.12 -IB check.py pinned result-fresh.json replay-fresh.json
```

The graph screen took 0.249 s of its 60 s discovery cap. Independent literal replay used 0.427 s of the 20 s reserve. It reconstructs the candidate list from rational rank inclusions, checks all 680 output rows and 3,554 dirty retirements per orientation, and reproduces the exact chart identities using opposite-pivot quotient reduction. A synthetic control reads the same parity at exactly two separate charts. The scientific exit status of both commands was zero. No candidate CI, compiler, precision or all-size replay was required by this local exclusion. Proof and implementation time were interleaved and were not separately timed.

[PR #8022](https://github.com/CrocSwap/integer-mult-bounds/pull/8022) supplied the profitable pool, published single-chart test, and independent literal verifier. Clear1nsight supplied the #7786 native word, #7830 supplier and #7863 consumer. Ali Romman supplied the #7776 graph extraction. The 36-call paired caller retains the #6834/#6980/#7001 lineage. OpenAI Codex materially assisted the proof, screen and replay.
