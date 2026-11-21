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

## Round 353 · no same-register fusion on the exact word

The 2,803 paid MOVEs use 2,803 distinct private registers across all 39,600 clocks. No private register receives two MOVEs, even before checking intervening observations. The corresponding family has exactly zero possible saving on the 36-call signed bill. Both native orientations were checked on all 630 public columns. The independent scan took 0.253 s. [Proof and source pins](r353/PROOF.md) · [Exact census](r353/receipt.json)

From `paired-768/`, run `python3.12 -IB r353/audit.py --peer inputs --accept r352/accept.json --out new-r353.json`. The expected SHA-256 is `6b16cc29bbe0901772a5fe8426e613247931bb0ec7b612d84aed741c21780721`. A different edit would have to remove or reroute a single paid transfer. The unique rank-seven MOVE at clock 15264 gives a concrete starting point for testing exact forward and adjoint support.

Ali Romman supplied the paired word and application. Clear1nsight supplied the inherited compiler and independent signed reader, Jacob Alan Sussman the integer flow, DreamingOfClouds the ambient-cap compiler, and zxv the weighted-exit argument. The original 451-factor #8026 analysis supplied the charged split-uplift bound. OpenAI Codex materially assisted the proof, implementation and independent replay. [Predecessor notices](inputs/PARENT-NOTICE) · [Weighted-exit proof](inputs/WEIGHTED-EXITS.md)


## Round 354 · an explicit missing output

The unique rank-seven MOVE, clock 15264 on owner 3226, carries a parity of 113 independent input coordinates. Its adjoint depends on output coordinate 171. Clearing the carrier on chart 0 and creating a zero on chart 585 toggles output 171 on basis input 4. This rules out the zero-cut edit at exactly one of the 2,803 paid operations. The other 2,802 were outside scope. The only later ADD that reads this carrier is at clock 30338. [Counterexample](r354/receipt.json) · [Proof and declared scope](r354/PROOF.md)

From `paired-768/`, run `python3.12 -IB r354/audit.py --peer inputs --accept r352/accept.json --scan r353/receipt.json --out new-r354.json`. The expected SHA-256 is `1c82c88222277886117a5c2a5e23220abd5d69f7967b54256fc64ecc025f5015`.

## Round 355 · no local XOR repair at the first read

At clock 30338 the four legal alternative donors are 1913, 2607, 2612 and 3430. Their rank is four. On basis input 171 each donor is zero and the required value is one. Allowing the receiver's current value adds no direction. A separate check found that basis input 60 also separates the target. The test excludes every local XOR combination at this chart and clock. An earlier change to an arrival remains open. [Independent proof](r355/PROOF.md) · [Exact separator](r355/receipt.json)

From `paired-768/`, run `python3.12 -IB r355/audit.py --peer inputs --accept r352/accept.json --source r354/audit.py --previous r354/receipt.json --out new-r355.json`. The expected SHA-256 is `e500abed99a9caf5d4633ef77b119d05bace82adb5b3c9d16cf0f2e30ec031fd`.

## Round 356 · independence on every ordered route

Group all 2,803 paid forward forms by ordered source and destination. Each of the 2,354 groups has full rank, even allowing a free cache of all earlier deliveries. The potential saving from replacing a sender's form by same-route earlier deliveries is zero across all 36 calls. At the separate chart-585 control, the five forms remain independent immediately after clock 30338. Input 171 XOR input 604 annihilates four named donors and selects register 3430 at 30339. This avoids a redundant four-donor build. Cross-route encodings and changed allocations remain open. [Route census and exact witnesses](r356/receipt.json) · [Proof](r356/PROOF.md)

From `paired-768/`, run `python3.12 -IB r356/audit.py --peer inputs --accept r352/accept.json --r354-code r354/audit.py --r355-code r355/audit.py --r355 r355/receipt.json --out new-r356.json`. The expected SHA-256 is `245c57639941873096fd13f2962a7a239eed23cc3e60317ffe8b09d6beb0abf3`. The next independent test checks the downstream adjoint forms on those same routes.

## Round 357 · independent downstream demands

All 2,803 adjoint forms are nonzero. Their ranks sum to 2,803 across the 2,354 ordered routes. The optimistic saving from combining proportional or dependent downstream demands on the same route is therefore zero. The test leaves cross-route schedules and new productive helpers open. [Exact reverse census](r357/receipt.json) · [Proof](r357/PROOF.md)

From `paired-768/`, run `python3.12 -IB r357/audit.py --peer inputs --accept r352/accept.json --r354-code r354/audit.py --r356-code r356/audit.py --forward r356/receipt.json --out new-r357.json`. The expected SHA-256 is `ee8e207c2352db335abf746293353aa36039613b589c0042513b6e6fbe0ff599`. The next helper test asks whether two different paid deliveries from the same source chart can carry a fresh input and cancel at every original public output.

