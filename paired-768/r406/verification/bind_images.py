"""Authenticate and materialize two exact signed runtime images."""
from argparse import ArgumentParser
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path, PurePosixPath
from subprocess import check_output, run
import json
import os
import runpy
import shutil
import sys
import tarfile

parser = ArgumentParser(description=__doc__)
for name in ("candidate", "peer", "historic", "archive_tree_pin", "output"):
    parser.add_argument(name, type=Path)
a = parser.parse_args()
a = {k: p.resolve() for k, p in vars(a).items()}
candidate, peer, historic, out = (a[k] for k in ("candidate", "peer", "historic", "output"))
head = "28926ef5702071cc952ebd7a36d855ac322d97ad"
peer_head = "b72d3fa097d2521939f6b8536029da674648d863"
origin = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
history = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
parent = "0618e75a22cec54d1651394ef83d088551b7f026"
base = "e54523517d0f03e58352e647c403a5af3e525a57"


def sha(body):
    return sha256(body).hexdigest()


def oid(kind, body):
    return sha1(f"{kind} {len(body)}\0".encode() + body).hexdigest()


def git(root, *args):
    return check_output(["git", "-C", root, *args])


def bound_commit(root, rev):
    body = git(root, "cat-file", "commit", rev)
    assert oid("commit", body) == rev
    return sha(body)


def blob(root, rev, path):
    data = git(root, "show", f"{rev}:{path}")
    assert oid("blob", data) == git(root, "rev-parse", f"{rev}:{path}").decode().strip()
    return data


def tar_entries(data):
    result, seen = {}, set()
    with tarfile.open(fileobj=BytesIO(data), mode="r:gz") as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            assert str(path) == member.name and not path.is_absolute() and ".." not in path.parts
            assert member.name not in seen
            seen.add(member.name)
            if not member.isdir():
                assert member.isfile()
                result[member.name] = archive.extractfile(member).read()
    return result


def read_pinned(root, revision, rel):
    body = blob(root, revision, rel)
    assert (root / rel).read_bytes() == body
    return body


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def map_changes(left, right):
    return {p: [left.get(p), right.get(p)] for p in sorted(left.keys() | right.keys())
            if left.get(p) != right.get(p)}


commit_hashes = {}
for root, rev in ((candidate, head), (peer, peer_head), (historic, history)):
    assert git(root, "rev-parse", "HEAD").decode().strip() == rev
    assert not git(root, "--no-optional-locks", "status", "--porcelain=v1", "--untracked-files=all")
    commit_hashes[rev] = bound_commit(root, rev)
assert git(candidate, "rev-parse", "HEAD^", "HEAD^^").decode().splitlines() == [parent, base]
assert [line for line in git(peer, "cat-file", "commit", peer_head).splitlines() if line.startswith(b"parent ")] == [b"parent " + parent.encode()]
candidate_rel = "research/p104-expanded-period-debit"
peer_rel = "research/p104-expanded-budget-signed"
history_rel = "research/p104-weighted-capped-allocation-490950"
old_package, new_package = peer / peer_rel, candidate / candidate_rel
receipt_path = peer.parent / "REPLAY-RECEIPT.json"
peer_receipt = receipt_path.read_bytes()
assert sha(peer_receipt) == "a4814658cbc17b342154d0ac6c6d93d2235099f6dc6fedc209f67795ba004425"
peer_receipt = json.loads(peer_receipt)
assert peer_receipt["head"] == peer_head and peer_receipt["exit_code"] == 0
for name, pin in peer_receipt["evidence_file_sha256"].items():
    assert sha((peer.parent / name).read_bytes()) == pin
assert read_pinned(candidate, head, candidate_rel+"/PREDECESSOR-RESULT.json") == read_pinned(peer, peer_head, peer_rel+"/RESULT-340.json")
overlaps = {}
for name in ("PEER-SOURCE.json", "peer8057.tar.gz", "prepare.py", "upstream_verify.py",
             "UPSTREAM-RESULT.json", "check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py"):
    actual = read_pinned(candidate, head, candidate_rel+"/"+name)
    assert actual == read_pinned(peer, peer_head, peer_rel+"/"+name)
    historic_name = {"upstream_verify.py": "verify.py", "UPSTREAM-RESULT.json": "RESULT.json"}.get(name, name)
    if historic_name:
        assert actual == read_pinned(historic, history, history_rel+"/"+historic_name)
    overlaps[name] = sha(actual)

