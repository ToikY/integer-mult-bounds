# Eight owned MOVE runs with no zero field to reinitialize

**No verified κ gain.** On exact #7546 at
`99438c43df7aac1e5dbcc43c1578fcd886c119ec` with signed #7113
at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, enumerate
owned MOVE runs between consecutive non-MOVE contacts, counting
both operands of ADD and COPY. The literal inventory has 74
owned lifetimes, 47 owned MOVEs, 47 eligible interior runs and
no eligible terminal CLEAR run. The COPY destination lifetime
has no run. No exact row is tested there.

The proposed edit would CLEAR an owned zero field immediately
before its first paid MOVE and INIT a fresh zero field in the
next contact chart. The necessary normalized arbitrary-input
row must vanish. The directed price ranks the runs by
`17 × sum r^(1−κ)` on the pinned comparator crossing,
granting zero extra paid cost. The signed invoice credits only
nonhosted public helpers and caller diagonals as targets. Owned
rises earn no productive target credit. Each of the eight tested
runs has one paid MOVE. The largest optimistic gross is about
101.33539296045362 raw for role 1530 at MOVE41658. No observed
saving follows from this quote.

All eight rows are nonzero. The signed normalized coefficient
of input 1 in role 1530 is −17/4. Independent forward replay
agrees on all eight support sizes and first nonzero
coefficients, and checks the owners and nested charts from the
literal tape. The 30-second wall cap did not bind. The eight-case
cap did, leaving 39 ordered runs unresolved. Neither an
alternative live-value transfer nor a paid construction was
tested. See [the ordered exact receipt](expected/RESULT.jsonl).

Use CPython 3.12 with assertions and an empty scratch root.
The three fetched dependencies are immutable commit bytes,
each authenticated in replay.

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

Credit #7307 for the earlier zero-row audit on #7277 and its
terminal direct-CLEAR test. This bounded round tests interior
CLEAR/INIT on the current #7546 word. #7555 supplied the
structural-cut motivation. It did not establish a zero run on
this word. #7482 supplied the exact normalized adjoint approach,
#7298 directed pricing, and #7113 the signed caller. OpenAI
Codex materially assisted.
