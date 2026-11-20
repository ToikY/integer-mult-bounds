# Calibrated midpoint births on the fixed BIT word

**No verified κ gain.** The frozen #7830 BIT word has 46 cohorts of independent helpers with the same source chart A and return chart B. A candidate would insert an independent input and return at a strictly nested midpoint c, carrying the intervention through already-paid sends. Both orientations were tested.

For one cohort J, let L contain every GF(2) row readable at c, including all arrivals, and let R contain every output response to independently modifying a send or terminal on c. Let V consist of vectors supported on J. The proposed calibration requires q in L ∩ V and d in R ∩ V with q·d=1. At a legal cut, choose h with d_h=1, put x⁰=x+e_h x_h and feed U=x⁰+d(x_h+q·x⁰) by source-local XORs on A. The read q·U=x_h is the first daughter's return. Pulse w+q·U on the selected sends, where w is the second daughter's new input. Since the frozen public map M is the identity on J with no off-cohort output on those directions, the result is Y=M x⁰+d(w+q·x⁰). The B-local output q·Y=w returns the second value and the correction Y_i+d_i Y_h restores every old output i≠h. The paid MOVE inventory would remain fixed while the productive grade g splits into positive a,b with a+b=g. The test grants all clock positions before checking chronology.

Of 58,512 chart/cohort/orientation combinations, 2,560 are strictly nested. In the forward orientation, 277 of the 1,280 nested pairs have a nonzero read in V and 94 a nonzero write in V. **None have both.** The adjoint swaps the two counts. This excludes the proposed one-cut calibration for all clocks and all members of these endpoint cohorts. It does not cover q and calibration k supported on different endpoint banks, main-port-assisted encodings, or extra paid traffic. First action on a broader construction: price a split where q uses the entire A-input bank, kM⁻¹ uses the entire B-output bank, and injection response Md lies in B; then test all pairings and chronological noninterference as in #7781.

## Reproduce

Use CPython 3.12. The primary program checks the compressed word and the graph extractor by SHA-256. The independent implementation authenticates the full literal-tape engine, verifies every arbitrary-input output and 3,554 dirty retirements per orientation, and identifies the same subspaces via quotient signatures of the cohort coordinates. Positive and orthogonal controls exercise the pairing test.

```sh
set -eu
root=inputs318
word=inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz
edge=inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py
literal=upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py
for file in "$word" "$edge" "$literal"; do mkdir -p "$root/$(dirname "$file")"; done
curl -fLsS https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/binary/WORD.json.gz -o "$root/$word"
curl -fLsS https://raw.githubusercontent.com/aliromman/integer-mult-bounds/4f7c67ae387cc91580f469aeda4d508b372b9ec1/research/p104-dual-supplier-lift/bit_native.py -o "$root/$edge"
curl -fLsS https://raw.githubusercontent.com/Clear1nsight/integer-mult-bounds/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/review/binary_operator.py -o "$root/$literal"
python3.12 -IB calibrate.py "$root" fresh.json
python3.12 -IB check.py "$root" fresh.json fresh-replay.json
```

The original 60-second discovery scope exhausted in 0.086 s. The independent check took 0.562 s. The primary receipt records each nested chart/cohort/orientation and its status, and the membership of all cohorts. Proof and implementation overlapped with other campaign work and have no separately instrumented timer. Hosted replay was unrun.

Clear1nsight supplied #7786's frozen native word, #7781's calibrated birth, and #7830's mixed supplier and literal replay engine. Ali Romman supplied #7776's annotated native graph. #7781 charges paid subdivisions to create the data path; this screen tests an existing path with read and calibration equal and supported inside J. OpenAI Codex materially assisted the argument and both verifiers.
