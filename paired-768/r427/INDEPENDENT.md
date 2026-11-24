# Round 427 independent source gate

Comparator is [#8095 at 826fed2c3382254beea1cba845938fca02fd2dfa](https://github.com/CrocSwap/integer-mult-bounds/pull/8095), conditional κ `0.003900857312000`. I inspected the retained runtime from Round 424 read-only. No native allocator, installation or external write was started. The scoped pointwise substitution passes.

## Literal suffix

The pinned runtime inputs are `typed_transport.py` SHA-256 `b76b9ad3dc0dd91473026c079585f830387eaa3c34c25a7820ee5057d5cbf941`, `transport.py` `9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818`, `grades.py` `6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d` and `unpowered_price.py` `a6c80d4605065889bb49144c034965a6bf33d8fad7f73ef97dcf1089e48316b4`. The exact price receipt authenticates the all-grade histogram and positive typed loads. `GradeVariant` produces positive integral productive grades k and paid grades r in `(1/2)Z`, with minimum `1/2`. Two-column bands e,d are even. The allocator uses 5r≤4k on every funded edge.

A nonzero interior grant is the floor of a positive type-weighted, share-weighted lower integral over

```text
(max(e, dk/r), min(e+2, (d+2)k/r)).
```

`Measure.mass` returns zero if its right endpoint is at or below its left endpoint. Thus a positive integer grant requires `-2r < re-kd < 2k`. The physical sender emits P=r(e−8) axes. `send_prefix` binds one pending recipient and returns Q=k(d−8) selected axes. Both are integral. Consequently

```text
0 < 8(k-r) + re - kd = P-Q
  <= 8(k-r) + 2k - 1
  <= 10k - 5.
```

The strict lower bound follows from `8k−10r≥0`, and the −1 from the strict integral upper endpoint. This covers every positive interior link, including same-type and mixed-type grants. It does not reduce the cost of a zero grant, exterior source, unmatched parent or late paid event. A sharper per-cell bound `10k−8r−gcd(2r,2k)` follows from the same lattice.

## Full weighted fringe substitution

For one band, type and paid index, `leaves_per_epoch` uses the identity below with K total births per replica, C replicas, q_i interior grants, B=max(0,K−j·delay[e]), and widths Q_i.

```text
K C P - B Σ q_i Q_i
  = K Σ q_i(P-Q_i) + K(C-Σq_i)P + (K-B)Σq_i Q_i.
```

Substitute only in the first term. The second retains its full ideal unmatched mass and rounding losses, including overlaps that round down to zero. The third retains the full cost of late lost prefixes. Exterior virtual grants, period charges already booked at 257/256, incomplete tails, final-group padding, ownership, phase, movement and fixed tape accounting follow the existing invoice. No event, owner or calendar change is required for this proof substitution.

Let `p_rk` denote funded grade shares, `D_r` weighted paid counts and `N_k` weighted productive counts. The installed typed split assigns each receiving label of type b share `p_rk w_b/N_k`. Summing both types recovers `D_r p_rk`. The outward allocator uses upper paid masses and lower productive masses for each cell. Its funded column inequality gives `Σ_r D_r p_rk r^t ≤ N_k k^t` for `t=1-c`, so `Σ_r D_r p_rk(r/k)^t≤N_k`. Changing variables from sender scale x to receiver y=x/(k/r) contributes this same `(r/k)^t` factor. Summing the bound over positive interior grants, replacing the directed integer lower count by the ideal integral upper bound, and extending the nonnegative integrand to y≥L gives a fringe numerator at most

```text
Σ_k N_k(10k-5) = 10 A - 5 Σ_k N_k <= (515/516)·10 A,
A = Σ_k k N_k = 677246016, k <= 258.
```

Only the already bounded matched contribution is scaled. This uses the upper capacity on each new **nonnegative** per-grade coefficient. It does not assume that every capacity is occupied or deduct five from a count of actual grants. The exact weighted target count is 23,989,248. The screen can use only A/258 for the conservative bound above while retaining the existing directed denominator `t Ψ`. The full factor decomposition remains valid under the same funded marginals.

The separate Round 427 price screen reports two directed precisions funding `1039699/2^23`, with the old factor rejected at that debit. Two ticks bring Gaussian above the guarded ordinary maximum, so the useful scalar target is `0.003900857312674`, projected Δκ `337/500000000000000` and recurring log₂ C 85945126846. This source gate validates use of the term in that screen. It does not certify a κ gain or an installed price overlay. The next gate is one exact overlay that updates the debit, selector, signed seam, independent price and matching source pins, then full independent replay.

## Predecessor scope and credit

The pointwise lattice statement already appears in stronger form in [the #8083 independent proof preserved by Round 409](https://github.com/ToikY/integer-mult-bounds/blob/8e7738d0cd3cd37d1aa9815c6ea129bf21e5e1ef/paired-768/r409/price/PEER-INTEGRAL.md). That analysis additionally integrates the periodic phases, with per-edge upper coefficient `9(k−r)+t r²/(2kL)` on the full weighted half-line. It does not assert that coefficient pointwise on each grant. R409 priced that stronger aggregate for the exact #8087 profile, using 1,971 phase intervals and two directed methods. Round 410 assembled a separate source profile and checked its authenticated price, but its native replay was unrun. Their printed fringe about 4.550681667 and debit `130699669/2^30` retain the earlier Gaussian word/rate and conservative exterior multiplier `22067/21981`. Those numbers are not portable to #8095. The distinct Round 427 work binds the weaker sufficient estimate to #8095's actual word, trial and funded invoice, retaining the calibrated exterior factor. [R409 exact price scope](https://github.com/ToikY/integer-mult-bounds/blob/8e7738d0cd3cd37d1aa9815c6ea129bf21e5e1ef/paired-768/r409/price/README.md)

Credit Clear1nsight for #8083’s strict overlap lattice and sharper phase average, the R409/R410 price and source replay, Ali Romman for #8057's typed allocator and signed caller, and floration for #8094’s underlying five-shortcut word. OpenAI Codex assisted with the independent source gate.
