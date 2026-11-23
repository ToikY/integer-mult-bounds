# Reproduce the 25-bit signed profile and independent invoice

Use CPython 3.12 and Git on a POSIX host. Check out these exact commits in clean detached worktrees, including their Git ancestry.

- Candidate `aea1699415250d865f7a635f4df0b76f406c47b4`
- Comparator [#8081 at 51011382](https://github.com/CrocSwap/integer-mult-bounds/commit/510113821774bb27f7ddaad4e8b94837a1c2cf52)
- Historical prerequisite `0618e75a22cec54d1651394ef83d088551b7f026` in both worktrees
- [#8072 source](https://github.com/CrocSwap/integer-mult-bounds/commit/75f7e1c44f48c43983016bcf8878c4d9e5e87c62) authenticated by ten retained Git blob pins
- [#8057 signed source](https://github.com/CrocSwap/integer-mult-bounds/commit/cbe847a953b971f9c6c5a0a6661e2008acd29086) authenticated by the archived input and 88 member hashes

From the clean candidate checkout, run all eight scientific modes.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-period-debit-25bit
```

From this evidence directory, supply the candidate and comparator worktree roots.

```sh
python3.12 -IB reproduce_invoice.py ./inputs/candidate ./inputs/comparator
```

The independent command authenticates the two clean detached roots and reconstructs the runtime images in a fresh temporary directory. It binds the 30 candidate paths and modes, the 31 comparator files, and 26 path-keyed receipt hashes to their exact bytes. It checks the entire independent result byte for byte. No prior temporary pointer or machine-specific interpreter path is required. Its expected output is `PASS_INDEPENDENT_25BIT_INVOICE 789df09bfe46ed6116f268ab4665dd2cf697da669385dd871d938c114fbb6d29`. [Comparison](independent-invoice.json) · [Candidate manifest](CANDIDATE-INPUTS.json) · [Authenticated comparator receipt](peer-evidence/REPLAY-RECEIPT.json)

The comparison found one exact profile line changed across 106 installed signed runtime files. It reconstructed both tier margins, precision at the two extent ends, the Gaussian period charge, the ordinary charge, the complete recurring invoice, the cutoff and the charged installer bound. The old #8081 rate and invoice are positive controls. The new debit one tick lower and the old period factor at the new debit both reject. At fixed ordinary coordinates Gaussian G−1 stays funded and G−2 rejects. Two finite signed tape controls reject the wrong return orientation. The scientific replay runs two- and four-column signed raw cases, exterior births and owner restoration, a nonzero nested return, the finite signed product `−345550037539`, and the actual setup. The installer formed the 18,845,935-bit carrier and 2,407,819 directory records. The five existing conditional premises remain, and the independent registration covers a symbolic terminal fence and finite signed executions. A terminal astronomical execution and a new WASI fuel trace are open.

The first independent replay printed all eight mode successes and terminal completion. Its outer macOS timing process failed when requesting a clock-rate setting. The original receipt and log preserve that failure and distinguish the scientific command's inferred exit from the wrapper's observed exit. One initial source-check failure log is retained locally because it contains machine paths; its exact digest remains in the receipt. The direct retry and repository checks have separate receipts. [Original timing diagnosis](initial-replay/README.md) · [Original timing receipt](initial-replay/REPLAY-RECEIPT.json) · [Installer audit](INSTALLER-AUDIT.md) · [Repository preflight](candidate-preflight.log) · [Historical check](historical.log) · [Onboarding summary](onboarding-summary.log)

The direct retry stopped after 177.13 s at the disk guard, observer exit 124. It reached the signed product step, which had passed on the original replay. [Retry receipt](DIRECT-RETRY-RECEIPT.json) · [Partial retry log](retry-replay.log)
