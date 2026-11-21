# A complete paid-mean bound for the paired supplier

On Ali Romman’s exact 768-factor #8027 binary word, the normalized paid mean is at most **0.66820519647103349021** after charging every split slab and positive remainder. The literal program retains the cost of specializing discarded productive outputs. The proof identifies zero extra recursive labels and retains both ordinary boundary records per original product. [Paid inventory and proof](r349/PROOF.md) · [Exact peer source](https://github.com/CrocSwap/integer-mult-bounds/tree/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain)

For the proposed one-case certificate at power 128, scale 1024 and Bernoulli mean bound 3/4, two exact computations find that coefficient 8 exceeds even the upper capacity bound. Coefficients 0–7 passed and the separate leading-term check passed at 128. Coefficients 9–127 remain untested. This excludes that coefficient argument. Individual input lengths and other all-height proofs remain open. [Independent obstruction](r349/receipt.json) · [Primary obstruction](r349/primary.json)

Use CPython 3.12 and the standard library from the handoff repository root.

```sh
python3.12 -IB paired-768/replay_r349.py
```

The command authenticates the pinned peer archive, paid inventory and predecessor receipt, then compares the fresh obstruction byte for byte with the saved independent result. The first decisive follow-up is the same fixed coefficient-8 test with mean bound 67/100, which the completed paid inventory already supports. The signed comparator at this checkpoint is 0.00389011519729. The failed degree-eight check contributes zero additional campaign gain. [Predecessor signed receipt](inputs/normalized-REPLAY.json) · [Independent signed acceptance](inputs/normalized-ACCEPT.json) · [Campaign PR](https://github.com/CrocSwap/integer-mult-bounds/pull/8029)

## Follow-up at mean 67/100

The follow-up passed the previously failing degree eight. It then failed at degree eleven. Heights 11 through 17 also fail the proposed finite-height envelope. Degrees 12–127 remain unresolved, and 128 has a separate leading-term guard. These two cases retire the scalar Bernoulli comparison for this campaign. The first test of a different mechanism is to charge the upper tail of the full 768-factor paid distribution at cutoff 4/5, including the positive split excess, and bound the norm of the sum of exit logs. [Second exact proof](r350/PROOF.md) · [Independent receipt](r350/receipt.json) · [Finite heights](r350/primary.json)

To replay the follow-up, run this from the handoff repository root with a fresh output path.

```sh
cd paired-768
python3.12 -IB r350/audit.py --predecessor-checker r349/audit.py --predecessor-price r349/receipt.json --accept inputs/normalized-ACCEPT.json --application inputs/APPLICATION.json --archive inputs/APPLICATION-SOURCES.tar.gz --binary inputs/covered-BINARY.json --prior-price inputs/normalized-PRICE.json --weighted inputs/WEIGHTED-EXITS.md --out new-r350.json
```

The expected SHA-256 is `ea84892ef2b2da5572e7cdabe54d228ee74f6671d11f87bd6aa263306fd8ffdc`.

## Round 351 · verified paid-tail bound

The paid rank above fraction 4/5 of the log cutoff contributes less than 9.804 × 10⁻⁹ of the completed weighted distribution, including the positive cost of splitting. This bounds its degree-128 norm by 9/10. The triangle inequality reduces every nonnegative integer height to two endpoint comparisons. Both pass. The fixed carrier now uses terminal numerator 4876 and its complete signed result is **0.00389011526022**, up 0.00000000006293 over the previous complete step and **0.00000000018372** (approximately **+0.00000472273946623954%**) over #8027. The complete 36/48-call replay took 76.71 s. Separate signed acceptance took 0.66 s. [Source proof](r351/PROOF.md) · [Signed replay receipt](r351/signed.json) · [Independent invoice and controls](r351/accept.json)

From `paired-768/`, the following rebuilds the independent component receipt. The signed application and invoice have separate receipts above.

```sh
python3.12 -IB r351/audit.py --law-checker r349/audit.py --law-receipt r349/receipt.json --failure r350/receipt.json --accept inputs/normalized-ACCEPT.json --application inputs/APPLICATION.json --archive inputs/APPLICATION-SOURCES.tar.gz --binary inputs/covered-BINARY.json --prior-price inputs/normalized-PRICE.json --weighted inputs/WEIGHTED-EXITS.md --out new-r351.json
```

The expected SHA-256 is `0f43bebea0a8a4a258e14ea7495ed9d2bdbfe8f952dafd423d7e1651b4807332`. The next test prices degree 40 from the distribution of the 768 constituent paid factors. It must pass all-height endpoint, terminal and ordinary-stock bounds before signed replay.

## Round 352 · verified fortieth moment

All 41 terms of the falling-factorial expansion agreed exactly with a separate enumeration of 769 binomial outcomes. The resulting bound on the fully charged paid logarithms passes at both endpoints for every height. With terminal numerator 1524 the complete conditional bound reaches **0.00389011527141**. That adds **0.00000000001119** over Round 351. The total gain over #8027 is **0.00000000019491**, or **+0.00000501039162510749%**. The unchanged five premises and signed caller are listed in the acceptance. The full signed replay took 74.47 s, followed by a separate 0.508 s invoice check. [Moment proof](r352/PROOF.md) · [Full signed receipt](r352/signed.json) · [Independent acceptance](r352/accept.json)

From `paired-768/`, this command reproduces the independently computed price, SHA-256 `5c9d36bad5d7fca162d135e9d8658ab408a6d89edd262be167747cc164c12229`.

```sh
python3.12 -IB r352/audit.py --law r349/audit.py --mean r350/receipt.json --old-primary r351/primary.json --old-independent r351/receipt.json --signed r351/signed.json --accept r351/accept.json --application inputs/APPLICATION.json --archive inputs/APPLICATION-SOURCES.tar.gz --binary inputs/covered-BINARY.json --weighted inputs/WEIGHTED-EXITS.md --out new-r352.json
```

At this point the fixed trial rate is itself below the relaxed comparison ceiling. The next test targets the physical paid word. Count all consecutive unobserved same-owner transfers and check whether a single legal replacement across the same endpoint charts saves paid work.

Ali Romman supplied the paired word and application. Clear1nsight supplied the inherited compiler and independent signed reader, Jacob Alan Sussman the integer flow, DreamingOfClouds the ambient-cap compiler, and zxv the weighted-exit argument. The original 451-factor #8026 analysis supplied the charged split-uplift bound. OpenAI Codex materially assisted the proof, implementation and independent replay. [Predecessor notices](inputs/PARENT-NOTICE) · [Weighted-exit proof](inputs/WEIGHTED-EXITS.md)
