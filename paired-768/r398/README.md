# Signed capped height balance at the same recurring clock

Exact head `8c800e1b6458526e1ce7a59150bba8a0d29d0027` binds terminal ordinary heights (8192,124986,524288) and Gaussian height 490463. The largest height is 524288. The paid conditional target is κ = 0.00389821380, an exact increment of 127/50000000000, or (12700/194910563)%, over independently reproduced κ = 0.00389821126 at `04228ea5a1292cf8526a20037060f6fc6e15a858`. The recurring log₂ bound is 318292711. The changed 515-bit entry conversion, private address bound 536870915 and seven-recipe native setup below 2^228 are charged. [Comparator evidence](../r396/README.md) · [Detached proof](PROOF.md) · [Local and hosted check status](CHECKS.md)

The previous height vector fails at the new booked rate on both suppliers. Its ideal ordinary recurrence misses by 182201655046251519551408650499/77580469414725995724800000000000000000. Its Gaussian rate falls short by 4059416987397526152183/1628272433561600000000000000000. The new literal gate checks neighboring stage cuts, direct and compiled dispatch with exact logical widths, and true H490463 Gaussian placement at period 1364 and first swap 1→272. It retains the same physical K7 gallery with 323165 returns of opened owners, 432 paid prefixes and 683705746532 charged singleton axes, and both finite signed tape cases. The bounded build passed in 76.704 seconds. [Local literal build](build.log) · [Sealed detached receipt](verified.json)

Use Git and CPython 3.12. From the clean candidate checkout at the exact head above, run the complete registered scientific replay.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-capped-allocation
```

For the lightweight independent verification, set `CANDIDATE` and `COMPARATOR` to clean Git roots at the exact heads above. From this evidence directory run

```sh
out=$(mktemp -d)
python3.12 -IB replay.py --candidate "$CANDIDATE" --comparator "$COMPARATOR" --out "$out/verified.json"
cmp "$out/verified.json" public-verified.json
```

The original exact detached replay took 0.205 seconds. The portable wrapper took 0.26 seconds against the two clean exact Git roots and makes its own temporary directory. All source and evidence paths are explicit. The portable receipt differs from the sealed original in the predecessor onboarding traceback path digest and the affected completed-log map digest. The raw sealed receipt and original logs remain preserved. [Full public replay receipt](public-verified.json) · [Declared path redactions](PATH-REDACTIONS.json)

Ali Romman supplied the signed weighted native source, physical tape, ownership and recurrence proofs. SYLforge supplied K7. Round 396 supplied the complete independently reproduced lower cutoff and both signed suppliers. Round 397 supplied the bounded independently priced height balance and physical seam receipt. OpenAI Codex materially assisted the construction, pricing, proof and replay. [Weighted predecessor #8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
