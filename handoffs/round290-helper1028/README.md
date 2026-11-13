# Helper1028 repair limits on the composed native word

The fixed early ADD and rung fusion uses the word from #7544 at
`d6be7d620c9c8337104daeb09fe01196eced5fe3` and signed #7113 at
`07a76c5e2738882c0cb322278e56f6cae3c9885d`. It moves the half of
role1028 into role1024 before MOVE36416 and replaces MOVE36418 and
MOVE36421 with one 3→302 move. Through the old ADD36417, the sole cut
deviation is −v/2 on role797, where v is the historical row1028.

The deviation reaches the endpoint as one impulse on role797. In the
original output coordinates v needs eight rows outside chart127.
A pair of arbitrary input probes gives the same complete edited
chart127 bank and requires different original role797 values. The
1052 chart127 rows cannot implement that terminal repair.

The complete chart23 bank immediately before MOVE36877 also fails.
Input x34=−2, x142=−4 gives the same zero edited bank on roles
25, 797, 1024 and 1025 as the zero input. The original role797 equals
1 on that input and 0 on the zero input. The replay derives the
separator from exact rows and verifies it with literal forward
propagation, including chart, ownership and COPY assertions.

The prospective signed paid delta is {1:−17,2:−17,3:+17}, with no
productive change. Its directed gross lies in
[0.11812076067945571, 0.11812076067945572] raw. Both fixed-bank repairs
fail, so no saving was realized. Earlier encodings, different cuts
and other carriers remain open. A new rank-one paid action per call
already consumes the projected gain.

## Replay

Use CPython 3.12 with assertions enabled. Fetch the exact public
word, application receipt and signed caller into an explicit scratch
directory, then verify their SHA-256 hashes in the replay.

```sh
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

Each exact runner has a 30-second cap. Both named repair cases
exhausted their scopes.

#7544 supplies the composed word. #7542 supplies the rung merges
and earlier ingress precedent, with #7481/#7480/#7334 the earlier
native lineage. #7113 supplies the signed caller. #7003 supplies
the paid fusion precedent, #7495 and Round 246 the endpoint-coordinate
method, and #7298 the directed tariff. OpenAI Codex and subagents
materially assisted.
