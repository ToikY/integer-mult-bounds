# r=16 invoice for the power-of-two cubic repair

**Scoped conditional comparison; no new κ.** The selected frontier stays
`κ = 0.003125804`.

## Result

For the `r=16` schedule in `research/cubic-pow2-repair`, the displayed repair
is cheaper than the eager restoring shears if and only if

```text
Δ = Q_{35/16}^a + Q_{85/8}^a + Q_{-205/16}^a + 2 L_{-8} - 16 L_{-1} < 0.
```

The shared `16 Q_1^a + 16 L_1` prefix cancels. [PROOF.md](PROOF.md) expands the
`r=16` identity directly and states two exact price laws:

- Coefficient-blind prices `Q_c = q` and `L_c = ℓ` give `Δ = 3q - 14ℓ`. The
  repair wins exactly when `q/ℓ < 14/3`. Unit prices save `11ℓ`. The same law
  at the known arity `r=4` gives `Δ = ℓ > 0`, so the repair loses.
- Binary synthesis prices `q + σ(c) u` and `ℓ + σ(c) u` give
  `Δ = 3q + 14u - 14ℓ`. If `u ≥ ℓ` and `q > 0`, synthesis already consumes the
  eleven-event gap.

No pinned input assigns numbers to these symbols. A runtime win is not
claimed. A repair-only residual `E ≥ 0` outside the six symbols tightens a
negative gap to `Δ + E < 0`.

## Scope

Task `joint-query-controller`, refined. The open question asks for one arity
and a supplied backend. The arity is `r=16`. The pinned proofs supply the
symbols and state that no numerical backend is included, so the result is the
gap and the two laws rather than a caller bill. This does not reopen helper
injection, change the connector alphabet, or meet the family expansion gate.

## Evidence and reproduction

[verify.py](verify.py) uses exact rationals. It rechecks the identity at
several powers of two, replays the retained children and the five repair
events, rejects a perturbed weight and a dropped shear, evaluates both price
laws, and checks four pinned disclaimer sentences. [RESULT.json](RESULT.json)
is compared to that recomputation.

From the repository root, CPython 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/cubic-r16-repair-invoice --check-only
python3 -B scripts/research_package.py --package research/cubic-r16-repair-invoice
```

The registered replay runs normal and optimized interpreters, each with a
120-second timeout. `verify.py --write` regenerates the receipt. The package
metadata check and both registered commands were the intended validation.
No selected-frontier cold replay, Lean build, or physical caller was run.

## Open next questions

1. Does one actual caller price `Q_c` and `L_c` for this cubic-reader
   alphabet? Substitute those values into `Δ`. The blocker is that the pinned
   proofs explicitly withhold a numerical backend; inventing one would not
   answer the question.
2. For a price law that is neither coefficient-blind nor affine in the binary
   length `σ`, which `r=16` charges flip the sign? Start from one named
   coefficient routine and its addition count. The blocker is the missing
   routine, not the displayed schedule.

## Credit

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel acceptance is claimed.

The schedule and general identity are AAAmirinu's `research/cubic-pow2-repair`.
apoursh's PR6212 and PR6215, and Nick Petalas's PR6200, supply the price
symbols, the dyadic three-query bound, and the statement that query counts are
not a runtime proof. Sricharan Vagvala / theon199's PR1532, Adam Gall's PR1205
and Hanson Sun's PR1246 remain the quadratic and linear deferral lineage
credited by those sources.
