# Chart-120 paid helper split on the 17-stage P104 caller

The conditional bound improves from κ = 0.003638885999709 in [#7116](https://github.com/CrocSwap/integer-mult-bounds/pull/7116) to κ = 0.003639006653941. The gain is exactly 0.000000120654232. The relative percentage gain is exactly `(12065423200/3638885999709)%`, approximately 0.003315691451%. The two directed price engines give the raw crossing in

```text
(0.00363900665394133313640894304318937,
 0.00363900665394133313640894304318938)
```

The upper endpoint of the independent #7116 crossing is 0.0036388859997098507738846037035138. The new conservative claim lies above it. The complex price binds. The retained BIT pin is 0.00376669 and all 58 outer checks pass. The maintainer-selected record is separate.

In the exact native word at cut 38670, split independent role 1447 from charts 597→127 into 597→120 and 120→127, each rank four. The same chart needs role 962, so the old rank-seven paid MOVE 597→207 at 38668 is split into 597→120 and 120→207, ranks four and three. Both changes are charged in every one of the 17 native invocations. Ten dyadic ADDs implement the cut basis and inverse on the rebound suffix. See [the application](APPLICATION.md) for the exact witness, the root substitutions and retained assumptions.

The archive contains the exact 17-file #7116 package at head `ee4a05f9c926cf85904c81b768d73acaf9e44b54`, tree `1accfb5a4299b9631fcac19e95f0f07996956070`. Its authenticated nested archives bind the original #7115 native and #7113 caller. The replay deterministically reconstructs the new 72,844-event word with canonical SHA-256 `ff51fcc949bc50a31230a784822ab6f0d079c9102abf22c75746b2b5cdd09553`.

From canonical main plus this package, run

```sh
python3.12 -B scripts/research_package.py --package research/p104-chart120-paid-helper-split
```

The scientific commands also run directly offline.

```sh
python3.12 -I -B research/p104-chart120-paid-helper-split/verify.py physical
python3.12 -I -B research/p104-chart120-paid-helper-split/verify.py composition
```

The source proof and exact compiler use the same assumptions as #7116 and the selected [#7000 application](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md). The replay rejects an omitted cut ADD, an extra rank-one paid term at the claimed price, an aliased caller owner, deficient odd grids, and a wrong chart phase.

Credit dillona and OpenAI Codex for the #7115 native and #7116 composition, Rohan Arun for the #7113 signed caller and application proof, ToikY for #7108–#7110, Ali Romman for the helper-splitting lineage, and CubeJerry, Douglas Colkitt and the selected application contributors. The predecessor package preserves the complete attribution chain. Prepared for ToikY with substantial OpenAI Codex assistance, including independent agent replays. Coordination record in [discussion #7111](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111).

## Open next questions

- Does a different paid cut improve the same complete caller? Start with the current literal word and charge all added routes, fields and recovery costs.
- Which inherited provider, compiler and fixed-tape assumptions can be discharged? Review the exact source application before extending the claim.
