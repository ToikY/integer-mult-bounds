"""Authenticate the archived signed source against the public scientific Git tree."""

import hashlib
import json
from pathlib import Path
import sys
import tarfile


def unique(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Duplicate JSON key {name}")
        result[name] = value
    return result


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def main():
    package = Path(sys.argv[1])
    here = Path(__file__).resolve().parent
    blobs = read(here / "source-blobs.json")
    manifest = read(package / "PEER-SOURCE.json")
    assert blobs["head"] == manifest["head"] == "cbe847a953b971f9c6c5a0a6661e2008acd29086"
    tar_path = package / "peer8057.tar.gz"
    assert hashlib.sha256(tar_path.read_bytes()).hexdigest() == manifest["archive_sha256"]
    actual = set()
    with tarfile.open(tar_path) as archive:
        for item in archive:
            if item.isdir():
                continue
            assert item.isfile() and item.name not in actual
            data = archive.extractfile(item).read()
            git_header = b"blob " + str(len(data)).encode("ascii") + b"\0"
            pinned = blobs["files"][item.name]
            assert len(data) == pinned["size"]
            assert hashlib.sha1(git_header + data).hexdigest() == pinned["sha"], item.name
            assert hashlib.sha256(data).hexdigest() == manifest["files_sha256"][item.name], item.name
            actual.add(item.name)
    assert actual == set(manifest["files_sha256"]) == set(blobs["files"])
    print(f"PASS matched {len(actual)} archive member Git blobs and SHA-256 hashes at #8057 {blobs['head']}")


if __name__ == "__main__":
    main()
