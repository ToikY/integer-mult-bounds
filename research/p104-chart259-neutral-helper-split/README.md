# Conditional κ = 0.003640102187396 from an independent chart-259 split

On exact [#7120](https://github.com/CrocSwap/integer-mult-bounds/pull/7120) at `b3d68cf1db9bf493ded2d8f4cb922939edc0ef95`, split a rank-eight native helper into ranks 3 and 5 at chart 259. Every paid MOVE is retained at its original rank, with the suffix pivot and owned labels relabeled. The exact claim `910025546849/250000000000000` exceeds #7120’s reported conditional `1819632053141/500000000000000` by **`419040557/500000000000000` = 0.000000838081114** on the same 17-stage caller, completed BIT predecessor and five framework assumptions. The signed margin of the old invoice is strictly negative at the new claim. The raw crossing is

```text
(0.00364010218739649072410851912941669,
 0.00364010218739649072410851912941670).
```

The cut is before source event 31,847. Role 231 starts at chart 3 and now retires at chart 259. Fresh arbitrary public input 1489 starts at chart 259 and finishes at chart 246. Two boundary bases and the inverse pair of cut bases add 20 ADDs and six SCALEs, with dyadic denominators at most 16. The entire normalized independent extension is proved in [PROOF.md](PROOF.md).

| Complete 17-stage invoice | #7120 | Chart 259 |
|---|---:|---:|
| Paid positions | 110,723 | 110,723 |
| Productive fields | 22,257 | 22,274 |
| Rank surplus | 1,424 | 1,424 |
| Empty-root credit | 0 | 0 |

The exact change is `ΔT={3:+17,5:+17,8:−17}`, with `ΔP={}`. The emitted word has 73,698 events, 1,490 public roles, 1,090 independent helpers and 51 owned fields. The native grid is `1125/F24`, and the full source-unit ordinary bill is **777,785,464**. The fresh common-format envelope has height 405, context mass exponent 1172 and `c=2344`. [APPLICATION.md](APPLICATION.md) gives the changed resource substitutions.

The frozen #7120 native word has canonical SHA-256 `4f19c6ee57b74d7c3ea1863df0b33fe275a3a7511f77084f05726ee216ebdc34`. The chart-259 word has canonical SHA-256 `0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc`. The signed 17-stage caller has unchanged SHA-256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`. The local constructor, witness and separate directed price replay are listed in [PROOF.md](PROOF.md).

The assumptions are `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape` and `analytic_recovery`, with the inherited nonzero-content premise for owned erasure. The claim is the certified lower point for this conditional invoice. Independent human and formal review, maintainer admission and compiled top-level execution are separate obligations.

Credit Ali Romman for the independent-helper split, Jerry Chen/CubeJerry for the owned-field and exact native/invoice engines, Matarener for the pairing search, dillona for the smooth swap and exact #7120 predecessor, ToikY for the chart-120 pattern incorporated in #7120, Rohan Arun for the signed 17-stage caller, and DreamingOfClouds, Douglas Colkitt, the #7000 reviewers and all retained source authors. Apache-2.0.

The exact relative percentage gain is `(41904055700/1819632053141)%`, approximately 0.023028862141%. The complete predecessor package is embedded verbatim and pinned at tree `c480f8103238a3bd5c06c4b71c266edcb2a5baf8`. The scientific replay uses Python 3.12 and no network.

```sh
python3.12 -B scripts/research_package.py --package research/p104-chart259-neutral-helper-split
```

## Open next questions

- Check a distinct helper group or a changed caller interface against the complete paid profile before proposing another step.
- Audit the retained all-size provider, compiler and fixed-tape assumptions independently of the finite application.

Prepared for ToikY with substantial OpenAI Codex assistance, including independent agent implementations and verification. [Canonical coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111)
