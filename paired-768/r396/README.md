# Literal K7 opening floor and signed price

Exact candidate `04228ea5a1292cf8526a20037060f6fc6e15a858` binds the lower ordinary opening floor of 18,960 and finite debit 1405/1024 to all five ordinary recipes. The independent and registered replay certify κ = 0.00389821126, an increment of 23/100000000000 over independently reproduced Round 394 at κ = 0.00389821103, exact head `19e67d1b36210e3047bbf3d04625d1262cba672a`. The fully charged recurring log₂ cost is at most 318,292,711, a reduction of 320. [Exact comparison](../r394/README.md) · [Arithmetic and physical preflight](../r395/README.md) · [Detached proof](PROOF.md)

The literal occupied K7 edge 49→64 runs 323,165 opens and closes and returns 432 paid prefixes. Independent accounting over all 2,907 bins gives 684,229,811,300 raw axes less 524,064,768 timed returned axes, charging exactly 683,705,746,532 singleton axes. The first two widths 18,952 and 18,954 return 108 and 120 prefixes. The old opening floor fails the new directed factor cap, and the old debit fails at the new heights even with ideal intermediate pricing. The signed phase and owner tests retain all 81 modulo-3 and 6,561 modulo-9 records, and both Gaussian placements retain period 1,364 at the two actual heights. [Sealed detached receipt](verified.json) · [Literal build log](build.log)

The first literal regeneration failed in the raw-stage patch context. Restoring the exact trailing context fixed it. The final bounded local build passed in 77.395 seconds. Metadata and committed-byte checks passed. All seven local registered scientific modes passed in 243.82 seconds, including the genuine nested loan with 4,507,783,464 axes, both owner returns, exact signed product −345550037539 and input restoration. Exact repository onboarding passed all 760 tests with 31 skips in 136.521 seconds. The registered historical replay passed its 19 controls. [Metadata and commit evidence](preflight.log) · [Complete local scientific replay](scientific.log)

Use CPython 3.12 and Git. From the clean exact candidate checkout root, run the full registered scientific replay.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-ordinary-floor
```

For the detached proof, set `CANDIDATE` and `COMPARATOR` to clean Git checkout roots at the exact commits above. Run from this handoff directory.

```sh
out=$(mktemp -d)
python3.12 -IB replay.py --candidate "$CANDIDATE" --comparator "$COMPARATOR" --out "$out/verified.json"
cmp "$out/verified.json" public-verified.json
```

The portable checker passed from two newly initialized exact Git roots, with no mutable pointer or prior temporary state. A repeat at the exact checkout roots took 0.36 seconds. The checker reproduces the sealed receipt byte for byte after substituting two redacted traceback digests and the consequent change to one completed-log manifest digest. The original sealed receipt is unchanged. [Public receipt](public-verified.json) · [Digest substitutions](PATH-REDACTIONS.json)

Ali Romman supplied the signed caller and original physical transfer, receiver and clock proofs. SYLforge supplied K7. Round 394 supplied the exact comparator and finite debit. Round 395 supplied the directed price and independent occupied-edge audit. OpenAI Codex assisted the construction, proof and independent replay. [Typed source #8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
