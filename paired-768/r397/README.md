# Matched-clock ordinary and Gaussian height preflight

The comparator is fully replayed Round 396 at `04228ea5a1292cf8526a20037060f6fc6e15a858`, κ = 0.00389821126. One proposed terminal vector changes ordinary heights to `(8192, 124986, 524288)` and Gaussian height to 490,463. It retains the same K7 floor 18,960, ordinary debit 1405/1024, Gaussian debit 64,944/524,288 and signed word. The directed invoice supports prospective κ = 0.00389821380. The exact old ideal ordinary ceiling and old Gaussian rate each fall short. **No verified κ gain.** [Exact comparator](../r396/README.md) · [Directed proof and both controls](audit/PROOF.md)

The ordinary decrease saves 1,144,000 log₂ clock units, and the Gaussian increase costs exactly that amount. The resulting complete log₂ C ceiling stays at 318,292,711 while the entry conversion rises from 514 to 515 bits. The largest native height is 524,288, requiring 20 descriptor bits and fitting the unchanged setup budget. The actual header is 2^1148403+4. Both signed tiers clear 54 strict and four functional conditions. [Exact complete price receipt](price/receipt.json)

The independent audit checks the five ordinary opening interfaces, adjacent cut and predecessor clipping at the two changed ordinary seams, actual direct and compiled caller geometry, and both physical Gaussian placements. The new height keeps the 112→258 share 1/624, first tickets (0, 272, 545), period 1,364 and signed swap 1→272. The modulo-3 and modulo-9 signed tape checks compare all 81 and 6,561 records and reject the wrong return sign. The separate exact all-size proof retains the existing five premises. One candidate and its two old-cap controls were tested. Other height vectors remain outside scope. [Original independent physical receipt](audit/receipt.json)

Use CPython 3.12 and Git. Set `COMPARATOR` to the clean checkout root at the exact Round 396 head. Run from this handoff directory.

```sh
out=$(mktemp -d)
python3.12 -IB replay-price.py --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check.py \
  --capsule "$COMPARATOR/research/p104-weighted-ordinary-floor" \
  --baseline-receipt evidence/round396/independent/verified.json \
  --baseline-log evidence/round396/scientific.log --out "$out/audit.json"
cmp "$out/price.json" price/public-receipt.json
cmp "$out/audit.json" audit/receipt.json
```

The sealed directed price took 0.090 seconds under its 60-second cap. Portable replay reproduced its exact comparison fields from a fresh Git root in 0.107 seconds. Only the predecessor onboarding traceback digest differs. The original physical audit ran in 6.736 seconds under its 90-second cap. Its sealed hash was authenticated during packaging. [Sealed and public log maps](price/COMPLETE.json) · [Public log map](price/COMPLETE-public.json) · [Portable price receipt](price/public-receipt.json)

The next gate is one literal terminal profile and its complete independent signed replay. Ali Romman supplied the typed weighted source, signed phase and native tape work. SYLforge supplied K7. Round 396 supplied the exact lower cutoff and complete signed comparator. OpenAI Codex assisted this preflight. [Original weighted source #8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
