# Verified integral-fringe improvement

**Round 430 · VERIFIED IMPROVEMENT**

The exact signed [campaign comparator #8095](https://github.com/CrocSwap/integer-mult-bounds/pull/8095) at `490cd470f86157d29c9d3f8da9f96d6e2c3c04e5` is locally and [hosted](../r426/REPLAY.md) reproduced at κ 0.003900857312000. This round independently reproduces κ **0.003900857312674** under the same five premises at [#8096](https://github.com/CrocSwap/integer-mult-bounds/pull/8096), exact head `40a82e7974cabfc8509363ea6ad8dd269e446098`.

| Comparison | Exact difference | Relative gain |
| --- | ---: | ---: |
| #8095, strongest reproduced before this result | 0.000000000000674 | +0.0000000172782531% |
| #8094, latest relevant external peer at κ 0.003900857267786 | 0.000000000044888 | +0.000001150721416% |

Round 430 adds the smaller Gaussian fringe bound at the exact same signed word, activated heights, and source premises. The weighted fringe factor is 515/516 and the booked debit is 1039699/2^23. The previous Gaussian debit and the next displayed rate are rejected by the directed controls. Ordinary pricing binds. The charged profile retains log₂ C 85945126846, activation exponent 268644472 and fixed setup below 2^228. External peer headline movement is zero at submission. The maintainer-selected #7000 remains separate.

Use Git, CPython 3.12 with assertions, and 8 GiB free on both volumes. From a clean checkout of the exact PR head:

```sh
scratch="$(mktemp -d /tmp/k7-integral-fringe.XXXXXX)"
TMPDIR="$scratch" python3.12 -IB scripts/research_package.py --package research/p104-k7-integral-fringe
```

The clean independent local registered suite passed all seven modes in 427.02 seconds. The onboarding suite ran 760 tests with 31 skips. Metadata, committed bytes and source history, changed-package planning, historical prerequisite and clean Git diff all passed. [Full local output](LOCAL-REGISTERED.log) · [Exact checked head and tree](HEAD-TREE.log) · [Timing and exits](LOCAL-EXITS.log) · [Measured independent staged replay](../r429/REPLAY.md). The initial [hosted #8096 run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45297786148) is tracked separately.

Credit #8083 and Round 409 for the prior stronger lattice proof, floration for #8094's exact stack, Ali Romman for the #8057 signed caller and #8042 quotient bound, SYLforge for K7, and #8095 for the precise comparator and verification fixtures. OpenAI Codex assisted proof, assembly and independent checking.
