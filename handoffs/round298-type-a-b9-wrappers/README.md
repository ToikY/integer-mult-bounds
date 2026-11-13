# Four-role boundary wrappers for the fixed Type A B9 transfer

**No verified κ gain.** This extends the
[fixed B9 transfer counterexample](https://github.com/ToikY/integer-mult-bounds/tree/a0f15df1216d0858ef2f5b4b6a90f3427fcce313/handoffs/round297-type-a-b9)
on #7546 at `99438c43df7aac1e5dbcc43c1578fcd886c119ec`
and signed #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`.
Keep the paid masks of that transfer and every interior event
in [1448,1746). Grant arbitrary constant rational entrance and exit
wrappers on Type A roles [0,1,10,11], supported only on the respective
four-role boundary bank. There is no assumed physical lowering.

The original and edited maps agree in the unit-body sector. For
each q=±1, use the ratio of the B9=−1 interval to the B9=+1 interval.
Any valid pair of wrappers must intertwine the old and new ratios
with a common entrance and have a common inverse exit supported
on the same four roles. The exact 16-variable affine system is
inconsistent. Its ten-equation certificate gives 0=4. Thus even
arbitrary constant rational wrappers on that bank do not restore the
required signed action. The original 4.490750678927025 raw gross
before wrappers is unchanged as an optimistic tariff quote. No
repair or construction advances.

Scope is one bank and one transfer, with both legal signed central
sectors and other bodies fixed at +1. Different banks, factor-dependent
or interior wrappers, and changed paid routes remain outside the scope.
A revisit needs a specific legal operation that bypasses the constant
boundary model and meets the full paid price.

Use CPython 3.12 with assertions and a clean scratch root:

```sh
replay_root="$(mktemp -d)"
sh fetch_inputs.sh "$replay_root"
python3.12 -I -B replay.py "$replay_root"
```

See [PLAN.md](PLAN.md) for the exact equations and remaining gates.
Credit #7402 for body-transfer screening, #7541 for the distinct
Type B transfer, #7309 for central phase, #7298 for the directed
tariff, #7546 for the comparator and #7113 for the signed caller.
OpenAI Codex materially assisted.
