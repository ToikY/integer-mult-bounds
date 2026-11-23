# Round 402 timing and admissions

Round opened 02:33:07 UTC. The one-case price screen used 0.028517 s wall time. The known-good #8070 replay was reused after exact receipt and source checks. Source tracing, active proof time and active editing time were not separately measured.

Literal build used 77.274 s (regeneration 6.328, price 17.297, calendar 53.649). Independent exact replay ran 02:40:34–02:44:23 UTC (229.50 s wall, 164.28 s user, 58.88 s system). First independently reproduced complete rate by 02:44:23 UTC, after 676 s elapsed from round start including preflight, preparation and concurrent tests. Observed modes price 18.339, calendar 54.428, raw 18.731, exterior 22.319, nested 23.082, product 91.325 and setup 1.144 s. Exit 0 and clean checkout.

Earlier onboarding ran 111.16 s and ended because the sparse fixture closure and process permissions were insufficient. Repair restored the prior passing fixture selection and allowed the process-liveness test. On the unchanged candidate, onboarding took 155.93 s (760 tests, 31 skips). The historical registered check passed its declared partial scope in 2.35 s. Two substantial jobs ran only on separate checkouts. At least 13,961,580,544 bytes free were observed during independent replay.

Publication preparation was not separately timed. Hosted verification begins with run 45102278869 at 02:48:22 UTC and is tracked separately. Timing environments and work differ, so no workflow speed claim or method change is adopted.

Hosted workflow ended in success at 02:59:55 UTC, 693 seconds after creation. Onboarding plan took 310 s. The separate historical job took 104 s (7 s explicit replay). The scientific job took 378 s, including 295 s for the explicit signed replay. All seven hosted scientific modes ran successfully on the exact head. [Run receipt](hosted/run.json) · [Scientific markers](hosted/scientific-markers.log)
