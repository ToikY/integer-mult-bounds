# Verified compact Gaussian debit retune

The exact Round 376 construction at `0aa94696f3876ea18a4ef68e28a7c442b4c22158` passed local independent price, complete registered signed product and both nonzero numerical controls. The release head `4ff66ca09aa7727768aeaf24ac444e69675804de` adjusts only the declared task stop rule. It passes the committed-byte, source-history, mode and registration checks. The construction gives conditional **κ = 0.00389821005**. The strongest independently reproduced prior witness, #8057 at `cbe847a953b971f9c6c5a0a6661e2008acd29086`, gives **κ = 0.00389821**. The exact absolute gain is 1/20000000000 and the exact relative gain is (1/779642)%, or about +0.0000012826399809143%. The new compact retune has higher activation, carrier and recurring cost bounds than #8057. The selected #7000 record is separate and unchanged. [Peer scientific replay](peer8057-replay.log) · [Exact new invoice and independent controls](PROOF.md)

The complete literal numerical replay traversed all 564,144 paid cuts, 105,216 owners and 358,410,240 axes at widths 6 and 474. The signed multiplier produced and independently checked −345550037539, with restoration, 138 bank shuttles and 157,248 H calls. Onboarding on the tested scientific head passed 760 tests with 31 skips. The unchanged historical fixture passed its declared scope. Hosted checks are reported separately in the canonical discussion. [Main replay](main-replay.log) · [Nonzero numerical replay](numerical-replay.log) · [Historical fixture](historical.log)

## Reproduce from clean pinned checkouts

Use CPython 3.12. Set `R374_PACKAGE` to `research/p104-compact-rounded-partitions` in a clean checkout of old `28f9516bbd758831650efd2f9fc3ed5a586f0eb5`. Set `R376_PACKAGE` to the same package directory at the exact release head above. Both dependencies are authenticated by the scripts. From this directory run:

```sh
sh replay-audit.sh "$R374_PACKAGE" "$R376_PACKAGE"
```

The command recreates the old calendar image, verifies exact capacities and funds, tests both parity residues, rejects two negative controls, and checks the fixed setup envelope. It recreates all three published independent receipts byte-for-byte. From the R376 repository root run:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-compact-rounded-partitions
python3.12 -IB scripts/research_package.py --package research/p104-compact-rounded-partitions-numerical-replay
```

The verified scope is this word, one Gaussian debit and one terminal ordinary height. The all-size conclusion still requires all five inherited premises. The local peer run verified the saved portable invoice as part of the price mode. Regenerating the optional Wasmtime installer evidence was outside this replay. [Previous literal source](https://github.com/ToikY/integer-mult-bounds/tree/28f9516bbd758831650efd2f9fc3ed5a586f0eb5/research/p104-compact-rounded-partitions) · [Calendar proof and setup accounting](audit/PROOF.md)

Ali Romman authored the compact #8055 tiers and weighted #8057 comparator. SYLforge provided K7. The #8056 contributions supplied the integer partitions and phase accounting. OpenAI Codex assisted the directionally rounded estimates, implementation and independent replays. [#8055](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) · [#8056](https://github.com/CrocSwap/integer-mult-bounds/pull/8056) · [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)