## Round 358 · the two-injection helper has no eligible pair

The 2,803 pairs of source chart and full output influence are all distinct. This allows different destinations and tests every paid departure. There is no way in this family to inject one fresh scalar immediately before two transfers on the same source chart while preserving all 630 old outputs. The maximum productive credit for the family is zero. A helper using three or more injections is a separate question. [Proof](r358/PROOF.md) · [Independent receipt](r358/receipt.json)

From `paired-768/`, run `python3.12 -IB r358/audit.py --peer inputs --accept r352/accept.json --r354-code r354/audit.py --r357-code r357/audit.py --r357 r357/receipt.json --out new-r358.json`. The expected SHA-256 is `bc62287d9b4c38a1722eebd98decfdef5c092ddd159795235e77fc8dd78892e1`.

## Round 359 · arbitrary-support helpers on a single source

Every one of the 635 source-chart matrices has a trivial kernel. On the largest chart, all 516 columns are independent. Consequently **every nonempty subset** of immediately pre-MOVE injections on one unchanged source chart alters at least one old public output. Allowing a free terminal decoder still gives zero possible productive credit. Other source charts, physical substitutions and different injection clocks remain open. [All chart ranks](r359/receipt.json) · [Independent proof](r359/PROOF.md)

From `paired-768/`, run `python3.12 -IB r359/audit.py --peer inputs --accept r352/accept.json --r354-code r354/audit.py --r357-code r357/audit.py --r358-code r358/audit.py --r357 r357/receipt.json --r358 r358/receipt.json --out new-r359.json`. The expected SHA-256 is `5a093254a2244c6289fb13aff19fd18eae5ec7b59d87d1e84a0023adc9a42d1c`.

The earlier matched solver comparison is also replayable from this directory with `python3.12 -IB r356/timing.py . new-timing.json`. Elapsed times depend on the machine. Both modes must produce the same rank, separator and full independent receipt. The recorded comparison was inconclusive for end-to-end speed, so the exact solver remains the default. [Recorded timings](r356/timing-result.json)

## Round 360 · every opcode-preserving single-frame substitution

There are 261,620 assignments of a different catalogued label to one of the 412 eligible original labels. Of those, 61,377 leave the dimension and price unchanged, and 104,059 violate a required positive paid or productive gap. The other 96,184 have 37 distinct complete profiles. Even before downstream costs, each has negative absolute signed margin at the comparator. Its margin decreases throughout the interval to the rational supplier ceiling. This exhausts the specified family while retaining all original MOVE opcodes and protecting the first 222 public endpoints. [Exact profile receipt](r360/receipt.json) · [Proof](r360/PROOF.md)

From `paired-768/`, run `python3.12 -IB r360/audit.py --peer inputs --accept r352/accept.json --out new-r360.json`. The expected SHA-256 is `5874d9ebb3838cd7bb4bed94c1c8dbb4845f468324dddde146b3111a773fe564`. An eligible extension must give a literal treatment of equal endpoints, change more than one assignment, or change the cost another way.

## Round 361 · substitutions that delete literal identities

All 3,010 ordered assignments to an actual neighboring chart were checked. Moving both endpoints to the identical physical frame allows deletion of that MOVE. Even with this credit, 2,552 assignments create another equal-dimension edge between different frames and four violate a productive gap. The remaining 454 give 11 complete invoices, all below the comparator. The most favorable signed margin upper bound is below −35.41835. None reached a build. [Proof](r361/PROOF.md) · [Complete price and scope](r361/receipt.json)

From `paired-768/`, run `python3.12 -IB r361/audit.py --peer inputs --accept r352/accept.json --math r360/audit.py --out new-r361.json`. The expected SHA-256 is `612b209c1567c8a811bfbce9cc50655c74f5c04be234d47db0b433218c09823e`. The next screen allows only one connected group of co-chart values to change, leaving unrelated uses of that label in place.

## Round 362 · every maximal group constrained by ADD

All 29,301 ADDs connect 6,866 live segments into exactly 636 components, one for each atlas label. Every one of the 2,803 paid boundaries and 408 productive endpoints agrees with the original label census. All 261,620 replacements are therefore covered by R360 and R361, including the 3,010 identity-eligible cases. Multiple simultaneous component changes remain open. [Graph proof](r362/PROOF.md) · [Verified scope and controls](r362/verified.json)

From `paired-768/` on CPython 3.12 use a fresh output directory.

```sh
python3.12 -IB r362/check.py --peer inputs --helper r360/directed.py --accept r352/accept.json --out fresh-362
python3.12 -IB r362/verify.py --word inputs/BINARY-CANDIDATE.json.gz --result fresh-362/result.json --r361 r361/excluded.json --out fresh-362/verified.json
```

