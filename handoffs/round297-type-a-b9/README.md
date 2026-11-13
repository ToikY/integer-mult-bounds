# Fixed Type A B9 transfer between paid idles

**No verified κ gain.** On #7546 at
`99438c43df7aac1e5dbcc43c1578fcd886c119ec` and the exact signed #7113
caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, transfer the eight
B9 axes from Type A role11 IDLE1745 to role1 IDLE1448. Keep the original
B9 at clock1742 and every other event in [1448,1746). The signed paid
delta over all 96 ports is {8:+96,16:−96,56:−96,64:+96}, paid rank mass
fixed, productive delta empty. The optimistic directed gross is about
4.490750678927025 raw before any repair.

At width one with q=+1, B9=−1 and the other bodies +1, the fixed
interval loses equality on the 36 exact interface columns. For
input role0, old output role11 is −2 and the edited value is +2.
Independent reverse replay
reconstructs all 36 rows, authenticates the geometry of all 96 Type A
central axes and gets exactly three differing entries. At width one
the selected two minus Walsh labels on axes 73 and 74 give factors
i·i = −1 in B9 and leave central q at +1. Both the all-positive
body equality and the mutation removing the retained IDLE1742
behave as expected. The primary and independent checks exit zero
in 0.11 and 0.16 seconds. One tested fixed interval
exhausts its declared scope within 30 seconds. Different wrappers,
other body factors, other clocks and independently charged
repairs remain open. This version has no admissible fully charged
saving. No candidate was built.

Use CPython 3.12 with assertions and an empty scratch root.
Input application, word, and exact caller are fetched by immutable
commit and authenticated in replay. The verifier's paid-price
tariff is package-local.

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

See [PLAN.md](PLAN.md) for the exact ordinary and signed scope.
Credit #7402 for the body-transfer screen, #7541 for a distinct Type B
B2 transfer, #7309 for central-phase direction, #7298 for directed
pricing, #7546 for the complete native basis and #7113 for the signed
caller. OpenAI Codex materially assisted.
