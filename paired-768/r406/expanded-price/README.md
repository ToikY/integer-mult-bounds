# Ordinary child mean at the #8078 recurring cap

The exact comparison pins [#8078 at b72d3fa](https://github.com/CrocSwap/integer-mult-bounds/commit/b72d3fa097d2521939f6b8536029da674648d863). Its stronger signed profile is κ 0.00389834, ordinary heights (8192,36220,575705), Gaussian height 978582 and whole recurring log₂ C 413727211. The mathematical price gate does not determine #8078's hosted status. It authenticates the exact published price and recomputes the old and prospective invoices separately.

The single prospective installation is κ **0.003898341157482** at ordinary heights **(8192,36030,569686)** and Gaussian height **987613**. It increases the installed κ by **578741/500000000000000** or **(578741/19491700000)%**, displayed as **+0.00002969166363%**. Exact excess over the old capped stopped upper is **1900221794381916834131/1641788158771200000000000000000**. The only verified claim here is an exact charged feasibility and cap proof. The actual full signed implementation and independent package replay remain pending.

| Charge | #8078 strong profile | Repriced profile |
|---|---:|---:|
| Ordinary heights | (8192,36220,575705) | (8192,36030,569686) |
| Gaussian and maximum native height | 978582 | 987613 |
| Ordinary finite debit | 11239/8192 | 11120/8192 |
| Gaussian finite debit | 64939/524288 | 64939/524288 |
| Entry log₂ C before conversion | 125660241 | 125660258 |
| Entry conversion | 717 bits | 719 bits |
| Terminal ordinary log₂ B | 198437568 | 196450715 |
| Whole recurring log₂ C | 413727211 | 413727178 |
| First terminal header | 2^1599173+4 | 2^1601995+4 |
| Conservative fixed serial setup | <2^228 | <2^228 |

The maximum native height increases by 9,031 while remaining a 20-bit height. At the old maximum native height the Gaussian limit would still be at most the old fixed-height stopped ceiling, even with the new ordinary debit. The clock savings and κ gain therefore concern same recurring cap with a deliberately stated maximum-height tradeoff. The new public header activates 2,822 exponent units later. The prospective ordinary cuts are (8290,44384,614134). The private scalar envelope increases from 1,002,067,971 to 1,011,315,715 log units. Entry conversion is separate from the inherited signed coefficient-recovery precision bound.

## Mathematical checks

For every canonical quotient low at a fixed placed frame the actual mean is at most `7/3 + 16/(3(9·3^(N−2)−1)) < 7/3+2^-40` for `N>=28`. The direct path has one paid child. Use tariff τ = `7/3+2^-16` at both ordinary moments with the fixed-frame mean `μ=7/3+2^-40`. Then `μ/τ=1539316278887/1539326345216` and the geometric series factor is `1539326345216/10066329`. This is larger than 32 and smaller than 64 times the #8076 series factor 2401. The two entry factors fit `2^34`; charge 17 extra fixed entry bits over #8078 (12 over #8076). The terminal clock charges nine extra fixed bits per ordinary stage over #8078, because the full prior series factors and the sharper new ones are retained together. The new whole terminal fixed charge including selection is 1758. The pinned 8/L envelope times `τ/(47/20)` fits the updated ordinary booking 11120/8192 and fails at 11119/8192. The signed owner routes and tape operations stay in the full local and earlier-stage bills. [Exact #8042 count](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/RECEIVER.md) · [Exact #8042 clock](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/ORDINARY-CLOCK.md)

The old debit requires ordinary sum at least 620117 and Gaussian height at least 978582 for the published peer rate, by the rounded known-good recurrence and strict relaxed Cauchy bound against sum 620116. Both costs are monotone, and at the old minimal pair `1731+320·620117+220·978582=413727211`. Any old profile improving the peer under the cap must keep the exact same Gaussian height. Thus the old stopped ceiling is at most `6400248450982567016889284269/1641788158771200000000000000000`, the unchanged Gaussian rate at that height minus the stopped guard. The exact new trial strictly exceeds that ceiling.

At each priced G the best relaxed ordinary invoice uses all permitted height sum M and h₁=8192. If h₁ is larger, moving one unit from h₁ to h₃ decreases the constrained weighted loss `(1/62500)/h₁+(1/250)/h₂+1/h₃`; the uniform derivative inequality in the script proves this. Since `M<2^20` over the priced interval, h₃ has room for the transfer. At fixed S = M−8192, the loss in h₂ is minimized by the first integer k with `250k(k+1)>=(S−k)(S−k−1)`. Solving this one-dimensional root with integer arithmetic checks the two exact successive finite differences. The script compares the relaxed ordinary ceiling to the actual rounded recurrence and caps the residual error. It independently brackets the last relevant G by a uniform Cauchy bound on the minimum ordinary sum required to reach the old κ. It then prices at most 16 cases.

The crossing `G=987613/987614` means lower G are bounded by the increasing Gaussian cap at 987613. Higher G face an ordinary cap no larger than the relaxed ordinary cap at 987614 because the available height sum decreases. The strict limiting rate at the new trial height is Gaussian. The exact stopped supremum of these two booking inequalities is `12918632163897138429382671467/3313879325081600000000000000000`. The candidate stays below this value. Its Gaussian `G−1` fails the new trial, and both bounds charge entry conversion before comparison. The positive directed margin, exact tested G list and all resource numbers are sealed in [the price receipt](receipt.json). Other tariffs, higher caps, stage families and operators remain open.

## Reproduction

Use CPython 3.12 and explicit dependency roots. Preserve the source and exact marks from the following links. No prior temporary state is required.

```sh
python3.12 -IB price_expanded.py \
  --peer-price PEER_CHECKOUT/research/p104-expanded-budget-signed/RESULT-340.json \
  --prior-price ROUND405_HANDOFF/price-audit/receipt.json \
  --factor-receipt ROUND404_HANDOFF/fringe-audit/result.json \
  --archive ROUND405_CHECKOUT/research/p104-weighted-child-tariff/peer8057.tar.gz \
  --receiver-proof PINNED_8042/RECEIVER.md \
  --clock-proof PINNED_8042/ORDINARY-CLOCK.md
```

Check the selected profile's exact public precision and fixed setup using its sealed receipt:

```sh
python3.12 -IB precision_selected.py receipt.json
```

The selected-profile arithmetic took 0.05 s, exit 0. It recomputes the binary cuts, first reachable header, both recovery precision hashes, both old entry prefix surcharges, both funding heights, upper-fence cost and complete conservative fixed setup. Its two first-header precision values have bit length 1,601,996 and SHA-256 `781ad33a959587ffd00d3cc17bcda6e5da0e4eb3fd47e620691a75fe73cd957e`. The actual source selector and physical recovery still need the full candidate replay. [Selected-profile receipt](precision.json)

The six inputs are authenticated by SHA-256. The exact Git blob ID of the #8078 result is checked separately. Use the [Round 405 handoff](https://github.com/ToikY/integer-mult-bounds/tree/eab0a7316cb6c3b65b48e22ca17a666592c49eac/paired-768/r405) for the exact #8076 price and its paired R404 factor. The first screen examined 15 profiles out of 16 and finished in 0.12 s. The Python process produced a complete terminal receipt and no error text. The outer collection wrapper returned 1 after trying to assign the reserved zsh variable `status`, so the first Python exit is unrecorded. Read [the collection note](collection-status.txt) for exact status.

If accepted after independent source review, materialize one new profile with the joined clock, suffix and child-factor proof. Keep the exact 20-bit setup condition, verify both stage-prefix branches and both sides of the public selector including exact precision, and replay all scientific modes with one independent builder-free verifier. A missing owner or routing charge, one smaller booking, or an actual replay failure remains a blocker on a complete κ result.

Credit Clear1nsight's exact #8078 enlarged invoice and original comparison, Ali Romman's #8042 receiver/clock and #8057 signed installer, SYLforge's #8052 K7 ordinary word, and #8073/#8076's suffix and charged geometric proofs. OpenAI Codex materially assisted the disjoint exact pricing audit.
