# Type B rank-137 root36 split at pre3058

This is the next priced experiment after [#7529](https://github.com/CrocSwap/integer-mult-bounds/pull/7529) closed the fixed native chart-246 repair. It uses the exact #7481 and #7113 inputs already bundled in that package. The experiment remains unrun. See [PLAN.md](PLAN.md) for the precise scope, price and predecessor credit.

From the repository root on POSIX with CPython 3.12:

```sh
python3.12 -I -B handoffs/round277/check_type_b_root.py research/p104-role1261-telescope-bound/inputs
```

The script checks one pair, one cut and one body order and parity within 30 seconds. A rank-two forbidden minor in either sector rules out the frozen prefix. A survivor needs exact basis, signed suffix and independent input and output verification, followed by complete repricing. A timeout leaves the case unresolved.
