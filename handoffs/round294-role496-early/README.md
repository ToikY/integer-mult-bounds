# Role496 earlier chart912 bank exclusion

**No verified κ gain.** The exact #7546 word at
`96e4a0dd34b98388d2911fd37df70c15e70840de` and signed #7113 at
`07a76c5e2738882c0cb322278e56f6cae3c9885d` bind the same proposed
rank-three fusion of role496 MOVEs 40952/40957 and omissions of ADDs
40954/40956 as the [later fixed-bank exclusion](https://github.com/ToikY/integer-mult-bounds/tree/6b4e5c0a2f69315f4cbaac036dcdcc445963c49e/handoffs/round293-role496).
This test uses the different early bank [496,903,984,1129] in
chart912 before event41782 while the two paid carriers are still live.

The adjoint test finds a nonzero exact span remainder. Independent
forward replay checks all 1,501 unit-coordinate probes. For zero and
unit input x₂, the full edited bank is [0,0,0,0]. Old role496 is
respectively 0 and −1, and its unchanged later ADD43371 requires
old role220 to return 0 and 1/2. The 28 colliding coordinates include
this minimum-support counterexample. Any deterministic repair from
only those four current values receives identical inputs. The one
case finished below its 30-second cap, in 0.15s for the adjoint and
0.82s for the independent replay. No case remains open at this cut.

The price before repairs is about 0.11813504186795777 raw, which is
below the cost of one extra rank-one position in the signed caller.
This result leaves earlier changed encodings or changed paid routes
and the separate role994 return before ADD46168 unresolved. With
both tested fixed banks excluded, pivot to a different source of
paid savings. Reopen this route only with a named distinct carrier
or legal earlier deadline and a charged repair that preserves the
other independent outputs.

Use CPython 3.12 with assertions and an empty scratch root from this
directory. The only network dependency is the fetch of three
immutable published inputs, checked against exact hashes by both
verifiers.

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

The exact [test plan](PLAN.md) gives input pins and legal donor
versions. Credit #7542 for the neighboring chart edits and role230
journey, #7544 and #7546 for complete literal replay, #7113 for the
signed caller, #7482 for normalized adjoint replay and #7298 for the
directed recurrence. OpenAI Codex materially assisted.
