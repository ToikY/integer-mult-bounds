# Four native helper input lifts

This package gives conditional **kappa 0.003129111**, up from PR6167's
**0.003128645**. The increase is **0.000000466**, or about **0.0149%**.
This is a small gain. It does not meet the donor's request for a large gain.

Four existing helper inputs start at later native frames. Exact scalar
corrections carry their correlated input directions to the source word.
An inverse helper basis at the output restores every independent input.
The four reduced productive targets are charged. The word still has
770 public inputs, 29 owned labels, 32 owned lifetimes and peak ownership 13.

The exact source is the compressed PR6167 word in
[PR6314](https://github.com/CrocSwap/integer-mult-bounds/pull/6314), head
`36533d4d1b4e2dd8672427461b12de3001b85810`. PR6314 changes scalar cost but
does not change kappa. This package starts from canonical main
`626e936ce4d61f2584316914fc71baf96940c512`, priority revision 8.
[SOURCES.json](SOURCES.json) pins all five live inputs. The source reader
authenticates them before it imports any predecessor code.

## Evidence and limits

[PROOF.md](PROOF.md) gives the basis identity, each native edit, the complete
invoice and the inherited assumptions. [construct.py](construct.py) regenerates
all 17,452 events from the pinned source. [RESULT.json](RESULT.json) records
the exact scalar replay, a separate dense transpose, all 2,930 native maps
with absolute phases, the physical caller, two rational price engines,
compiler bounds and 54 strict plus four functional outer predicates.

The raw crossing lies strictly in
`(0.00312911821812, 0.00312911821813)`. The previous complete profile fails
at the new claimed kappa. Thus the gain comes from the changed invoice.
It does not come from a smaller safety margin or omitted helper credit.

All five framework assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. The large uniform word
and rounded integer multiplier are not materialized. These are author checks;
they do not establish independent acceptance or practical speed. The selected
frontier remains unchanged.

Coordination is in the
[canonical Discussion claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19205459).
The latest direct checks distinguish this input-boundary change from
Discussion5600's fixed-boundary public-prefix rewrite and Discussion5593's
tree caller. Protected contact events and frames 1091/1092 remain fixed.
The overlap cache had complete remote pagination; sparse local notes and
unpublished work remain coverage limits.

## Reproduce

Use Python 3.12 and the standard library. From the repository root:

```sh
python3.12 -W error -B research/p104-native-input-lifting/verify.py
python3.12 -O -W error -B research/p104-native-input-lifting/verify.py
python3.12 scripts/research_package.py --package research/p104-native-input-lifting --check-only
python3.12 scripts/research_package.py --package research/p104-native-input-lifting
```

The final status is `PASS_P104_NATIVE_INPUT_LIFTING_KAPPA_003129111`.
The direct verifier creates a fresh bytecode-cache namespace before it imports
package or source modules. It writes no package files unless `--write` is
specified. It checks the decompressed word bytes, so gzip header differences
do not affect the certificate. `--build-only` checks the construction, exact
scalar endpoint, ownership and scalar controls; it does not check the full claim.

An official export needs this package and the five inputs in
[VERIFY.json](VERIFY.json). The direct verifier also works without Git or
network access. The registered runner needs Git for provenance checks.

## Open next questions

Can several new correlated directions share one native input lift? Start with
one exact helper group and its departure map, then emit every correction and
charge the complete bill. The present finite searches do not prove optimality.

Can a helper output basis support an extra native exit reduction? A bounded
output-direction screen found no accepted word. A new test needs a different
explicit basis or correction, an arbitrary-input proof and full pricing.
Check the live Discussion claims before work. [TASK.json](TASK.json) gives
the first steps and missing obligations for both questions.

## Credit

New work: Ali Romman with substantial OpenAI Codex assistance. No subagents.
The same assistant made the construction and the author checks. Apache-2.0.

The direct word is by DreamingOfClouds, with Claude Opus 5.5 assistance, in
PR6314. It retains Ali Romman's PR6167 and the PR6144/6143 source work.
The unchanged checker and price chain retain Cinna Davis, David Arias,
Gareth Davidson, Jacob Alan Sussman, zxv, Cao Yifan, flyingviper,
Pierre-Loic Doulcet, Joel Pulikkan, Scratch-net and all earlier source credit.
[NOTICE](NOTICE) retains the source notice. No predecessor construction or
general basis identity is claimed as new.
