# First installed replay of the frozen proof candidate

**2026-11-23 UTC · Round 424 · NO VERIFIED GAIN**

Exact [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) at `c20a08dc0a79a989e3515068560d5da371c0a2a8` is independently reproduced at κ 0.003900857267786 through the [seven exact scope receipts](../r423/REPLAY.md). [Frontier and overlap](FRONTIER.md) found no stronger complete comparable witness.

| Check | Local result |
| --- | --- |
| Cold install, 60 s cap | Exit 0 in 0.31 s |
| Literal price, 150 s cap | Exit 0 in 6.89 s, κ 0.003900857312000 |
| Dirty physical relay, 90 s cap | Exit 0 in 5.90 s, both directions and bad-Fourier negative |

Installation selector SHA-256 is `c5d83f8c6acdab6828185bc6bb67537cf320ba79ab177f9da535edae7b5af72e`. [Installed price](OBSERVED-PRICE.json) keeps log₂ C 85945126846, activation exponent 268644472 and fixed setup below 2^228 under the same premises. The [charged price difference](PRICE-DIFFERENCE.json) is 0.000000000044214, or +0.000001133443163% relative to exact #8094. It remains provisional until complete signed replay.

The [physical receipt](PHYSICAL.json) tests the rank-five graph relay at node 104493, donor 94870, chart 365 → 529 and return tag (9977, 0, 104493). The dense oracle checked 2,048 dirty forward and 2,048 adjoint values. The original owner survived and scratch retired. The scope is one physical column with a synthetic identity boundary.

Use CPython 3.12 and Git, external scratch and the 8 GiB reserve. Follow the [pinned clean source assembly and first installed commands](../r420/RESTART.md) and compare [the exact exits](EXITS.log) and authenticated observations. The next checks are the two signed helper-173 widths, actual nine-recipe census, price, calendar, raw, exterior, nested and product. Keep all unrun or capped scopes visible.

Credit floration for #8094's profile and word, Ali Romman for #8057 and the #8042 quotient bound, SYLforge for K7, and #8085/#8087 for the reused period lemma. The candidate reprices that lemma at the #8094 resource point and composes it with the charged ordinary child tariff. OpenAI Codex assisted.
