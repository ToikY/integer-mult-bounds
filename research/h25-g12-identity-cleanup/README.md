# G12 identity conversion and preflight close repair

**Partial source repair. No κ, no N22/P07 adoption, no H25 execution.**

## Scope and evidence

This takes contributor task A from the open H25 cache handoff on
[discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19307764),
whose canonical thread is [PR6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321)
at `ca9d90e93dc495e1e5e5ef6d271ff1e4f089cd0c`. The catalogue card is
`portable-replay`. Scope is **changed**: that card starts from the gzip-container
comparison, and this package repairs two named G12 custody defects instead.
The connection is the handoff's comparison blocker, not a new multiplication
supplier. Selected κ stays `781451/250000000`. The five framework assumptions
stay in force.

The frozen parent emits `candidate_pin` as the accepted nine-tuple and puts
manifest identity in field 4 as `(dev, ino, full_st_mode, size, mtime_ns, ctime_ns)`.
The consumer then builds a file record whose `_file_record` validator requires
that field to be a dictionary with exactly those string keys. A raw tuple fails
`G12-N12` before any later identity check.

The chosen representation is the existing nine-tuple. The corrected parent names
the packer `_handoff_identity_tuple`. The corrected consumer converts that tuple
with `_identity_dict_from_handoff` before the file record is built. A dictionary,
a short or long tuple, a non-integer, a nonpositive inode, or a non-regular mode
is rejected at that boundary. `_file_record` still checks key domain, integer
domain, regular-file mode and size.

Two parent preflight `finally` blocks closed directory descriptors with a bare
`os.close` loop. If a close raises, that exception replaces the pending primary
(for example `G12-N05: prior output/evidence/custody path exists`) and the loop
stops, so later descriptors stay open. The corrected parent uses
`_finally_close_known`: every descriptor is closed independently, close failures
are appended to the existing ordered secondary list, a pending primary is left
to propagate, and a successful body with a failed close still fails.

`verify.py` checks the vendored predecessor SHA-256 values and their PR6321 git
blob ids `80482f9a9af1f471bc567c52cc31e6dc8a39c26f` and
`19cb9376c2d757e1deb354608a1351c39e4daae1`, the tuple rejection, the conversion
round trip, the repaired close behavior, and a miniature bare-finally control
that still replaces the primary and stops early. Importing either corrected
module leaves the launch and the handoff unselected. The historical absolute
root is not used.

## What this does not establish

The frozen snapshot is not edited. The corrected files are a successor, not a
reviewed integration and not a runtime. The other 18 negative branches, schema
predicates, syscall races, allocation failures, ownership, aliases and the
adapter path were not reviewed. No N22 or P07 body credit is claimed. P02's
bridge is untouched. No cache speedup is measured. Unknown cost tails stay
unknown.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/h25-g12-identity-cleanup --check-only
python3 scripts/research_package.py --package research/h25-g12-identity-cleanup
```

Directly: `python3 -B research/h25-g12-identity-cleanup/verify.py` prints
`PASS_H25_G12_IDENTITY_CLEANUP`. Pins are in [SOURCES.json](SOURCES.json).
The predecessor `.py.txt` files are inert copies of the PR6321 sources and are
not a replay of that handoff.

## Open next questions

1. Do the corrected parent and consumer satisfy the remaining G12 source checks
   for N22 and P07, including all 18 negative branches? That review is what
   task A requires before body credit. Start from the corrected files and the
   real parent-to-adapter-to-consumer path. It is blocked here because this
   package stops at the two named defects, and the historical one-use runtime
   admission is not transferable.
2. Can the accepted P02 v4 reference bridge be implemented without changing
   producer order or the rejected pure-side-only retention? P02 is the other
   lane of the same handoff. Start from `DESIGN-v4.json` in the PR6321 archive.
   This package does not contain that implementation.

## Credit

Chris R / Clear1nsight, PR6321, PR6029 and the retained Douglas R. Colkitt
circuit, network and verification lineage. The predecessor source bytes and
their notices are unchanged. Prepared by unpaidmoon with substantial Cursor
Grok assistance. Apache-2.0. No independent human or proof-kernel acceptance
is claimed.
