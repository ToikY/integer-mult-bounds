#!/usr/bin/env python3
"""Check the two G12 custody repairs. Does not launch the H25 parent."""

import hashlib
import importlib.util
import os
import stat
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
PASS = "PASS_H25_G12_IDENTITY_CLEANUP"

PREDECESSOR_SHA256 = {
    "predecessor/g12_reference_parent_v1.py.txt":
        "160b8c5de808b9b31532608a89fa5e209110caea132145cd431ffade4403079e",
    "predecessor/g12_reference_cold_consumer_v1.py.txt":
        "89ad17cfa90e895e2cb105e80cc57c82be4bf1a4a85a9d44322016c4344e3849",
}
CORRECTED_SHA256 = {
    "corrected/g12_reference_parent_v2.py":
        "176f0ae0748e8f02a9a89b23e0d0fa684b6c6734ad0a68f705a802695046005e",
    "corrected/g12_reference_cold_consumer_v2.py":
        "dc8a0b62d4175ee447469b7e66798160b85777f44e34d34e98b08af83a9f5a6d",
}
# Git blob ids of the frozen files at PR6321 commit
# ca9d90e93dc495e1e5e5ef6d271ff1e4f089cd0c, path
# research/h25-cache-source-handoff/snapshot/areas/cache-s0308-source-completion-v2/
# g12-custody-implementation/.
UPSTREAM_BLOBS = {
    "predecessor/g12_reference_parent_v1.py.txt":
        "80482f9a9af1f471bc567c52cc31e6dc8a39c26f",
    "predecessor/g12_reference_cold_consumer_v1.py.txt":
        "19cb9376c2d757e1deb354608a1351c39e4daae1",
}
BARE_PREFLIGHT = (
    "            finally:\n"
    "                for descriptor in reversed(fds):\n"
    "                    os.close(descriptor)\n",
    "        finally:\n"
    "            for descriptor in reversed(parent_fds):\n"
    "                os.close(descriptor)\n",
)
RAW_PIN = (
    "tuple(manifest_record['identity'][k] for k in _ID_NAMES)"
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_bytes():
    for name, expected in {**PREDECESSOR_SHA256, **CORRECTED_SHA256}.items():
        path = PACKAGE / name
        digest = sha256(path)
        if digest != expected:
            fail(name + " sha256 " + digest)
    for name, blob in UPSTREAM_BLOBS.items():
        # git hash-object of the vendored predecessor, without invoking git.
        data = (PACKAGE / name).read_bytes()
        header = b"blob " + str(len(data)).encode("ascii") + b"\0"
        got = hashlib.sha1(header + data).hexdigest()
        if got != blob:
            fail(name + " is not the PR6321 blob " + blob)


def check_source_shape(parent_text, consumer_text):
    for snippet in BARE_PREFLIGHT:
        if snippet not in parent_text:
            fail("predecessor lost a bare preflight finally")
        if snippet in (PACKAGE / "corrected/g12_reference_parent_v2.py").read_text():
            fail("corrected parent still has a bare preflight finally")
    corrected_parent = (PACKAGE / "corrected/g12_reference_parent_v2.py").read_text()
    if corrected_parent.count("_finally_close_known(") != 3:
        fail("expected helper definition plus two preflight call sites")
    if RAW_PIN not in parent_text:
        fail("predecessor pin shape changed")
    if RAW_PIN in corrected_parent:
        fail("corrected parent still inlines the identity tuple")
    if "_handoff_identity_tuple(manifest_record)" not in corrected_parent:
        fail("corrected parent does not name the tuple handoff")
    if "identity': identity" not in consumer_text.replace(" ", ""):
        # The predecessor installs the unpacked value directly.
        if "'identity': identity" not in consumer_text:
            fail("predecessor consumer installation site missing")
    corrected_consumer = (PACKAGE / "corrected/g12_reference_cold_consumer_v2.py").read_text()
    if "identity = _identity_dict_from_handoff(identity_tuple)" not in corrected_consumer:
        fail("consumer does not convert at the handoff boundary")
    if "'identity': identity_tuple" in corrected_consumer:
        fail("consumer still stores the raw tuple in the file record")


def sample_identity():
    return (11, 22, stat.S_IFREG | 0o444, 4, 33, 44)


def check_identity(parent, consumer):
    identity = sample_identity()
    converted = consumer._identity_dict_from_handoff(identity)
    if list(converted) != list(consumer._ID_NAMES):
        fail("converted identity key order")
    if tuple(converted[name] for name in consumer._ID_NAMES) != identity:
        fail("converted identity values")
    record = {
        "path": "/custody/manifest.json",
        "sha256": "ab" * 32,
        "bytes": 4,
        "identity": converted,
        "nlink": 1,
    }
    consumer._file_record(record)
    raw = dict(record, identity=identity)
    try:
        consumer._file_record(raw)
    except RuntimeError as error:
        if "G12-N12" not in str(error):
            fail("raw tuple rejected for the wrong reason: " + str(error))
    else:
        fail("raw identity tuple passed FileRecord validation")
    packed = parent._handoff_identity_tuple({"identity": converted})
    if packed != identity:
        fail("parent handoff tuple does not round-trip")
    if parent._handoff_identity_tuple({"identity": consumer._identity_dict_from_handoff(packed)}) != packed:
        fail("parent/consumer identity round-trip")
    rejects = (
        converted,
        identity[:-1],
        identity + (0,),
        ("11", 22, identity[2], 4, 33, 44),
        (11, 0, identity[2], 4, 33, 44),
        (11, 22, stat.S_IFDIR | 0o555, 4, 33, 44),
    )
    for value in rejects:
        try:
            consumer._identity_dict_from_handoff(value)
        except RuntimeError:
            continue
        fail("converter accepted " + repr(value))


def closed(fd):
    try:
        os.close(fd)
    except OSError:
        return True
    return False


def check_cleanup(parent):
    # Old bare finally replaces the primary and stops after the first close error.
    live_a, live_b = os.pipe()
    already = os.pipe()
    os.close(already[0])
    os.close(already[1])
    order = []

    def old_close(fd):
        order.append(fd)
        os.close(fd)

    caught = None
    try:
        try:
            raise RuntimeError("G12-N05: prior output/evidence/custody path exists")
        finally:
            # Descriptor order matches the predecessor: reversed, bare os.close.
            for descriptor in reversed((live_a, already[0], live_b)):
                old_close(descriptor)
    except OSError as error:
        caught = error
    if not isinstance(caught, OSError):
        fail("control: bare finally did not replace the primary")
    if order != [live_b, already[0]]:
        fail("control: bare finally did not stop at the first close error; order=" + repr(order))
    # live_a is earlier in the original list, hence later in reversed order, so it stays open.
    if closed(live_a):
        fail("control: bare finally unexpectedly closed the descriptor after the error")

    # Repaired helper: primary survives, every descriptor is attempted.
    left, right = os.pipe()
    bad = os.pipe()
    os.close(bad[0])
    os.close(bad[1])
    tail_r, tail_w = os.pipe()
    secondaries = parent._RawG12Errors()
    repaired = None
    try:
        try:
            raise RuntimeError("G12-N05: prior output/evidence/custody path exists")
        finally:
            parent._finally_close_known((tail_r, bad[0], left, right, tail_w), secondaries)
    except RuntimeError as error:
        repaired = error
    if repaired is None or "prior output" not in str(repaired):
        fail("close failure replaced the preflight primary")
    if len(secondaries) != 1:
        fail("expected one retained close failure, got " + str(len(secondaries)))
    for fd in (tail_r, left, right, tail_w):
        if not closed(fd):
            fail("a later or earlier descriptor was not closed")

    # A successful body with a failed close stays unsuccessful.
    stale = os.pipe()
    os.close(stale[1])
    os.close(stale[0])
    kept = parent._RawG12Errors()
    try:
        try:
            pass
        finally:
            parent._finally_close_known((stale[0],), kept)
    except OSError:
        pass
    else:
        fail("successful body plus failed close was treated as success")
    if kept:
        fail("the sole close failure was also stored as a secondary")

    # Clean closes add no secondary and close both ends.
    one, two = os.pipe()
    empty = parent._RawG12Errors()
    parent._finally_close_known((one, two), empty)
    if empty:
        fail("clean close recorded a failure")
    if not closed(one) or not closed(two):
        fail("clean close left a descriptor open")


def main():
    parent_text = (PACKAGE / "predecessor/g12_reference_parent_v1.py.txt").read_text()
    consumer_text = (PACKAGE / "predecessor/g12_reference_cold_consumer_v1.py.txt").read_text()
    check_bytes()
    check_source_shape(parent_text, consumer_text)
    parent = load("g12_parent_v2", PACKAGE / "corrected/g12_reference_parent_v2.py")
    consumer = load("g12_consumer_v2", PACKAGE / "corrected/g12_reference_cold_consumer_v2.py")
    check_identity(parent, consumer)
    check_cleanup(parent)
    # Importing the corrected modules must not launch a worker or touch the
    # historical absolute root. Both entry globals stay unselected.
    if parent.G12_REFERENCE_LAUNCH_SELECTION is not None:
        fail("parent import selected a launch")
    if consumer.G12_REFERENCE_HANDOFF is not None:
        fail("consumer import selected a handoff")
    print(PASS)


if __name__ == "__main__":
    main()
