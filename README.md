# Frozen BIT word and supplier checks, Rounds 321–329

Round 329 independently reproduced a conditional increase of 0.00000000000010 over #7863 on its original 451-factor template. Round 327 excluded the second 64-pair batch, and Round 328 isolated a promising finite cutoff with an open physical transfer. [Results, replay command and credit](ROUNDS-327-329.md)


**Rounds 324–326 closed with no verified κ gain.** All six primary and independent receipts reproduce. The packet-724 helper split is excluded at its funded midpoint. The two-chart price screen reached its 64-pair cap. An exact restart is available for the remaining 627 pairs. [Results, source credits, proof and restart](ROUNDS-324-326.md)

```sh
python3.12 -IB replay_324_326.py ./work
```

**No verified κ gain.** The submissions use the 680-owner binary word from #7786. The strongest locally reproduced complete peer application in this checkpoint is #7863 at b3e4412fe01f07dc58305616fabf96345f49a781, conditional κ = 0.00387992804346. Its finite schedule improves the earlier #7830 headline by exactly 0.00000000000790 on the same signed raw word. The 451-factor, seven-stage compiler, cover, stock, nested-seed and precision obligations remain conditional. The fixed 480-factor, six-stage realization does not by itself establish them. Canonical main e54523517d0f03e58352e647c403a5af3e525a57 selects #7000 at 0.00363005817. [Peer application](https://github.com/CrocSwap/integer-mult-bounds/pull/7863) · [Independent peer replay](https://github.com/CrocSwap/integer-mult-bounds/pull/7973) · [Local replay instructions](benchmark/HANDOFF.md)

## Reproduce

Run these from the handoff checkout with CPython 3.12. The first command checks the primary and independent scientific receipts from all three rounds, fetching pinned public sources when needed. The second separately checks both archived peer packages with a fresh compiler and expanded consumer audit. Give it a new output directory.

```sh
python3.12 -IB replay.py ./research-work
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3.12 -IB benchmark/reproduce.py ./benchmark-work
```

| Round | Decisive question | Outcome |
|---|---|---|
| 321 | Can an earlier paid arrival at the receiver let two new scalars replace that arrival and two same-route deliveries? | All 115,156 eligible triples leave a rank-three public defect with other equations frozen. The named three-delivery control produced ranks zero, one, two and three as the deletions accumulated. |
| 322 | Can a helper split at one existing midpoint using separate source and return encodings, with zero added paid traffic? | All 2,560 nested cases, including both orientations and the main coordinates, failed even with whole-clock access. The remaining 55,952 cases failed nesting. |
| 323 | Can two charts independently store the required helper parity before a common cut, then inject it into their future sends to exchange two productive destinations? | Among 3,112 strictly improving equal-mass transpositions, 24 had exactly one eligible forward reader and 3,088 had none. None had an adjoint reader. All 3,958,464 memberships were checked. No pair reached the common-cut or future-injection test. The same counts give a separating-input proof for any two local linear maps prepared independently on the frozen stock. [Proof and boundary](round323/HANDOFF.md) |

Each declared scope exhausted. None reached a literal candidate build or a new all-size bound. Original discovery and independent runner times appear in the receipts. The Round 323 all-clock test took 0.249 s and its independent replay 0.427 s. Active design time overlapped with research, peer comparison and publication and was not separately measured. The all-clock test saved unnecessary clock searches, but a matched timing trial has not established a change to the default solver.

## Publication and overlap

The one-chart transposition result was first posted to #7111 and later registered as #8022 at 8bd02daca9f4e7a227f6c552905930eed9498655. The closest peer proofs change paid senders (#8002), study 679 owners while keeping productive grades fixed (#7970), or rebuild terminal decoders after paid omissions (#7985). The hosted planner and both replay jobs passed. The scientific log records 3,112 pairs, 636 charts, 680 public columns in each direction, and 3,554 dirty retirements in each direction. [Full comparison](OVERLAP.md) · [#8022](https://github.com/CrocSwap/integer-mult-bounds/pull/8022) · [Scientific job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/44908211484/job/136859179717)

Round 320's 758 same-route pairs that omit no protected bridge are contained in #7978's broader two-omission, one-replacement domain. Its one further pair comprises deliveries 3544 and 3553 on 509→1. The latter is the protected bridge. The old public handoff retains the literal defect for that pair. Round 321 instead measures whether two independent corrections can repair a three-delivery loss. [#7978](https://github.com/CrocSwap/integer-mult-bounds/pull/7978) · [Round 320 handoff](https://github.com/ToikY/integer-mult-bounds/tree/43a72a325f98a2c9bf65f0e92f7e644429b9b3ef/round320)

## Decision at the end of Round 323

Start with the listed forward pair (238, 672) whose parity is readable at chart 8. Test whether an existing paid send from that chart can make a downstream local XOR, zero on every original public input, carry this parity. The downstream correction must preserve the original paid carrier and both returns. For each proposed clock, compare the forced pulse column and all retained outputs before pricing or building. This changes the next round by targeting communication that creates a new downstream observation because no two charts begin with the required parity.

Clear1nsight supplied #7786, #7830, #7863, #7973 and the literal tape engine. Ali Romman supplied #7776's graph extraction and endpoint checks. The paired caller reuses the #6834/#6980/#7001 lineage. #7781 supplies the predecessor birth and #8022 supplies the exact transposition roster. DreamingOfClouds supplied the #7852 toolkit. OpenAI Codex materially assisted the research and verification.
