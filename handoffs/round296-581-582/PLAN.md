# Next incremental gate · one native 581/582 bypass

Pin independently reproduced [#7546](https://github.com/CrocSwap/integer-mult-bounds/pull/7546) at replay-only head `99438c43df7aac1e5dbcc43c1578fcd886c119ec`, κ `0.003648411294790`, signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Exact #7546 canonical native `bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745`, compressed `6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32`, complete application `a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f`. All five file hashes are built into the runner. Record fresh peer and exact head checks before launch.

## Literal change and first reads

Let x and y be old chart3 fields581 and582 at pre36507. Change the existing ADD36507 from 581+=582 to 581+=2·582. Role581 takes its unchanged paid MOVE36508 from chart3 to595 and delivers x+2y through old ADD36509 to1556. This matches the combined old updates at 36509 and36511. Omit 582's MOVE36510 to595 and its ADD36511, and check that the original 1556 state is recovered before any later observer. Its subsequent old reads at39462/39464/39466 and CLEAR39468 inherit the exact row. Role581 keeps its required +2·1503 ADD39904. Omit the old +2·1503 into582 at39905. Change its MOVE41558 from 595→767 to direct 3→767 at the old clock, preserving the named paid rank-three continuation as the fused endpoint. The 1503 lifetime and its reads remain unchanged.

The role581 error at first outward ADD42252 into316 is +y, after its unchanged paid MOVE41553 to766, incoming ADD41554 from428 and MOVE42251 to879. The complete old live chart879 bank there is [316,581,1078,1258]. The role582 error before ADD42255 into1398 is −2·old1503@39905, after its unchanged incoming ADD41559 from430 and MOVE42254 to880. Its complete chart880 bank is [582,1080,1259,1398]. Earlier 428 and430 were legally coframed in 766 and767 at their incoming ADDs but left before the outward deadlines; this model allows their existing updates and excludes changing their earlier encodings. Both banks grant arbitrary rational scalar readout but preserve every old donor as read-only. The old paid arrivals supply the known directions; the unknown is whether they contain the two specified restoration directions at the fixed actual deadlines. The complete second bank is evaluated only if an exact nonzero-self repair to the first is supplied and applied.

With zero added paid work, signed ΔP=`{1:-17,3:-17,4:+17}`, ΔT empty. The exact gross upper (17(1+H_3-H_4)) is below one rank-one paid call. The runner emits both exact directed endpoints before support. A single extra rank-one call anywhere consumes the gross. The two final banks use their existing charts, with no new common intermediate detour. Any supported literal sequence must fully charge scalar lowering, coframe routing, signed native action/adjoint, ownership/read-only guards, exact grid, precision and tape.

## One case, hard 30 seconds

Authenticate the full word and caller, price the edit, check exact old/edited owned1556 equality at pre36512, then solve the first named bank. Stop at the first nonzero-self support failure and preserve the exact quotient or unsupplied row and unrun gate. If both pass, preserve literal repairs and run independent whole-word/all-input replay plus full directed price before advancing to a complete claim. General changed carrier encodings or different coframe banks remain outside the exclusion.

In a clean replay root put the five inputs under `inputs/` as `ROLE902-WORD.json.gz`, `ROLE902-APPLICATION.json`, `7113-CALLER.json`, `pricing.py`, and `gate.py`. Stage this runner under `next-581-582/`. Use CPython 3.12 and the standard library.

```sh
python3.12 -I -B next-581-582/check_581_582.py inputs
```

Chronology and syntax checked. No candidate science launched here. The earlier co-encoding is a materially different mechanism from the two direct late-bank role496 variants or a productive split with a stationary input row. [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) supplies the funded producer precedent, [#7542](https://github.com/CrocSwap/integer-mult-bounds/pull/7542) the adjacent native rung examples, [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) the cut-row technique and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the exact tariff. Targeted PR queries find no match for these exact roles, old clocks or deadlines. OpenAI Codex materially assisted.
