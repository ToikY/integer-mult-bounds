# Next incremental gate · earlier chart912 restoration of role496

Pin exact [#7546](https://github.com/CrocSwap/integer-mult-bounds/pull/7546) at `96e4a0dd34b98388d2911fd37df70c15e70840de`, conditional κ `0.003648411294790`, with exact signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The role902 native word has compressed SHA256 `6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32` and canonical SHA256 `bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745`. The complete #7546 application receipt is `a3a225d99dab3573a20cd69616e4b50b18ec20511f460bdfe3c9a6171b9f914f`; signed caller bytes are `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`. Pin `gate.py` SHA256 `aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9` and `pricing.py` SHA256 `f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182`.

## One edit and one decisive cut

Replace public496's paid MOVE40952 729→730 and MOVE40957 730→912 with one direct rank-three MOVE 729→912 at the old exit. Omit ADD40954 (496 += 230) and ADD40956 (994 −= 496). Preserve the other paid clocks, including 230's MOVE40953 261→730 and 994's MOVE40955 261→730. At chart730, the required old230 is on the original already-paid route 40953→40964 (next chart913), while edited496 never visits chart730. No legal transfer from this source to edited496 has been shown.

At chart912 immediately before event41782, edited496, hosted903, hosted984 and public1129 form the exact live bank. Their previously paid arrivals are MOVE40958 for 984, MOVE41776 for 1129 and MOVE41777 for 903. After ADD41778, if `a,b,c` denote the respective 903,984,1129 values before ADD41778, the exact read-only bank values at the cut are
`903=(b-a)/2`, `984=(a+b)/2`, `1129=c-a`.
These follow from `1129-=903`, `903-=984`, `984+=903/2`, `903*=−1/2` at 41778–41781. Role496 has retained ADD40959, `496+=984/2`, then no contact or frame move until ADD43371. The test grants only arbitrary rational read-only use of these available sender rows into the one legal coframed receiver496, including a nonzero own scale. Preserve all hosted donor values through MOVE41783 (984 to228) and MOVE41786 (903 to148) and their first outward ADD41784 and ADD41787. The unchanged 1129 value remains available through the actual cut.

R293's later bank exclusion at pre43371 [220,496,1129] has a nonzero exact span remainder (receipt SHA256 `d8fd9b6f8671622c4d3e3f03155ed2574b2f8ffb84cbf6c0c82c5027976fbc41`). It does not test the two new donor rows. Here the first affected outward deadline of 496 remains ADD43371 into220, after 220's paid MOVE43370. Because no 496 contact occurs between the early cut and this read, an exact early correction that leaves the donors unchanged reaches the deadline.

Role994 has a separate missing old496/230 dependence. Its next scalar write on chart913 is ADD40961, followed by the existing chart913 updates and paid MOVE45805 to127. Its first outward deadline is ADD46168 into992. Role496 reaches chart127 only on MOVE46169, one clock late. A first-bank pass merely earns one separately bounded gate for 994. The verifier checks that the other chart912 rows were unaffected by omissions at this cut.

## Cap, price, restart

One cut, pre41782, and 30 seconds wall including reference authentication and exact directed quote. Use exact normalized adjoint and rational elimination inherited from R293's late bank. The signed paid delta is `{1:-17,2:-17,3:+17}` with no productive change. Its gross is `17(1+H2−H3)`, about 0.11813504 raw, and is rigorously less than one raw. One extra rank-one child in even one signed copy consumes this gross. No new paid operation is assumed. Scalars, routing, ownership/restoration, grid, precision and tape remain due on any construction. Test for `old496 = α edited496 + β old903 + γ old984 + δ old1129` with `α≠0`. A rank or proportionality failure excludes the fixed read-only earlier bank. A cap is unresolved. A pass requires exact coefficients and a separate 994 gate, followed if successful by real legal scalar lowering, full signed forward/adjoint, complete paid and ordinary costs, and independent replay. Changed donor encodings, alternate earlier cuts and paid route changes remain open.

In a clean replay root, put the five authenticated files named above under `inputs/` as `ROLE902-WORD.json.gz`, `ROLE902-APPLICATION.json`, `7113-CALLER.json`, `gate.py`, and `pricing.py`. Stage this script under `next-role496-early/` and use CPython 3.12 with standard library.

```sh
python3.12 -I -B next-role496-early/check_496_early_bank.py inputs
```

Desk work checked chronology, pins and syntax. Scientific support, pricing replay and independent verification have yet to run. [#7542](https://github.com/CrocSwap/integer-mult-bounds/pull/7542) supplies the surrounding 1077 compensation and moved 230 route. [#7544](https://github.com/CrocSwap/integer-mult-bounds/pull/7544) supplies the independently verified composition. #7546 supplies the exact role902 word. [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) supplies the exact row approach and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed tariff. No exact matching prior claim appeared in the five targeted PR queries. OpenAI Codex materially assisted.
