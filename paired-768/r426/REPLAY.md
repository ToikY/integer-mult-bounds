# Round 426 conditional gain and publication

**VERIFIED IMPROVEMENT** under the same five signed premises.

| Quantity | Exact result |
| --- | --- |
| Prior strongest reproduced and latest peer | [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094), `c20a08dc0a79a989e3515068560d5da371c0a2a8`, κ 0.003900857267786 |
| First reproduced publication | [#8095](https://github.com/CrocSwap/integer-mult-bounds/pull/8095), `826fed2c3382254beea1cba845938fca02fd2dfa`, κ 0.003900857312000 |
| Exact campaign gain | 0.000000000044214, or 22107/500000000000000 |
| Relative gain | +0.000001133443163% rounded, exact 2210700/1950428633893 percent |
| New peer κ movement | Zero at publication refresh |
| Resource profile | Recurring log₂ C 85945126846, activation exponent 268644472, maximum native height 134217727, fixed setup below 2^228 |

The narrower same-stage child-volume bound funds tariff 2391/1024 and debit 1414404/2^20. The existing 257/256 period lemma at #8094's resource point funds Gaussian debit 1039701/2^23. The signed caller, tape and precision premises are shared. Gaussian pricing binds. The structural setup correction charges the added 2^40 allowance in both lookup and aggregate arithmetic. See the scoped proof in the PR.

From a clean checkout of the current exact PR head, use CPython 3.12 with assertions enabled, Git, and the 8 GiB reserve on the checkout and temporary volumes.

```sh
scratch="$(mktemp -d /tmp/k7-sharper-period.XXXXXX)"
TMPDIR="$scratch" python3.12 -IB scripts/research_package.py --package research/p104-k7-sharper-period
```

The original staged checks and verifier repair are documented in [Round 425](../r425/REPLAY.md). The first complete registered run passed in 422.16 seconds. Review then corrected one proof sentence recording those passed scopes. The final publication head changed only that proof sentence and completed a new clean registered replay in 418.24 seconds. [Exact head and tree](HEAD-TREE.log) · [Local scientific output](LOCAL-REGISTERED.log) · [Exact exits](LOCAL-EXITS.log) · [Committed bytes and source](LOCAL-COMMITTED.log) · [Onboarding](LOCAL-ONBOARDING.log) · [Historical prerequisite](LOCAL-HISTORICAL.log).

## Hosted cap and exact repair

The first hosted [candidate job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45291039331/job/138101423169) passed all six core scopes plus the dirty relay and two-column typed scope. The four-column typed probe reached its 100-second inner cap. The setup census after it was skipped in that run. The two-column hosted probe completed about 62 seconds after the physical receipt, compared to about 37 seconds in local verification.

The repair at `490cd470f86157d29c9d3f8da9f96d6e2c3c04e5` changes only the four-column time allowance to 160 seconds and reauthenticates the verifier. Both typed fixtures, every assertion, the 285-second group cap, the 1,200-second registered total, and all scientific inputs stay fixed. The exact repaired head passed the fresh local registered replay in 405.13 seconds, plus onboarding, committed bytes and source history and the selected historical prerequisite. [Repair head and tree](repair/HEAD-TREE.log) · [Exact repaired local output](repair/LOCAL-REGISTERED.log) · [Hosted tree readback](repair/HOSTED-TREE.json).

## Next research after the improvement

[Round 427](../r427/REPLAY.md) evaluates a separate integer matched-fringe bound. [Round 428](../r428/REPLAY.md) verifies its literal price and signed seam. Any additional improvement requires its own exact full replay.

Credit floration's #8094 word and profile, Ali Romman's #8042 bound and #8057 signed stack, SYLforge's K7 construction, #8076/#8082's ordinary accounting, #8085/#8087's period proof, Clear1nsight's #8089 control, and Jerry Chen's separately pinned #7257 CI repair. OpenAI Codex materially assisted.

## Hosted exact-head verdict

[Run 45294927135](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45294927135) passed all three checks. [Onboarding](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45294927135/job/138112789178), the [historical prerequisite](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45294927135/job/138114765990), and the [actual candidate scientific replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45294927135/job/138114766017) all concluded success. The recorded merge commit was `fd65d181851b25b853b6073ba82cd7d71758d915` with the exact locally tested head tree `e1cf39a363705bc9c03f1c7b8fa5b8419e15caa2`. The four-column receipt followed the two-column receipt by about 106 seconds. The installed census directory SHA-256 matches the local digest. The job emitted the full registered package pass marker at 00:26:40 UTC. [Actual hosted markers](repair/HOSTED-SCIENCE.log) · [Exact PR rollup](repair/PR-CHECKS.json).
