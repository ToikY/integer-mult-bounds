# Fixed chart515 productive readout for role1264

**No verified κ gain.** On the exact #7546 word, head
`99438c43df7aac1e5dbcc43c1578fcd886c119ec`, with signed #7113 at
`07a76c5e2738882c0cb322278e56f6cae3c9885d`, public1264 first lifts
from chart3 to chart515 at MOVE38879. A proposed split would make
that rank-three output productive and use the existing rank-six
continuation for a fresh independent input. Its optimistic increase
in the signed moment is about 0.35298744576954605 raw before any
admission or repair costs, less than one rank-one paid position.

One exact case asks for old independent x1264 from the complete
chart515 bank [446,1203,1264] before ADD38880. The pinned adjoint
calculation leaves a 60-term exact remainder. In independent
literal forward replay, zero and the input x516=2, x1264=1 produce
the same bank [0,0,0] but require x1264 outputs 0 and 1. The
x1264 input alone gives a nonzero current bank direction. The
forward check exhausted all 1,500 potential companion coordinates
and found 24 collisions. Its 1.16-second wall time and the
0.18-second adjoint check were below the 30-second cap.

This exclusion covers all deterministic recoveries from those
three current bank values. It leaves other banks and earlier
co-encodings unresolved. The suffix, signed physical typed
interface and complete application were outside the replay after
the required readout failed. Reopen only with a named source for
the missing direction that preserves the existing paid invoice.

Use CPython 3.12 with assertions and an empty scratch root from
this directory. The immutable fetch supplies three files, each
authenticated by both verification paths.

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

See [PLAN.md](PLAN.md) for exact scope and typed-output obligations.
#7546 supplies the word and #7113 the signed caller. Credit #7156
for the distinct causal split precedent, #7482 for exact normalized
cut rows, and #7298 for directed pricing. OpenAI Codex materially
assisted.
