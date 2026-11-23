# Round 408 first test

**Status at Round 407 freeze** — prepared and syntax checked. The mathematical gate, candidate build, and independent signed replay are unrun. Use it only after the live frontier refresh and the complete Round 407 verification. If a stronger comparable independent witness supersedes the frozen one, reprice the trial against that witness before using this decision.

## Exact scope and cap

One case at offset 8 and lower band 1874. Keep the actual two-type donor calendar, owner/return schedule, ordinary contraction, signed caller, and 25-bit setup. Reduce the Gaussian debit by pricing the matched interior suffix through its integrated phase average. Keep the conservative exterior factor `1+1032/263772` from the matched-suffix proof. The trial takes no credit for stacking the tighter `257/256` exterior factor used by Round 407.

The input checkout is exact Round 407 head `aea1699415250d865f7a635f4df0b76f406c47b4`. Its terminal receipt `research/p104-period-debit-25bit/RESULT-460.json` has SHA-256 `8c8b7cebbdea179329d225d828f31e37e2fddfcfd177750803ae81e39726def8`, conditional κ `0.003898460000505`, and complete recurring `log2 C = 4354317451`. The archived signed source is authenticated by `PEER-SOURCE.json` and is taken from [#8057's exact head](https://github.com/CrocSwap/integer-mult-bounds/commit/cbe847a953b971f9c6c5a0a6661e2008acd29086). The two peer prose and code files are authenticated provenance. The gate neither executes the peer checker nor reads its numerical outcomes as evidence. Get both files from [#8083's exact tree](https://github.com/Clear1nsight/integer-mult-bounds/tree/dd2e2ff28102557f7c30619d6abd8a861e363d1d/research/p104-integrated-gaussian-suffix).

From the directory containing this handoff, supply a clean detached checkout and the exact `INTEGRAL.md` and `appendix/weighted_suffix.py`. Run this on macOS or Linux with Git and Python 3.12 or later.

```sh
python3.12 -IB check_offset8.py \
  --baseline ./inputs/round407-checkout \
  --integral ./inputs/peer8083/INTEGRAL.md \
  --pricer ./inputs/peer8083/weighted_suffix.py > offset8-receipt.json
```

All source content is either read directly from the three input paths or restored afresh into a private working directory from the authenticated archive. The timed gate has one case and a 30-second wall cap. Stderr shows the last completed stage. Exit 124 leaves the one case unresolved. Preserve the previous receipt or stderr and reuse the same restart command once the budget is renewed. A non-timeout gate failure should identify the failed input, hypothesis, or bound before a distinct route is selected.

## What the screen checks

The accounting identity includes each issued suffix, each unissued parent, and prefixes that miss the funding cutoff.

$$
K C P-B\sum_i q_iQ_i
=K\sum_iq_i(P-Q_i)+K(C-\sum_iq_i)P+(K-B)\sum_iq_iQ_i .
$$

The pinned source uses lower directed integer grants and upper directed births. It splits each typed allocation across all actual recipient ports. The gate reconstructs the 51 coefficients independently from 88 typed shares, using both actual sender multiplicities and literal paid and target label counts. The source offsets give `P-Q = 8(k-r)+re-kd` on an overlap. The exact period of both phases is checked per grade pair and all constant pieces obey the positive support and upper bound induced by `gcd(2r,2k)`.

With `z=k/r`, the two phases yield `S(y)=8(k-r)+k a(y)-r a(zy)`, where `a(y)=y-2 floor(y/2)`. The continuous primitive `b=a²/2-a` lies in `[-1/2,0]`. Hence `J=k b(y)-(r/z)b(zy)` has derivative `S-9(k-r)` almost everywhere, `J(L)≥0` at the even lower edge, and `J≤r/(2z)`. Integrating against `y^(-1-t)` and extending the positive suffix to the half-line gives the weighted coefficient bound `9(k-r)+t r/(2zL)`. This bound concerns the weighted total. Individual grants may exceed it.

The boundary checks bind the live code for flooring, even bands, actual offset, and four-aligned periods, and test the monotone endpoints at `H=1024`. The unpaid interior bottom interval remains charged via Ψ. Ceil/floor uncertainty, missing grants, late drains, the exterior donor, partial period and last productive group remain in the proof. Their allowance uses the archived invoice and [#8083's finite-error argument](https://github.com/CrocSwap/integer-mult-bounds/pull/8083). Directed arithmetic derives the factor and bounds it below `2^(130699669/2^30)`. The adjacent-book control concerns this accounting expression, so it does not rule out a tighter future proof.

The prior comparison uses the same three-stage ordinary recurrence and recurring cap. Its Cauchy relaxation gives an integer ordinary-height sum of at least 650656 for any gain. Charging 1731 fixed, 320 per ordinary height and 220 per Gaussian height gives a predecessor Gaussian height ceiling of 18845935. The trial checks strict separation from the resulting Gaussian stopped upper with debit `64934/524288`. It also prices the entry and terminal signed margins, the `2^40` extra indexed setup actions, and the first terminal header `2^19182389+4`.

## Decision at the gate

The fixed trial is κ `0.003898460003746` with ordinary heights `(8192,38102,604363)`, Gaussian height `18531230`, and projected complete recurring `log2 C = 4285082571`. If the source, factor, and signed arithmetic pass, the trial projects a signed gain of `3241/10^15` over the frozen Round 407 witness. Build only this one installed debit and profile after the overlap and budget checks. Then require a clean independent price, calendar, raw, exterior, nested, product, and setup verification against the literal construction. No κ result is claimed by this handoff. If the projected gain or a finite-charge obligation fails, retire this instance and retain the exact failing stage. Other offsets, period-factor stacking, and alternative height profiles are outside this test.

The matched-suffix integration and finite-error decomposition come from [#8083](https://github.com/CrocSwap/integer-mult-bounds/pull/8083). [#8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072) supplied the original offset-8 typed calendar, [#8081](https://github.com/CrocSwap/integer-mult-bounds/pull/8081) supplied the 25-bit recurring profile and setup path, and [#8085](https://github.com/CrocSwap/integer-mult-bounds/pull/8085) supplied the separate period tightening on the Round 407 branch. The atanh/Taylor interval routine is reused from the Round 406 independent price. The inherited five signed all-size assumptions remain in force. AI assistance was used to prepare the arithmetic gate and handoff.
