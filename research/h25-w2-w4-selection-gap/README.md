# h25-w2-w4-selection-gap

**No new κ.** The selected record stays `781451/250000000`. This package does not adopt the PR6335 drafts, seal a runtime, or admit W5.

## Scope and evidence

Original card: `supplier-boundary-audit`. Scope status: **refined**. Discussion
[#1166 comment 19330344](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19330344)
asks for a review of the W2/W4 source-selection and producer interfaces in
`ACCEPTED-DRAFT-SOURCE-IDENTITIES-v1.json` and of dependency N1 in
`NEXT-DEPENDENCIES-v1.json`. That is one uncovered candidate interface. It is
not a transfer of the #5719 causal certificate onto #5718, and it is not a
#5717 owned-lifetime replay.

Audited head: PR [#6335](https://github.com/CrocSwap/integer-mult-bounds/pull/6335)
`d34b84f1e1d9fb4bdcf26eda8817c3603fea3051`. Package base:
`626e936ce4d61f2584316914fc71baf96940c512`. The PR head is not an ancestor of
that base. `pinned/` holds unchanged byte copies of the five inputs. The
verifier hashes them and, when that commit is present in the local Git
database, also compares them with `git show`.

### What the records already agree on

The identity record selects exactly two drafts:

| Role | Path suffix | SHA-256 | Bytes |
|---|---|---|---:|
| W2 target | `bounded_serialization.py` | `fdeeb791c6cb0c03a5ab15903d51c3eb4cc5ff2a945c50d7f550acfe11376f3d` | 23844 |
| W4 draft | `parent_readback_v3_DRAFT_v2.py` | `6fc0577690c3865c1d67b4c288f860e5c81c8aebb3cffab18ab8a2269b12a572` | 29105 |

`source_adopted` is false. N1 ends with "No source adoption has occurred."
`new_launcher_admission_receipt_producers` is "Not implemented/integrated in
this source round; required before W5." N2 therefore stays open. The static
AST import lists published on those two profiles match a fresh parse.

### The N1 gap

N1 requires a reclosed W2/W4 source and control graph: the F05 hash-and-line
trace if F05 is selected, the W4 `decimal`/`_decimal` Context/signals/`re`
dependencies, all original controls, and the exact authentic inputs.

The published selection does not close that sentence.

- **F05 is undecided and its control is unselected.** The identity object has
  no F05 selection bit. Its first required update still says "if F05 selected."
  Line 490 of the selected W2 file is `info["status"] = "FAILED_EVIDENCE_RETAINED"`.
  The trace that targets that line is `PRIMARY_STATUS_LINE = 490` and
  `sys.settrace` in `new_failure_controls.py`
  (`742f1de31551d43c2665ad6166577c104a0acc746b3503cc60c5f11798c9a24d`). That
  file's `TARGET_SHA256` is the W2 hash above, and its imports include `sys`.
  The selected W2 profile's direct imports do not include `sys`. The control
  path is not one of the two selected sources.
- **The decimal extension and trap names are not in the import field.** The W4
  draft imports `Context`, `localcontext`, and the nine `Context` traps
  `Clamped`, `DivisionByZero`, `FloatOperation`, `Inexact`, `InvalidOperation`,
  `Overflow`, `Rounded`, `Subnormal`, and `Underflow`. The identity field lists
  the modules `decimal` and `re`, not `_decimal` and not those names.
- **Controls and authentic inputs are outside the two profiles.** N1 names
  them. The identity record does not.

`verify.py` checks these facts and four mutants: an added `sys` import, a true
`source_adopted` flag, a rewritten N1 sentence, and `PRIMARY_STATUS_LINE = 491`.
Each mutant flips the fact that makes the published gap true. The drafts are
not imported or executed.

Orientation only: `python3 -B scripts/research_selected_baseline.py` printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with selected κ `781451/250000000`.
That command is not a supplier replay. The priorities prose still names the
earlier #5599 figure; this package does not edit that prose or the selected
record.

## Reproduce

From the repository root, CPython 3.12 standard library (the same checks pass
on the interpreter used to develop this package):

```sh
python3 -B research/h25-w2-w4-selection-gap/verify.py
python3 -O -B research/h25-w2-w4-selection-gap/verify.py
python3 scripts/research_package.py --package research/h25-w2-w4-selection-gap --check-only
```

Expected first line: `PASS_H25_W2_W4_SELECTION_GAP`, then `n1_closed=false`.
No Lean, Docker, serializer, or selected-frontier replay was run.

## Credit

The W2 and W4 drafts, the identity record, and N1 are Chris R / Clear1nsight,
PR6335, with the retained Douglas R. Colkitt / CrocSwap circuit and verification
lineage cited there. The pinned copies are unchanged. Apache-2.0.

Prepared by unpaidmoon with substantial Cursor Grok assistance.

## Open next questions

- Is F05 selected? If it is, the identity has to gain `new_failure_controls.py`,
  the `sys.settrace` admission, and the existing target hash before any control
  run. If it is not, N1's conditional trace clause should be closed by an
  explicit reject bit. Blocked by a separate integration assignment; this audit
  does not execute the control.
- What `_decimal` extension and `Context` trap closure does the intended
  interpreter actually load for the W4 draft? The import field does not record
  them. Blocked by N3's separately admitted provider acquisition. Source
  freezing is not a runtime seal.
- Which trusted request and receipt producers satisfy N2? None are selected,
  and W5 stays unadmitted.
