# Exclude a fixed equal-mask Type B square

The signed #7113 caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d`
executes identical rank-48 idles on role36 at clocks 1887 and 1940
with mask B3 through B8. This test uses exact comparator #7544
`d6be7d620c9c8337104daeb09fe01196eced5fe3`. It asks whether the
two idles can become one ordinary square translation on the same
represented field while fixing every other operation.

Use one width-one fibre at port 15 with B3 = −1, the central phase
and all other bodies +1. Two negative Walsh labels at axes 25 and 26
realize that fibre. The ordinary square translation has eigenvalue +1,
as on the all-positive fibre. If M is the map of the 52 intervening
ordinary events, the original sign window is DMD where D reflects
role36. The proposed window is M. On input role36, the output at
role37 is −1 in DMD and +1 in M. The exact difference is supported
on the row or column of role36. Its minor on roles 36 and 37 is
`[[0,2],[-2,0]]`, determinant 4 and rank exactly two.

A repair with sector-identical left and right wrappers and bypass
plus one varying rank-one action has difference rank at most one.
Cross-fibre routing, sector-dependent wrappers and alternate paid
routes remain open. The independent literal replay checks all 36
columns, with equal unit-body controls and an omitted-idle mutation
that changes the signed output. It also lifts the witness through
the full normalized Type B caller to an integral input with role36
output −30 versus +30.

The proposed raw eight-port paid saving is
`757.2305097672699867199081907628603` to
`757.2305097672699867199081907628607` before ancillary costs.
The exact fixed edit fails, so realized saving is zero and
conditional κ is unaffected. The replay tests one fixed case
with each verifier capped at 30 seconds.

## Replay

Use CPython 3.12 with assertions. From this directory, fetch the
pinned public inputs into an explicit scratch directory.

```sh
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

Both engines authenticate their inputs by path and compare the full
mathematical receipts. Only measured elapsed time varies.

#7113 supplies the signed caller. #7544 and #7542/#7481/#7480/#7334
supply the comparison lineage. #7360 supplies the singleton-square
projector argument, #7315 the disjoint idle precedent, #7541 the
distinct B2 transfer and #7298 the directed tariff. OpenAI Codex and
subagents materially assisted.
