"""Seal the eight actual mode markers and distinguish wrapper from workload status."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from subprocess import check_output

HEAD = "aea1699415250d865f7a635f4df0b76f406c47b4"
PACKAGE = "research/p104-period-debit-25bit"
RUNNER_BLOB = "091b4c8f58bac9a9580d76025b887dc5c873d05f"
MODES = ("price","calendar","raw","exterior","nested","product","setup","8072-parent-source-pins")
PASS = tuple(f"PASS_25BIT_PERIOD_SIGNED {mode}" for mode in MODES[:-1]) + (
    "PASS_PARENT_8072_CHANGED_FILE_BLOBS 10 75f7e1c44f48c43983016bcf8878c4d9e5e87c62",)
WRAPPER_ERROR = "time: sysctl kern.clockrate: Operation not permitted"


def artifact_json(path):
    return json.loads(path.read_bytes())


def row(log, label):
    lines = [line[len(label):] for line in log.splitlines() if line.startswith(label)]
    assert len(lines)==1, label
    return json.loads(lines[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout",type=Path)
    parser.add_argument("evidence",type=Path)
    args = parser.parse_args()
    root,evidence = args.checkout.resolve(),args.evidence.resolve()
    def git(*args):
        return check_output(["git","-C",str(root),*args]).decode().strip()
    def read(name):
        return (evidence/name).read_text().strip()
    assert git("rev-parse","HEAD")==HEAD and git("status","--porcelain")==""
    assert read("pre-replay.status")==read("post-replay.status")==""
    assert read("python-version")=="Python 3.12.14"
    assert git("rev-parse",f"{HEAD}:scripts/research_package.py")==RUNNER_BLOB
    runner = git("show",f"{HEAD}:scripts/research_package.py")
    assert "code = process.wait(timeout=timeout)" in runner
    assert 'require(code == 0, f"verification command exited {code}")' in runner
    assert 'run_python_replay(argv, root, command["timeout_seconds"])' in runner
    assert 'print("PASS_REGISTERED_RESEARCH_PACKAGE " + package' in runner

    spec = artifact_json(root/PACKAGE/"VERIFY.json")
    assert len(spec["commands"])==8
    raw = read("replay.log")
    checks = list(re.finditer(r"^CHECK (.*)$",raw,re.M))
    assert len(checks)==8
    scope = []
    for position, (mode, entry, mark, scanned) in enumerate(zip(MODES,spec["commands"],PASS,checks,strict=True)):
        assert scanned[1]==entry["checks"]
        end = checks[position+1].start() if position+1<len(checks) else len(raw)
        assert mark in raw[scanned.end():end].splitlines(), mode
        scope.append(dict(mode=mode, result="pass", exit_code=0, source="committed runner checks each child exit",
                          timeout_seconds=entry["timeout_seconds"], terminal_marker=mark))
    end_marker = f"PASS_REGISTERED_RESEARCH_PACKAGE {PACKAGE} outcome=completed"
    assert raw.splitlines().count(end_marker)==1 and raw.index(end_marker)>checks[-1].end()
    assert raw.endswith(WRAPPER_ERROR)
    for label, code in [("lp-zero",1),("lp-nonzero",1),("p-zero",0),("p-nonzero",7)]:
        assert int(read(f"time-probe-{label}.exit")) == code
        assert (WRAPPER_ERROR in read(f"time-probe-{label}.log")) == label.startswith("lp-")
    assert int(read("replay.exit")) == 1
    summary = artifact_json(evidence/"replay-summary.json")
    assert summary["exit_code"]==1 and summary["clean_detached_after"]
    assert summary["head"]==HEAD
    series = [json.loads(line) for line in read("replay-observed.jsonl").splitlines()]
    assert series[0]["running"] and not series[-1]["running"]
    assert min(sample["free_bytes"] for sample in series) == summary["minimum_sampled_disk_free_bytes"]
    assert summary["minimum_sampled_disk_free_bytes"] >= 8*2**30
    timings = {field: float(re.search(rf"^{field} ([0-9.]+)$",raw,re.M)[1]) for field in ("real","user","sys")}

    invoice = artifact_json(evidence/"independent-invoice.json")
    assert read("independent-invoice.exit")=="0" and invoice["candidate_head"]==HEAD
    assert len(invoice["runtime_candidate"])==106 and invoice["runtime_delta"]==["installations.py"]
    book = row(raw,"PASS_25BIT_PERIOD_PROFILE ")
    installed = row(raw,"PASS_EXPANDED_SETUP ")
    product = json.loads(next(line for line in raw.splitlines() if line.startswith('{"H_calls":')))
    assert book["kappa"]==invoice["candidate"]["tiers"]["terminal"]["k"]=="779692000101/200000000000000"
    assert book["complete_log2_C"]==invoice["candidate"]["complete_recurring_log2_c"]==4354317451
    assert book["prior_stopped_cap"]==invoice["stopped_comparator"]["exact_cap"]
    assert [(row["records"],row["paid_exchanges"]) for row in book["signed_tape_controls"]]==[(81,3),(6561,1)]
    assert all(row["wrong_signed_return_rejected"] for row in book["signed_tape_controls"])
    assert installed["actual_terminal_carrier_bits"]==invoice["fixed_setup"]["actual_carrier_bits"]==18845935
    assert installed["directory_records"]==2407819 and installed["directory_bytes"]==36094651
    assert installed["serial_transition_upper"]==invoice["fixed_setup"]["total_transitions"]
    assert product["product"]=="-345550037539"
    for mark in ("PASS_TYPED_RAW48 0 columns 2 paid 282576","PASS_TYPED_RAW48 1 columns 4 paid 281568",
                 "PASS_EXTERIOR_TYPED_RAW","PASS_NONZERO_INTERIOR 282576 281568 9841 4507783464",
                 "PASS_EXACT_SYMBOLIC_UPPER_FENCE 1724 1874","PASS_LITERAL_LOWER_CUTOFF 1874",
                 "PASS_DIRECTED_ORDINARY_DEBIT 18960 11239/8192 375/376"):
        assert mark in raw

    files = ("PLAN.md","PLAN-SHA256.txt","admission-disk.log","admission.utc",
             "candidate-ls-tree.log","git-lineage.log","check-only.log","check-source.log",
             "check-source-first.log","independent_check.py","independent-invoice.json",
             "independent-invoice.start.utc","independent-invoice.end.utc","independent-invoice.exit",
             "materialize_trees.py","post-replay.status","pre-replay.status","python-version",
             "registered_replay.py","replay-end.utc","replay-observed.jsonl","replay-start.utc",
             "replay-summary.json","replay.exit","replay.log","reserved-scope.json","run_invoice.zsh",
             "seal_replay.py","time-probe-lp-zero.log","time-probe-lp-zero.exit",
             "time-probe-lp-nonzero.log","time-probe-lp-nonzero.exit","time-probe-p-zero.log",
             "time-probe-p-zero.exit","time-probe-p-nonzero.log","time-probe-p-nonzero.exit","README.md")
    result = dict(head=HEAD, command=["python3.12","-IB","scripts/research_package.py","--package",PACKAGE],
                  runner_blob=RUNNER_BLOB, start_utc=read("replay-start.utc"),end_utc=read("replay-end.utc"),
                  timings_seconds=timings, minimum_sampled_free_bytes=summary["minimum_sampled_disk_free_bytes"],
                  clean_detached_before_and_after=True,actual_modes=scope,skipped_modes=[],
                  outcome="verified_scoped_registered_execution",
                  workload_completion=end_marker,
                  direct_workload_process_status=None,
                  workload_exit_supported_by="All child statuses accepted by committed runner, success marker, and ordinary main fallthrough",
                  outer_timing_wrapper=dict(exit_code=1,error=WRAPPER_ERROR,
                                            zero_and_seven_controls_both_returned_one=True),
                  exact_ceiling_vs_8081=invoice["stopped_comparator"],
                  setup=installed,
                  signed_materialized_files=106,signed_materialized_delta=["installations.py"],
                  signed_tape_negative_controls=book["signed_tape_controls"],signed_product=product,
                  conditional_kappa=book["kappa"],complete_recurring_log2_c=book["complete_log2_C"],
                  file_sha256={name:sha256((evidence/name).read_bytes()).hexdigest() for name in files})
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
