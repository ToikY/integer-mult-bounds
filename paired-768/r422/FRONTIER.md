# Round 422 frontier refresh

Read-only snapshot at 2026-11-23 22:51 UTC. Canonical `main` was `e54523517d0f03e58352e647c403a5af3e525a57`, with #7000 still the selected record. No newer comparable claim surfaced in 55 recently updated PRs across all states, 25 latest-created PRs (highest number #8094), a 100-closed-PR scan for recent merges, or 15 recently updated discussions. The exact #8087 and #8089–#8094 review lists were empty at the snapshot.

| PR | Exact head | Comparable claim and verification |
| --- | --- | --- |
| [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) | `c20a08dc0a79a989e3515068560d5da371c0a2a8` | κ `0.003900857267786`. Strongest relevant peer claim. [Hosted run 45143810893](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45143810893) concluded `action_required` with zero jobs. Independent local replay pending at snapshot. |
| [#8090](https://github.com/CrocSwap/integer-mult-bounds/pull/8090) | `9eb499cd6abccf9985eaf093e97ec75c71514a55` | κ `0.003900826966095` claimed, below #8094. |
| [#8089](https://github.com/CrocSwap/integer-mult-bounds/pull/8089) | `39a03a1317b6d066c76f7fea6a5fcbbcd10cf738` | Hosted scientific replay succeeded for `research/p104-shortcut-eta-target`. [Exact job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45130994532/job/137548042982) |
| [#8087](https://github.com/CrocSwap/integer-mult-bounds/pull/8087) | `aea1699415250d865f7a635f4df0b76f406c47b4` | Hosted scientific replay succeeded for `research/p104-period-debit-25bit`. [Exact job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45121099547/job/137516069048) |

#8091 audits retimed packet conservation, #8092 constructs a selected native/finite compiler under three retained contracts, and #8093 treats explicit direct circulant precision. Their exact PR claims did not replace the comparable numeric frontier. The [#1166 runner request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19842065) had zero replies. The latest #7111 checkpoint observed was Round 421.
