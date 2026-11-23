# Ordinary η lift at the exact seven-recipe profile

The source-bound check supports the written ordinary η lift at the fixed #8094 profile. It applies the same five scientific premises as the inherited ordinary receiver. The invocation, signed owner and multiplication, precision, and finite nine-recipe setup obligations still need full replay.

The five terminal heights, paid rates and stage cuts come from exact #8094 at c20a08dc0a79a989e3515068560d5da371c0a2a8. Its runtime patch installs η = 1/256 only on the terminal profile. The two entry recipes keep η = 39/10000. The literal carrier inherited by the same archive computes
`w=max(E_prev+1,ceil_root(e,250))` and
`g=ceil_root(e**eta.numerator,eta.denominator)`. It retains the same profile when dispatching the earlier service. The actual body uses `c,r=divmod(e-k,w)`, so `c<=e/w`. The inherited per-prefix work bound and proof are in the #8057 clock. [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) · [#8084 at af73b476](https://github.com/CrocSwap/integer-mult-bounds/blob/af73b476d5fdeaa763e0bff2dd87b2ecaf097c49/research/p104-ordinary-eta-lift/PROOF.md) · [Inherited physical clock](https://github.com/CrocSwap/integer-mult-bounds/blob/cbe847a953b971f9c6c5a0a6661e2008acd29086/research/tiered-native-multiplier/CLOCK.md)

The two profile values each satisfy `1/258<eta<1/250`. Thus `g<=w<=e` at an admitted call. If `m=ceil(w/g)>1` then `w>=(m-1)g+1`; dividing by `m` gives a smallest component width `u>=g/2` after the integer balanced split. The case `m=1` has `u=w`. Consequently `mc<=2e^(1-eta)` and `m<=2w^(1-b_prev)`. The latter uses `g>=w^eta` and `b_prev<eta`. The growing-width term has the asserted rate by strict stage funding. The entry and terminal rates, including the fixed terminal η lift, satisfy these conditions and `eta+b_i<1/2`. The direct coarse service bounds and the clock for previous-service calls retain this dependence. Computing the new component root uses a fixed degree 256 with numerator 1. The checked source uses the same binary search as the older degree 10000 profile. Three nondyadic inputs exercised the inherited function.

In the growing first stage, `2 eta>1/250` gives `w+1<=9u^2`. At every admitted width, `w<=e` and `u>=e^eta/2` give `w+1<=2^259 u^258`. Write `j=floor(log2 u)`. At every terminal height `H>=31808`, `H/256-1>=123`, so `j>=30`. Since `H<=258(1+log2 u)`, the retained physical coefficient cost has log₂ bounded above by `2660000(1+log2 u)<u`. The last inequality follows from `2660000(j+2)<2^j` at 30 and monotonicity. The exposed fibre of at least `3^(u-1)>2^u` supplies the same charge. The unchanged entry roots retain their two older surcharge values, 0 and 25,818,582. No extra high-fibre charge was needed across the five terminal stages. With the audited reserve and tariff choice from Round 412, the existing ordinary bills remain 125433364 and 85899221583 log bits. The actual direct dispatcher sends e satisfying `ceil(e/w)<=N^8` to the direct receiver; every quotient entry has `e>N^8`, above the sufficient width-log guard `ceil((2H+64)/(1-eta))<3H`. The receipt checks this guard and its lower-adjacent negative, all seven literal stage cuts, and the old η clamp negative.

The finite calendar floor 4474 is wired separately by the exact #8094 prepare script. Its rank-stock and coupling check uses H = 1024 as the smallest sufficient scale. The terminal change to η neither changes those labels nor occurs in the calendar's scale bound. This audit verifies the source anchors and the direct clock inequalities. It does not execute that calendar, a native receiver, the public signed product or the expanded installer.

## Replay

CPython 3.12 with assertions. Use exact clean checkouts for #8084 and #8094 and the immutable [#8073 copy of the inherited archive](https://github.com/CrocSwap/integer-mult-bounds/blob/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e/research/p104-weighted-k7-suffix/peer8057.tar.gz). This bounded command authenticates all three inputs, reads archive members in memory and needs no previous installation or temporary state.

~~~sh
python3.12 -IB check.py \
  --eta-proof "$ETA_CHECKOUT/research/p104-ordinary-eta-lift/PROOF.md" \
  --composed "$COMPOSED_CHECKOUT/research/p104-shortcut-word-eta-27bit-5stage" \
  --archive "$K7_ARCHIVE" > reproduced.json
cmp reproduced.json RECEIPT.json
~~~

One profile pair, seven recipe rows, three root controls. First run completed in 0.08 seconds elapsed with exit 0 under the 30-second runner cap. The separate ordinary and installed work remains conditional. Full head and hashes appear in the receipt.

Credit Clear1nsight's #8084 written lift, floration's #8094 composition, Ali Romman's #8057 and retained physical compiler clocks, SYLforge's K7, and the inherited signed caller and physical receiver. OpenAI Codex assisted with the independent source audit and replay.
