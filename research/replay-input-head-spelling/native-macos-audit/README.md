# Native macOS corroboration of PR3007

PR3007's exact Git-spelling repair passes its registered replay on native macOS,
and the additional observations below cover both Unicode precomposition modes.
This answers the [native-platform handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2983#discussioncomment-18978628).
It is independently executed platform corroboration using the author's public
fixtures, with additional observations and baseline comparisons. It is not a
separately implemented verifier or independent human review.

## Exact scope and evidence

- Audited PR3007 head: `3cb500b743f36e13d21b6a46f126846bf36bad32`.
- Authenticated pre-repair runner: `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`.
- Session orientation main: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
- Host: macOS 26.5.2 arm64, CPython 3.12.14, Apple Git 2.50.1 (Apple Git-155).
- Fixture volume: actual ASCII case aliases and NFC/NFD aliases identify the
  same files, checked with `Path.samefile`, rather than inferred from the OS name.
- Registered replay: **9 new groups + 5 retained groups pass, zero skips**;
  source-authenticated before/after replay reports 3 baseline omissions,
  3 repaired rejections and 2 canonical positive controls.
- Additional native observation matrix: `core.precomposeunicode=false/true`
  crossed with initially NFC/NFD filenames. All four cases reject the alternate
  Git spelling before publishing matrix output and select the exact consumer.
  Four actual case-only rename fixtures select both old and new consumers.
- Full metadata: **16 baseline-accept / repaired-reject comparisons** = four
  fixture configurations × three ASCII aliases plus one Unicode alias. Four
  canonical fixtures pass both validators (eight validator calls). The added
  dependencies are intentionally unpinned, as the schema permits; this is not
  a claim that wrongly spelled SOURCES provenance pins pass.
- All 13 package/input source files are compared byte-for-byte with the exact
  PR head before loading fixtures. Imports use a fresh private bytecode-cache
  namespace. Source hashes are included in `native-observations.json`.
- The selected source-binding/arithmetic baseline passes at orientation main.
  Its scope is source bindings, not a full construction replay.

| Git precomposition | Initially created form | Exact HEAD/diff spelling | Alternate spelling |
| --- | --- | --- | --- |
| false | NFC | `src/caf\u00e9.json` | NFD rejected |
| false | NFD | `src/cafe\u0301.json` | NFC rejected |
| true | NFC | `src/caf\u00e9.json` | NFD rejected |
| true | NFD | `src/caf\u00e9.json` | NFD rejected |

Normal and optimized Python execution produce byte-identical observation JSON.
The JSON preserves the raw UTF-8 and NUL-framed diff bytes. This distinction
matters: the original test creates NFC and forces precomposition off, so it
alone does not exercise an NFD HEAD entry or Git's NFD-to-NFC conversion.

## Reproduce

Use Python 3.12 and Git on native macOS with a case/Unicode-insensitive temporary
volume. A case-sensitive or non-Mac host fails the extra probe explicitly;
that is an unavailable native prerequisite, not a pass.

Keep this audit directory separate from the checkout under test. In a new
scratch checkout, fetch both exact commits; the registered differential and
this probe require the baseline object even with a shallow clone:

```sh
git clone --filter=blob:none --no-checkout --single-branch --depth=1 https://github.com/CrocSwap/integer-mult-bounds.git pr3007-check
git -C pr3007-check fetch --depth=1 https://github.com/petalas/integer-mult-bounds.git 3cb500b743f36e13d21b6a46f126846bf36bad32
git -C pr3007-check fetch --depth=1 origin 836b19bfa309ceafbc8ee32a15e8c4b10dde7e11
git -C pr3007-check sparse-checkout init --no-cone
printf '/scripts/\n/tests/\n/research/replay-input-head-spelling/\n' > pr3007-check/.git/info/sparse-checkout
git -C pr3007-check checkout --detach 3cb500b743f36e13d21b6a46f126846bf36bad32
```

From `pr3007-check`, run:

```sh
python3.12 -B scripts/research_package.py --package research/replay-input-head-spelling
```

Then run the saved probe from anywhere, passing the checkout path:

```sh
python3.12 -I -B /path/to/audit/native_probe.py /path/to/pr3007-check
```

Expected markers are `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_NATIVE_MACOS_HEAD_SPELLING`. The probe emits a complete JSON receipt;
`registered-replay.log` preserves this host's registered output. Rough runtime
is tens of seconds after source retrieval; no dependencies are installed.
The audit does not modify the checkout under test. Fixtures are disposable.

## Remaining obligations and stopping point

The requested native macOS check passes; no production repair or redundant
registered package is warranted by these observations. This directory is a
source-bound evidence attachment for the existing PR, not a new supplier or
an instruction to merge it. Native Windows execution remains the actionable
handoff: run PR3007's registered command on Windows and report its intentional
filename-control skips separately. Distinct tracked names that physically
alias, concurrent writers, hostile-repository limits, hosted CI and full cold
supplier replay retain their prior scope. No selected-frontier or κ change.

Entry overlap covered 261 open PR bodies including drafts, the current active
board, recent #1166 handoffs and all comments in #2983. The local helper was
used offline because `gh` was unavailable and reported missing remote cache;
connector/UI reads supplied the bounded live coverage. Older global Discussion
and closed-PR history were not exhaustively paginated. This is a claimed,
explicitly complementary platform check, not a discovery-priority claim.

## Credit

Nick Petalas/PR3007 supplied the repair, registered reproducer, Git/CLI fixtures
and native-platform handoff. Arham Tahir/PR2994 supplied the native macOS
counterexamples and precise repair contract. Retain Nick Petalas/PR2986 and
EdDiboi's earlier alias finding; woklerx/PR1891, Charles Bethin, Douglas Colkitt
and the retained runner/scaffold lineage. This audit changes none of their
source files or attribution.

Native execution, additional observation probe and handoff by ToikY with
substantial OpenAI Codex assistance. Apache-2.0. Independent automated source
review was used; no independent human review or formal proof is claimed.
