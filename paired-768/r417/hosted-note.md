# Hosted coverage of the changed rank-five relay

Refreshed against GitHub 2026-11-23 21:58–22:01 UTC. The exact [#8089 head 39a03a1](https://github.com/CrocSwap/integer-mult-bounds/pull/8089) kept all three successful checks. Its [scientific replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45130994532/job/137548042982) ran the registered package on merge bd3ae68d4e46e26718733e9b5b04c64f22e0a3a9. The exact [#8094 head c20a08dc](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) has one [completed action-required run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45143810893) with zero jobs.

- **Algebra and placement.** The hosted rational map used the same exact chart word and checked 1,291 terminal roles, explicitly including changed label 104493 in its graph. The hosted atlas verifier checked the required pairs and 1,938,432 monomial basis images. Its loader check binds all 48 chronological paid streams to the changed graph and rejects an altered graph or old fallback. This evidence verifies algebra and binding. The placement test instruments exterior alignment on a rank-112 to rank-258 edge. [Rational map](https://github.com/CrocSwap/integer-mult-bounds/blob/39a03a1317b6d066c76f7fea6a5fcbbcd10cf738/research/p104-shortcut-eta-target/check_rational.py) · [Atlas](https://github.com/CrocSwap/integer-mult-bounds/blob/39a03a1317b6d066c76f7fea6a5fcbbcd10cf738/research/p104-shortcut-eta-target/check_atlas.py) · [Path binding](https://github.com/CrocSwap/integer-mult-bounds/blob/39a03a1317b6d066c76f7fea6a5fcbbcd10cf738/research/p104-shortcut-eta-target/check_path_binding.py)
- **Raw, exterior and nested.** Both full typed itineraries ran on finite fixture fields. Raw and exterior seed the first-native helper label 1544. Nested seeds the same parent helper and lends at paid ordinal 3418, with child helper tag `("helper",9977,0,14)` in the log. The exact source dependency cone for node 104493 spans 275 vertices and 273 initial positions. Neither seeded label 1544 (layout index 1290) nor label 14 (index 14) is among those inputs. The declared dirty inputs cannot activate that node in the seeded graph. The complete typed fixture and owner cleanup therefore give no specifically measured dirty payload or reverse-path result for charts 365 → 529. The valid product fixture separately reported `typed_native_calls=0`. [Hosted mode dispatch](https://github.com/CrocSwap/integer-mult-bounds/blob/39a03a1317b6d066c76f7fea6a5fcbbcd10cf738/research/p104-shortcut-eta-target/verify.py) · [Authenticated archive preparation](https://github.com/CrocSwap/integer-mult-bounds/blob/39a03a1317b6d066c76f7fea6a5fcbbcd10cf738/research/p104-shortcut-eta-target/install.py) · [Product counters](https://github.com/CrocSwap/integer-mult-bounds/blob/39a03a1317b6d066c76f7fea6a5fcbbcd10cf738/research/p104-shortcut-eta-target/check_product_path.py)

Reproduce the recorded structural support check from the handoff root using the sealed Round 411 word and engine. The canonical layout hash and archive digest are the same as the published word replay.

```sh
python3.12 -IB - <<'PYCODE'
from hashlib import sha256
from pathlib import Path
import gzip
import json
import runpy

root = Path("paired-768/r411/relay")
raw = (root / "w5669_shortcut5.json.gz").read_bytes()
assert sha256(raw).hexdigest() == "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149"
_, layout = runpy.run_path(str(root / "complex-source/verify_split_helpers.py"))["rebuild"]()
assert sha256(json.dumps(layout, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
g = json.loads(gzip.decompress(raw))
assert dict((i, (a,b)) for i,a,b in g["moves"])[104493] == (365,529)
forms = dict(g["forms"])
pending, seen, leaves = [104493], set(), set()
while pending:
    i = pending.pop()
    if i in seen:
        continue
    seen.add(i)
    if i < 0:
        leaves.add(~i)
    else:
        pending.extend(d for d, _ in forms[i])
assert (len(seen), len(leaves)) == (275,273)
for label, index in ((1544,1290), (14,14)):
    assert layout["source_labels"].index(label) == index and index not in leaves
print("PASS_104493_FIXTURE_INPUTS_OUTSIDE_DEPENDENCY_CONE")
PYCODE
```

A dedicated nonzero fixture with a donor in the cone and signed phase, spectator preservation and actual owner return has distinct coverage. Keep the fixed-setup census and active native product test separate. Credit Clear1nsight's hosted suite, floration's changed graph and Ali Romman's inherited typed fixture. OpenAI Codex assisted with the coverage check.
