# Round 444 periodic-tail source compatibility

Scope is exact #8098 fae237c8aee774bb2256d4e394fed9f3934147c2 and its installed K7 ordinary floor 1156. I read the retained ordinary `transport.Plan` and `Recipe.open` and the #8097 materialized price and ordinary-floor checks. The inspected runtime transport SHA-256 is `9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818` and selector SHA-256 is `2d55f0269164878a6507c6756f2f27ccd6b3a6d2cbd5b3232e89ebc8e1b7a422`. The transfer is a valid source-level bound under the current proof assumptions. No native suite, Git mutation or publication ran.

## Literal grant and finite extension

The ordinary recipe uses even bands e,d in `range(L,U,2)`, with L=1156, carrier M=2^H, and `U=2 floor(M/(2048·134))`. It prices K=M^82 birth ticks and measure density proportional to `V x^(−1−t)`, V=M^6 and t=1−c>0. The allocator splits a positive cell share among all identical-grade target labels and issues the integer floor of its lower measure on

```text
[max(e, d k/r), min(e+2, (d+2) k/r)).
```

Empty intersections grant zero. Edges must satisfy r>0, positive share and 5r≤4k. The physical widths are P=r(e−8) for the paid parent and Q=k(d−8) for the selected recipient. With z=k/r>1, substitute y=x/z. The overlaps partition a subset of `[L,U/z)` in y, with endpoints of zero measure. The density becomes `z^(−t)y^(−1−t)dy`. At any y interior to the resulting even-band cells, e=zy−a(zy) and d=y−a(y), where a(v)=v−2 floor(v/2). Therefore

```text
S(y) = P−Q = 8(k−r)+k a(y)−r a(zy).
```

This expression also defines S outside the finite range. For every y≥L, 0≤a<2 and `S>8(k−r)−2r≥0` by 5r≤4k. Thus the integer downward grant bound may be multiplied by S, and extending the resulting integral to infinity only adds nonnegative mass. This argument neither assumes full occupation nor assigns a new physical loan. All 24 occupied K7 cells must still be authenticated for the exact numeric comparison.

## Normalization and alignment

Put b(v)=a(v)^2/2−a(v), a continuous period-two primitive with values in [−1/2,0] and derivative a(v)−1 away from its breakpoints. Let `J(y)=k b(y)−(r/z)b(zy)`. Then `J'=S−9(k−r)` almost everywhere. Since L is even, b(L)=0 and J(L)≥0. The donor phase a(zL) need not vanish. Also `J≤r/(2z)` everywhere.

For f(y)=y^(−1−t), the bounded primitive kills the infinite boundary term. Integrating by parts gives

```text
∫_L^∞ f J' = −f(L)J(L) + ∫_L^∞ (−f') J ≤ f(L)r/(2z).
∫_L^∞ f S  ≤ (L^(−t)/t) [9(k−r)+t r/(2zL)].
```

The correction is a width coefficient: dividing `f(L)r/(2z)` by `L^(−t)/t` produces `tr/(2zL)` exactly. The post-substitution factor z^(−t) multiplies the entire bracket before summing the edge weights. This is an upper bound on the complete matched integral. It need not bound the suffix of an individual granted event. The current implementation may safely retain the extra positive `+rδ` per weighted edge. In the price calculation this replaces only the old bracket `(9k−8r)(r/k)^t−r(Lr/(Lk+4r))^t+rδ`. The same positive tΨ denominator normalizes the matched numerator. [#8083 independent finite-range and phase proof](https://github.com/ToikY/integer-mult-bounds/blob/8e7738d0cd3cd37d1aa9815c6ea129bf21e5e1ef/paired-768/r409/price/PEER-INTEGRAL.md) · [Round 411 K7 specialization](https://github.com/ToikY/integer-mult-bounds/blob/a5d5fd437a3bb3d0a78f3fb4f6412db8a04bb42a/paired-768/r411/audit/README.md)

## Entire invoice and remaining gate

The literal `leaves_per_epoch` charges `K C P−B sum(q_i Q_i)` for B=max(0,K−j·delay[e]). This equals matched suffix `K sum(q_i(P−Q_i))`, unmatched full field `K(C−sum(q_i))P`, and late-prefix loss `(K−B)sum(q_i Q_i)` combined. Change only the matched term. Keep the full unmatched, grant and birth rounding, delayed prefixes and paid singleton paths. The exterior branch still uses `4 ceil(M/(4 size))`, complete cycles, final-group padding and its original stock, finite error and return charges. Preserve the complete factor

```text
tariff · (256/255) · (4097/4096) · (1028/1024)
  · (1024·134·L)^c · (1+fringe/L+δ) / (1−δ)^4.
```

Retain existing non-interior `+δ` and per-edge `+rδ`, charged geometric budget 2401, setup, precision and signed tape/owner accounting. The #8097 floor tests and old periodic-envelope controls remain meaningful as predecessor evidence. A bounded aggregate fixture may test the new bound on the same finite event sum. It cannot impose a per-event cap with this mean. [Exact #8097 ordinary floor and verifier](https://github.com/SYLforge/integer-mult-bounds/blob/e1c251401fe254909ac7e7bf2c773b921a1b6b57/research/p104-10shortcut-3type-28bit-6stage/check_ordinary_floor.py)

No extra phase alignment, signed caller, routing or ownership hypothesis is needed by the analytic replacement. The five baseline all-size contracts remain premises, including actual native phase and spectator semantics and precise caller recovery. The current scope is a compatibility proof and a source-price test. An exact literal price must match the installed 24-cell roster and hold at both directed precisions before building. The resulting selector, full signed candidate and independent replay remain unverified. The old Round 411 full-reserve impossibility result concerned its different L=4474 envelope and does not settle this L=1156 invoice.
