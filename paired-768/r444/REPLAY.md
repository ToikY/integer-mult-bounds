# Fixed-profile periodic tail price

**Round 444 · NO VERIFIED GAIN**

The exact [#8098 release fae237c8](https://github.com/CrocSwap/integer-mult-bounds/commit/fae237c8aee774bb2256d4e394fed9f3934147c2) independently certifies κ **0.003900862349168** at debit `1411927/2^20`. The [Round 443 joint ceiling](../r443/REPLAY.md) closes the quotient-mean and contraction family at this charged budget and debit grid. This test changes one separate term, the interior matched periodic tail at the ordinary cutoff L=1156.

For an occupied cell `(r,k)`, write `z=k/r` and `t=1−c`. Replace the previous tail term `(9k−8r)(r/k)^t−r(Lr/(Lk+4r))^t` by `(r/k)^t[9(k−r)+tr/(2zL)]`. The cell condition `5r≤4k` makes the physical matched suffix nonnegative. Its finite integral can extend to the half-line. At the even recipient cutoff, a bounded primitive of the period-2 axis offset gives the new normalized correction. Arbitrary donor phase is covered by the primitive lower bound. Keep both δ concessions and all late, exterior, unmatched, precision, reserve, tape, clock and setup costs. [Source-specific applicability proof](PROOF-REVIEW.md)

The screen authenticated the literal K7 profile and all **24** certificate cells. Both 112-bit and 192-bit comparisons reject the existing price at `1411926/2^20` and fund that debit with the new tail term. The whole-factor saving exceeds `7.4341255353924e−7`, and the remaining margin below the debit allowance exceeds `2.9957969351337e−7`. The scoped calculation projects κ **0.003900862349171**, exactly `3/10^15` above the independently signed #8098 rate. The same Gaussian cap, fixed clock, activation and `log₂ C=171810078109` are charged. One fixed profile and one debit were tested. A lower debit with the changed term remains untested. The literal new proof and complete signed replay are open. Verified campaign Δκ for this round is zero. [Exact directed receipt](SCREEN.json) · [Independent replay](INDEPENDENT.md)

## Clean replay

Use CPython 3.12 with assertions, Git, and 8 GiB of free space on the checkout and scratch volumes. Set `CHECKOUT` to the exact #8098 checkout and `HANDOFF` to the checkout containing this document. The paths and immutable source dependencies are authenticated by the script.

```sh
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = fae237c8aee774bb2256d4e394fed9f3934147c2
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB "$HANDOFF/paired-768/r444/check_periodic_bill.py" \
  --package "$CHECKOUT/research/p104-10shortcut-child-tariff" \
  --helper "$HANDOFF/paired-768/r438/check_minimal_debit.py" \
  --handoff-root "$HANDOFF/paired-768"
```

The group exhausted the declared price scope in 0.61 seconds under the 45-second cap, with exit 0. No alternative cutoff or physical schedule was tested. [Execution receipt](EXECUTION.log)

Build one literal price-proof edit by changing the named tail expression in the complete primary and independent price receipts, retaining the existing direct bound as a predecessor control. Compare both the tested debit and the next lower debit before freezing a single signed target. Bind the new selector and run the full registered signed suite before a κ claim.

Credit Clear1nsight’s #8083 primitive integration and the earlier Round 411 ordinary audit at L=4474. SYLforge supplied #8097’s full-reserve periodic source and six-stage profile. Ali Romman supplied the signed receiver and predecessor clock work. #8098 supplied the exact current profile and invoice. OpenAI Codex materially assisted.