historical_selected = {}
for rev in (parent, base, "6f100d4bb5083f8c35d96fd95a539811c62f245c", "20ecf2891d80b5acf18d980b2164fb44ea7faa90"):
    commit_hashes[rev] = bound_commit(candidate, rev)
    if rev not in (parent, base):
        body = blob(candidate, rev, "certificates/selected-result.json")
        assert oid("blob", body) == "b1fea0c94436b236cc2b7d41a7be032811b94c81"
        historical_selected[rev] = sha(body)
assert git(candidate, "diff", "--name-only", base, parent).decode().splitlines() == [
    "docs/ci-verification.md", "research/historical-selected-replay-gap/README.md",
    "research/historical-selected-replay-gap/SOURCES.json",
    "research/historical-selected-replay-gap/VERIFY.json", "research/historical-selected-replay-gap/verify.py"]
historical_unchanged = {}
for name in ["docs/ci-verification.md", "scripts/research_package.py", *git(
        candidate, "ls-tree", "-r", "--name-only", parent,
        "research/historical-selected-replay-gap").decode().splitlines()]:
    actual = read_pinned(candidate, head, name)
    assert actual == blob(candidate, parent, name)
    historical_unchanged[name] = dict(sha256=sha(actual), git_blob=oid("blob", actual))
declarations = json.loads(read_pinned(candidate, head, candidate_rel+"/SOURCES.json"))
assert declarations["base_commit"] == parent
for row in declarations["files"]:
    path = row["path"]
    data = read_pinned(candidate, head, path)
    assert blob(candidate, parent, path) == data and sha(data) == row["sha256"] and oid("blob", data) == row["git_blob"]

archive_blob = (new_package / "peer8057.tar.gz").read_bytes()
manifest = json.loads((new_package / "PEER-SOURCE.json").read_bytes())
assert manifest["head"] == origin
assert sha(archive_blob) == manifest["archive_sha256"] == "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
external = a["archive_tree_pin"].read_bytes()
assert sha(external) == "9b698d0aea6a8510d4f6dc09735ae884c3894aea2051043381d3313422731927"
external = json.loads(external)
assert external["head"] == origin
members = tar_entries(archive_blob)
assert members.keys() == external["files"].keys() == manifest["files_sha256"].keys() and len(members) == 88
member_pins = {}
for name, body in members.items():
    record = external["files"][name]
    assert oid("blob", body) == record["sha"] and len(body) == record["size"]
    assert sha(body) == manifest["files_sha256"][name] and record["mode"] in ("100644","100755")
    member_pins[name] = dict(sha256=sha(body), **record)
installer = tar_entries(members["research/tiered-native-multiplier/source/installer.tar.gz"])
assert len(installer) == 10


def materialize(root, package, include_old_result):
    source = root/"source"
    runtime = root/"runtime"
    for name, body in members.items():
        target = source/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    weighted = source/"research/frequency-weighted-native-multiplier"
    runpy.run_path(str(package/"prepare.py"))["materialize"](weighted)
    runpy.run_path(str(package/"retune.py"))["install"](weighted, "340")
    if include_old_result:
        shutil.copyfile(package/"PREDECESSOR-RESULT.json", weighted/"PREDECESSOR-RESULT.json")
    run([sys.executable, "-IB", weighted/"bootstrap.py", runtime], check=True,
        env={**os.environ, "GIT_CEILING_DIRECTORIES": str(out)})
    return weighted, runtime


old_source, old_runtime = materialize(out/"peer-image", old_package, False)
new_source, new_runtime = materialize(out/"candidate-image", new_package, True)
old_image, new_image = inventory(old_runtime), inventory(new_runtime)
runtime_diff = map_changes(old_image, new_image)
assert old_image.keys() == new_image.keys() and len(new_image) == 106
assert list(runtime_diff) == ["installations.py"]
old_line = 'TERMINAL = Profile((8192, 36220, 575705), 978582, Q(".00389834"))'
new_line = 'TERMINAL = Profile((8192, 36400, 575525), 978537, Q(".0038983400039"))'
old_calendar = (old_runtime/"installations.py").read_text()
assert old_calendar.count(old_line) == 1 and old_calendar.replace(old_line, new_line) == (new_runtime/"installations.py").read_text()
source_diff = map_changes(inventory(old_source.parent), inventory(new_source.parent))
print(json.dumps(dict(commits_sha256=commit_hashes, source_overlap=overlaps,
                      historical_selected_sha256=historical_selected, historical_unchanged=historical_unchanged,
                      package_provenance=declarations, archive_tree_pin=str(a["archive_tree_pin"]),
                      source_files=member_pins, inner_installer_sha256={name: sha(body) for name, body in installer.items()},
                      runtime_prior=old_image, runtime_candidate=new_image, runtime_diff=runtime_diff,
                      source_diff=source_diff, terminal_lines=[old_line,new_line]), sort_keys=True, indent=2))
