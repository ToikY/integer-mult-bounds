# Round 444 independent exact-source price replay

I verified checkout HEAD `fae237c8aee774bb2256d4e394fed9f3934147c2` and sealed handoff HEAD `9e87f3be3e84db5660503419d2095cdf6d4ff5a0`. From the Round 444 artifact, I replayed `draft/check_periodic_bill.py` with CPython 3.12 and assertions, the exact package root, `paired-768/r438/check_minimal_debit.py` and the explicit `paired-768` handoff root. It used fresh external temporary storage, completed in about 0.43 seconds and exited zero with byte-identical SCREEN.json. The script installs only the authenticated predecessor inputs needed for the price screen. No candidate or full native scientific suite ran.

The replay reconstructed all 24 price cells under the actual full-reserve K7 profile. Both exact precisions put the new upper charge strictly below the lower allowance for `1411926/2^20` and the previous lower charge strictly above the upper allowance. I independently subtracted the upper new charge from the lower allowance and matched both positive gaps.

| Directed precision | Exact funding reserve |
| --- | ---: |
| 112 bits | `1555506701510330659094621263/2^112` |
| 192 bits | `1880492214039424829205995690919675350250729587232834/2^192` |

The source compatibility proof is recorded in [proof-review.md](proof-review.md). It applies the primitive bound to the matched interior sum, keeps both error concessions and leaves all unmatched, late, exterior, padding, reserve, precision and signed tape charges in the invoice. The measured factor priced those same terms under tariff `5024210149/2152336000`, reserve 256/255 and geometric budget 2401. This scope tests only the adjacent debit. No smaller debit or global optimum is claimed.

Independent renewal of the exact fixed recurrence matched the old, tested and Gaussian ceilings. The new projected booking `0.003900862349171` clears the entire preceding ordinary crossing and lies below the new ordinary crossing. Its next tick fails ordinary and Gaussian remains slack. The exact projected gain over the reproduced #8098 is `3/10^15`, with entry conversion 242079 and recurring log₂ C 171810078109. No gain is certified here. The next gate is one literal proof, receipt and selector overlay, with exact retained and failure controls, then complete independent signed replay.
