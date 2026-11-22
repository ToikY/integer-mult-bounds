# Coverage-preserving hosted replay repair for #8058

Exact repair `622700947484d1a742019ce752f926acffc9b780` leaves the numerical word, the complete original Gaussian replay, the reported κ, and all signed inputs byte-identical to `81f578a512bac27b373cc7868981e45b62f2ce3d`. That branch’s previous hosted numerical job was cancelled after 35 minutes without a scientific verdict. The three new registered jobs separate the two full signed witnesses and the unchanged phase census. [PR #8058](https://github.com/CrocSwap/integer-mult-bounds/pull/8058) · [Cancelled job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45077684057/job/137379564429) · [Exact new run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45083016705)

The independent local 6- and 474-column witnesses covered respectively 282,576 and 281,568 paid cuts, 52,608 owners each, and 4,480,128 and 353,930,112 axes. Their actual signed output digests, all phase probes, writes and peak stock matched strict controls. Both leave zero live handles. The unchanged phase census passed the three callback totals 80,165, 84,104 and 80,165 with the exact residue count. The union independently checked 564,144 paid cuts, 105,216 owners and 358,410,240 axes. Removing one paid cut from a copy of the actual receipt makes the union reject. [Coverage receipt](union.log) · [Manifest and committed-source checks](preflight.log)

Use Git and CPython 3.12 at the exact repair checkout. Run from the repository root.

```sh
out=$(mktemp -d)
runner=research/p104-compact-rounded-partitions-numerical-replay/project.py
python3.12 -IB "$runner" 0 --out "$out/copy-0.json"
python3.12 -IB "$runner" 1 --out "$out/copy-1.json"
python3.12 -IB "$runner" phase --out "$out/phase.json"
python3.12 -IB "$runner" union --receipts "$out/copy-0.json" "$out/copy-1.json" "$out/phase.json"
```

The native signed sources, rounded compact supplier and original package authors are credited in #8058. OpenAI Codex assisted the projection repair and independent coverage check.
