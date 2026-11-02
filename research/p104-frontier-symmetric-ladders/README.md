# Frontier price-null fibre: a distinct word at PR6167's exact invoice net, no new kappa

This package ships a second legal word whose complete price is identical to the merged
word of [PR6167](https://github.com/CrocSwap/integer-mult-bounds/pull/6167)
(conditional kappa 0.003128645, raw crossing between 0.00312865201590 and 0.00312865201591).
**No kappa is claimed.** The word differs from PR6167's in 13,713 of its 22,821 events and in
the endpoint frames of 17 helper registers. The frame table, the main endpoints, the
public and owned inventories and the 799 input columns are unchanged.

## What varies and what does not

The paid-call histogram and the helper-rank histogram both change (here the helpers
are credited at ranks 1..9 differently from PR6167), but they change together:
for every rank r, (helpers of rank r) minus (paid calls of rank r) is the same as in
PR6167. The root of the price equation depends on the word only through these nine
differences, so the raw crossing is identical, not just close. [RESULT.json](RESULT.json)
records both histograms.

Why the differences cannot move. Write a register's timeline as a chain of dimensions.
It pays one call per step, of the step's size, and a helper is also credited its
whole span. So a register's net contribution is its multiset of step sizes, minus its
span if it is a helper. Three exact consequences:

- A helper with a single step contributes nothing, whatever its two endpoints are.
  Such a helper can be re-spanned freely. 13 of these moved here.
- Re-ordering the stops of a chain with fixed endpoints keeps the step multiset. 19 chains do.
- A stop at s in a window (a, b) costs the two gaps (s-a) and (b-s). Moving one stop in a
  main chain and one in a helper chain can cancel exactly. Two registers do this here.

[verify.py](verify.py) classifies every changed register this way, checks the summed
change is zero, and then replays the word through the unmodified pinned chain.

## Size and symmetry of the family

Starting from PR6167, 59 words with exactly this price were found (58 distinct event
programs, 39 distinct per-register chain signatures). They are the optimal
frame assignments of PR6167's own events; one of them is a plain re-assignment of PR6167
with nothing inserted. Alternative Fano-plane ladder frames were inserted in each
of the 8 root intervals (415 single choices, all legal, 28 of 28 pairs and the 8-root
combination legal), but after frame assignment none of the inserted frames carries any event:
the ladders of all 8 roots keep PR6167's dimensions. The family is therefore the
price-null freedom above, not a family of different ladders. Its size was not enumerated.

The shipped word comes from the design that transports the ladders under an order-4
group acting freely on the two orbits of four roots. That design could be applied to
4 of the 8 roots; on the other four the residual forbids it, and after assignment the
transported frames carry no events. So the word is **not** symmetric under an order-4
group, and its register count is PR6167's (770 public registers).

## Evidence

```sh
python3.12 -I -O -B research/p104-frontier-symmetric-ladders/test_portability.py
python3.12 -I -B research/p104-frontier-symmetric-ladders/verify.py
python3.12 scripts/research_package.py --package research/p104-frontier-symmetric-ladders
```

These are author checks. Independent review is pending.

## Coordination and credit

Base word and checker: PR6167 by Ali Romman (OpenAI Codex assistance), over PR6144 and
PR6143 by DreamingOfClouds and PR5827. Precedent for a no-kappa package at unchanged price: PR6169.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. See [NOTICE](NOTICE).

## Open next questions

- Is the set of optimal frame assignments exactly the union of the three freedoms above?
- Can a re-spanned helper enable a stop drop elsewhere? The freedom is null for price, not for legality.
