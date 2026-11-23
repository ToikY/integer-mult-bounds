"""Run the one registered #8081 replay with a monitored shared disk reserve."""
from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
from shutil import disk_usage
import fcntl
import json
import os
import signal
import subprocess
import time

GIB = 2**30
NEAR_FLOOR = 8 * GIB + 32 * 2**20
ADMIT_FLOOR = 8 * GIB + 128 * 2**20
LIMIT = 1200
LOCK = "/tmp/p104-toiky-0039/physical-product.lock"
PACKAGE = "research/p104-expanded-budget-25bit"
COMMIT = "510113821774bb27f7ddaad4e8b94837a1c2cf52"


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--python", default="python3.12")
    args = parser.parse_args()
    root, evidence = args.repository.resolve(), args.evidence.resolve()

    def git(*argv):
        return subprocess.check_output(["git", "-C", root, *argv])

    assert git("rev-parse", "HEAD").decode().strip() == COMMIT
    assert not git("status", "--porcelain")
    (evidence/"pre-replay.status").write_bytes(b"")
    assert not (evidence/"replay-start.utc").exists(), "The exact invocation is already recorded"
    assert "source_history_commits" in (evidence/"check-source.log").read_text()
    initial_free = disk_usage(evidence).free
    assert initial_free > ADMIT_FLOOR
    # Probe without retaining the lock. The verified product code acquires it
    # around the fixture on its own, with neither bypass nor an alternate lock.
    if Path(LOCK).exists():
        with open(LOCK, "rb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(lock, fcntl.LOCK_UN)
    env = dict(os.environ)
    env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               P104_PHYSICAL_PRODUCT_LOCK=LOCK)
    command = [args.python, "-IB", "scripts/research_package.py", "--package", PACKAGE]
    (evidence/"replay-start.utc").write_text(utc()+"\n")
    (evidence/"reserved-scope.json").write_text(json.dumps({
        "max_replay_seconds": LIMIT, "disk_guard_bytes": NEAR_FLOOR,
        "initial_disk_free_bytes": initial_free, "command": ["python3.12", *command[1:]],
        "numerical_threads": 1, "common_product_lock": True,
    }, indent=2)+"\n")
    start = time.monotonic()
    low_water = initial_free
    status = "registered run reached terminal exit"
    with (evidence/"replay.log").open("wb") as log, (evidence/"replay-observed.jsonl").open("w") as monitor:
        process = subprocess.Popen(
            ["/usr/bin/time", "-lp", *command], cwd=root, env=env, stdout=log,
            stderr=subprocess.STDOUT, start_new_session=True,
        )
        while True:
            free = disk_usage(evidence).free
            low_water = min(low_water, free)
            elapsed = time.monotonic()-start
            poll = process.poll()
            monitor.write(json.dumps({"utc":utc(), "elapsed_seconds":round(elapsed,2),
                         "free_bytes":free, "running":poll is None})+"\n")
            monitor.flush()
            if poll is not None:
                code = poll
                break
            if free <= NEAR_FLOOR or elapsed >= LIMIT:
                status = ("disk reserve guard interrupted the replay" if free <= NEAR_FLOOR
                          else "whole registered run reached its wall cap")
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()
                code = 124
                break
            time.sleep(0.75)
    (evidence/"replay-end.utc").write_text(utc()+"\n")
    (evidence/"replay.exit").write_text(str(code)+"\n")
    final_status = git("status", "--porcelain")
    (evidence/"post-replay.status").write_bytes(final_status)
    (evidence/"replay-summary.json").write_text(json.dumps({
        "head": COMMIT, "exit_code": code, "scope": status,
        "wall_seconds_over_observer": round(time.monotonic()-start,2),
        "minimum_sampled_disk_free_bytes":low_water,
        "clean_detached_after":not final_status,
    }, indent=2)+"\n")
    raise SystemExit(code)


if __name__=="__main__":
    main()
