# One moved G20 correction frame does not lower the paid moment

**Negative result. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).
Admitted BIT saving on this base is `17/5000`. The baseline binding check
returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. That command is not a
supplier replay.

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every one-to-three-contact A2 conjugation keeps its scalar endpoint when
exactly one correction is moved onto a different frame of the published
one-edge route table. Of the 28,149 frames that can host that meeting,
28,123 do not emit. The 26 that emit raise the paid-query moment on the
whole interval `(0, 1)`, by `H4` or by `5 H2 − 2 H4`. The argument is in
[PROOF.md](PROOF.md).

## Task and overlap

Base `626e936ce4d61f2584316914fc71baf96940c512`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card says to review the
#5679/#5708 chain and stop when a proposed cut does not improve the paid
moment. This package is the moved-frame clause those earlier screens left
open.

Ordered eligible list for session r69, rebuilt on 2026-11-01 against that
main. Open handoffs from the 19 October index (discussion comments
19030045, 19030047, 19030049, and 19030053) come first and are dropped: the
`(w, q, v_N)` consumer, the fresh T385 wrapper, the L546 six-tape bill, and
the single-ADD retiming class are already delivered by this account or
closed on main. Discussion #1166 through 2026-11-01 has no newer finite
handoff index. The newest posts are H25 serializer handoffs and completed
claims, not a replacement of the priority table. The priority table is the
revision-8 "Next bounded decisions" table. A row stays while that table
still states the decision. Catalogue cards not named by the table follow.
Dropped before the cut: work this account already delivered, results closed
on current main, questions covered by an open pull request, and topics
already on a fork `cursor/*` branch, including the port-0 G20 tariff and
the one-to-three-contact screen.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. **This package.** BIT (`bit-helper-contract`): one correction of a
   #5708 one-to-three-contact conjugation, moved off its contact frame.
3. New decoders and interfaces.
4. Supplier audit (`supplier-boundary-audit`).
5. All-size audit (`uniform-transfer-audit`).
6. Verification tooling (`replay-runtime`).
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

[#6290](https://github.com/CrocSwap/integer-mult-bounds/pull/6290) certified
the 765 contact-frame conjugations. [#6305](https://github.com/CrocSwap/integer-mult-bounds/pull/6305)
certified four or more contacts with corrections kept on the contact frame.
`research/g20-neutral-two-step-obstruction` allows catalogue routes after a
neutral first move and states that changed correction frames stay outside
its quantifier. The local overlap search finds the moved-frame question in
those three write-ups and does not find a replay of this one-move domain.

## Census

| Domain | Missing route | `H4` loss | `5 H2 − 2 H4` loss | Saving |
|---|---:|---:|---:|---:|
| One moved correction, length 1..3 | 28,123 | 2 | 24 | 0 |

The fixed-frame control reproduces 605 missing routes, 153 losses
`2H1 − H2`, one loss `H1 + H2 + H4`, and 6 neutral words. For `0 < t < 1`
and `x = 2^t`,

```text
5·2^t − 2·4^t = x(5 − 2x) > 0
```

because `1 < x < 2`. `4^t` is positive. The verifier rejects every other
shape, and on each interval that emits a moved frame it replays every
catalogue frame, not only the one-edge meeting set.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
finishes in about one minute here.

```sh
python3 -I -B research/g20-moved-correction-frame/verify.py
python3 -I -O -B research/g20-moved-correction-frame/verify.py
python3 -B scripts/research_package.py --package research/g20-moved-correction-frame --check-only
python3 -B scripts/research_package.py --package research/g20-moved-correction-frame
```

The direct verifier prints

```text
PASS_G20_MOVED_CORRECTION_FRAME candidates=765 moved_trials=28149 missing_edge=28123 emitted_h4=2 emitted_5h2_minus_2h4=24 savings=0 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier6030-verify`.

## Open next questions

1. Can two corrections in one interval, or one length-4 conjugation with a
   moved frame, lower the paid moment? #6305 already excludes length 4 and
   above when every correction stays on its contact frame. The first step is
   one two-move pair, or one length-4 interval with one moved frame, on this
   word and route table. No saving seed is supplied by the one-move census.
2. Do the six neutral one-step neighbors and the 645 common-frame expansions
   in the #5708 README have an executable rule? That sentence is still
   local-only. The first step is to recover the search or to show that the
   phrases name domains already certified. The published package does not
   contain the search.

## Credit

The emitted word, route table, A2 relation, and the local-only 765 count are
Ali Romman's `research/g20-conjugation-admission`, following Dugongue,
ai-nanachi, and the retained G20 lineage named there. The contact-frame
length-1..3 census is unpaidmoon's #6290. The length-4-and-above contact-frame
obstruction is Nick Petalas's #6305. The fixed-frame neutral two-step
obstruction is the package prepared for @CubeJerry. This package only moves
one correction frame inside the length-1..3 domain.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
