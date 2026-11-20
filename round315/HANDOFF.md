# Pure midpoint helper split on the 680-owner BIT word

**No verified κ gain.** A zero-paid birth would let an old helper `h` return at an intermediate chart and let a fresh independent value from that chart take its place at the old terminal. The proposed edit reads exactly `x_h` at the midpoint, then adds `w + x_h` to original sends whose combined effect on all outputs is exactly the singleton `e_h`. Its two strictly positive daughter grades sum to the original grade. This would give positive productive credit at every exponent strictly between zero and one, before full construction, ordinary compilation, precision and tape accounting.

On exact #7830 both the prefix read and the suffix write would have to exist at the same chart. The test grants every arrival and every send over the entire word. It counts 636 charts, 458 productive helper owners, and both orientations. Of 582,576 triples, 524,368 have strictly intermediate dimension. **Zero** of these admit both singleton directions even before testing exact nesting or clocks. All declared cases are resolved. Mixed directions, jointly transformed terminal banks, added traffic and changed source words remain open. First test for a calibrated variant: take a permitted nonzero direction supported at the start bank and require its response to lie inside the terminal bank; then reconstruct the calibrated read, injection, terminal return and the independent new input in chronological order.

## Replay

Use CPython 3.12 with assertions enabled. From a fresh copy of this handoff run the following commands. The two scripts authenticate the three downloaded files. `result.json` identifies every dimension-eligible helper by its bit in the chart's hexadecimal mask.

```sh
set -eu
root=inputs315
word=inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz
edge=inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py
literal=upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py
for file in "$word" "$edge" "$literal"; do mkdir -p "$root/$(dirname "$file")"; done
curl -fLsS https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/binary/WORD.json.gz -o "$root/$word"
curl -fLsS https://raw.githubusercontent.com/aliromman/integer-mult-bounds/4f7c67ae387cc91580f469aeda4d508b372b9ec1/research/p104-dual-supplier-lift/bit_native.py -o "$root/$edge"
curl -fLsS https://raw.githubusercontent.com/Clear1nsight/integer-mult-bounds/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/review/binary_operator.py -o "$root/$literal"
python3.12 -IB birth.py "$root" fresh.json
python3.12 -IB check.py "$root" fresh.json fresh-replay.json
```

The original local replay used the already authenticated equivalents in Round 308. The exact graph check took 0.187 s under its 60-second cap. The independent implementation ran the literal forward and adjoint tapes, checked all 680 public outputs and 3,554 dirty retirements per orientation, and reproduced all counts in 0.310 s. Hosted checks were unrun for this handoff.

Clear1nsight supplied the word in #7786, the mixed supplier and the independent literal tape engine in #7830. Ali Romman supplied the #7776 graph and the productive endpoint checks. The #7781/#7786 births used paid subdivisions and more general calibrated directions. Earlier #6197 addresses a distinct paid ascent on #6030. The canonical campaign comparator was independently reproduced at 0.00387992803556, head `87fbf4f7b35b0f18ab12b5767775a9a424cf0b15`. OpenAI Codex materially assisted the screening argument and its two verifiers.