Expected SHA-256 for `fresh-362/verified.json` is `f9d7dd7e5c19672a61edf9f67fe14deb863ecad872eb1d7c2e1700b0d5bce07b`. The controls reject a changed ADD and an omitted SWAP. The public checkout includes the pinned #8027 binary, application archive and caller plus the #8029 acceptance. The next test permits two coupled assignments and charges each shared edge once.

## Rounds 363–364 · all 197 two-chart repairs with one movable obstruction

The 3,010 original single-contraction seeds have 458 empty obstruction sets, 1,688 with multiple blocking charts, 667 with one protected blocking chart and 197 with one movable blocking chart. In the last group, replacing both incident chart labels by a common frame deletes exactly two literal MOVEs in each proposal. Every proposal clears the signed price screen. All 197 fail physical nesting at a named paid boundary. Independent replay rechecks a nonzero exact rational product and two rank inequalities for every failure. This retires this one-blocker, same-frame repair on the #8027 physical word. Other frame substitutions, new frames, and changes to intervening transport are open. [Case selection and price](r363/PROOF.md) · [Combined scope](r364/PROOF.md) · [All 197 counterexamples](r364/verified.json)

Run on CPython 3.12 from `paired-768/` using new output directories.

```sh
python3.12 -IB r363/repair.py --peer inputs --helper r360/directed.py --accept r352/accept.json --r361 r361/excluded.json --out fresh-363
python3.12 -IB r363/verify.py --word inputs/BINARY-CANDIDATE.json.gz --run fresh-363 --out fresh-363/verified.json
python3.12 -IB r363/repair.py --peer inputs --helper r360/directed.py --accept r352/accept.json --r361 r361/excluded.json --start 128 --out fresh-364
python3.12 -IB r364/verify.py --base fresh-363 --follow fresh-364 --word inputs/BINARY-CANDIDATE.json.gz --out fresh-364/verified.json
```

The first block reaches its 128-case cap. The second exhausts the remaining 69. Expected final SHA-256 is `34647db7214629169a5e1522fab663e9bc06aec13ebcfcd98dce263c68eca283`. Independent discovery took 0.261 s and 0.270 s respectively. The corresponding reserve checks took 0.076 s and 0.088 s. Initial proof and implementation took about 72 s and the final combined verifier took about 43 s to write. No new complete candidate or hosted run was needed for these exclusions. Credits for the literal word, pricing and signed verification appear in the two proofs.

## Round 365 · all adjacent transpositions of unequal-dimension internal charts

All 969 eligible pairs share a real paid MOVE. Swapping the two labels throughout the word preserves the mutual paid edge. Of these swaps, 941 create another paid leg of zero grade between distinct frames. Swapping charts 113 and 276, for example, makes the MOVE at clock 2,130 go from 276 to 277, two different frames of equal dimension. The remaining 28 have one complete signed profile and a raw signed margin strictly below −856.89 at the comparator, decreasing up to the rational supplier ceiling. The price gate excludes all 28 even before extra construction costs. Zero cases remain in this family. [Proof and timing](r365/PROOF.md) · [All original case IDs and decisions](r365/cases.json) · [Independent receipt](r365/verified.json)

From `paired-768/` with CPython 3.12, use fresh output locations.

```sh
python3.12 -IB r365/primary.py --inputs . --out primary-365.json
python3.12 -IB r365/swap.py --peer inputs --helper r360/directed.py --accept r352/accept.json --out fresh-365
python3.12 -IB r365/verify.py --peer inputs --helper r360/directed.py --run fresh-365 --out fresh-365/verified.json
```

Expected SHA-256 for the final independent receipt is `87c2665df6209110a968a93ff4265ac18b7f127e1d08bf5a66c8790f4ef496f4`. Both signed orientations of the original word pass. The reserve reconstructs every zero-grade counterexample and each of the 28 full inventories and detects one extra rank-one charge.

**Paused after Round 365.** Rounds 363–365 add no verified κ gain. The strongest complete result independently reproduced here is #8029 at `c3837013dd7e2c50f6c3065c8f99d52a33b617bb`, κ = 0.00389011527141. The signed replay passed on that exact head. The historical gain over #8027 is 0.00000000019491, exactly (12994/2593410051)%. A subsequent peer reports the same rate on its smaller physical installation. The observed numerical gap to that peer is 0%. The selected record at canonical main remains #7000. [Campaign PR](https://github.com/CrocSwap/integer-mult-bounds/pull/8029) · [Hosted scientific replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/44932940455/job/136934402900) · [Subsequent peer report](https://github.com/CrocSwap/integer-mult-bounds/pull/8030)

If the investigation resumes, rerun the R363/R364 commands to recover the top pair’s exact counterexample at clock 8,105. The first new test would trace whether a different already-paid incoming transport can supply the missing direction before that read while preserving its old outputs. Require the exact sender, receiver, available subspace and restoration clock; price the diversion once across the signed caller before building. That route is untested.
