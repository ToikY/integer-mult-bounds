# First-read counterexamples for 32 paid binary returns

Round 308, 20 November 2026. **NO VERIFIED GAIN.** The 32 selected grade-six MOVE deletions each lack a legal receiver operand at their first protected read. All comparable rates here use the five conditional premises and the complete outer binary integer multiplication application.

## Comparator and scope

The strongest complete claim found and independently reproduced in this round was [#7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) at `87fbf4f7b35b0f18ab12b5767775a9a424cf0b15`, κ ≥ 0.00387992803556. Its two words have canonical SHA-256 `d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d` and `7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48`. The unchanged 38-role caller has compressed SHA-256 `757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b`. The 36 BIT and 48 rational calls retain native all-column, owned erasure, compiler, precision/tape and analytic recovery premises. The rational raw bracket is [0.00388013644474, 0.00388013644475], while the lower binary bracket is [0.003879928046154, 0.003879928046155]. The admitted ordinary BIT cap is 0.003879928035646. The five-premise benchmark differs from [#7837’s four-premise grade-14 result](https://github.com/CrocSwap/integer-mult-bounds/pull/7837) at 0.00387992802601. The selected result on main `e54523517d0f03e58352e647c403a5af3e525a57` remains #7000 at 0.00363005817.

The 14:51 UTC refresh checked canonical main, public open proposals, the recent κ-title search, recent closed and archive search, and the active discussion board and its coordination threads. The previous proposed chart-373/1062 composition was already replayed in the earlier sprint. Its rate 0.0036518250428 was surpassed. It adds no gain in this round.

At each single-packet deletion, pin all other paid payloads, all chart tags, prior reads and the original read clock. Allow an arbitrary XOR of **all** other live receiver rows, including the destination's old value in the relaxed test. A nonzero target on an input annihilated by this whole set excludes even arbitrary deterministic receiver-local reconstruction with the same observations: that input and zero are indistinguishable there. Unknown co-encodings, rescheduling or replacement traffic lie outside the exclusion. The per-packet gross saving before repair would have been 36 rank-six calls. A repair cost or exclusion for other mechanisms has not been inferred.

The pool contains 2,874 single-MOVE private packets. Original priority was descending paid grade, ascending number of reads, then increasing MOVE clock. The first three were clocks 11616 (35→612), 11813 (104→619), and 11954 (20→613). Their first read clocks were 32980, 33015 and 32985. All three receiver stocks had rank 3. The fixed budget was 32 cases or 30 seconds. It exhausted its 32-case allowance in 0.0402 seconds. All 32 excluded, no survivors, 2,842 untested. The exact frozen order, read and write clocks, sender rows, tested and unvisited clocks and distinguishing inputs are in `screen.json`. One forward obstruction suffices for a two-orientation construction. No changed adjoint or scientific candidate replay was needed or run.

## Reproduce the exclusion

Use CPython 3.12 with assertions enabled. From the directory containing this handoff:

```sh
curl --fail --location --output word.json.gz https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/binary/WORD.json.gz
python3.12 -IB screen.py word.json.gz fresh.json
python3.12 -IB check_separators.py word.json.gz fresh.json
python3.12 -IB check_separators.py word.json.gz screen.json
```

Both programs authenticate the compressed word. The scalar checker packs the 32 explicit binary inputs into lanes and recreates every read directly, without using Gaussian elimination. It checks the chart and old receiver stock, all 680 public outputs, and private retirement. Its observed wall time was 0.04 s. Runtime is the sole nondeterministic field in the screen. A corrupted input or false separator must fail. Independent complete **baseline** replay took 23.75 s for the producer and 26.78 s for the independent application. Its 21 direct and 127 inherited producer pins authenticated; BIT.json, AUDIT.json and RESULT.json matched the producer's published bytes. The independent rational application and audit also matched. [Exact baseline replay instructions](https://github.com/Clear1nsight/integer-mult-bounds/blob/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/README.md#reproduce) · [Earlier-chain hosted replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/44688740120/job/136129188933) · [Shared planner failure](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/44688740070/job/136129189017)

The screen was prepared between the comparator replay and its first run. Proof and implementation time were interleaved with source tracing and were not separately timed. No campaign CI job ran for this handoff. The positive control was the original complete peer application. The scalar replay uses the zero input and the reported witness for each obstruction.

## Next test and credits

Inspect the two IDLE_ONE events on each of the sixteen twice-used binary caller roles. Freeze the exact 798-event caller. First test the 32 assignments that place each pair's union at one original endpoint and remove the other event. Check the full formal polynomial transfer in both directions, keeping all 38 independent output labels and every other event fixed. Stop at the first exact survivor or 32 cases/30 s. Any survivor still needs physical stage admission, ordinary costs, a new supplier and the complete independent application.

Clear1nsight supplied the #7786 word, #7830 mixed cutoff, replay and expanded application. Dugongue's #7831 and Rohan Arun's #7835 supplied the preceding capacity schedules. Ali Romman's #7776 lineage supplies the dual caller and original tariff. CubeJerry and DreamingOfClouds contributed the paired-caller lineage through #6980 and #6834. [#7833](https://github.com/CrocSwap/integer-mult-bounds/pull/7833) separately excludes a fixed adjoint three-ingress repair on charts 510–518. This handoff checks forward first-read deletion of the listed packets. OpenAI Codex materially assisted the screen and scalar replay.
