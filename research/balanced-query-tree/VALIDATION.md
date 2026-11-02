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

The committed-byte and POSIX execute-mode preflight passed for all 33
package and input files. The official export and its input inventory check
also passed. The tested scientific commit is
`76d2baa05d6e7701ab32a275f246ab485671f2f1`.

```sh
python3 scripts/check_research_commit.py --package research/balanced-query-tree --check-modes
python3 scripts/export_research_package.py export --package research/balanced-query-tree --ref HEAD --output /tmp/balanced-query-tree.tar.gz
python3 scripts/export_research_package.py check --check-inputs /tmp/balanced-query-tree.tar.gz
```

The exported package passed the full optimized Python 3.12.13 replay from
a separate directory. All source files and directories were read-only,
and PATH contained no Git. Hashes and modes of all 34 files, including the
export receipt, stayed unchanged. A separate copied export with one
changed byte in the source WORD.json.gz failed its SHA256 check before
that source code was imported.

```text
PASS_SEALED_READONLY_GIT_FREE_REPLAY files=34
PASS_CORRUPTED_SOURCE_REJECTED before import; exit=1
```

The final validation-record commit changes documentation only. All Python
files, the complete receipt, literal caller and source pins are unchanged
from the sealed scientific replay. Canonical main remained at the stated
base in the publication refresh. Its ancestry to this branch was checked.
Hosted CI, independent scientific acceptance and proof-kernel acceptance
are not claimed. The full-history ancestry mode is unavailable in this
shallow checkout. The uniform word and rounded multiplier are not
materialized.
