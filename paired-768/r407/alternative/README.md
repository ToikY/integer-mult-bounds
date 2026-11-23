# Round 407 alternate Gaussian matched-suffix price

**Decision:** one fixed price case clears #8081’s exact stopped crossing and reduces its complete recurring clock. This is a provisional price transfer. It does not certify a new signed bound. The lead period result remains the sole candidate selected for this round.

| Input or charge | Exact value |
|---|---:|
| Compared complete profile | #8081 at `510113821774bb27f7ddaad4e8b94837a1c2cf52` |
| Matched-suffix ingredient | #8083 at `dd2e2ff28102557f7c30619d6abd8a861e363d1d`, companion offset-8 proof |
| Comparator κ | 0.00389846 |
| Old stopped ceiling at recurring cap 4354317571 | 15407802515941573408769828489/3952279237427200000000000000000 |
| Prospective κ | 0.003898460003746 |
| Exact booked gap over #8081 | 1873/500000000000000 |
| Exact gap over the stopped ceiling | 14804106726632462711/3952279237427200000000000000000 |
| Gaussian debit | 130699669/1073741824 |
| Ordinary heights and minimum Gaussian height | (8192,38102,604363) and 18531230 |
| Complete recurring log₂ C | 4285082571, down 69235000 |
| First terminal header and entry conversion | 2^19182389+4 and 8603 bits |
| Maximum native height | 18531230, still in the charged 25-bit domain |
| Fixed serial setup | below 2^228 including the original extra 2^40 indexed actions |

## Scope and compatibility

The Gaussian invoice in #8081's RESULT-460 exactly matches its retained #8072 UPSTREAM-RESULT Gaussian row. The #8081 exact package pins ten #8072 files, the #8057 archive, and the original installed calendar. The checked source still uses `size=(e-8)*k`, `q=4 ceil(M/(4*size))`, weights 5 and 451, 51 grade cells, 88 typed allocations, lower band 1874 and upper scale 263772. Neither installation overlay edits the archived typed transport. These are the same ingredients required by the **offset-8** branch of #8083's [exact integral proof](https://github.com/Clear1nsight/integer-mult-bounds/blob/dd2e2ff28102557f7c30619d6abd8a861e363d1d/research/p104-integrated-gaussian-suffix/INTEGRAL.md) and [directed pricer](https://github.com/Clear1nsight/integer-mult-bounds/blob/dd2e2ff28102557f7c30619d6abd8a861e363d1d/research/p104-integrated-gaussian-suffix/appendix/weighted_suffix.py).

The offset-8 proof prices the total matched **interior** suffix against the decreasing target-coordinate density. Its periodic primitive accounts for both even-band phases, including the donor phase at the lower edge. The overlap tuple gives a nonnegative physical suffix at every funded pair with 5r≤4k. This is needed to extend the upper integral beyond the actual overlaps. Late starts, unmatched fields, dyadic rounding, chronological ownership and exterior service retain their own paid terms. The proof keeps the exterior multiplier 1+1032/263772 and the actual four-aligned period. The smaller `257/256` period upper therefore plays no role here. No change is made to the ordinary rate recurrence or its 375/376 contraction. The six-column offset and altered physical transfers are outside this case.

The #8083 proof's recorded accounting-factor enclosure for this branch is (1.088033933515, 1.088033933516). The checker verifies the indicated debit and one smaller grid point with directed 192-bit square roots. It takes the reported factor interval as input. A full verification must independently rebuild the 51-cell factor and bind the actual 88 typed allocations. Rooted in the leading case's ordinary triple, the checker books the largest strict 15-decimal rate below its stopped ordinary ceiling and computes the least admissible Gaussian height directly. It checks the positive margins for both tiers, all 54 strict and four functional inequalities per tier, the prefix and stripe stocks, both entry/terminal charges, the 25-bit encoding and full indexed setup allowance. The old installed ordinary triple, Gaussian height one smaller, and Gaussian debit one smaller each miss their controlled bound.

The published #8086 stacked profile reports κ 0.003898348449639 in a 20-bit height class. Its ordinary reserve and Gaussian grid treatments are distinct from this matched-suffix price. It leaves #8081 as the stronger complete comparison for this case. The prospective trial here would need to be repriced against the exact stopped crossing of the strongest independently reproduced witness at any later launch.

## Reproduce one case

From this directory, use CPython 3.12, a clean exact #8081 checkout, and downloaded exact copies of the two linked #8083 files. The example uses a local directory named `inputs` for these three explicit roots.

```sh
python3.12 -IB check.py --peer inputs/peer-8081 \
  --integral inputs/8083-INTEGRAL.md --pricer inputs/8083-weighted_suffix.py
```

The successful single case finished in 0.25 s with exit 0 under the 30 s limit. An initial interpreter check resolved to Python 3.9 and stopped on the directed-square-root helper before pricing any profile. The CPython 3.12 run produced `receipt.json`. The script and receipt SHA-256 are `586a9f150e602ded0e7bce8a1765ef59637b97fe43b1378e781d63e349cf6a98` and `296ae9eca0fa121aa27ea9a0f249b913671e9d360be1afa9933c39acbbe10719`.

The next verification gate is a cold exact installer and signed replay for one promoted profile with the #8083 offset-8 complete factor reconstructed from the materialized #8081-family runtime. Preserve the paid exact 25-bit constructor and all eight registered modes. The algebra here does not execute the expanded setup service or the changed physical profile. The exact older #8081 scientific replay supplies the five underlying signed premises. Credit Clear1nsight for #8081 and #8083, Ali Romman for the #8057 source, SYLforge for the K7 word, and the #8072 allocation proof. OpenAI Codex materially assisted this scoped arithmetic comparison.
