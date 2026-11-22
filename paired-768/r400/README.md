# Final literal allocation and signed replay

Exact release `2d0d7d378929269b00dcabfac1099b2bb23b3b3b` installs ordinary heights `(8192, 124847, 524288)` and Gaussian height 490,664. It certifies conditional **κ = 0.0038982141167032**. This is **0.0000000003167032**, or **(395879/48727672500)%**, above independently reproduced #8068 at κ = 0.00389821380. It exceeds that predecessor's exact installed Gaussian ceiling by `170173756287357890503/1645720738201600000000000000000`. The predecessor's true ordinary ceiling already covers the new target. Its Gaussian height is binding. [#8068](https://github.com/CrocSwap/integer-mult-bounds/pull/8068) · [Exact comparison replay](../r398/README.md) · [Detached proof](PROOF.md)

The whole-family ceiling is `104641888400286240891629336349/26843545600000000000000000000000` under the native height cap 524,288 and the old signed recurring log₂ ceiling 318,292,711. The middle ordinary height falls from 124,986 to 124,847, and the Gaussian height rises from 490,463 to 490,664. Gaussian heights 490,664 and 490,665 tie. The installed choice 490,664 saves 220 log₂ clock units over the tie and 260 over the comparator, with complete recurring log₂ C ≤ 318,292,451. The 515-bit entry conversion, private control log ceiling 536,870,915, 297.6n-bit live bound, both 54 strict and four functional signed gates, and fixed setup below 2²²⁸ remain charged. [Whole-family preflight](../r399/README.md) · [Sealed literal evidence](verified.json)

The literal calendar runs the occupied ordinary edge through all 2,907 bins, 323,165 opens and closes, 432 paid prefix returns and 683,705,746,532 net singleton axes. The two finite phase fixtures check all 81 modulo-3 and 6,561 modulo-9 records and reject both wrong returns. The literal positive height 490,664 keeps the genuine same-owner period 1,364, tickets (0, 272, 545) and first signed swap 1→272. The bounded literal price, constructor and calendar gates passed in 76.985 seconds, and exact metadata and committed bytes passed. [Build receipt](build.log) · [Static checks](preflight.log)

All seven exact-head scientific modes passed locally in 216.00 seconds. The nonzero nested grant was 4,507,783,464 axes with both owner returns. The exact signed product −345550037539, input restoration and fixed setup checks passed. Onboarding passed 760 tests with 31 skips in 141.786 seconds. The registered historical replay passed its declared partial scope. [Scientific replay](scientific.log) · [Onboarding](onboarding.log) · [Historical replay](historical.log)

Use CPython 3.12 and Git. From a clean checkout of the exact release, run all seven registered scientific commands.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-optimal-allocation
```

For the independent detached check, set `CANDIDATE` to that clean checkout root and `COMPARATOR` to the clean checkout of exact #8068 `8c800e1b6458526e1ce7a59150bba8a0d29d0027`. Run from this handoff directory.

```sh
out=$(mktemp -d)
python3.12 -IB replay.py --candidate "$CANDIDATE" --comparator "$COMPARATOR" --out "$out/verified.json"
cmp "$out/verified.json" public-verified.json
```

The portable checker passed from two fresh exact Git roots in 0.255 seconds. It reproduces the sealed receipt byte for byte after substituting one path-redacted onboarding traceback digest and the three resulting Round 399 manifest and receipt digests. The original sealed evidence is retained. [Public detached receipt](public-verified.json) · [Digest substitutions](PATH-REDACTIONS.json)

Ali Romman supplied the signed weighted native caller and its physical transport, receiver and restoration proof. SYLforge supplied K7. #8068 supplied the exact signed comparator. Round 399 supplied the primary and independent whole-family allocation proof. OpenAI Codex assisted the construction, proof and replay. [#8057 signed provider](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [Original transport](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/TRANSFER.md)
