# Round 342 — the bounded power-18 screening run was capped

**CAPPED / UNRESOLVED.** The price, limiting comparison and two nonroot source inequalities passed. The sole primary discovery run stopped during root-capacity arithmetic, before checking any finite height or Newton coefficient. No candidate or campaign κ gain was certified by this run.

| Evidence | Result |
| --- | --- |
| Comparator | The complete Round 341 supplier at κ=0.00387992804544, p=19, J=747. Scientific receipt SHA-256 42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd. |
| Frozen case | p=18, h=1804, μ₁=749/1000, B=5/2; x cut k₀^(7/8); 32 explicit heights and 19 Newton terms on each side. Exact source pins are in primary.json. |
| Necessary pricing | At total signed/cover/ordinary prices, conditional on the unproved contractions, the base, carrier and tail guards admit J=708. The seven-stage cap is 0.00387992804555917. The prospective tested point 0.00387992804554 gives prospective claim 0.00387992804547, exactly 0.00000000000003 above the comparator; its predicted separation above the generous old ceiling is 209/33400000000000000. |
| Terminal limit | (749/1150)^18 < 0.000444745531; (5/2)η_lower >0.000472218048. |
| Unchanged paid band | Complete t-fraction lower bound >0.9602565264. For a partial sibling family below threshold the multiplier exceeds 2.7368278715. For the admitted unsplit band it exceeds 10.9015101059. |
| Capped | The last confirmed step was both nonroot branches. The next gate is the price of the small-x root and the upper root/exit mass bound. Small-x coefficient rows 0–18, large-x heights 0–31 and shifted coefficient rows 0–18 all remain unresolved by this primary run. |

**Timing and verification.** Source tracing began 16:42:26 UTC, implementation started at about 16:42:55 and syntax validation was complete by 16:43:52. The single scientific run started 16:44:26.910. Necessary price/terminal completed at +0.00106s; nonroot guards finished at +41.560s. The 45-second discovery alarm was delivered after a long arithmetic primitive returned. Elapsed time was 65.275s (65.15s process CPU), 5.275s beyond the 60-second total allocation. No second scientific run was started. The intended in-run reserve was lost. Receipt readback and hash validation after exit confirmed the specific positively checked subset; no hosted or complete application replay was run by the builder.

**First restart action.** Fix the directed logarithm endpoint for the exact integer one in `power_lower`: use `upper_log_b = F(0) if b == 1 else F(Decimal(b).ln().next_plus())` when subtracting log(b). In Decimal's default exponent range, taking the next representable value above exact zero before converting to Fraction creates an approximately million-decimal-place denominator. The source bound needs the exact zero for log(1). Preserve all other enclosures and the frozen p, h, partition and controls. Authenticate and reuse the saved price/nonroot fields to restart at the root gate; do not broaden the experiment. Arrange a fresh wall-clock limit in a supervising process and persist progress before each long operation so a deferred Python signal cannot consume the reserve. A restart needs another authorized budget. An independent proof, if obtained, is separate evidence and should be identified separately.

Original CPython 3.12 entry point, recorded **as run**:

```sh
python3.12 -IB campaign-20261120/round342/screen.py --campaign-root campaign-20261120 --out campaign-20261120/round342/primary.json
```

Original script SHA-256 10cbcc0fe5c7f44c9a2852a13e6acdf87b52471d52b9685c579c05fc63aab2ea. Capped receipt SHA-256 3102b30dd179473189560b3181f072561c490a956571949b672b7c4c9954bcca. The R341 source grouping is due to the preceding #8026 work on the Pascal compiler of Jacob Alan Sussman, the ambient proof of DreamingOfClouds, zxv's weighted exits and Clear1nsight's original #7863 word. R336 supplied the measured tilted mean and variance; R339 supplied the positively charged moments.
