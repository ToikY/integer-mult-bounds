# One-packet repair after two deletions on the same BIT route

**No verified κ gain.** The exact 680-owner binary word supplied by #7786 and used in #7830 contains 2,874 paid packets. It has 759 pairs of packets traveling on the same directed chart route, across 246 repeated routes. Every pair has a rank-two public defect when both deliveries are suppressed and all other equations are frozen. A single scalar packet with any available input form and any downstream output response can change the public operator by rank at most one. None of the 759 pairs can therefore be repaired by that single replacement. This conclusion allows an optimistic choice of the new packet's clock, readout and output pulse. Changed background transfers, multiple replacement packets, and nonlocal ordinary operations that independently supply another direction remain unresolved. The proposed gross saving was one paid packet at its route's grade per native invocation, before paying for any repair.

## Rank check

Let V_i,V_j be the two original payload rows in chronological order and C_i,C_j the public responses to single arrival pulses. Setting both arrivals to zero changes the public transfer by

```
(C_i + β C_j) V_i + C_j V_j,
```

where β is the effect of the earlier pulse on the later sender. The two-column correction is triangular and invertible over GF(2). Thus whenever both old rows and both old columns are independent, the full defect has rank two for either β. The primary verifier enumerated every pair in clock order and found two independent rows and columns each time. The independent implementation replayed all 680 basis inputs together on the literal tape, zeroed the two delivered payloads at the exact clocks, subtracted the intact public output and row-reduced the actual defect. All 759 defects had rank two. The unedited control had rank zero. An individual deletion had rank one. Complete source ownership replay checked 3,554 dirty retirements in each orientation.

## Replay

From this handoff, with CPython 3.12 and assertions enabled:

```sh
set -eu
root=inputs320
word=inputs/7786/research/p104-iterated-returns/binary/WORD.json.gz
edge=inputs/cache/source/research/p104-dual-supplier-lift/bit_native.py
literal=upstream-cache/research/p104-mixed-rank-supplier/review/binary_operator.py
for file in "$word" "$edge" "$literal"; do mkdir -p "$root/$(dirname "$file")"; done
curl -fLsS https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/binary/WORD.json.gz -o "$root/$word"
curl -fLsS https://raw.githubusercontent.com/aliromman/integer-mult-bounds/4f7c67ae387cc91580f469aeda4d508b372b9ec1/research/p104-dual-supplier-lift/bit_native.py -o "$root/$edge"
curl -fLsS https://raw.githubusercontent.com/Clear1nsight/integer-mult-bounds/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/review/binary_operator.py -o "$root/$literal"
python3.12 -IB pairs.py "$root" fresh.json
python3.12 -IB check.py "$root" fresh.json fresh-replay.json
```

All three source files are authenticated at read time. Per-route labels, counts and ordered result digests appear in the primary receipt. The primary run took 0.045 s of 60 s; independent replay took 1.348 s of 20 s. Both exited zero. Hosted scientific replay was unrun for this handoff. Upon resumption, a two-delete/one-return proposal must identify an additional independent action from a named earlier encoding or other changed background equation. Replay the new background with both candidate deliveries disabled and require its public defect to have rank at most one before attempting a splice.

Clear1nsight supplied the exact #7786 native word, #7830's five-premise mixed supplier, and its literal tape engine. Ali Romman supplied the #7776 native graph and response computation. The independently reproduced #7830 comparator is 0.00387992803556 at `87fbf4f7b35b0f18ab12b5767775a9a424cf0b15`. OpenAI Codex materially assisted the proof, screen and replay.
