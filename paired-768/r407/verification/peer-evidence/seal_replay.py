"""Seal exact local and hosted #8081 replay evidence without machine-specific roots."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent


def read(name):
    return (root/name).read_text()


def decoded(name):
    return json.loads(read(name))


def digest(name):
    return sha256((root/name).read_bytes()).hexdigest()


log, hosted = read("replay.log"), read("hosted-markers.log")
head = read("exact-head").strip()
assert head == "510113821774bb27f7ddaad4e8b94837a1c2cf52"
modes = ("price","calendar","raw","exterior","nested","product","setup")
mode_markers = ["PASS_ENLARGED_BUDGET_SIGNED 460 "+mode for mode in modes]
mode_markers.append("PASS_PARENT_8072_CHANGED_FILE_BLOBS 10 ")
for scope in mode_markers + ["PASS_REGISTERED_RESEARCH_PACKAGE research/p104-expanded-budget-25bit outcome=partial"]:
    assert log.count(scope) == hosted.count(scope) == 1, scope
markers = {
    "exact_price":"PASS_WEIGHTED_COMPLETE_PRICE 4354317571",
    "symbolic_cutoff":"PASS_EXACT_SYMBOLIC_UPPER_FENCE",
    "signed_two":"PASS_TYPED_RAW48 0 columns 2",
    "signed_four":"PASS_TYPED_RAW48 1 columns 4",
    "genuine_exterior":"PASS_EXTERIOR_TYPED_RAW",
    "nested_grant":"4507783464",
    "signed_product":'"product": "-345550037539"',
    "charged_installer":'"actual_terminal_carrier_bits": 18845937',
    "actual_directory":'"directory_records": 2407819',
}
assert all(value in log for value in markers.values())
assert all(markers[key] in hosted for key in ("exact_price","charged_installer","actual_directory"))
summary = decoded("replay-summary.json")
assert read("replay.exit").strip() == "0"
assert summary["exit_code"] == 0 and summary["clean_detached_after"]
assert not read("pre-replay.status") and not read("post-replay.status")
assert summary["minimum_sampled_disk_free_bytes"] >= 8*2**30
assert read("comparison.exit").strip() == "0"
manifest = decoded("checkout/research/p104-expanded-budget-25bit/VERIFY.json")
comparison = decoded("comparison-invoice.json")
assert comparison["head"] == head
invoice = comparison["independent"]
assert invoice["complete_recurring_log2_C"] == 4354317571
assert comparison["actual_runtime_delta"] == ["installations.py"]
assert invoice["exact_stopped_cap"] == "15407802515941573408769828489/3952279237427200000000000000000"
live = decoded("hosted-readback.json")
assert live["headRefOid"] == head and len(live["statusCheckRollup"]) == 3
assert all(item["status"] == "COMPLETED" and item["conclusion"] == "SUCCESS" for item in live["statusCheckRollup"])
run = decoded("hosted-run.json")
assert run["headSha"] == head and run["status"] == "completed" and run["conclusion"] == "success"
jobs = {job["databaseId"]:job for job in run["jobs"]}
assert all(jobs[item]["conclusion"] == "success" for item in (137495482768,137496902866,137496902870))

evidence = [
    "README.md","exact-head","git-lineage.log","package-ls-tree.log","check-only.log","check-source.log",
    "registered_replay.py","reserved-scope.json","replay.log","replay.exit","replay-start.utc","replay-end.utc",
    "replay-summary.json","replay-observed.jsonl","python-version","pre-replay.status","post-replay.status",
    "independent_compare.py","comparison-invoice.json","comparison-invoice.time","comparison.exit",
    "hosted-readback.json","hosted-readback.utc","hosted-run.json","hosted-markers.log","seal_replay.py",
]
assert len(set(evidence)) == len(evidence)
rate, prior = Q(".00389846"), Q(".00389834")
out = dict(
    head=head,compared_peer_head=comparison["compared_head"],conditional_kappa=str(rate),
    peer_movement_vs_8078=str(rate-prior),peer_percent_vs_8078=str(100*(rate-prior)/prior),
    exact_stopped_family_ceiling=invoice["exact_stopped_cap"],complete_recurring_log2_C=4354317571,
    entry_conversion=8744,max_native_height=18845936,
    fixed_setup_transition_upper=invoice["fixed_setup"]["transitions"],
    actual_runtime_delta=comparison["actual_runtime_delta"],clean_detached_checkout=True,
    committed_files=31,archive_members=88,actual_runtime_files=106,
    command=["python3.12","-IB","scripts/research_package.py","--package","research/p104-expanded-budget-25bit"],
    python_version=read("python-version").strip(),profile="460",
    start_utc=read("replay-start.utc").strip(),end_utc=read("replay-end.utc").strip(),
    timing_seconds={name:float(re.search(r"^"+name+r" (\d+\.\d+)$",log,re.M).group(1))
                    for name in ("real","user","sys")},
    peak_rss_bytes=int(re.search(r"^\s*(\d+)\s+maximum resident set size$",log,re.M).group(1)),
    minimum_sampled_disk_free_bytes=summary["minimum_sampled_disk_free_bytes"],exit_code=0,
    per_mode_timeouts_seconds=[row["timeout_seconds"] for row in manifest["commands"]],
    registration_outcome="partial",scope="All eight registered high-profile modes executed",
    modes=[{"mode":mode,"result":"pass"} for mode in [*modes,"8072-parent-source-pins"]],
    failed_modes=[],skipped_modes=[],signed_scope_markers=markers,
    hosted=dict(job=137496902866,url=jobs[137496902866]["url"],run=45114926967,
                conclusion="success",head=head,actual_scope_count=8,raw_log_sha256=digest("hosted-science.raw.log")),
    evidence_file_sha256={name:digest(name) for name in evidence},
)
(root/"REPLAY-RECEIPT.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print("REPLAY-RECEIPT.json",digest("REPLAY-RECEIPT.json"))
