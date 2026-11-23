# Round 403 capped allocation screen

The exact reference is [#8071 at 9555f2df](https://github.com/CrocSwap/integer-mult-bounds/commit/9555f2df027f4a182722f736c97e5efafa5382c6), κ 0.00389821412325. The 15 package paths and modes, original full independent replay, historical inputs and current hosted jobs match. Latest comparable external #8057 remains at 0.00389821. The maintainer-selected #7000 remains separate. [Round 402 closeout](../r402/CLOSEOUT.md)

From a clean handoff checkout with CPython 3.12, run these commands. The comparator argument points to a clean exact #8071 checkout.

```sh
python3.12 -IB paired-768/r403/saved-allocation.py
python3.12 -IB paired-768/r403/check_invoice.py comparator-checkout paired-768/r402/verification/REPLAY-RECEIPT.json
```

The saved search was capped at 14 exact prices and 30 s for Gaussian heights 490639–491151. It evaluated 11 prices in 0.014396 s, exit 0. Gaussian height 490949 is Gaussian-limited. Height 490950 is ordinary-limited and passes the full independent price at κ 0.003898214283192. Both have ordinary heights (8192,124649,524288). Higher Gaussian height 490951 is infeasible at this target even with the best ordinary heights under the cap. The selected candidate was the only one advanced to a build. [Screen output and exact examined cases](saved-allocation.log)

The whole invoice is 318292011 recurring log₂ C, 60 below the exact comparator. The first terminal header is 2^1148553+4, 97 exponent units higher than #8071. Entry conversion takes 515 bits and maximum height stays 524288. The signed allocation calculations include all 54 strict and four functional inequalities per tier. The independent tangent and integer rounding argument bounds every competing profile within the stated three-stage clock and height family. The test changes the allocation and leaves both finite-factor bookings fixed. It does not settle other cost models, providers, or stage counts. An actual improvement still needs the literal signed replay. [Exact signed price, adjacent controls and certified ceiling](price-receipt.json)

Ali Romman's #8057 supplies the original signed pipeline and #8055 fixed setup. SYLforge's #8052 supplies K7. #8068–#8069 supply the capped integer allocation method, #8070 the Gaussian booking, and #8071 the finer ordinary booking used here. Codex materially assisted the exact screen and independent proof.
