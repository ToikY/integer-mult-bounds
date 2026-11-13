# Opposite ADD pairs and paid MOVE stops on exact #7481

**NO VERIFIED GAIN.** The benchmark is [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) at `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b`, κ `0.003647081039689`, with the signed [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Each replay authenticates the supplied inputs by relative path. Run from this directory on POSIX with CPython 3.12 and the standard library.

```sh
receipt=$(mktemp)
python3.12 -I -B lead/check_inverse_fusion.py > "$receipt"
python3.12 -I -B pivot/check_inverse_independent.py . "$receipt" "$(shasum -a 256 "$receipt" | cut -d' ' -f1)"
```

Expect `PASS_INDEPENDENT_INVERSE_FUSION_CENSUS`. Each process is capped at 30 seconds. The screen exhausted all 176 exact keys within the 256-case cap and matched the independent enumeration, prices and first blockers. There were 130 noncommuting contacts and 46 changed destination operands at protected or owned operations under the fixed guard. Zero keys remain unresolved in this scope. The receipt contains all case keys, exact directed gross intervals, and barriers. The 46 conservative guard failures leave open identities that preserve every protected source while changing a transient unobserved destination.

The separate [chart-115 construction #7526](https://github.com/CrocSwap/integer-mult-bounds/pull/7526) is a zero-paid-saving positive control. It removes two inverse ADDs across identical physical MOVEs and reduces the signed ordinary upper bound by 544 source units. Paid and productive profiles stay fixed. Wrong signs, source writes, and an additional middle observer are rejection controls.

## Next decision

The prepared role1261 correction test is unrun. It checks one chart-246 cut before ADD39469 under a 30-second cap. Run after refreshing the comparator.

```sh
python3.12 -I -B pivot/check_1261_telescoping.py inputs
```

The exact historical correction is (old910 at pre39438 + old953 at pre39441)/2. If the seven unchanged donors span it, require a legal exact coefficient schedule, full signed physical replay, preservation of protected reads and ownership, and a positive fully charged price before claiming a gain. The hypothetical paid gross is about 0.25649690069 raw across 17 calls. One added paid rank-one child per call costs 17 raw. A separator retires this one cut, and a cap leaves it unresolved. See [chronology and price details](pivot/HANDOFF.md).

## Credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) and [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) supplied the native chronology. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplied the caller. [#5265](https://github.com/CrocSwap/integer-mult-bounds/pull/5265) demonstrated inverse ADDs on an older word. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) supplied commutation logic. [#7494](https://github.com/CrocSwap/integer-mult-bounds/pull/7494) is the same-word fixed-peer retiming precedent. [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplied exact covectors and directed pricing. Source licenses remain Apache-2.0. OpenAI Codex and subagents materially assisted the proof, implementation and replay.
