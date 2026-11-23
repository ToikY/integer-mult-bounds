# Fixed-grade capacity limits on rejoining #8087’s paid splits

At exact [#8087 at aea16994](https://github.com/CrocSwap/integer-mult-bounds/commit/aea1699415250d865f7a635f4df0b76f406c47b4), rejoining three or more of the 1,008 type-zero rank-one splits is impossible in the fixed grade roster, at the installed raw trial, with recipient eligibility $5r\le4k$. The absolute capacity of the legally accessible targets fails even if their entire available mass is assigned to compulsory high grades. The two-removal histogram passes all 21 proper directed Hall cuts and matches the total cut. One removal follows by monotonicity. These are grade-capacity results. Physical routing, ownership, signed return, the new finite debit and a complete κ gain remain open.

## Source and replay

Use Git and CPython 3.12 on a clean detached checkout of #8087. From this evidence directory pass the exact checkout as an explicit root.

```sh
python3.12 -IB replay_grade_cut.py ./inputs/peer8087
```

The script pins the committed terminal result and the unchanged public rank receipt included here. It inverts the independently reconstructed (1,1)-weighted scale-(1,8) census, undoing the 1,008 baseline splits. It remixes those entire ranks at the current weights (5,451) and scales (1,2). The clean-input run reproduced all label counts and the exact #8087 directed raw margin. It took 0.29 s and exited 0. Independently implemented integer arithmetic matched its margin, absolute shortage, least proportional slack, and both gross-moment endpoints. [Python receipt](GRADE-CUT.json) · [Independent integer result](INDEPENDENT-ARITHMETIC.json)

The unchanged authenticated [#8087 signed runtime](https://github.com/ToikY/integer-mult-bounds/blob/ae140fb88d8afe644de3767517611525552cd8e0/paired-768/r407/verification/independent-invoice.json) contains `clock_ports.py` SHA-256 `7d67eb9db9c50fec056440ef17acc6566cdcac740f44d74790213a5179d34b1e` and `unpowered_price.py` SHA-256 `a6c80d4605065889bb49144c034965a6bf33d8fad7f73ef97dcf1089e48316b4`. The included [R368 raw census](https://github.com/ToikY/integer-mult-bounds/blob/a636a3892e7036b782168bbba260419c6b2be309/paired-768/r368/primary/receipt-final.json) was already bound to the signed producer through the [R378 full-rank and cell comparison](https://github.com/ToikY/integer-mult-bounds/blob/44ad9f1dcd50ff68cfabb5629703fb49f9e77afc/paired-768/r378/price/price.py). The rank-one target count is 1,008 before weighting and 5,040 afterward. There are no half-grade targets. Other positive grades start at two.

## Capacity proof and exact scope

Let $c=17145637307/2^{42}$, $t=1-c$ and $s$ be the number of type-zero splits retained. A grade has powered mass $r^t$. At $s=1005$, the downward sum of every paid grade $r\ge1$ exceeds the upward sum of all eligible targets $k\ge2$ by exactly

```text
110419835000470055474627290238631 / 81129638414606681695789005144064
```

as a directed lower bound on the true shortage. The calculation uses independent 112-bit outward integer intervals. Any $s<1005$ adds five paid units of grade one for each successive unsplit. Target capacities and eligibility remain fixed. Therefore the exclusion covers any subset of **3 through 1,008** removals under these exact premises. It also applies to nonproportional assignments that keep the same allowed edges and physical powered target capacities.

At $s=1006$, use directed upper paid and lower target moments, and scale the latter by the ratio of paid to target total as in the installed allocator. The allowed sets are nested in descending source grade. Every proper upper-tail Hall inequality holds, and the total cut is equality. The least proper slack is at grade one. Moving to $s=1007$ increases the normalized target capacities and decreases or preserves every compulsory paid upper tail with grade at least one. The half-grade full cut stays an equality. Thus the one-removal and two-removal histograms both have grade support. The gross saving of two removals is bounded above by `4390517591624778117018107149485/162259276829213363391578010288128` in raw powered moment. A raw moment saving cannot be reported as a κ or full recurring-cost gain.

## What this changes

Stop screening three or more removals in this fixed family. Keep at most the last two chart-owned split sites as physical candidates. The first is paid ordinal 1593, `(return, 9977, 0, 91966)`, chart 59→447. A merged grade-one loan needs a target of grade at least two and must return both independent half-axis sets to the original owner before the old physical generator resumes. The next test would be one exact signed first-read and return check with the new grade-one route, then the full changed 51/88-cell or newly counted calendar debit and caller invoice. A different raw trial, new target tags, changed scales or replacement legal edges require a separate comparison.

The existing [#8074 same-value reroute exclusion](https://github.com/CrocSwap/integer-mult-bounds/pull/8074) and [#8079 productive-mask exclusion](https://github.com/CrocSwap/integer-mult-bounds/pull/8079) test different changes. [Round 368](https://github.com/ToikY/integer-mult-bounds/blob/a636a3892e7036b782168bbba260419c6b2be309/paired-768/r368/adapter/PROOF.md) supplied the actual return tags and an older paid-split proof. [Round 375](https://github.com/ToikY/integer-mult-bounds/blob/888b4e162261ffc1953ac18e867c2c21af4b8164/paired-768/r375/FRONTIER.md) supplied first-cut slack under its predecessor weights. This result rechecks the changed 5/451-weighted exact #8087 raw trial and proves the absolute exclusion and all proportional upper-tail cuts at that profile. Ali Romman supplied #8057’s signed provider and caller, Clear1nsight supplied #8081’s full 25-bit installer, and #8087 supplied the verified comparison and current price. OpenAI Codex materially assisted the proof and reproduction.
