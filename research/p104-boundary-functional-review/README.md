# Independent review of the #5718 boundary functionals

**Scoped verification. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).

On the pinned PR5718 word, the input nuisance `k` and the output nuisance
`g = k - c` are different covectors. The three early cleanup operations
restore every scalar endpoint only in the published order. Moving
`743 -= 146/2` ahead of the 126 and 188 restorations fails exactly those
two rows. [PROOF.md](PROOF.md) records the identities. The checker replays
the pinned source and final words and does not import the predecessor
constructor.

## Task and overlap

Base commit `626e936ce4d61f2584316914fc71baf96940c512` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. Catalogue card
`p104-side-correction`. Scope status: **refined**.

The card asks whether a legal helper split improves the complete invoice.
This package does not search for another split. It answers the first open
question of `research/p104-two-boundary-helper-split`: a separate reviewer
checks the two boundary functionals and the early cleanup order.

Session selection, in first-mention order of `open_questions` from the
`TASK.json` files of packages named by PR number in revision-8
`docs/research/current-priorities.md`, skipping #5599 because that PR is
the selected frontier rather than an open assignment. Questions answered
by a later merged package are dropped:

1. #5679: Can a cut use a different physical role for the early output?
2. #5679: Can the changed split word enable another paid-query removal?
3. #5679: Can a stronger Gaussian caller consume the completed BIT component?
4. #5708: Can noncoordinate public input contracts give another split?
5. #5708: Can a stronger Gaussian caller consume this BIT component?
6. #5718: Can a separate reviewer verify the different input/output bases and early cleanup order?
7. #5718: Do other pairs of legal boundary functionals support profitable helper splits?
8. #5718: Can the retained framework assumptions be resolved?
9. #5615: Does a current source cut gain a channel under the full dyadic criterion?
10. #5717: Can the same explicit-inventory audit be rebound to a successor with a changed caller or helper ABI?

Item 6 is this package. Dropped before this list: #5708's longer-identity
question, answered for one-to-three contacts by #6290 and for four or more
fixed-frame contacts by #6305, and #5611's physical-target question,
answered by #6297. The 19 October handoff index in discussion #1166 is
already closed. The later H25 serializer handoffs are open engineering
lanes on their own draft PRs and are not this finite scalar question.

The phrase "early cleanup order" occurs only in the #5718 README and task
file. #5844 checks a different claim: the #5719 causal certificate does not
transfer onto this word.

## Validation

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-boundary-functional-review --check-only
python3 -I -B research/p104-boundary-functional-review/verify.py
python3 -I -O -B research/p104-boundary-functional-review/verify.py
python3 -B scripts/research_package.py --package research/p104-boundary-functional-review
```

The direct runs and the registered replay print
`PASS_P104_BOUNDARY_FUNCTIONALS_DIFFER_AND_CLEANUP_ORDER` with term counts
`carrier=88 input=87 output=118 partner=171`, then
`PASS_REGISTERED_RESEARCH_PACKAGE`.

Controls: the published order has no endpoint failure; inverse-first cleanup
fails exactly rows 126 and 188; the opposite 146 sign fails only row 743;
the recorded witness carrier, cleanup triple and 118-term output functional
must match the replay. A zero partner covector would make the two
functionals equal and fail the difference check.

Not run: the #5718 native maps, physical caller, pricing adapter, ordinary
admission, Lean, Docker, and `scripts/research_selected_baseline.py` beyond
reading the selected record.

## Credit

The word, witness and source archive are flyingviper's
`research/p104-two-boundary-helper-split`, following Ali Romman's PR5713
and Joel Pulikkan / GamingPuzzled's PR5684. No predecessor file is modified.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Open next questions

1. Do other legal boundary pairs at another coframed cut improve the signed
   bill? The first step is one new cut whose input and output functionals
   are written down before any search. This review does not supply that cut.
2. Does the scalar order obstruction still fail after native maps and the
   physical caller? The first step is to replay the predecessor caller on
   the three-instruction swap alone. Those engines were not run here.
