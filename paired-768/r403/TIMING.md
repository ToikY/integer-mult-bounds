# Round 403 timing

Round opened 03:04:49 UTC. The exact screen considered 11 prices and finished in 0.014396 s. Independent price and complete invoice gate took 0.24 s, with one candidate below both charged limits. Active source tracing, proof and implementation times were not separately measured.

Literal build used 77.286 s (regeneration 6.435, price 17.404, calendar 53.446). The fresh scientific replay ran 03:12:19–03:15:56 UTC, 217.61 s wall, 161.29 s user, 53.25 s system. It passed all seven modes and returned clean. The first complete independent decision was available shortly after that replay, with the sealed arithmetic around 03:16 UTC. The baseline 229.50 s replay receipt was reused only after checking exact source bytes, hashes, modes, Git prerequisites and live checks.

Onboarding test fixture admission began 03:11:39 UTC. Comparing a foreign Git object in the sparse checkout stopped the first preflight before any tests ran. Comparing the trees in their own pinned checkouts corrected the check and confirmed identical test, workflow and runner sources. The full suite then ran once at 03:14:11, passing 760 tests with 31 skips in 146.54 s. Historical replay passed its declared partial scope in 2.35 s with all 19 expected rejection controls. The 152 s calendar gap between initial preparation and test launch includes the correction, unrelated work and tooling overhead. It is not an active preparation estimate.

This was the planned up-front fixture/history/process trial. The tested tree and coverage match the prior passing suite (155.93 s). The initial preflight prevented a futile test launch. Time to decision also includes the unrelated preparation correction and different overlapping local work. The speed comparison is inconclusive, and the existing verification default stays. Hosted waiting and preparation for publication are separately timed.

The supplementary independent reconstruction corrected a source-hash lookup for cached functions with no change to mathematics or the signed replay. The final two clean-checkout reconstruction outputs match byte for byte. Sealed log and provenance are retained separately from active proof or runner time.

Hosted workflow 45105496814 began at 03:21:27 UTC on the exact opened head. Plan job 137465700007 is tracked with the signed scientific phase and the small historical prerequisite separately.

Hosted workflow ended in success at 03:32:47 UTC, 680 seconds after creation. Onboarding took 284 s, historical job 102 s with 7 s explicit replay, and scientific job 391 s, including 280 s for the actual seven-mode replay. [Exact hosted receipt](hosted/run.json) · [Actual scientific markers](hosted/scientific-markers.log)
