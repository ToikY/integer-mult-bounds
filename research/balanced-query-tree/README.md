# Conditional kappa 0.00314933 from a binary query tree

This changes the complete caller on the unchanged PR6167 P104 supplier.
The author-checked conditional saving is **0.00314933**, an increase of
**0.000020685** over PR6167's 0.003128645, about 0.661%. This is a modest
improvement. The selected frontier
stays unchanged.

The new four-field module combines two query suppliers, one paid thin
query and two whole idle calls. It returns a query supplier and two
independent Gaussian outputs. A binary tree of these modules replaces the
paired path. Root subtree sizes 4, 7 and 8 give 19 full calls, 16 thin queries and
34 main fields per port. The new complete bill contains 14214 productive
fields and 70523 paid calls, with rank-mass surplus 808. The exact raw
crossing is in `(0.00314934401301, 0.00314934401302)`.

Start with [PROOF.md](PROOF.md), the literal
[CONTROLLER.json](CONTROLLER.json), the exact [RESULT.json](RESULT.json),
and [SOURCES.json](SOURCES.json). The four-field checker is separate from
the full caller generator. The full source word, transpose, native phases,
new caller phases, both price engines, compiler and outer ledger are part
of the registered replay. [VALIDATION.md](VALIDATION.md) states the checks
that actually ran.

The claim retains five assumptions: native all-column implementation,
owned erasure, uniform compiler, precision/tape cost and analytic recovery.
The enormous uniform word and rounded multiplier are not materialized.
Independent scientific acceptance and proof-kernel verification are not
claimed. No global optimum or practical runtime speedup is claimed.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/balanced-query-tree --check-only
python3.12 -B scripts/research_package.py --package research/balanced-query-tree
```

The scientific marker is:

```text
PASS_BALANCED_QUERY_TREE_KAPPA_00314933
```

The normal and optimized commands compare the exact retained receipt and
do not write source files. `--write-result` is an explicit authoring option.
Controls reject a missing paid idle, thin query, central translation,
wrong query orientation, the source completion cutoff and insufficient BIT
saving. Every external input is checked by SHA256 and Git blob hash before
its code is imported.

## Scope and credit

Base: canonical main 626e936ce4d61f2584316914fc71baf96940c512, priority 8.
The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19340371)
records the caller work and the excluded active local-word scopes.
The initial stage-mask screen repeated an earlier stronger result and is
not a new contribution. The later tree construction changes the caller.

Cinna Davis @1337isnot1337 supplies the query-thinned path and thin-query
interface in the [PR4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)
lineage. Ali Romman @aliromman supplies the all-forward binding in
[PR5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544) and the
unchanged source in [PR6167](https://github.com/CrocSwap/integer-mult-bounds/pull/6167).
DreamingOfClouds @DreamingOfClouds supplies the immediate local-word
lineage in [PR6144](https://github.com/CrocSwap/integer-mult-bounds/pull/6144).
All earlier native, helper, recursion, compiler, BIT
and outer authors retain their source credit in [NOTICE](NOTICE) and the
18 authenticated predecessor files. The new contribution is the query
extension, its tree composition and the complete conditional calculation.
Prepared for Ali Romman with substantial OpenAI Codex assistance. No
subagents. Apache-2.0.

## Open next questions

1. Does independent scientific review confirm the four-field extension,
   its paid complement and the complete conditional calculation? Start
   with the separate module checker and literal Laurent word. Author
   checks and CI do not discharge this review obligation.
2. Can a changed query-extension interface give a larger complete gain?
   First state its independent inputs and full paid idle bill. The present
   tree is one construction and is not a global optimum.
