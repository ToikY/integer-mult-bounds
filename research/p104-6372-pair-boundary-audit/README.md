# Independent PR6372 two-anchor rational audit

This is an **in-progress local checkpoint**, not yet the completed contribution.
The first session checks the changed contact block and exact local identities.
The second session is reserved for complete emitted-word restoration and endpoint
binding after refreshing main and overlap. Frozen checkpoint files and inputs
remain preserved separately.

The exact candidate is PR6372 head
`b556600ffe14be72406b03a47c661f3c7f1aff06`, on PR6353 head
`db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`. Canonical main is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision8,
selected6030 unchanged. This is independent verification of a newly changed
two-anchor contact block, not another count of the older nine-anchor result.

## Local question

Anchors224/227 have input directions
`u_a=2e224+v`, `u_b=2e224-v`, where
`v=e227+e228-e229-e232+e233-e238+e239-e449`. The anchor block of B0 has
determinant−4, a unit over the dyadic rationals. A changed departure basis C
mixes rows193,169 and742, swaps pivots into the anchor positions and eliminates
the other response in row204. Those public rows remain arbitrary; they must
not be silently initialized to zero.

The source preparation A includes **nine existing owned temporary lifetimes**.
The audit interprets their INIT/CLEAR and scalar operations, rather than using
the public-only preparation shortcut from the older PR6355 audit. It checks
complete functionals over all770 arbitrary public inputs, the two unit pairings,
off-anchor correction support and the response columns. The two new shadows
779/780 add two further dual preparation zero obligations.

These are scalar-projection checks. MOVE is treated as identity in the rational
transfer calculation; non-extreme native frames are labels for ordering and
common-frame comparisons. No complemented native basis, absolute phase or
physical operator correctness follows from that projection. Eleven zero rows
at **dual preparation** CLEARs do not imply zero forward CLEAR functionals or
permission to erase them.

## Reproduce the checkpoint

With Python3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-6372-pair-boundary-audit --check-only
python3.12 -B scripts/research_package.py --package research/p104-6372-pair-boundary-audit
```

The manifest runs two independent local checkers normally and optimized. The
default commands compare exact typed retained receipts; `--emit` prints fresh
candidates without writing files or asserting receipt equality. Source Python
and the upstream proof are authenticated provenance data, never imported.
All six retained source files have byte-exact SHA256 and Git-blob pins. Package
copies make standalone replay independent of foreign Git history or network.

`LOCAL-PROOF.md` explains the exact local argument. `TASK.json` records the
partial outcome, stop rule and open next questions. The final verification
record will distinguish semantic coefficient controls from source/receipt
transport controls and list which parts remain unrun.

## Scope, overlap and credit

[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19355422).
The author explicitly requests independent checks of this pair's unit responses,
zero rows and complete debit. The earlier search excluded this contact block;
the construction changes that hypothesis. No generic nilpotent basis theorem
is newly discovered here.

PR6355 and the other B7 contributions concern earlier exact source scopes.
Unpaidmoon's stage-one contact and ordinary-bound findings also retain their
distinct credit. Old all-width, spectator and native-contact proofs were read;
a proposed uniform-route corollary was set aside instead of counting it as a
new supplier gate. The overlap snapshot is bounded and non-atomic, with sparse
local/code/history/private/Discussion coverage; no-match is not novelty proof.

Credit stays with Ali Romman and PR6372/6353/6349/6348/6350, DreamingOfClouds,
Cinna Davis, the native/helper/caller/compiler authors and the complete retained
[NOTICE](sources/NOTICE). The older scalar transpose audit PR6355 and its
limitations retain credit. New independent source-specific checkers and proof
review are ToikY's work with substantial OpenAI Codex assistance and bounded
separately assigned agents. Same-session reviews are author-side evidence.
Apache-2.0.

## Open next questions

Complete the full public endpoint and literal restoration/lifetime/debit binding
in the next session, preserving these exact inputs and checkpoint receipts.
Native implementation, physical caller applicability, owned erasure, complete
funding/compiler/outer admission, all five framework assumptions and human
acceptance remain separate. There is no new kappa, multiplier theorem or
selected-frontier change. No merge or closure is authorized by this package.
