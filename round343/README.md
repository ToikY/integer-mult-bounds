# Round 343 — primary replay and independent signed consumer agree

The same frozen p=18, h=1804 source-capacity certificate that timed out on the Round 342 primary runner passes with corrected exact endpoint arithmetic. Its certified conditional κ is **0.00387992804547**, compared with **0.00387992804544** for the preceding p=19/J747 proposal. The increase is exactly **0.00000000000003**. This is one construction and one gain shared by the independent Round 342 result and this completed primary replay. The R342 primary receipt remains capped.

| Gate | Verified outcome |
| --- | --- |
| Physical and source premises | Same original #7863 451-factor word, fixed carrier, stock, signed caller, ownership, routing, precision, tape and recovery. All four source receipts are authenticated before pricing. |
| Source geometry | The paid band exceeds 0.9602565264 of the completed t-weight. Both nonroot lower bounds exceed 5/2. The low-x root inequality passed; the large-height upper bound on root t-weight relative to exits is at most 10⁻²⁵ at G=32. |
| All-size contraction | 19 small-x Newton ratios at shift zero, 32 explicit large-x heights 0–31, and 19 shifted large-x ratios at shift 32 all match independent rational values exactly. Both highest Newton ratios occur at j=18 and are below 0.000444745531; both capacity lower bounds exceed 0.000472218048. The closest explicit ratio-to-capacity comparison occurs at G=31 and is below 0.538. No unvisited height remains in this certificate. |
| Complete comparison | J=708; seven strict ordinary prices give cap 0.00387992804555917, and the complete signed consumer tests 0.00387992804554. The claimed point clears the generous p19 complete ceiling by 209/33400000000000000. Every stage, the cap, tested point, claim and strict separation matched the independent result; the signed receipt independently binds the consumer files and controls. |

**Reproduction.** From the sealed campaign checkout with CPython 3.12, choose a fresh output path and run

```sh
python3.12 -IB campaign-20261120/round343/run.py --campaign-root campaign-20261120 --out round343-replay.json
```

The supervisor isolates the child in a separate process group, imposes a 45-second wall-clock deadline using SIGKILL, and retains the last atomically persisted stage on a cap. Fifteen seconds of the 60-second round are reserved for receipt checks. The R342 screen is authenticated at 10cbcc0fe5c7f44c9a2852a13e6acdf87b52471d52b9685c579c05fc63aab2ea; both endpoints of log(1) are replaced with exactly zero. The R342 price, limiting test and nonroot bounds must still match its sealed receipt, SHA-256 3102b30dd179473189560b3181f072561c490a956571949b672b7c4c9954bcca. All scientific and verification results otherwise come from the same frozen case. The timestamped JSON contains all original input hashes, seven stage records, source bounds and all 70 ratios. Runtime metadata will vary across clean replays.

| UTC event, 2026-11-21 | Timing |
| --- | --- |
| Source and control inspection | 16:47:14–16:47:32 |
| Endpoint and external watchdog implementation | 16:47:32–16:48:22 |
| Prelaunch receipt and schema checks | 16:48:22–16:48:29 |
| Single supervised replay | 16:48:43.317–16:48:43.374, 0.057225 seconds including child startup |
| Independent and signed receipt match complete | 16:48:43.375, 0.058216 seconds from supervisor launch |

Sealed primary SHA-256 846c6441860cf5e91cf958a7f4a77e7bdf5befa8c519b82a157142f34535c4e9. Independent scientific receipt f91280ef454af5d74559788e7f63fd442d8778937c52575160be2718354defcd. Independent signed binding 148a6315592977093c90de293ca3a904da5cf8dd2fa7840d3a23538d1a87857b. R343 reused the existing independently run consumer, with no new hosted job launched by the primary runner. The prior full consumer and any hosted publication results are tracked separately by the lead.

Clear1nsight supplied #7863's word, Jacob Alan Sussman the finite integer flow, DreamingOfClouds the ambient-cap lemma, and zxv the weighted-exit method. The previous #8026 work supplied R336’s paid variance, R339’s moments, R341’s sibling/multiplicity and ordinary-price bounds, and the independent signed application. The new scientific change is the p18 height-dependent root/exit comparison and paid-band nonroot bound. The R343 implementation fixes the replay endpoint and enforces the time limit externally.
