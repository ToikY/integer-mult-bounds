# Fixed nested Type B idle square

On the exact signed #7113 caller, the candidate reduces Type B IDLE2324
and IDLE2355 to one rank-eight B16 call and an ordinary B9–B15 square.
It keeps the existing IDLE2337. On port 15 at width one, compare the two
fixed fibres all-positive and B9 negative (Walsh axes 73,74).
Then the original normalized boundary difference has rank 3, whereas
the proposed word can supply at most rank 1. The exact independent
minor on rows (52,36,37), columns (36,37,52) has determinant 77.
Thus fixed wrappers fail, and even arbitrary sector-independent
linear wrappers and a sector-independent bypass cannot fix the
difference. The original word and proposed edit do agree at unit bodies.
Other masks, clocks and cross-fibre routes remain open.

The fully priced positive gate was never reached. Projected eight-port
gross [882.24727829181406823, 882.24727829181406824] is before repairs
and ancillary costs. No exponent change from this test.

Reproduce from CPython 3.12. Supply an explicit fresh input directory.
The checksum assertions authenticate each of the three referenced sources.

```sh
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

All 36 columns and independent rows completed in 0.06 and 0.08 seconds.
Each runner has a 30-second cap. The omitted-reflection control gives
rank 2. The shared retained wrapper scope and exact argument are in
[independent/SCOPE.md](independent/SCOPE.md). The next route changes a
native helper itinerary. [#7544](https://github.com/CrocSwap/integer-mult-bounds/pull/7544)
has the constructive separate result.

Credit Rohan Arun/#7113 for the signed caller, Clear1nsight/#7481 and
#7480/#7334 for the replayed comparison, #7360 for the related square
mechanism and #7541 for the distinct B2 relocation and independent
propagation engine. #7298 supplies the directed tariff. OpenAI Codex
and subagents materially assisted.
