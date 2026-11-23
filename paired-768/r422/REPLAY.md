# Round 422 exact #8094 replay checkpoint

**2026-11-23 UTC · NO VERIFIED GAIN**

Clean [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) pin `c20a08dc0a79a989e3515068560d5da371c0a2a8`, Git tree `0f702e9a2275bc2678f33fc178ed9a8c072d907e`. Use CPython 3.12 with assertions and Git. See the exact [source and environment pins](peer-inputs.log) and [frontier coverage](FRONTIER.md).

| Scope | Local result |
| --- | --- |
| Price, calendar, raw, exterior, nested | All five passed in unchanged registered order |
| Product | Unresolved after the registered 100-second cap |
| Setup | Passed as a separate unchanged 60-second stage after the aggregate stopped |

The aggregate [registered command](peer-registered.log) exited 1 at 23:03:27 UTC after 466.57 wall seconds. [Setup](peer-setup.log) exited 0 at 23:04:01 UTC after 1.02 seconds. It passed 4,071 integer pairs and 7,396 rational cases. The setup scope checks serial arithmetic and the reported legacy subtotal. The installed nine-recipe census and expanded lookup accounting are distinct. The first launch exited 1 before calculating price due to Git discovering a stale enclosing worktree in nested scratch. Fresh external scratch fixed that launch condition without changing the replay input or verifier. Disk reserve at corrected launch was about 40 GiB free. [Peer hosted run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45143810893) still requires action and has zero jobs.

From a clean checkout at the exact pin, put temporary files in fresh writable space outside any enclosing checkout. Verify 8 GiB free on checkout and scratch volumes and use one substantial runner. On POSIX:

```sh
export TMPDIR="$(mktemp -d /tmp/croc-8094.XXXXXX)"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
python3.12 -IB scripts/research_package.py --package research/p104-shortcut-word-eta-27bit-5stage
```

To resume the unresolved product stage without repeating the six unchanged scopes, run the same exact stage once using the 220-second signed product cap in the archived #8057 frequency-weighted manifest. Retain the original 100-second timeout and record the extended scope separately. This command uses the registered driver's isolated subprocess and timeout implementation:

```sh
python3.12 -IB -c 'from pathlib import Path; import runpy,sys; m=runpy.run_path("scripts/research_package.py"); m["run_python_replay"]([sys.executable,"-IB","research/p104-shortcut-word-eta-27bit-5stage/verify.py","product"],Path.cwd(),220)'
```

The first terminal result of that one product attempt controls the next decision. If it passes with unchanged pins, preserve its own exit and receipt alongside the six passes. If it caps or fails, retain #8094 as the stronger unfinished claim and diagnose the result before promoting any comparator. The strongest prior comparable completed hosted witness was [#8089](https://github.com/CrocSwap/integer-mult-bounds/pull/8089) at κ 0.0039. The maintainer-selected result is #7000. There is no campaign Δκ.

The [frozen candidate](../r420/RESTART.md) reassembled byte-for-byte from this public head. [Independent ratio and rate accounting](COMPARISON.md) identifies the exact ordinary and Gaussian crossings and checks their composition. Its projected rate 0.003900857312000 requires a genuine installed receipt, exact signed physical and owner checks, full product, and census. None ran in this round. Resume these from the pinned source only after settling the product comparison.

Credit floration's #8094 retune and shortcut word, Ali Romman's #8057 signed stack and #8042 quotient pricing, SYLforge's K7 source and [#8085](https://github.com/CrocSwap/integer-mult-bounds/pull/8085) for the exterior period proof. OpenAI Codex assisted in replay and exact comparison.
