# Returning the full Gaussian loan at two rank-one cuts

The exact [#8053](https://github.com/CrocSwap/integer-mult-bounds/pull/8053) package at `e25494616bf149217644ce08d949181ea3600e13` authenticates its inherited #8052 archive by path. The new adapter differs from that reconstructed source by the one literal `SMALL_SPLITS = 1006`. The shared literal source gives these two affected payments in the base scale of the 48-call Gaussian word:

| Zero-based paid clock | Native return tag | Old and new chart labels on the original move |
| --- | --- | --- |
| 1592 | `("return", 9977, 0, 91990)` | `64 → 445` |
| 1593 | `("return", 9977, 0, 91966)` | `59 → 447` |

For each, the physical routine applies the right monomial chart to the live value, stores it under one fresh token, and suspends at its return tag. The adapter splits only the ordered active axis list of that one Job. For any positive even (w), real `Job.select` is an ordered projection that retains its owner. The sequences at indices (0,dots,w/2-1) and (w/2,dots,w-1) are disjoint and concatenate to the original list. Replacing those two adapter packets by the original Job keeps the one owner, axis order, and complete basis. This identity applies to arbitrary input lines and phases. The adapter performs no chart or phase action of its own.

Before the change the physical generator remains suspended on the same native yield across both smaller adapter yields. It then consumes the same token and applies the left chart once. After the change one full packet references the same token between the same right-chart and left-chart operations. No owner is acquired, retired, or resumed by slicing. The following native row only becomes active after that token has been returned. Under the inherited exact caller contract, every requested independent axis receives the same signed local map. Permuting the schedule for disjoint single-axis maps preserves their tensor product. The new coupling and complete replay verify the separately changed external calendar and ownership schedule.

The checker authenticates the `retimed_supplier.py` one-line difference, reconstructs the underlying chart moves and confirms both paid ordinals. It matches the operative syntax for right chart, acquire, yield, return and left chart. Executions of the real `Job.select` cover five positive even widths and both natural and reordered nonconsecutive axis IDs. Dropped axes, ownership substitution, and swapped halves are each rejected. Tested in 3.05 s, below the 15-second reserve. The separate whole-emitter test in `primary/check_emitter.py` checks all 564,144 old and 564,142 new symbolic requests in both scales. The full nonzero physical replay is a separate gate.

With CPython 3.12 from any clean work directory, use explicit inputs. The fixed-carrier input is the public `research/p104-gaussian-fixed-carrier` directory from exact #8053. The variant is an unpacked edited `research/p104-k7-retimed-binary` directory from the campaign patch. Keep `adapter/check.py` beside `../primary/price.py` so its authenticated restore helper is available. Use a fresh output filename.

```sh
python3.12 -IB adapter/check.py --fixed-carrier /path/to/fixed-carrier-package --variant /path/to/edited-package --out fresh-adapter.json
```

The physical Gaussian supplier and chart implementation are inherited from Ali Romman's #8042 and its pinned predecessors. SYLforge's #8052 supplies the installed multiplier. #8053 supplies the preceding exact coupling and comparison. OpenAI Codex assisted the proof and implementation. [#8042](https://github.com/CrocSwap/integer-mult-bounds/pull/8042) · [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052)
