# The r=16 cubic-repair invoice against eager restoration

This note answers the first open question of
`research/cubic-pow2-repair`: compare that package's displayed repair with
`r L_-1` at one power-of-two arity. The arity is `r=16`, the first power of
two not already attained by the pinned `r=4` identity or by the pure-entry-B
family. No new repair schedule is claimed. The schedule and the polynomial
identity are AAAmirinu's, rechecked here at `r=16` by direct expansion.

## Pinned prices

Nick Petalas's PR6200, as retained in
`research/dyadic-cubic-repair/sources/pr6200-PROOF.md`, prices a complete
weighted cube by `Q_c` and a complete source shear `a += c*b` by `L_c`.
A query price includes its coefficient, source access, private restoration
and return. Zero operations are omitted. Both the eager program and the
deferred program contain the same `r` original cubes and the same `r`
forward shears, with bill

```text
r Q_1^a + r L_1.
```

Those terms cancel in the comparison. The eager program then appends `r`
restoring shears `a -= b`, costing `r L_-1`. The deferred program instead
appends the five displayed repair events. For `r=16` those events and
weights, from `research/cubic-pow2-repair/PROOF.md`, are

```text
c1 = 35/16,  c2 = 85/8,  c0 = -205/16,
y -= c1 a^3,  a -= 8 b,  y -= c2 a^3,  a -= 8 b,  y -= c0 a^3.
```

## Theorem 1 (displayed gap)

At `r=16` the displayed marginal gap, repair minus eager restoration, is

```text
Δ = Q_{35/16}^a + Q_{85/8}^a + Q_{-205/16}^a + 2 L_{-8} - 16 L_{-1}.
```

The five-event schedule is strictly cheaper than the sixteen restoring
shears on displayed events if and only if `Δ < 0`. An additive repair-only
obligation `E ≥ 0` that is outside these six symbols replaces the test by
`Δ + E < 0`.

The common prefix cancels by the price definition above, so this is the
comparison with `r L_-1` requested by the handoff. It is not a comparison
against the whole eager program, and it does not price routing, precision,
storage, dispatch or controller work except where a chosen law folds that
work into `Q` or `L`.

## The r=16 identity used by the invoice

Let `S1 = 16·15/2 = 120` and `S2 = 16·15·31/6 = 1240`. The deferred excess
over `16 A^3` is

```text
f_16 = 360 A^2 B + 3720 A B^2 + 14400 B^3.
```

Expanding the three cubes gives the same coefficients. The `A^3` coefficient is

```text
35/16 + 85/8 - 205/16 = (35 + 170 - 205)/16 = 0.
```

The `A^2 B` coefficient is

```text
3 (35/16 · 16 + 85/8 · 8) = 3 (35 + 85) = 360.
```

The `A B^2` coefficient is

```text
3 (35/16 · 256 + 85/8 · 64) = 3 (560 + 680) = 3720.
```

The `B^3` coefficient is

```text
35/16 · 4096 + 85/8 · 512 = 35·256 + 85·64 = 14400.
```

Starting from the deferred source `a = A+16B`, the first shear leaves
`A+8B` and the second leaves `A`. The three subtractions therefore remove
`f_16`, and the sources return to `(A,B)`. This is the special case `r=16`
of the pinned general argument; the expansion above does not depend on that
write-up's intermediate formulas.

## Theorem 2 (the pinned texts do not instantiate the gap)

The four live inputs contain these sentences and do not contain an
assignment of `Q_{35/16}`, `Q_35/16`, `L_{-8} =` or `L_-8 =`:

- PR6200: "No numerical backend price is substituted here."
- `research/dyadic-cubic-repair/PROOF.md`: "No such backend is supplied."
- `research/cubic-pow2-repair/README.md`: "Fewer repair queries or shears alone do not prove a cheaper execution."
- `research/cubic-pow2-repair/PROOF.md`: "It does not prove the two-shear count optimal, compare physical tariffs", read with line breaks folded.

This is a check of those four files, not a repository-wide absence proof.
No numerical backend is supplied by the handoff's own inputs, so a single
runtime winner is not determined. The next two theorems evaluate the gap
under two exact laws stated here. Neither law is read off a caller.

## Theorem 3 (coefficient-blind law)

Suppose every nonzero coefficient has the same cube price `q` and the same
shear price `ℓ`:

```text
Q_c^a = q,  L_c = ℓ,  for every nonzero c in the schedule.
```

Then

```text
Δ = 3q + 2ℓ - 16ℓ = 3q - 14ℓ.
```

If `ℓ > 0`, the repair is strictly cheaper exactly when `q/ℓ < 14/3`, a tie
at `14/3`, and strictly dearer above it. In particular, the unit
substitution `q = ℓ` gives `Δ = -11ℓ < 0`: sixteen unit shears cost eleven
more unit events than three cubes and two shears. That substitution is the
event count the predecessor forbids treating as a runtime proof. It remains
a valid conditional answer if a backend really is coefficient-blind.

The same cancellation at a general power `r = 2^s ≥ 4` gives
`Δ = 3q - (r-2)ℓ`, hence the threshold `q/ℓ < (r-2)/3`. At the already
known arity `r=4` the threshold is `2/3`. Unit prices then give
`Δ = ℓ > 0`, so the three-query repair is strictly dearer than four
restoring shears. A coefficient-blind saving at `r=16` does not transfer
to `r=4`.

## Theorem 4 (binary synthesis law)

Write a nonzero dyadic as `c = m 2^v` with `m` odd. Charge one event for a
nonzero shift (`v ≠ 0`) and `popcount(|m|)-1` additions. Call this length
`σ(c)`. Then `σ(1) = 0`, `σ(8) = 1`, `σ(35/16) = 3`, `σ(85/8) = 4` and
`σ(205/16) = 5`. Suppose the symbols are exactly

```text
Q_c^a = q + σ(|c|) u,  L_c = ℓ + σ(|c|) u,
```

with `q, ℓ, u` independent of the coefficient. Substituting the five repair
events and the sixteen restoring shears gives

```text
Δ = 3q + (3+4+5)u + 2(ℓ + u) - 16ℓ = 3q + 14u - 14ℓ.
```

Consequences, still inside this hypothesis:

- If synthesis is free (`u = 0`), Theorem 3 is recovered.
- If each extra shift or add costs at least one shear (`u ≥ ℓ`) and
  `q ≥ 0`, then `Δ ≥ 3q ≥ 0`. The displayed repair is not strictly cheaper.
- If also `q > 0` or `u > ℓ`, then `Δ > 0`: coefficient synthesis consumes
  the eleven-event gap before any further residual `E`.

Law 4 prices synthesis inside `Q` and `L`. Adding `σ` again as part of `E`
would double-count it. PR6200 already says a query includes its coefficient,
but it does not fix `σ`, `u`, `q` or `ℓ`.

## What remains outside both laws

Shear-count optimality is not claimed. Child fusion, intermediate
observation, a non-dyadic coefficient ring, and any caller whose cube and
shear prices are not constant on the blind law or not affine in `σ` need
their own substitution into Theorem 1. The selected frontier is unchanged.
