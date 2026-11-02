# The selected pricing rejects the PR5708 BIT component as admitted BIT

**Negative result. No new κ.** The selected conditional exponent stays
**781451/250000000** (`0.003125804`).

PR5708's ordinary component

    C = 3507719059749/1000000000000000

cannot occupy the admitted `bit_saving` input of the selected PR6030 pricing.
The pricing requires

    atom > ordinary > admitted > TESTED

with ordinary recomputed from the thinned controller as
`8590884599/2500000000000`. That ordinary value is strictly below C, so the
gate fails. The outer ledger is not the cause: its only `bit_saving` check is
`bit_saving − a`, and every pinned check stays positive at `bit_saving = C`.
The complex uniform saving `10940329/3500000000` remains below both `17/5000`
and C, so accepting C as a ledger input would not raise κ.

C does lie strictly between the stock atom `1/250` and the retained admitted
BIT `17/5000`. The cover that would make the ordinary formula equal C is
`3507565220149/996000000000000`, not the pinned `69/20000`.

## Task and overlap

Base commit `626e936ce4d61f2584316914fc71baf96940c512` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. Catalogue card
`bit-helper-contract`. Scope status: **refined**.

The card asks whether a changed G20 path improves the complete BIT moment.
This package does not change the PR5708 word. It answers open question 3 of
`research/g20-conjugation-admission`: whether a stronger Gaussian caller can
consume that BIT component. The caller tested here is the selected pricing
assembly, not a new Gaussian construction.

Session r72, item 5 of the ordered eligible list. The 19 October handoffs
(discussion comments 19030045, 19030047, 19030049, and 19030053) are closed.
The five newer H25 contributor handoffs are open pull requests and are
excluded. The remaining list is the revision-8 first-mention open questions
of #5679, #5708, #5718, #5611, and #5615, after dropping delivered items:

1. #5679: a different physical role for the early output. The common-frame
   part is answered by `research/g20-free-carrier-split-obstruction`; paid
   frame changes remain open.
2. #5679: another paid-query removal on the changed split word.
3. #5679: a stronger Gaussian caller for that completed BIT component.
4. #5708: a noncoordinate public input contract. The longer-identity question
   that originally sat here is delivered by #6290 and merged #6305.
5. #5708: a stronger Gaussian caller for this BIT component. This package.
6. #5718: an independent check of the two boundary bases and early cleanup.
7. #5718: another profitable pair of boundary functionals.
8. #5718: one retained framework assumption.
9. #5615: whether a current source cut gains a channel under the full dyadic
   criterion. #5611's physical-target question is delivered by #6297.

`research/g20-global-caller-audit` audits the PR5708 caller and leaves the
outer-assembly question open. `research/selected-ordinary-reseed-contract`
reseeds the ordinary levels from the selected backend. Neither compares C
with the selected stock gate. `research/outer-ledger-kappa-region` proves the
#5599 ledger region; this package evaluates the #6030 parameter shape at C.

## Validation

Environment: Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/g20-component-stock-gate --check-only
python3 -B scripts/research_package.py --package research/g20-component-stock-gate
```

Both registered commands pass, including the optimized command. The verifier
prints `PASS_G20_COMPONENT_STOCK_GATE`. The launcher prints
`PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `negative-result`.

The verifier recomputes ordinary from atom, after_cover, and ε, and matches
the selected claim. It loads the pinned ledger and compares `bit_saving =
17/5000` with `bit_saving = C`. Strict checks other than
`actual_bit_above_effective` agree, and that one check increases by
`C − 17/5000`. Functional checks, including pricing's `β(1−atom)`, agree.
Failure controls: `bit_saving = 0.0027` fails a strict check; `bit_saving = a`
is not strictly positive; dropping ε or using `before_cover` changes ordinary;
the implied cover is not `69/20000`.

Not run: the PR5708 caller, native maps, compiler closure, tape movement,
analytic recovery, and any edit of the thinned controller. Those unknown
costs are not zero. The five framework assumptions remain.

## Credit

Ali Romman's PR #5708 supplies the component and the open question. The
selected PR #6030 pricing retains DreamingOfClouds, Ali Romman, and the
credited P104 lineage. The thinned-controller BIT numbers and zxv's PR #4359
ledger are used as pinned inputs, not re-proved. `research/g20-global-caller-audit`
and `research/selected-ordinary-reseed-contract` are the neighbouring
readings. Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0. No independent human or formal-kernel acceptance is claimed.

## Open next questions

The structured questions are in `TASK.json`.

1. Can a thinned-controller cover of `3507565220149/996000000000000` replace
   `69/20000` and still meet the odd-prime stock rule? First step: check that
   rule and the 48-field owned reserve against this cover. A larger admitted
   BIT under that cover would still sit above the complex uniform saving.
2. Does a successor outer ledger read `bit_saving` anywhere except
   `bit_saving − a`? First step: diff the ledger called by the selected
   pricing and repeat the two-value comparison.
