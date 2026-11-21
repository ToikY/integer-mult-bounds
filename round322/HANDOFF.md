# Separate-bank zero-paid helper births on the frozen binary word

**NO VERIFIED GAIN.** The #7786 native word used by #7830 and #7863 has no zero-new-paid, single-midpoint birth in the calibrated #7781 template below. All 58,512 chart, helper-endpoint cohort and orientation combinations were tested. Of these, 2,560 had strict nested chart geometry. The other 55,952 failed the geometry test. No case remained unresolved inside the stated scope.

Let the complete public transfer be M, with arbitrary input x, including all 222 main coordinates. A helper h starts at A and returns at B. At a strictly intermediate chart c with unchanged original paid paths, require

- a pulse with output response v=Md supported at B, where d is supported at A and v_h=1;
- a readable row q supported at A and a separately readable calibration row k with k M⁻¹ supported at B;
- qd=kd=1.

The source may pre-encode using any legal main or helper coordinate on A. The returned fields may use any legal main or helper coordinate on B. These tests follow from substituting U=x⁰+d(x_h+qx⁰), with x⁰=x+e_hx_h, and injecting a fresh value plus kU using c’s sends. The old coordinate h must return qU=x_h at c. At B, the remaining independent outputs must be recoverable and the new output must equal the fresh input. Given valid chronological read and write stock, the gross productive change across 36 invocations would be 36·(a^(1−κ)+b^(1−κ)−(a+b)^(1−κ)), with a and b the two strict chart distances. No candidate reached this stage. A gross difference alone would still require a native construction, ownership and restoration replay, and full pricing of the changed XORs, private stock, precision/tape and recursive compiler.

The all-clock relaxation grants every read and every send at c regardless of chronology. Across the 2,560 nested combinations, 2,189 lacked a nonzero supported pulse, 361 then lacked a source read, seven then lacked a return calibration, and the last three could not meet the three binary pairing equations together. No chronological prefixes needed testing. A different transfer, extra paid path, a coordinated two-midpoint construction, or independent physical input populations spanning multiple starting charts would reopen a distinct question.

The graph extractor and literal tape engine compute the deciding conditions independently. The graph test intersects the two restricted pulse spaces and searches its basis combinations. The literal check uses the actual forward and adjoint public maps and computes opposite-pivot quotient kernels. For a fixed q, k M⁻¹ and h, let their three binary functionals on the allowed pulse space be f,g,l. A pulse with three evaluations equal to one exists iff all three are nonzero and f+g+l is nonzero. The independent check applies this criterion to every case, verifies all 680 public columns and 3,554 dirty retirements each way, and exercises a positive and a rank-inconsistent synthetic control. Discovery took 0.091 s of 60 s. Independent replay took 1.321 s of 20 s. Active proof and implementation were interleaved and were not separately timed.

## Reproduce with CPython 3.12

From this directory, build an empty input tree with these three public files. Both scientific scripts check the returned source hashes. The result.json receipt gives every nested case; replay.json records the independent recount.

```sh
set -eu
root=./inputs322
word=inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz
edge=inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py
lit=upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py
mkdir -p "$(dirname "$root/$word")" "$(dirname "$root/$edge")" "$(dirname "$root/$lit")"
curl -fLsS https://raw.githubusercontent.com/Clear1nsight/integer-mult-bounds/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/binary/WORD.json.gz -o "$root/$word"
curl -fLsS https://raw.githubusercontent.com/aliromman/integer-mult-bounds/4f7c67ae387cc91580f469aeda4d508b372b9ec1/research/p104-dual-supplier-lift/bit_native.py -o "$root/$edge"
curl -fLsS https://raw.githubusercontent.com/Clear1nsight/integer-mult-bounds/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/review/binary_operator.py -o "$root/$lit"
python3.12 -IB split.py "$root" fresh.json
python3.12 -IB check.py "$root" fresh.json checked.json
```

The #7885 fixed-source representative cases and the #7891 two mixed helper-469 windows have narrower local fixtures. #7991 funds an intermediate split with a changed paid course. Clear1nsight supplied the #7781 calibrated birth, the #7786 word, the #7830 literal evaluator, and the #7863 application. Ali Romman supplied the #7776 graph extraction and arbitrary-input producer basis operations. Predecessor #6834/#6980/#7001 contributed the paired caller. Campaign Round 318 covered directions restricted jointly to a common endpoint cohort. OpenAI Codex materially assisted the screens, proof and replay. Hosting was unrun for this analysis.
