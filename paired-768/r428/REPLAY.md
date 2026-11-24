# Install and price the two-tick interior fringe overlay

**Round 428 · NO VERIFIED GAIN**

The exact comparable science from [#8095](https://github.com/CrocSwap/integer-mult-bounds/pull/8095) is κ 0.003900857312000. Its timeout-only head update `490cd470f86157d29c9d3f8da9f96d6e2c3c04e5` has unchanged proof and construction and completed local replay. [Round 427](../r427/REPLAY.md) gives the independent directed fringe proof and scope.

One new overlay changes six source paths. Two source assemblies matched, and the candidate installation image was `6dc565fad3b91bcb43ff71397897afcc54fd5f9d595a8f88b91234994d8e70be`. The [actual literal receipt](OBSERVED-PRICE.json) and [independent price](INDEPENDENT-PRICE.log) passed Gaussian debit 1039699/2^23 with fringe multiplier 515/516. Ordinarily charged costs, the signed caller, and log₂ C 85945126846 remain fixed. The exact literal price supports prospective κ 0.003900857312674 and prospective Δκ 0.000000000000674. The [signed stage seam](SIGNED-SEAM.log) rejected the previous Gaussian debit at the new rate and the next rate tick at the fixed profile. [Original per-stage exits and budgets](EXITS.log).

Use Git, CPython 3.12 with assertions, and a fresh external writable scratch volume with 8 GiB free on the checkout and scratch volumes. From the handoff root set COMPARATOR_CHECKOUT to the clean exact #8095 head above. Run:

```sh
scratch="$(mktemp -d /tmp/croc-fringe-overlay.XXXXXX)"
export TMPDIR="$scratch"
peer8094="$COMPARATOR_CHECKOUT/research/p104-k7-sharper-period/source/peer8094"
python3.12 -IB paired-768/r420/overlay/assemble.py --package-root "$peer8094" --output "$scratch/frozen"
python3.12 -IB paired-768/r428/assemble.py --frozen "$scratch/frozen" --output "$scratch/candidate"
candidate="$scratch/candidate/research/frequency-weighted-native-multiplier"
python3.12 -IB "$candidate/bootstrap.py" "$scratch/runtime"
python3.12 -IB "$candidate/receipt.py" "$scratch/runtime"
python3.12 -IB "$candidate/independent_price.py" "$scratch/runtime"
python3.12 -IB "$candidate/check_stage_seam.py" "$scratch/runtime"
```

Preserve the actual observed price before setting any expected result. One source build and one exact profile, with the 45, 60, 150, 90 and 150-second staged caps documented above. There is no requirement for a previously registered runtime or personal checkout. The exact proposal passed its literal cost and seam gates. Complete independent dirty physical, both true-helper typed widths, installed nine-recipe census, production calendar, raw, exterior, nested and signed product remain the next gate. Use `check_setup.py` to authenticate the new installed selector and retain the previous census controls.

Credit #8083 and Round 409 for the sharper earlier lattice bound, Ali Romman's #8057 signed program and #8094/#8095's actual comparable source stack. This proposal instantiates the bound in the current complete price and uses the indicative scalar only after all remaining verification. OpenAI Codex materially assisted.
