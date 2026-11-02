# Validation record

The full authoring replay passed on Python 3.12.13:

```sh
python3.12 -I -B research/balanced-query-tree/verify.py --write-result
```

It checked the four-field Laurent identity, all 1156 caller entries, all
638401 source coefficients through a separate transpose, native maps and
absolute phases, 7904 caller contacts, every main and idle target, the full
invoice, two rational price engines, paid completion, compiler and all 58
outer predicates. Caller failure controls and the old-cutoff/low-BIT
controls were rejected.

An earlier complete run passed the native checks, then stopped at the
interval engine's exponential-domain guard. The final calculation squares
an outward interval for the half exponent. It does not change or bypass
the retained engine's domain check.

Package metadata and source pins passed. Both registered Python 3.12.13
modes (normal and optimized) passed. The package runner confirmed that
neither mode changed the package or declared input files:

```sh
python3.12 -B scripts/research_package.py --package research/balanced-query-tree
```

```text
PASS_BALANCED_QUERY_TREE_KAPPA_00314933
PASS_REGISTERED_RESEARCH_PACKAGE research/balanced-query-tree outcome=completed
```

Committed-byte preflight and sealed export replay are pending.
Hosted CI, independent scientific acceptance and proof-kernel acceptance
are not claimed. The full-history ancestry mode is unavailable in this
shallow checkout. The uniform word and rounded multiplier are not
materialized.
