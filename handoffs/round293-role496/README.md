# Role496 fixed chart912 bank exclusion

**No verified κ gain.** On the exact #7546 word at
`96e4a0dd34b98388d2911fd37df70c15e70840de`, with signed #7113 at
`07a76c5e2738882c0cb322278e56f6cae3c9885d`, test the role496 fusion
of MOVEs 40952 and 40957 (729→730→912). The proposed direct 729→912
MOVE omits ADD40954 into496 and ADD40956 into994. The only legal live
bank for the tested repair before ADD43371 is [220,496,1129].
Returning old496 from these three edited values is impossible. The
adjoint support test exhausts this one cut and emits a nonzero exact
full-bank remainder. The signed paid delta if the unbuilt splice
needed no repair would be {1:−17,2:−17,3:+17}. Its optimistic gross
saving is about 0.11813504186795777 raw. The inadmissible version has
no fully charged saving.

The independent forward replay applies the literal direct MOVE and
both omitted ADDs to all normalized public coefficient columns.
Of the 1,501 one-coordinate probes, 28 collide with zero on the
edited bank and separate the old role496. The first is input role2
equal to 1 with all other values zero. Both probes give edited
[0,0,0]. Old role496 is −1 on that input, requiring old receiver220
to return 1/2 at ADD43371, while the zero input requires 0.
The collision excludes any deterministic repair given only those
three bank values. The adjoint and forward receipts took 0.18 and
0.84 seconds locally, both exit 0.

Use CPython 3.12 and an empty scratch root. Fetch authenticates
through the replay scripts against exact SHA256 pins, including the
signed application receipt. The only network dependency is fetching
the three published inputs at the stated commit.

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

The original 30-second case cap was not reached. The earlier paid
984 and 903 arrivals leave chart912 before the fixed deadline.
The next test is the bank [496,903,984,1129] at pre41782, before
984 and 903 leave on their paid moves. That earlier repair, the separate return of
994 before ADD46168, and altered producer encodings are outside the
exclusion. A viable variant must name an earlier carrier of the
missing role230 direction and repay every added operation. Only
then does the 994 deadline merit a build attempt.

Credit #7542 for the neighboring role1077 compensation and paid role
230 path, #7544 for its composition, #7546 for the exact comparator,
#7113 for signed pricing context, #7482 for exact normalized cut rows
and #7298 for the directed tariff. Existing source credits apply.
OpenAI Codex materially assisted this test and its independent replay.
