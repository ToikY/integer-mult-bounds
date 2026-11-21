# Round 341 · conditional improvement from source multiplicities

Root inputs, partial sibling groups and complete sibling groups give three disjoint cases in the exact finite compiler. Counting equal-rank paid labels separately gives a uniform source-capacity multiplier of 8/5. At h=1804 all 20 power-19 coefficients pass, including the limiting coefficient at index 19. The loss falls from 786/H to 747/H on the original carrier. The new complete claim clears the old relaxed ceiling by exactly 871/100200000000000000. [Exact construction and paid invoice](https://github.com/CrocSwap/integer-mult-bounds/blob/70c410a0b219d906a4162bd37e81fdb8ea0854b6/research/bit-451-carrier-cover/tensor/SIBLING.md)

| Comparator | Previous κ | Round 341 κ | Exact Δκ | Relative increase (rounded) | Exact percentage |
|---|---:|---:|---:|---:|---:|
| [Round 339, #8026](https://github.com/CrocSwap/integer-mult-bounds/blob/156137f70e7819cca8d86a1925d4c2873c77552e/research/bit-451-carrier-cover/tensor/MEAN.json) | 0.00387992804541 | 0.00387992804544 | 0.00000000000003 | +0.000000000773210215470% | (100/129330934847)% |
| [External peer #7863](https://github.com/CrocSwap/integer-mult-bounds/commit/b3e4412fe01f07dc58305616fabf96345f49a781) | 0.00387992804346 | 0.00387992804544 | 0.00000000000198 | +0.0000000510318742466754% | (1100/21555155797)% |

Round 340 had no verified gain. Its whole-family scalar-shift exclusion concerned the previous power-20 envelope and comparison grid. This round improves a different term. Main separately selects #7000 at κ = 0.00363005817. [Round 340 exclusion](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19797815) · [Selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

**Scientific evidence.** The signed consumer tested 0.00387992804551 against the seven-stage cap 0.00387992804552674. It replayed 48 rational calls in both orientations, checking 1,661,521 coefficients in each, and passed 54 strict and four functional conditions. The original binary supplier uses 36 signed calls. The working power-20 predecessor passed. Dropping the source gain fails the power-19 capacity test. An incorrect productive target multiplicity, an extra rank-one paid charge and a low supplied cap were separately rejected. The primary screen ran in 0.0150 seconds and the separate cold signed consumer took 26.532 seconds. `independent/receipt.json` is the independent component result. `independent/signed.json` binds it to five signed files and both consumer failure controls. Hosted job status is recorded on the PR and its timestamped discussion update. The result retains the five premises covering all-column native action, owned erasure, compiler closure, precision and tape, and analytic recovery. The original and nested productive stocks must be restored after every physical stage. [Exact registered package](https://github.com/CrocSwap/integer-mult-bounds/blob/70c410a0b219d906a4162bd37e81fdb8ea0854b6/research/bit-451-carrier-cover/README.md) · [PR #8026](https://github.com/CrocSwap/integer-mult-bounds/pull/8026)

**Clean reproduction.** Check out `70c410a0b219d906a4162bd37e81fdb8ea0854b6`. From that repository root under CPython 3.12 on POSIX, run

```sh
python3.12 -IB scripts/research_package.py --package research/bit-451-carrier-cover
```

The final scientific marker is `PASS_COMPLETE_SIBLING_CAPACITY claim=0.00387992804544`. The component receipt SHA-256 is `42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd`. The exact signed application is `8d5a5fa30f79b5f39fabc2bb320f38ac291761c0012de5d22540a142b1d767af` and the expanded audit is `e8dbc8054ecd54bb6d089346cf84220499d8683fd2043b0650817ad0bd0dd806`. [Independent verifier](https://github.com/CrocSwap/integer-mult-bounds/blob/70c410a0b219d906a4162bd37e81fdb8ea0854b6/research/bit-451-carrier-cover/tensor/sibling_audit.py) · [Registered driver and five input digests](https://github.com/CrocSwap/integer-mult-bounds/blob/70c410a0b219d906a4162bd37e81fdb8ea0854b6/research/bit-451-carrier-cover/tensor/sibling.py)

**Original Round 342 starter, archived.** The primary run reached its cap. For current replay use [the corrected external-timeout command](../ROUNDS-341-343.md). From the same repository root, set `HANDOFF` to this handoff's directory and run the frozen starter. It tries one p=18, h=1804 source certificate. The 45-second screen leaves 15 seconds of a one-minute round for validation. On a failed bound or timeout, record its exact stage and remaining scope. [Full prospective decision](NEXT.md)

```sh
pkg=research/bit-451-carrier-cover
work=$(mktemp -d)
mkdir -p "$work/round321/benchmark/producer" "$work/round336/independent" "$work/round339/independent" "$work/round341/independent"
tar -xOzf "$pkg/source7863.tar.gz" package-sanitized/BIT-451.json > "$work/round321/benchmark/producer/BIT-451.json"
cp "$pkg/grid/RESULT.json" "$work/round336/independent/receipt.json"
cp "$pkg/tensor/MEAN.json" "$work/round339/independent/receipt.json"
cp "$pkg/tensor/SIBLING.json" "$work/round341/independent/receipt-with-minimum.json"
python3.12 -IB "$HANDOFF/next_screen.py" --campaign-root "$work" --out "$work/decision.json"
```

Jacob Alan Sussman supplied the finite Pascal compiler, DreamingOfClouds the ambient-cap proof, zxv the tensor and weighted-exit induction, and JoyboyBrian earlier mean and clipping analyses on 260 factors. Clear1nsight supplied the #7863 physical schedule, #7830 prices and #7973 independent consumer. Ali Romman supplied the paired caller and all-height criterion. The retained cover authors, Dugongue, Rohan Arun and Cinna Davis supplied fallback, cutoff and recovery components. The earlier #8026 proofs supplied the charged paid moments, seven-stage rate and signed replay. OpenAI Codex materially assisted the proof, implementation and independent verification. [#4480](https://github.com/CrocSwap/integer-mult-bounds/pull/4480) · [#5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042) · [#5070](https://github.com/CrocSwap/integer-mult-bounds/pull/5070) · [#5351](https://github.com/CrocSwap/integer-mult-bounds/pull/5351) · [#7973](https://github.com/CrocSwap/integer-mult-bounds/commit/ac3df5d5c8889f464f575e32dfea43714abf08ca)
