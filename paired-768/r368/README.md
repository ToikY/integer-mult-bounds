# Gaussian support cut and two unsplit paid returns

[#8053](https://github.com/CrocSwap/integer-mult-bounds/pull/8053) at `e25494616bf149217644ce08d949181ea3600e13` supplies the fixed-carrier benchmark. There are 1,008 unit-rank productive targets. An optimistic exact 5/4-descent bound excludes 1,005 split rank-one requests even with freely redistributed shares. A complete priced transport with 1,006 splits retains 54 cells and reduces the paid inventory from 564,144 to 564,142 at unchanged productive inventory. The two changed return tags and native chart moves are recorded in the adapter proof. The signed trial is κ = 0.0038981730255. The 1,008-split predecessor has negative raw margin at the new Gaussian price. [Primary proof](primary/PROOF.md) · [Independent arithmetic](independent/PROOF.md) · [Literal adapter](adapter/PROOF.md)

Use CPython 3.12, Git on PATH, and a clean checkout of exact #8053. Set `FIXED_CARRIER` to the checkout's `research/p104-gaussian-fixed-carrier` directory. Run from this directory. Use fresh output names.

```sh
python3.12 -IB primary/price.py --fixed-carrier "$FIXED_CARRIER" --out fresh-price.json
python3.12 -IB primary/check_emitter.py --fixed-carrier "$FIXED_CARRIER" --price fresh-price.json --out fresh-emitter.json
python3.12 -IB independent/support.py --package "$FIXED_CARRIER" --arithmetic ../gaussian-fixed-carrier/audit.py --out fresh-support.json
python3.12 -IB prepare.py --source "$FIXED_CARRIER" --out fresh-variant
python3.12 -IB adapter/check.py --fixed-carrier "$FIXED_CARRIER" --variant fresh-variant --out fresh-adapter.json
```

The arithmetic and adapter receipts are independent of the candidate's finite scientific replay. The exact 1,005-split exclusion concerns the original two-scale source and rank-descent schedule. More general supplier or interface changes remain open.
