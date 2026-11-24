# Charge the interior integer fringe at the reproduced profile

**Round 427 · NO VERIFIED GAIN**

Use [exact #8095](https://github.com/CrocSwap/integer-mult-bounds/commit/826fed2c3382254beea1cba845938fca02fd2dfa) as the source comparator, κ 0.003900857312000 with full independent local replay. [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) was the external comparable peer at κ 0.003900857267786. The new scoped screen advances no campaign κ. The earlier #8095 improvement remains separately verified locally.

For an actual positive integer grant from even parent band e to even receiver band d, overlap requires (er<(d+2)k). Productive k is integral and paid r is a positive half-integer. Hence the actual integer suffix (r(e-8)-k(d-8)) is at most (10k-8r-1≤10k-5). The invariant applies to matched interior grants. Preserve full unmatched, late, terminal and exterior charges. With funded receiver capacities and total weighted target-axis mass A, there are at least A/258 weighted target slots in the aggregate upper bound. The resulting fringe numerator is bounded by ((515/516)10A). Routing, ownership, restoration, precision, tape and fixed setup keep the same proven invoices. The [independent audit](INDEPENDENT.md) identifies the exact issued-prefix interfaces and the scope of the substitution.

This certifies the **price screen** at Gaussian debit 1039699/2^23, two ticks below the existing booked 1039701/2^23. Both 112- and 192-bit bounds passed. The old fringe at the tested debit fails the negative control. The ordinary inequality then binds at the fixed heights, with projected κ 0.003900857312674 and projected exact Δκ 0.000000000000674. The screened recurring log₂ C stays 85945126846. The test did not seek the minimum possible Gaussian debit.

From the handoff checkout use Git, CPython 3.12 with assertions, a clean checkout of the exact comparator and 8 GiB free on the relevant volumes. Use fresh external scratch on POSIX. The package sources are authenticated before being installed for the source-only bound. No existing runtime is needed.

```sh
scratch="$(mktemp -d /tmp/croc-fringe.XXXXXX)"
TMPDIR="$scratch" python3.12 -IB paired-768/r427/check_fringe.py \
  --package "$COMPARATOR_CHECKOUT/research/p104-k7-sharper-period"
```

One fixed profile and a 45-second cap. A clean archive export produced the byte-identical [receipt](RECEIPT.json) in 0.35 seconds. Histories with different bin parity, nonintegral actual axes, nonpositive grant, different target support or unverified marginal capacity remain outside this result.

Next prepare one literal price overlay. Implement the reduced bound in the same installed Gaussian and independent price routines, retain the exact old-fringe negative and all signed costs, and verify the selected scalar and stage seams. Stop on source or budget mismatch. Complete independent scientific replay is still required before any further κ claim. At this fixed profile, further Gaussian-only saving cannot lift the ordinary ceiling.

Credit [#8083](https://github.com/CrocSwap/integer-mult-bounds/pull/8083) and its [pinned Round 409 referee proof](../r409/price/PEER-INTEGRAL.md) for a strictly stronger prior lattice bound and matched-phase calculation, Ali Romman's #8057 for the signed typed receiver, and #8094/#8095 for the scoped comparator. This artifact instantiates a conservative consequence at #8095's exact resource point. OpenAI Codex materially assisted the replay and arithmetic.
