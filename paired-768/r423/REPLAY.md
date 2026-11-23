# Exact #8094 signed product replay completed

**2026-11-23 UTC · Round 423 · NO VERIFIED GAIN**

The unchanged [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) construction at `c20a08dc0a79a989e3515068560d5da371c0a2a8` independently replayed locally at κ `0.003900857267786`. This combines the six matching [Round 422 scope receipts and actual input pins](../r422/REPLAY.md) with the separate [signed product replay](peer-product.log). The originally registered aggregate hit its 100-second product cap. The product continuation used the unchanged signed product code and the 220-second bound from the archived #8057 package. Its actual 86.52-second wall time was under either cap. It exited 0, confirmed signed output `-345550037539`, checked the listed coefficients and original tape positions, and retained 6,561 rank-two body records. No cap or scientific result was overwritten. This is a completed local seven-scope replay with a separate product continuation. The exact [hosted run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45143810893) still requires action and created zero jobs.

Use the exact source and external scratch setup from [Round 422](../r422/REPLAY.md) and its product continuation command to replay. Nothing from an old runtime is required. Original input, verifier and cap are distinguished from the controlled retry. The local reproduced comparison moves to #8094. The previously strongest completed hosted #8089 remains κ `0.0039`, and selected #7000 is unchanged. No campaign Δκ.

## Next decisive test

Use the [frozen Round 420 reproducible source](../r420/RESTART.md). Reuse the byte-identical authenticated assembly and cold-install the candidate once. Recompute actual price before any result file is installed. The scientific price must match κ `0.003900857312000` and recurring log₂ C `85945126846` under the same premise and setup cap. Then run the signed directed owner-lifetime check at node 104493 with its Fourier-direction negative. Separate 60, 150 and 90-second caps. Stop on a source, price, phase, owner or restoration mismatch. These stages alone cannot certify a gain. Keep both typed widths, installed setup and complete independent candidate replay as open gates.

Credit floration's exact profile and shortcut word, Ali Romman's signed #8057 multiplier and inherited product fixture, SYLforge's K7 word, #8085's period proof, and Clear1nsight's #8089 peer control. OpenAI Codex assisted with the cold replay and independent comparison.
