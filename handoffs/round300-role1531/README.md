# Fixed chart117 readout for the owned role1531 fusion

**No verified κ gain.** On [#7546](https://github.com/CrocSwap/integer-mult-bounds/pull/7546)
at `99438c43df7aac1e5dbcc43c1578fcd886c119ec` with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at
`07a76c5e2738882c0cb322278e56f6cae3c9885d`, consider joining the
two rank-one lifts at MOVE44261 and MOVE44263. The proposed edit
moves the intervening ADD of −4 times role995 back to chart117.
The existing owner of role1531 and the first outward ADD into917
remain required. The signed paid delta would be {1:−34,2:+17}
with fixed productive positions and rank mass. The exact directed
optimistic gross is about 0.08587349617870836 raw before the
required scalar recipe and physical lowering.

The eight actual read-only chart117 donors have rank eight.
Old role995 increases their rank to nine. On inputs
`x2=1, x7=−1` with the others zero, every donor gives zero
and old995 gives one. Holding the old role1531 coefficient at
one, no ordinary ADD combination on this bank supplies the
needed −4 multiple. Independent forward replay also checks the owner: all nine chart117
rows, including role1531, agree on this probe and zero. Old role917
after ADD44265 is −2 on the probe, versus 0 on zero. No deterministic
correction using only those nine values can recover both outputs in
this fixed continuation.

The ten relevant normalized rows, including the old target and
host, agree coefficient for coefficient between historical #7334
pre44242 and #7546 pre44261. Thus this corroborates
[#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355)
on the current word and replays a separating input that also
annihilates the host. It does not extend #7355's rank scope.
This is one pre-MOVE case within the
30-second cap. Other cuts, changed earlier encodings, and
support at the later chart are outside this scope. A literal
fusion and complete application did not advance.

Use CPython 3.12 with assertions from a clean checkout.

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

Credit #7355 for the older monotone ADD fusion screen, #7378 and
#7393 for neighboring role1531 work, #7546 and #7113 for the exact
word and signed caller, #7482 for the exact row method and #7298
for directed pricing. OpenAI Codex materially assisted.
