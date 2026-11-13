# Independent inverse census and next version-aware restoration

Exact independently reproduced #7481 head 89eaa9d8cae37c1540de98f2d29a3abaabb96a2b, κ 0.003647081039689, signed #7113 head 07a76c5e2738882c0cb322278e56f6cae3c9885d. Reuse current comparator replay after matching exact source paths and verifier.

## Independent exact census

CPython 3.12.14, standard library, 0.22 seconds wall, 0.20 user, 0.01 sys, exit zero. Authenticated full primary receipt SHA-256 f9afe7f6843947532062156e116f7172510dcc4348e77feb6f95ee8b6dbedf0b. The independent scanner builds a forward chart and lifetime ledger, groups eligible ADDs by ordered operands in chronological order, and computes scalar commutation from both sparse elementary-matrix products. It agrees on 62,945 eligible public ADDs, 4,577 opposite pairs, 1,256 interval incidences and 1,080 incidences with other middle contacts. It checks all 176 selected case keys, exact prices and barrier clocks. Of these, 130 are noncommuting and 46 encounter the protected/owned operand rule. Zero unvisited. The engine independently reconstructed the same scoped guard; it grants no alternate replacement of an inverse by a historical drift correction.

From this directory with explicit R276 replay root and receipt paths:

```sh
python3.12 -I -B check_inverse_independent.py "$R276_ROOT" "$R276_PRIMARY_RECEIPT" f9afe7f6843947532062156e116f7172510dcc4348e77feb6f95ee8b6dbedf0b
```

## Next incremental test

Remove ADD38491, where role1191 subtracts role1261 in chart509, and replace ADD39469 with its exact historical net contribution. Fuse role1261’s ranks3+3 at MOVE38490/39433 into a rank-six 3→770 MOVE at the old second clock. ADD38491 is its sole middle contact. Role1191 is never read between its two changed ADDs. Its three intervening scalar events (38494,38538,38878) only read unchanged donors into 1191. In particular the protected source964 at ADD38538 stays unchanged, even though old 1191's transient destination value differs. All old chart529, owned, COPY and other protected contacts outside the interval are unmodified. Under normalized coordinates there is no observable outlet for the changed transient 1191 before the correction. A dedicated independent replay must prove this for the emitted tape and compare the relevant operand and guard rows, rather than inferring timed protection from equal final output.

Let v be old1261 at pre38491. After its retained updates ADD39435, ADD39438 and ADD39468, the chart246 row is v+(old910@pre39438 + old953@pre39441)/2, because role1145 receives −953 at ADD39441 between the two 1145 reads. Role910 also changes by −894 at ADD39465, and neither historical donor may be used as if its old version were presently coframed. The fixed new correction is that exact historical half-sum. At pre39469 the complete chart246 bank is [1145,1191,1192,1261,1443,1485,1486,1487]. Old1191 is excluded as a donor and its self coefficient stays exactly one. The seven read-only donors include current1261 and the already-paid 1145 arrival via MOVE39467. Their exact support remains unresolved. A separating input excludes this single fixed chart bank. A rational span pass must still have legal coefficients, exact common-grid and precision charges, exact signed forward/adjoint and ownership effects, and a fully charged directed positive price before one candidate build. One case, one cut, 30-second cap, no paid repair.

Complete recursive invoice delta across 17 native copies is paid {3:−34,6:+17}, productive unchanged. Gross lies in [0.25649690068998409,0.25649690068998410] raw, before all ordinary, tape, routing and precision charges. Any added paid rank one per copy costs 17 and does not fit. The original inverse-only census rejects this key because source1261 changes and the fixed structural guard conservatively treats the protected ADD38538 as a barrier. The new edit explicitly leaves the protected donor unchanged and replaces, rather than drops, the accumulated nonzero difference. #7494 covers a distinct fixed single outward ADD slide, and its exact target and operands are held fixed. Refresh exact site overlap before running.

The prepared script was syntax checked, not executed. From this directory with the exact R276 inputs explicitly provided:

```sh
python3.12 -I -B check_1261_telescoping.py "$R276_ROOT/inputs"
```

## Retired alternative

Direct owned1503 529→595 descent at old MOVE39820 would replace ranks1+5 by rank6 after dropping MOVE39814. Its paid path no longer supplies the old contribution to public497 at ADD39815; both 992's old ADD39817 and owned1532's old ADD39876 also consume 497 before it leaves chart520. Public497's next chart914 is incomparable to529, so changing its earlier arrival to529 would require a new paid itinerary. Adding a rank-two 529→127 lift to public146 and changing its target rank7→9 is already negative even granting these early repairs free. Its signed gross is 17(H1+H5+H9−H6−H2−H7), enclosed by exact endpoints −317196413477620733789673300436945965622372291927/2500000000000000000000000000000000000000000000000 and −126878565391048293515869320174687936637972242353/1000000000000000000000000000000000000000000000000. This is approximately −0.1268785653910483 raw. Role146 also has later old reads in chart529 after ADD39882. Do not build this variant. #7489 covers the distinct original owned1532 MOVE39884 removal using one retimed 992 path.

Credit #7481/#7480 native chronology, #7113 caller, #7003 structural commuting and #7494 timing, #7482 exact covectors and #7298 directed pricing. Only the independently authorized inverse census ran in R276. No public writes or new discovery solve.
