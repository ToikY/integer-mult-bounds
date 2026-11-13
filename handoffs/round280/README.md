# Paired outward-read co-encoding

[Round 280](https://github.com/CrocSwap/integer-mult-bounds/pull/7538) rules out the two named early encodings for owned1548 at their first deadline. The next test switches to paired public outward reads. It looks for two coframed sources whose exact outward updates can be combined at their first receiver, with both independent values restored along a fully charged return detour.

From this fork snapshot's root with CPython 3.12:

```sh
replay_inputs=$(mktemp -d)
cp research/p104-owned1548-early-encoding-bound/inputs/7481-WORD.json.gz \
   research/p104-owned1548-early-encoding-bound/inputs/7481-APPLICATION.json \
   research/p104-owned1548-early-encoding-bound/inputs/7113-CALLER.json "$replay_inputs/"
cp handoffs/round280/pricing.py "$replay_inputs/"
python3.12 -I -B handoffs/round280/check_paired_outward.py "$replay_inputs"
```

The input tariff file is bundled next to the runner and is authenticated as part of the replay. Refresh exact overlap and the live comparator before executing. One literal pass, 64 ranked keys, 30 seconds, and at most one nomination. The test is unrun. A nominated route still requires a literal construction, exact signed action, ownership and both restored outputs, and complete independent pricing and replay. See [PLAN.md](PLAN.md).
