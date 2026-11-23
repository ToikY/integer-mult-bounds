# Exact K7 ordinary price inputs at #8094

The fixed #8094 head is c20a08dc0a79a989e3515068560d5da371c0a2a8.
Its ordinary word and trial are unchanged from #8090 and the frozen #8057
K7 source. The existing floor is 4474, booked suffix 186/25, child tariff
2401/1024 and debit 1420718/2^20 = 710359/524288. The reserve factor
256/255 is absent in this assumption class.

Reproduce these small inputs with CPython 3.12, assertions and the exact
existing public source archive. The command reads nested archives in
memory and creates no installer or runtime.

~~~sh
python3.12 -I -B extract_k7.py /exact/path/to/peer8057.tar.gz > reproduced.json
cmp reproduced.json K7-INPUTS.json
~~~

The archive SHA-256 is
0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c.

The receipt reconstructs 2,796 native MOVE rank counts and 408 helper
target boundaries directly from the frozen K7 graph. It applies the
36 copies and fixed root-grade counts, then cross-checks every signed
bin against the exact asserted invoice in check_binary_k7.py.
It reproduces the literal strict_moment.py 112-bit outward integer
power function at all ranks 1 through 134 and both c and 1-c, then
regenerates all 24 transport cells using the exact frozen certify
function. Every cell pays its full row and exact receiving-label mass.

K7-INPUTS.json contains target and paid bins, each cell's exact rational
share, directed Psi, old pointwise suffix bound and all nested source
digests. No binary native action or caller proof was executed here.
The next test can use these cells to integrate the directed ordinary
cutoff phase on the full floor-4474 domain, reprice the complete factor
and compare 1420717/2^20. Any lowered booking needs the parameterized
all-size suffix proof before installation. Credit SYLforge #8052,
Ali Romman #8057, floration #8090/#8094, and the credited ordinary
floor, child tariff and signed producer chain. OpenAI Codex assisted.
