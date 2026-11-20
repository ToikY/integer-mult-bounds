# Frozen binary word research handoff, Rounds 311–320

**No verified κ gain.** The strongest comparable five-premise witness independently reproduced in this block was [#7830 at 87fbf4f](https://github.com/Clear1nsight/integer-mult-bounds/tree/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier), at 0.00387992803556. It uses 36 binary calls and 48 rational calls. The signed caller's compressed SHA-256 is 757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b. The exact native word's canonical SHA-256 is d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d. The producer and independent five-premise application passed on 2026-11-20. The separate four-premise #7837 claim is 0.00387992802601. Main e54523517d0f03e58352e647c403a5af3e525a57 selects #7000 at 0.00363005817. The peer frontier was refreshed at close. [Baseline receipts and scope](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19776813)

## Reproduce

From this handoff checkout, CPython 3.12 with the standard library is sufficient. A fresh work directory downloads five public files at exact commits, authenticates their SHA-256 digests and reconstructs the saved scientific receipts. The comparison omits elapsed time only. Use an existing input tree with `--input-root`. Large receipts are gzip-compressed. All paths below are relative to this handoff checkout.

```sh
python3.12 -IB replay.py ./work
```

For the final decision alone, run `python3.12 -IB replay.py ./work --round 320`. The final positive control checks the unmodified public map. A single missing paid delivery gives a rank-one defect. Every two-delivery case is identified by the route, packet labels, pair order and per-route digest in round320/result.json.gz. The literal verifier zeroes both deliveries, replays all 680 independent inputs and computes the actual rank of the difference from the original operator.

| Round | Edit and resolved scope | Result |
|---|---|---|
| 311 | Fixed-order one-helper projection and direct return, 916 orientations and helpers | Best directed saving zero |
| 312 | Cheaper sender at the original clock, all 5,748 oriented packets, tested twice | No legal cheaper sender, including receiver-local XOR correction |
| 313 | One direct bridge for a same-endpoint pair-sum, all 151,010 oriented pairs | 18 tied and all others worsened; independent replay and corrupt-packet control passed |
| 314 | Relocate one entire internal chart to an existing chart, 249,555 placements | 987 nesting-admissible, zero improved |
| 315 | Split a helper at a free midpoint, 582,576 oriented chart/helper cases | Zero simultaneous singleton read and return among 524,368 dimension-eligible cases |
| 316 | Relocate a whole helper-only endpoint chart and reprice paid and productive ranks, 12,065 placements | 17 nesting-admissible, zero improved |
| 317 | Relocate one proper connected component of the chart-local dependency graph, 18,415 placements | 6,862 tied and 24 worsened among 6,886 admitted |
| 318 | Read and return mixed directions within one shared-endpoint cohort, 58,512 oriented chart/cohort cases | Of 1,280 nested cases per orientation, none had both a nonzero read and a nonzero write |
| 319 | Any rational replacement frame at one of 393 internal charts, all nine dimensions | 2,320 infeasible, 824 worsened, 393 tied at the original dimension |
| 320 | Replace two same-route deliveries with a single scalar contribution while freezing the rest of the transfer | All 759 pairs on 246 directed routes left a rank-two public defect; none qualifies |

The final discovery used 0.045 seconds of its 60-second cap and the original independent check used 1.348 seconds of its 20-second cap. Every pair in the declared domain reached a decision. Per-round receipts give solver and independent replay times where measured. Source tracing, proof and implementation overlapped and have no reliable separate timing. There is no comparable total-effort measurement showing a workflow speedup. These tests stop at decisive feasibility or raw price gates. The complete new-candidate compiler, ordinary, precision, tape and all-size replay apply only to a surviving edit. None of these edits reached that gate.

## Remaining question

A re-encoding that changes another paid payload can alter the two-deletion defect. On resumption, first name an earlier paid send that can convey one missing direction for one specific pair. Check its sender stock, arrival clock, independent receiver outputs and restoration before pricing the entire repair. A third unchanged equation cannot supply a second direction through a one-dimensional replacement. Round 320 was the stopping point.

Clear1nsight supplied the #7786 word, #7781 helper births, and #7830 supplier and literal tape engine. Ali Romman supplied #7776's graph extraction and endpoint verification. The paired caller retains the #6834/#6980/#7001 lineage. Dugongue’s #7831 and Rohan Arun’s #7835 supplied predecessor finite cutoff schedules. OpenAI Codex materially assisted the constructions, screens, proofs and replays. [Round 309 caller replay](https://github.com/ToikY/integer-mult-bounds/tree/e3b072d1f247b8c950a6b984d0ab0a83d2103e2b/handoffs/bit-idle-endpoints-309) · [Registered Round 310 scientific package](https://github.com/ToikY/integer-mult-bounds/tree/8bd02daca9f4e7a227f6c552905930eed9498655/research/bit-helper-exchange-obstruction) · [Canonical checkpoint](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19777560)
