# Exact preflight for the lower ordinary opening floor

The comparator is the fully replayed Round 394 release at `19e67d1b36210e3047bbf3d04625d1262cba672a`, κ = 0.00389821103. One proposed configuration moves the actual K7 lower band from 32,768 to 18,960, changes the ordinary debit from 703/512 to 1405/1024 and rebalances terminal ordinary heights to `(8192, 129406, 523443)` with Gaussian height 485,263. The signed price supports prospective κ = 0.00389821126 and complete log₂ C ≤ 318,292,711, 320 below the comparator. **No verified κ gain.** The literal installed construction and full independent scientific replay remain separate gates. [Exact comparison and replay](../r394/README.md)

The new full factor lies in [2.588135791280, 2.588135791281]. The new floor clears the directed 1405/1024 factor cap. The old floor's directed lower bound exceeds it and the old 703/512 debit stays a positive comparator control. The unchanged contraction, Gaussian debit, setup and signed recovery remain charged. [Directed price receipt](price/public-receipt.json) · [All-size price and controls](audit/PROOF.md)

The six audited native configurations are the five true binary ranks through the actual opening interface with recorded constructor arguments and one reduced physical Plan on the occupied 49→64 grade edge. The latter runs all 323,165 opens and closes, 432 paid prefix returns and 683,705,746,532 charged singleton axes, and clears all pending owners. Its first two real bands use widths 18,952 and 18,954. Both actual Gaussian placements, including the new height, retain period 1,364 and swap 1→272. The modulo-3 and modulo-9 signed tape controls reject the wrong sign. The reduced finite calendar covers one edge and the exact tested floor. Other floors, other edits and expanded astronomical data remain outside this test. [Independent physical receipt](audit/receipt.json)

Use CPython 3.12 and Git. Set `COMPARATOR` to a clean checkout root at the exact Round 394 head. Run from this handoff directory.

```sh
out=$(mktemp -d)
python3.12 -IB replay-price.py --comparator "$COMPARATOR" --out "$out/price.json"
python3.12 -IB audit/check.py \
  --capsule "$COMPARATOR/research/p104-weighted-ordinary-debit" \
  --baseline-receipt evidence/round394/independent/verified.json \
  --baseline-log evidence/round394/scientific.log --out "$out/audit.json"
cmp "$out/price.json" price/public-receipt.json
cmp "$out/audit.json" audit/receipt.json
```

The portable directed replay passed from a fresh Git root in 0.125 seconds. The adapter checks exact bytes against the sealed receipt after substituting only the predecessor onboarding traceback digest. The original independent physical audit passed in 33.763 seconds of its 90-second cap, and the sealed audit hash was authenticated during packaging. [Sealed price](price/receipt.json) · [Sealed and public log digests](price/COMPLETE.json) · [Public log digests](price/COMPLETE-public.json)

Next, bind the exact binary `Recipe(..., level_floor=18960)` in the signed installer and independently replay the literal floor, header and complete invoice. Ali Romman supplied the signed typed Gaussian calendar and ordinary chronology, transfer and tape proofs. SYLforge supplied K7. Round 394 supplied the 703/512 finite envelope and signed comparator. OpenAI Codex assisted the preflight and audit. [Typed installation #8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
