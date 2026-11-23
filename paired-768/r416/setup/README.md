# Exact nine-recipe setup arithmetic

At exact [#8094 c20a08dc](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8), the prepared price receipt still calls the archived serial clock with (2^{68}) indexed actions. It records the resulting legacy subtotal. The written enlarged installer bound explicitly adds (2^{40}) actions to both the total action multiplier and the lookup store. The larger subtotal remains below (2^{228}). [Exact #8094 setup proof](https://github.com/CrocSwap/integer-mult-bounds/blob/c20a08dc0a79a989e3515068560d5da371c0a2a8/research/p104-shortcut-word-eta-27bit-5stage/SETUP-27BIT.md)

The checker reconstructs the literal #8094 and [Round 415](../../r415/RESTART.md) installation declarations from the authenticated #8057 archive and #8094 prepare edits. It binds both images to their recorded SHA-256 values. Both profiles have seven ordinary and two Gaussian recipes. Their maximum lazy (92H+1) datum width is 12,348,030,885 bits, below (w=2^{38}), and their two explicit carrier widths are 1,025 and 208,654 bits. All scalar encodings fit the 128-bit guard. The literal entry ordinary heights of 3,000 and 3,080 fall below the written 8,192 description in the #8094 proof. Its upper width guard and action allowance still hold for those entry heights.

With `n = 2^68 + 2^40`, `w = 2^38`, `h = 2w + 2`, `L = 8(4wn) × 512 × 128`, and `E = 2^16(h+4)(7h+9) + 8 × 2^16(h+4)^2`, the exact bound is

```text
(n+1) (L+E+2^120) 2^32
  = 217364571993743287866367176320080817069553173293686105666269057384448
  < 2^228.
```

The nine-recipe allowance `2 × 2048(2^25+1) + 9 × 2^24 = 137589952512` fits within `2^40`. The checker rejects oversized and zero-stop scalar controls, reproduces the inherited 2^68-action result, and compares both against the deliberately incomplete variant that increases the action multiplier while leaving the lookup store stale. Coverage ends at source identity and arithmetic.

## Clean replay

Use CPython 3.12 and Git. From a clean handoff checkout, set `COMPOSED_CHECKOUT` to the exact #8094 checkout above and run

```sh
python3.12 -IB paired-768/r416/setup/check.py \
  --package-root "$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage"
```

The output matches [RECEIPT.json](RECEIPT.json). It reads authenticated archives in memory and applies only the installed profile source hunk to a newly created temporary directory. The recorded run exited 0 in 0.08 seconds.

The next gate is a fresh nine-recipe fixed constructor and directory census for each exact installed image, with `Recipe.width` and `Recipe.open()` guarded. The signed stack progression uses the same explicit physical presets as the pinned package. The prior #8081 observation covered seven recipes. The numeric transition comparison relies on the inherited action and datum assumptions.

After native admission and bootstrap, run the census once for each prepared runtime with its matching selector and exact portable directory. Use an explicit scratch root with the required 8 GiB availability. The harness will authenticate the source images. It then measures both real positive carriers and checks all actual directory records. The 150-second cap applies separately to each serial census.

```sh
python3.12 -IB paired-768/r416/setup/check_installed.py \
  --profile peer --runtime "$PEER_RUNTIME" --portable "$PEER_PORTABLE" --scratch "$SETUP_SCRATCH"
python3.12 -IB paired-768/r416/setup/check_installed.py \
  --profile candidate --runtime "$CANDIDATE_RUNTIME" --portable "$CANDIDATE_PORTABLE" --scratch "$SETUP_SCRATCH"
```

The harness passed static binding and scalar guard controls for both selectors in Round 416. The installed directory census remains unrun. Recording its result would supply the relevant measured evidence for the conditional numerical setup cap. Signed native and product outcomes remain separate.

Credit Ali Romman for the #8057 literal source and serial arithmetic clock, the #8081 enlarged fixed-setup argument, floration for the exact #8094 source composition, and the Round 415 profile materialization. OpenAI Codex assisted with the independent checker.
