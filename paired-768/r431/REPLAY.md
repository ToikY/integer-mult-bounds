# Price the ordinary tariff at the exact minimum rank

**Round 431 · NO VERIFIED GAIN**

The exact comparator is [#8096 at 40a82e7974cabfc8509363ea6ad8dd269e446098](https://github.com/CrocSwap/integer-mult-bounds/commit/40a82e7974cabfc8509363ea6ad8dd269e446098), κ 0.003900857312674, with the same conditional signed caller. The [full local proof and source receipts](../r430/REPLAY.md) reproduce the strongest comparable value. Its hosted status and the earlier #8095 hosted pass are tracked separately.

The existing canonical quotient proof bounds the same-stage child mean by ((21x+3)/(9x-1)) for (x=3^{N-2}) and (N ≥ 9). This quotient decreases on the whole admitted domain. The maximum of that bound is exactly 22965/9841. Book tariff 10981863/4703998 by dividing that mean by the existing contraction 2390/2391. This keeps the same geometric sum 2391. It multiplies the existing uniform ordinary finite factor by 2351616/2351999. The child schedule, setup, routing, precision, ownership and tape stay fixed.

The exact directed screen at 112 and 192 bits verifies that multiplying this ratio by (2^{128/2^{20}}) gives a value below one. The candidate ordinary debit is 353569/262144, 128 ticks lower on the existing grid. The original tariff fails that transfer test. The independent convexity check uses (2^{1/8192}≤8193/8192) to prove the same strict inequality using only rationals. The whole fixed-profile bound then switches to the existing Gaussian crossing, with projected κ 0.003900857313143 and prospective Δκ 0.000000000000469. The exact recurring coefficient remains log₂ C 85945126846. The [directed receipt](RECEIPT.json) and [independent scope audit](INDEPENDENT.md) support this decision only for the pinned charge and rank assumption.

Use CPython 3.12, Git and fresh external storage with 8 GiB free. From the handoff root and an exact clean #8096 checkout:

```sh
scratch="$(mktemp -d /tmp/croc-tariff.XXXXXX)"
TMPDIR="$scratch" python3.12 -IB paired-768/r431/check_tariff.py \
  --package "$COMPARATOR_CHECKOUT/research/p104-k7-integral-fringe" \
  --power-check paired-768/r427/check_fringe.py
```

One exact profile and a 45-second cap. The immutable package was authenticated and assembled into fresh scratch. The source and price replay completed in 0.26 seconds from a clean export, with no new native run. The next gate is one literal price overlay with independent ordinary pricing, signed stage seams and the full charged proof crossovers. Exact operator obligations and clean complete replay remain required before a κ claim.

Credit Ali Romman's #8042 canonical quotient receiver and #8057 signed stack, SYLforge's K7 construction, the earlier exact quotient derivation and charged tariff in R414/R415, and #8095/#8096 for the independently reproduced signed profiles. OpenAI Codex assisted.
