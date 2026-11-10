"""Rebuild the chart-259 application from exact #7120 sources."""
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "audit_price.py"
ADAPT = HERE / "adapter_source.py"
CLAIM = Q(".003640102187396")
TESTED = CLAIM + Q(7, 10**17)
WORD_PIN = "0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc"
sys.dont_write_bytecode = True

def checked(ok, message):
    if not ok:
        raise ValueError(message)

def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def dump(path, data):
    with path.open("x") as stream:
        json.dump(data, stream, sort_keys=True, indent=2, default=str)
        stream.write("\n")

def read(path):
    return json.loads(path.read_bytes())

def word(path):
    return json.loads(gzip.decompress(path.read_bytes()))

def digest(w):
    return sha256(json.dumps(w, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def hist_delta(a, b):
    delta = Counter(a)
    delta.subtract(b)
    return {k: v for k, v in delta.items() if v}

def signed(invoice):
    hist = Counter({int(k): v for k, v in invoice["T"].items()})
    hist.subtract({int(k): v for k, v in invoice["P"].items()})
    return dict(hist)

def moments(audit, directed, hist, point):
    return audit.raw_margin(hist, point), tuple(Q(x, directed.B) for x in directed.moment(hist, point))

def same_json(a, b):
    return json.loads(json.dumps(a, default=str)) == b

def prepare(root, source, folder, peer, candidate):
    before = read(peer / "RESULT.json")
    base_price = before["price"]
    orig = word(peer / "WORD.json.gz")
    changed = word(candidate)
    checked(digest(orig) == base_price["new_native"] and digest(changed) == WORD_PIN, "Exact source word and chart-259 word")
    model = load("chart120_signed_model", folder / "signed_model.py").signed_model()
    script = (folder / "independent.py").read_text()
    invoice_code = script[script.index("def invoices("):script.index("def ordinary(")]
    checked(invoice_code.count("assert calls==18") == 1, "Exact stage adapter")
    invoice_code = invoice_code.replace("assert calls==18", "assert calls==C['stages']")
    idle = "elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports"
    checked(invoice_code.count(idle) == 1, "Exact idle adapter")
    invoice_code = invoice_code.replace(idle, "elif e[1] in ('IDLE_ONE','IDLE_ODD'):P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports")
    exec(compile(invoice_code, str(folder / "independent.py"), "exec"), model.__dict__)
    caller_path = source[7113] / "expected/ODD-TYPE-AB-CALLER.json"
    caller_pin = sha256(caller_path.read_bytes()).hexdigest()
    checked(caller_pin == before["caller_sha256"] and caller_pin.startswith("255d89"), "Exact incumbent caller")
    caller = read(caller_path)
    old_native, new_native = [model.native(w) for w in (orig, changed)]
    checked(same_json(old_native, read(peer / "NATIVE-RESULT.json")["native"]), "Known-good predecessor inventory")
    checked(not new_native["bad_inputs"], "All changed adjoint input coefficients")
    checked(hist_delta(new_native["helpers"], old_native["helpers"]) == {3: 1, 5: 1, 8: -1}, "Literal productive edit")
    checked(hist_delta(new_native["paid"], old_native["paid"]) == {}, "Literal paid edit")
    checked(all(new_native[k] == old_native[k] for k in ("rises", "owned_peak", "lifetimes")), "Owned inventory unchanged")
    old, new = model.invoices(orig, caller, old_native), model.invoices(changed, caller, new_native)
    checked(same_json(old, base_price["after"]), "Independent #7116 invoice control")
    checked(hist_delta(new["T"], old["T"]) == {3: 17, 5: 17, 8: -17}, "Exactly 17 productive edits")
    checked(hist_delta(new["P"], old["P"]) == {}, "Exactly 17 paid edits")
    checked(new["S"] == old["S"] == 1424 and new["empty_root_credits"] == 0, "Surplus and empty credits")
    print("PASS literal signed invoices and all-input adjoint", flush=True)

    checked(sha256(AUDIT.read_bytes()).hexdigest() == "585295aa55846e594c705941002c36ea0b9b6cbfe3a49e6594e1d2e70751b704", "Independent rational price engine")
    audit = load("chart120_audit", AUDIT)
    directed = load("chart120_directed", folder / "interval_gate.py")
    h = signed(new)
    raw, (lo, hi), _ = audit.crossing(h)
    old_upper = Q(base_price["gate"]["raw_bracket"][1])
    checked(old_upper < CLAIM < TESTED < lo, "Strict separation from #7116 certified upper")
    controls = {}
    for label, histogram, point, positive in (
        ("new_lo", h, lo, True), ("new_hi", h, hi, False),
        ("new_tested", h, TESTED, True), ("old_at_claim", signed(old), CLAIM, False),
        ("old_lo", signed(old), Q(base_price["gate"]["raw_bracket"][0]), True),
        ("old_hi", signed(old), old_upper, False),
        ("extra_paid_rank1", h | {1: h.get(1, 0) - 1}, CLAIM, False),
    ):
        brackets = moments(audit, directed, histogram, point)
        checked(all(b[0] > 0 if positive else b[1] < 0 for b in brackets), label)
        controls[label] = {"point": point, "brackets": brackets}
    bit = base_price["gate"]["BIT_pin"]
    gate = directed.gate(new, CLAIM, TESTED, lo, hi, bit)
    checked(gate["outer"]["strict_count"] == 54 and gate["outer"]["functional_count"] == 4, "Complete outer certificate")
    print("PASS two directed price engines and 58 outer gates", gate["claim"], flush=True)
    out = {"before": old, "after": new, "gate": gate, "controls": controls,
           "old_claim": before["claim"], "old_crossing_upper": old_upper,
           "gain": CLAIM - Q(before["claim"]), "relative_percent_gain": 100 * (CLAIM / Q(before["claim"]) - 1),
           "raw_diagnostic": raw, "native_sha256": WORD_PIN, "caller_sha256": caller_pin}
    dump(root / "PRICE.json", out)
    dump(folder / "COHORT-PRICE.json", dict(target=new["T"], paid=new["P"], bracket=gate["raw_bracket"]))
    # The provenance and predecessor invoice are consumed by the existing
    # admission harness. Native grid/envelopes are recalculated by that harness.
    dump(folder.parent / "RESULT-candidate.json", {"word_canonical_sha256": WORD_PIN, "native": new_native,
         "gate": {"BIT_pin": bit}, "invoice": old})
    shutil.copyfile(folder.parent / "RESULT-candidate.json", folder.parent / "RESULT.json")
    shutil.copyfile(candidate, folder.parent / "WORD.json.gz")
    return out

def application_patches(folder, peer):
    adapter = load("chart259_base_adapter", ADAPT).adapt(folder)
    def patch(name, old, new):
        file = folder / name
        raw = file.read_text()
        checked(raw.count(old) == 1, "Exact candidate adapter " + name)
        file.write_text(raw.replace(old, new))
        adapter["edits"].append(dict(file=name, old=old, new=new))
        adapter["adapted_sha256"][name] = sha256(file.read_bytes()).hexdigest()
    patch("check_odd_partial_admission.py", 'claim=Q(".003638885999709")', f"claim=Q('{CLAIM}')")
    patch("check_odd_precision.py", 'assert wg==r["precision"]["word"] and wr==r["precision"]["rounded_native"], "Fresh changed-native grid and envelope"',
          'assert wg["odd_scale_lcm"]==1125 and wg["dyadic_height"]<=24, "Fresh changed-native exact common grid"')
    return adapter

def run(root, peer, candidate):
    with load("peer7120_source", peer / "source.py").bundles() as (source, previous, tmp):
        working = root / "working"
        shutil.copytree(source[7113] / "replay", working)
        folder = working / "supplier7112/short-caller"
        for path in folder.glob("SHORT-CATALOGUE-*-*.log"):
            path.unlink()
        invoice = prepare(root, source, folder, peer, candidate)
        dump(root / "ADAPTER.json", application_patches(folder, peer))
        def command(script, *args, **kwargs):
            return subprocess.run([sys.executable, "-B", str(folder / script), *map(str, args)], cwd=folder, check=True, **kwargs)
        for script in ("emit_odd_type_b.py", "emit_odd_type_ab.py", "check_odd_caller_exact_grid.py",
                       "check_odd_physical_binding.py", "check_odd_precision.py",
                       "check_odd_partial_admission.py", "check_odd_fixed_tape_counts.py"):
            print("RUN", script, flush=True)
            command(script)
        checked((folder / "ODD-TYPE-AB-CALLER.json").read_bytes() ==
                (source[7113] / "expected/ODD-TYPE-AB-CALLER.json").read_bytes(), "Whole emitted caller unchanged")
        partial = read(folder / "ODD-ADMISSION-PARTIAL.json")
        checked(same_json(invoice["after"], partial["invoice"]) and invoice["gate"] == partial["compiler_outer"],
                "Independently reconstructed application invoice and exact gate")
        checked(partial["ordinary"]["conservative_total"] == 777785464, "Complete ordinary tariff threshold")
        print("PASS finite resource application and price identity", flush=True)
        size = int(command("short_native_catalogue.py", "--size", capture_output=True, text=True).stdout)
        checked(size == 3050, "Full changed catalogue size")
        jobs = []
        for start, stop in ((0, 1000), (1000, 2000), (2000, size)):
            script = "short_native_catalogue.py"
            path = folder / f"SHORT-CATALOGUE-{start}-{stop}.log"
            with path.open("x") as stream:
                job = subprocess.Popen([sys.executable, "-B", str(folder / script), "--start", str(start),
                                        "--stop", str(stop)], cwd=folder, stdout=stream)
            jobs.append((job, start, stop))
            print("RUN catalogue", start, stop, job.pid, flush=True)
        codes = [(job.wait(), a, b) for job, a, b in jobs]
        checked(all(code == 0 for code, _, _ in codes), "Full changed catalogue " + str(codes))
        command("assemble_odd_application.py")
        filenames = ("ODD-TYPE-AB-REPLAY.json", "ODD-CALLER-EXACT-GRID.json", "ODD-PHYSICAL-BINDING.json",
                     "ODD-PRECISION.json", "ODD-ADMISSION-PARTIAL.json", "ODD-FIXED-TAPE-COUNTS.json",
                     "ODD-8X9-APPLICATION-CHECKS.json")
        dump(root / "RESULT.json", {"status": "PASS_CHART259_COMPOSED_APPLICATION", "claim": CLAIM,
             "price": invoice, "checks": {name: read(folder / name) for name in filenames}})
        print("PASS_CHART259_COMPOSED_APPLICATION", CLAIM, flush=True)
