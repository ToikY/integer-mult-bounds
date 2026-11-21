# All original paid forms are independent within each ordered chart leg

The #8027 word makes 2,803 paid MOVEs on 2,354 different ordered chart pairs. For **every** pair (source chart, destination chart), GF(2) rank equals the number of MOVEs using the pair. Every transmitted form is nonzero. In particular, a later such form is never a duplicate or an XOR of earlier arrivals on the same ordered leg. The maximum saving from reusing only those arrivals is zero even before charging lifetimes, repairs or routing. The current independently accepted complete comparator remains R352 at 0.00389011527141.

| Occurrences of one ordered chart pair | Number of pairs | Rank per pair |
|---:|---:|---:|
| 1 | 2120 | 1 |
| 2 | 38 | 2 |
| 3 | 177 | 3 |
| 4 | 19 | 4 |

**Replay.** Starting with 630 independent public inputs and zero private state, replay all 39600 operations, propagating exact GF(2) rows, rational chart tags and live owned values. Take the full forward row inside the original owned register at each paid crossing. Process each route's rows in chronological order with exact elimination over all 630 coordinates, storing an original-clock representation if a dependency is found. For grade r, at most the sum of its route deficits could be saved if only fixed same-route arrivals can provide each canceled forward form. Each removal has at most 36·r^(1−κ) raw value on the fixed caller. Every grade-one through grade-seven deficit was zero; the complete directed gross interval is [0,0]. Checking the unknown restoration or routing costs could only reduce a gross saving. No splice passed the necessary rank condition. The original forward and adjoint public matrices, paid grades and private retirement were also replayed. All 2803 arrivals were visited; the result does not classify transports on a different ordered leg, cross-route bases or altered original encodings. [Exact peer source](https://github.com/aliromman/integer-mult-bounds/tree/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain)

**Fixed-four alternative at chart 585.** Immediately before clock 30338 the original five arriving forms in registers 1913, 2607, 2612, 3226 and 3430 have joint rank five. The archived R355 donor forms for 1913, 2607, 2612 and 3430 match the original rows; the original row for 3226 is the authenticated missing 113-coordinate form F. Clock 30338 only updates receiver 3604. At 30339 the same receiver reads 3430. The other four original arrivals remain in chart 585 with unchanged values. The public input e₁₇₁+e₆₀₄ gives zero on all four and one on the form from 3430. Consequently a repair using an XOR of the four fixed other arrivals cannot replace 3430's contribution at this later deadline. This statement does not grant access to an independently changed sender or a modified receiver.

**Reproduce.** CPython 3.12, exact #8027 package at fb9b6a7b0d27da1cf98430893a3016bf811e2aa4, word b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69. Cold run 0.248322 seconds under the 30-second cap with 10-second verification reserve. Receipt 245c57639941873096fd13f2962a7a239eed23cc3e60317ffe8b09d6beb0abf3 includes the 2354 individual route counts and ranks plus the extra chart-585 separator. Reopen if a new word changes a route's rank or if a different paid route supplies an independent direction before the tested read and retains its required original return. Ali Romman supplied the native word and its signed caller, Clear1nsight and the retained authors supplied the literal and pricing machinery, and R354–355 supplied the earlier cut and receiver forms. OpenAI Codex materially assisted the independent implementation and verification.

```sh
python3.12 -IB audit.py --peer PEER_8027 --accept R352_ACCEPT.json \
  --r354-code R354_INDEPENDENT/audit.py --r355-code R355_INDEPENDENT/audit.py \
  --r355 R355_INDEPENDENT/receipt.json --out fresh.json
```
