# Install and price the exact minimum-rank tariff

**Round 432 · NO VERIFIED GAIN**

Compare exact [#8096](https://github.com/CrocSwap/integer-mult-bounds/commit/40a82e7974cabfc8509363ea6ad8dd269e446098), κ 0.003900857312674 and the same five signed premises. [Round 431](../r431/REPLAY.md) establishes the exact quotient mean, preserved geometric sum and whole ordinary factor. No external peer change.

The [five-path overlay](ASSEMBLY.json) produces literal selector `4793148b05ea33ef5140d9afe4f79c409ec7e9493314afec295ba810e03f13d8`. The [actual price](OBSERVED-PRICE.json) uses tariff 10981863/4703998 and ordinary debit 353569/262144, with unchanged contraction 2390/2391 and sum 2391. The [independent directed price](INDEPENDENT-PRICE.log) rejected the old tariff at the new booking. The [signed seam](SIGNED-SEAM.log) checked the changed price and rejected the old debit and adjacent rate. The exact literal candidate gives κ 0.003900857313143 and a prospective increase of 0.000000000000469. The Gaussian debit stays 1039699/2^23 and becomes binding. All charged heights, setup, caller and log₂ C 85945126846 stay fixed. A full independent replay is the next gate.

Use Git, CPython 3.12 with assertions, a clean exact #8096 checkout and fresh external scratch with 8 GiB available. Run from the handoff root:

```sh
scratch="$(mktemp -d /tmp/croc-tariff-overlay.XXXXXX)"
export TMPDIR="$scratch"
peer8094="$COMPARATOR_CHECKOUT/research/p104-k7-integral-fringe/source/peer8094"
python3.12 -IB paired-768/r420/overlay/assemble.py --package-root "$peer8094" --output "$scratch/frozen"
python3.12 -IB paired-768/r428/assemble.py --frozen "$scratch/frozen" --output "$scratch/fringe"
python3.12 -IB paired-768/r432/assemble.py --frozen "$scratch/fringe" --output "$scratch/candidate"
candidate="$scratch/candidate/research/frequency-weighted-native-multiplier"
python3.12 -IB "$candidate/bootstrap.py" "$scratch/runtime"
python3.12 -IB "$candidate/receipt.py" "$scratch/runtime"
python3.12 -IB "$candidate/independent_price.py" "$scratch/runtime"
python3.12 -IB "$candidate/check_stage_seam.py" "$scratch/runtime"
```

One exact source and a five-stage run with caps 45, 60, 150, 90 and 150 seconds. [Exact exits](EXITS.log). After the receipt matches, run the unchanged signed scientific verifier and both supplemental typed widths on the exact installation. Use the [setup selector adapter](check_setup.py) to retain the original nine-recipe controls. Stop on the first source, price, ownership or scope mismatch or timeout. Keep all unchecked scopes visible.

Credit Ali Romman's exact #8042 quotient and #8057 signed stack, SYLforge's K7 word, R414/R415's earlier child-mean and tariff derivation, and the exact #8095 and #8096 signed comparison. OpenAI Codex materially assisted.
