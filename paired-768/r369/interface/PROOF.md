# Fractional quarters on the existing Gaussian band grid

Round 369 tested one recipe. At the 1,006 established two-piece rank-one returns in the smaller Gaussian copy, replace the two halves with exact one-quarter and three-quarter packets. Keep the original bands, packet owners and return itinerary. The comparator is #8054 at f6f4ecd5dd717ce2b155dd564469e9693ac90f6d with κ = 0.0038981730255 and Gaussian exponent 133940467/2^35. Ali Romman supplies the K7 word and retimed multiplier. The two-return predecessor supplies the literal 1,006 changed returns and all signed replay. OpenAI Codex assisted this check. [#8054](https://github.com/CrocSwap/integer-mult-bounds/pull/8054)

The carrier rank is N = 2^H with H = 20,000,000. The allocator admits every even band in [32768, 2 floor(N/(2048·1224))). In particular the band [32770,32772) has positive density and a positive, upward-rounded replica count. Its native column width is 32770−8 = 32762, positive and even. An exact quarter packet needs 16381/2 selected axes and the remainder needs 49143/2. A fractional count violates the existing event guard and cannot be emitted by the decoder. The installed half-and-half recipe issues 16,381 axes to each packet at that width. Divisibility of N by four gives no divisibility guarantee for this band's width. The earlier finite two-column zero-row control is narrower than this exact production obstruction.

A separate two-band control inside the real compiler kernel issues a valid half packet, then rejects the literal quarter variant at the same residue. It uses two independent grade-one targets and two paid requests to isolate the precise error. The positive admissible production-band witness and exact fractions are independent of this small executable control.

A different contract could use floor(w/4) and w−floor(w/4) with w=e−8. They sum to w and differ from absent integral exact quarters by at most 1/2 on the current width grid. For every compatible target k≥1, the original nested-prefix bound leaves spare at least 8k−10r≥1/2 at r=3/4 and at least 11/2 at r=1/4. The original 10k fringe can increase by at most 1/2, still bounded by 21k/2. The predecessor lower bound for Ψ becomes 4^(−c) P log(5/4)>0.19P. With the same source mass ratio and power bounds, the fringe coefficient is bounded by (21/2)·1.06/(.996·.99·.19)<64. The external width loss uses an integral productive rank and its 1−10/L factor is unaffected by paid-packet rounding. This argues only for a prospective rounded compiler. It leaves its literal scheduled leaves, grid and full signed accounting open. [Exact predecessor transport proof](https://github.com/CrocSwap/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/TRANSFER.md)

Run with CPython 3.12 and an explicit unpacked #8054 package source directory. The script authenticates the five referenced inputs by path. It passed in under one second.

```sh
python3.12 -IB check.py --package "$PEER_8054_PACKAGE" --out fresh.json
```

Expected output SHA-256 is 72290130a0eae0e087c9431b07db0f3950996714c65e9aedb761aa9bf6138d33. The fixed exact-quarter proposal has no unresolved cases and no verified κ gain.
