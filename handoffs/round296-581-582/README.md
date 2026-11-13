# Fixed chart879 return after the 581/582 co-encoding

**No verified κ gain.** On exact #7546 at
`99438c43df7aac1e5dbcc43c1578fcd886c119ec` with signed #7113 at
`07a76c5e2738882c0cb322278e56f6cae3c9885d`, set ADD36507 to
581 += 2·582 in chart3. Keep role581's original paid entry to
chart595 and its ADD to owned role1556. Bypass the later role582
chart595 route with one direct rank-four MOVE to chart767 at old
41558, omitting ADD36511 and ADD39905. The signed edit's optimistic
gross is about 0.13905166682428763 raw. An extra rank-one position
costs more than that across the complete invoice.

The ordered owned1556 update agrees exactly at post36511.
At the first required outward read of role581 before ADD42252,
the chart879 bank is [316,581,1078,1258]. Its full normalized
span lacks old581. The exact adjoint residual has 119 nonzero
terms. The independent literal forward replay verified all 73
nonzero owned1556 coefficients and found no one-coordinate
collision. With unit inputs at coordinates 0 and 146 together,
the edited bank equals its value on zero while the required old
role316 after ADD42252 is 1/2 instead of 0. That establishes
support-two minimality. The exact adjoint and independent checks
exited zero in 0.25 and 0.76 seconds. This excludes the fixed earlier encoding with a repair
that only reads the actual current bank. The separate role582
return at ADD42255, changed encodings and altered paid routes
remain unresolved. The test covered one scoped case, stopped when
its first gate failed, and stayed below its 30-second cap.

Use CPython 3.12 with assertions and a clean scratch root.
The exact published input files are authenticated by both verifiers.

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

Credit #7481 for the distinct verified early producer precedent,
#7546 and #7113 for the exact word and caller, #7482 for the exact
normalized readout and #7298 for directed price. OpenAI Codex
materially assisted.
