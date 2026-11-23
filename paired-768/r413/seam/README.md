# Seven ordinary cut and width checks on exact #8094

Scope was fixed at the two entry and five terminal ordinary recipes, with a 60-second runner cap. The scalar check exhausted seven cases in 0.06 seconds with exit 0. It authenticates three files from [exact #8094 c20a08d](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8) and the archived entry profile. The entry η remains 39/10000. The terminal η is 1/256. The raw ordinary floor is 4474 in all seven recipes.

| Slot | Rank log H | First admitted trit-width log | First compiled dyadic log with stage maximum set to slot | Compiled dyadic anchor before next uncapped cutoff |
| --- | ---: | ---: | ---: | --- |
| Entry 1 | 3,000 | 3,077 | 24,097 | No |
| Entry 2 | 3,080 | 6,221 | 27,718 | Yes |
| Terminal 1 | 31,808 | 32,000 | 255,486 | Yes |
| Terminal 2 | 502,922 | 534,986 | 4,055,377 | Yes |
| Terminal 3 | 7,951,907 | 8,486,957 | 64,150,243 | Yes |
| Terminal 4 | 125,730,703 | 134,217,724 | 1,014,332,582 | No |
| Terminal 5 | 134,217,727 | 268,435,515 | 1,207,959,541 | Yes |

Each slot has a direct anchor at admission, with stocked trit-width-to-chart-width ratio at least 2^(H+63). At every later slot's admission, the predecessor floor gives chart width 2^(previous cut)+1. A full-width prior-stage call at that point would have exactly the required log. Entry slot 2 and terminal slot 5 have a predecessor rank clearance of one after the two-bit guard. Lowering the terminal height to the previous cut plus two fails that guard. The old 39/10000 η also rejects the terminal booking.

For integral width log s the direct predicate reduces to 2^(s−8H) at most the chart width. The width is the greater of the prior floor and ceil(2^(s/250)). If t=s−8H is at least ten, Bernoulli gives 2^(250t−1) < (2^t−1)^250 < 2^(250t), so the root branch satisfies the predicate exactly when s≥250t. The floor branch satisfies it through s=8H+previous cut. The two endpoint checks use the exact branch with greatest allowed s. The earlier quotient stock sufficient log, ceil((2H+64)/(1−η)), is below 3H for all seven slots.

The capped anchors match the scope of the peer's seam probe, which selects a fixed maximum stage and mocks receiver and body calls. The finite result leaves actual signed caller reach, native action, tape and ownership behavior, the all-size clock and the η proof transfer open. It gives no κ gain.

## Replay

Use CPython 3.12 and a clean checkout of exact #8094. Set K7_ARCHIVE to the public [frozen #8057 archive](https://github.com/CrocSwap/integer-mult-bounds/blob/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e/research/p104-weighted-k7-suffix/peer8057.tar.gz) as copied verbatim in #8073. The replay verifies the archive and member, uses no installed state, and reads files in memory.

```sh
python3.12 -IB check.py \
  --package-root "$PEER8094_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage" \
  --archive "$K7_ARCHIVE" > reproduced.json
cmp reproduced.json RECEIPT.json
```

Credit floration for #8094's stage profile and seam probes, Clear1nsight for #8084's η-lift, Ali Romman for #8057 and the inherited receiver and ordinary clock, and the Round 411 audit for exact scalar source pins. OpenAI Codex assisted with the independent finite checks.
