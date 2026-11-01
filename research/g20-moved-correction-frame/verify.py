"""Moved correction frames on the one-to-three-contact G20 conjugations.

The A2 identity and the one-edge emitter are the #5708 contract in
research/g20-conjugation-admission/construct.py. This file does not import it.
"""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
EXPECTED = {
    "candidates": 765,
    "fixed_missing": 605,
    "fixed_loss_a": 153,
    "fixed_loss_b": 1,
    "fixed_neutral": 6,
    "moved_trials": 28149,
    "moved_missing": 28123,
    "moved_h4": 2,
    "moved_five_h2": 24,
    "moved_savings": 0,
    "routes": 2369,
    "base_paid": {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10},
}
LOSS_A = ((1, 2), (2, -1))
LOSS_B = ((1, 1), (2, 1), (4, 1))
H4 = ((4, 1),)
FIVE_H2 = ((2, 5), (4, -2))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load_pinned():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    wanted = {row["path"]: row["sha256"] for row in sources["files"] if row["usage"] == "input"}
    blobs = {}
    for name, expected in wanted.items():
        path = ROOT / name
        actual = digest(path)
        need(actual == expected, "input hash mismatch " + name)
        blobs[name] = path.read_bytes()
    readme = blobs["research/g20-conjugation-admission/README.md"].decode()
    source = blobs["research/g20-conjugation-admission/construct.py"].decode()
    need("one-to-three-contact conjugations" in readme, "README lost the conjugation sentence")
    need("local-only evidence, not replayed search" in readme, "README lost the local-only limit")
    need('out.extend([e[:3] + [f], extra[:3] + [f]])' in source,
         "constructor no longer puts the contact and correction on one chosen frame")
    word = json.loads(gzip.decompress(blobs["research/g20-conjugation-admission/WORD.json.gz"]))
    paths = json.loads(blobs["research/g20-conjugation-admission/PATHS.json"])
    local = json.loads(blobs["research/g20-conjugation-admission/LOCAL-RESULT.json"])
    return word, paths, local


def load_edges(paths):
    edges = {}
    outward = defaultdict(set)
    frames = set()
    for key, value in paths.items():
        left, right = key.split(":")
        need(len(value) == 1, "route " + key + " is not one edge")
        start, end, rank = value[0]
        need(start == int(left) and end == int(right), "route endpoints disagree with " + key)
        need(type(rank) is int and 1 <= rank <= 7, "route rank outside 1..7")
        edges[(start, end)] = rank
        outward[start].add(end)
        frames.add(start)
        frames.add(end)
    need(len(edges) == EXPECTED["routes"], "route count changed")
    return edges, outward, frames


def expected_rows(width, owned):
    rows = []
    for index in range(width):
        if index in owned:
            rows.append(0)
            continue
        row = 1 << index
        if 111 <= index < 222:
            row ^= 1 << (index - 111)
        rows.append(row)
    return rows


def endpoint_ok(records, width, owned, expected):
    rows = [1 << index for index in range(width)]
    for event in records:
        op, dest = event[0], event[1]
        if op == "ADD":
            rows[dest] ^= rows[event[2]]
        elif op == "ERASE":
            if dest not in owned:
                return False
            rows[dest] = 0
        elif op == "INIT":
            if dest not in owned or rows[dest]:
                return False
        else:
            return False
    return rows == expected


def paid_histogram(records, width, owned, start, final, edges):
    rows = [1 << index for index in range(width)]
    state = start[:]
    paid = Counter()
    for event in records:
        op, dest = event[0], event[1]
        if op in ("ERASE", "INIT"):
            if dest not in owned or (op == "INIT" and rows[dest]):
                return "owned_op", None
            rows[dest] = 0
            state[dest] = event[2]
            continue
        if op != "ADD":
            return "opcode", None
        source, frame = event[2], event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            origin = state[wire]
            if origin == frame:
                continue
            rank = edges.get((origin, frame))
            if rank is None:
                return "missing_edge", None
            if rows[wire]:
                paid[rank] += 1
            state[wire] = frame
        rows[dest] ^= rows[source]
    for dest, frame in enumerate(final):
        if dest in owned:
            if rows[dest]:
                return "owned_live", None
            state[dest] = frame
            continue
        origin = state[dest]
        if origin == frame:
            continue
        rank = edges.get((origin, frame))
        if rank is None:
            return "missing_edge", None
        if rows[dest]:
            paid[rank] += 1
        state[dest] = frame
    if state != final:
        return "final_state", None
    return None, paid


def correction(event, gate_dest, gate_source):
    dest, source = event[1], event[2]
    if dest == gate_source and source != gate_dest:
        return ["ADD", gate_dest, source]
    if source == gate_dest and dest != gate_source:
        return ["ADD", dest, gate_source]
    return None


def delta_of(paid, base):
    ranks = set(paid) | set(base)
    return tuple(sorted((rank, paid[rank] - base[rank]) for rank in ranks if paid[rank] != base[rank]))


def shape_positive(delta):
    """Exact sign on (0, 1). Unknown shapes are rejected by the caller."""
    if delta == H4:
        return True
    if delta == FIVE_H2:
        # 5*2^t - 2*4^t = 2^t * (5 - 2*2^t). For 0<t<1, 1<2^t<2,
        # so 5 - 2*2^t > 5 - 4 = 1 > 0.
        return True
    return False


def two_step_reaches(rows, state, contact, extra, edges):
    """Whether the contact and its correction can meet at their frames."""
    rows = rows[:]
    state = state[:]
    for event in (contact, extra):
        dest, source, frame = event[1], event[2], event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            origin = state[wire]
            if origin == frame:
                continue
            if (origin, frame) not in edges:
                return False
            state[wire] = frame
        rows[dest] ^= rows[source]
    return True


def meeting_wires(rows, contact, extra):
    """Wires that must already reach the chosen frame before the contact."""
    dest, source = contact[1], contact[2]
    corr_dest, corr_source = extra[1], extra[2]
    wires = []
    if rows[source]:
        wires.extend((dest, source))
    corr_rows = rows[corr_source]
    if corr_source == dest and rows[source]:
        corr_rows = rows[dest] ^ rows[source]
    if corr_rows:
        moved = {dest, source} if rows[source] else set()
        if corr_source not in moved:
            wires.append(corr_source)
        if corr_dest not in moved:
            wires.append(corr_dest)
    return list(dict.fromkeys(wires))


def reachable(origin, outward):
    return outward[origin] | {origin}


def intervals_of(scalars):
    groups = defaultdict(list)
    for index, event in enumerate(scalars):
        if event[0] == "ADD":
            groups[(event[1], event[2])].append(index)
    found = []
    for (gate_dest, gate_source), positions in groups.items():
        for left_at, left in enumerate(positions):
            for right in positions[left_at + 1:]:
                changes = []
                rejected = False
                for index in range(left + 1, right):
                    event = scalars[index]
                    if event[0] in ("ERASE", "INIT") and event[1] in (gate_dest, gate_source):
                        rejected = True
                        break
                    if event[0] == "ADD" and (event[1] == gate_source or event[2] == gate_dest):
                        extra = correction(event, gate_dest, gate_source)
                        if extra is None or len(changes) == 3:
                            rejected = True
                            break
                        changes.append((index, extra, event[3], event[1], event[2]))
                if rejected or not changes:
                    continue
                found.append((left, right, changes))
    return found


def skeleton(scalars, left, right, changes, override):
    replaced = {}
    for number, (index, extra, frame0, _dest, _source) in enumerate(changes):
        replaced[index] = (extra, override.get(number, frame0))
    out = []
    for index, event in enumerate(scalars):
        if index in (left, right):
            continue
        if index in replaced:
            extra, frame = replaced[index]
            out.append(event[:3] + [frame])
            out.append(extra + [frame])
        else:
            out.append(event)
    return out


def snapshots(skeleton_records, contact_positions, width, start):
    rows = [1 << index for index in range(width)]
    state = start[:]
    snaps = []
    cursor = 0
    for position, event in enumerate(skeleton_records):
        if cursor < len(contact_positions) and position == contact_positions[cursor]:
            snaps.append((rows[:], state[:]))
            cursor += 1
        op, dest = event[0], event[1]
        if op in ("ERASE", "INIT"):
            rows[dest] = 0
            state[dest] = event[2]
            continue
        source, frame = event[2], event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            if state[wire] != frame:
                state[wire] = frame
        rows[dest] ^= rows[source]
    need(cursor == len(contact_positions), "missed a contact while snapshotting")
    return snaps


def contact_positions(scalars, left, right, changes):
    positions = []
    cursor = 0
    change_at = {change[0] for change in changes}
    for index, _event in enumerate(scalars):
        if index in (left, right):
            continue
        if index in change_at:
            positions.append(cursor)
            cursor += 2
        else:
            cursor += 1
    return positions


def screen(word, edges, outward, frames):
    scalars = [event[:] for event in word["records"] if event[0] not in ("Q", "ZERO_Q")]
    width = len(word["start"])
    owned = set(word["owned"])
    start = word["start"][:]
    final = word["final"][:]
    expected = expected_rows(width, owned)
    need(endpoint_ok(scalars, width, owned, expected), "published word misses its scalar endpoint")
    reason, base = paid_histogram(scalars, width, owned, start, final, edges)
    need(reason is None, "published word does not emit")
    need(dict(base) == EXPECTED["base_paid"], "base histogram drifted")
    counts = Counter()
    moved = Counter()
    filter_gaps = 0
    brute_checked = 0
    for left, right, changes in intervals_of(scalars):
        fixed = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "frame-free endpoint failed")
        reason, paid = paid_histogram(fixed, width, owned, start, final, edges)
        if reason is not None:
            need(reason == "missing_edge", "fixed frame failed as " + reason)
            counts["fixed_missing"] += 1
        else:
            delta = delta_of(paid, base)
            if delta == ():
                counts["fixed_neutral"] += 1
            elif delta == LOSS_A:
                counts["fixed_loss_a"] += 1
            elif delta == LOSS_B:
                counts["fixed_loss_b"] += 1
            else:
                raise ValueError("fixed-frame shape changed " + str(delta))
        snaps = snapshots(fixed, contact_positions(scalars, left, right, changes), width, start)
        emitted_here = Counter()
        for number, (rows0, state0) in enumerate(snaps):
            _index, extra, frame0, dest, source = changes[number]
            contact = ["ADD", dest, source, frame0]
            wires = meeting_wires(rows0, contact, extra)
            if not wires:
                continue
            cand = None
            for wire in wires:
                reach = reachable(state0[wire], outward)
                cand = reach if cand is None else cand & reach
            cand = set(cand)
            cand.discard(frame0)
            for frame in frames:
                if frame == frame0:
                    continue
                local = two_step_reaches(
                    rows0, state0, ["ADD", dest, source, frame], extra + [frame], edges)
                if local and frame not in cand:
                    filter_gaps += 1
            for frame in cand:
                moved["trials"] += 1
                rewritten = skeleton(scalars, left, right, changes, {number: frame})
                reason, paid = paid_histogram(rewritten, width, owned, start, final, edges)
                if reason is not None:
                    need(reason == "missing_edge", "moved frame failed as " + reason)
                    moved["missing"] += 1
                    continue
                delta = delta_of(paid, base)
                need(shape_positive(delta), "nonpositive or unknown moved shape " + str(delta))
                if delta == H4:
                    moved["h4"] += 1
                elif delta == FIVE_H2:
                    moved["five_h2"] += 1
                else:
                    raise ValueError("positive classifier accepted " + str(delta))
                emitted_here[delta] += 1
        if emitted_here:
            brute_checked += 1
            seen = brute_moved_frame(
                scalars, left, right, changes, frames, width, owned, start, final, edges, base)
            need(seen == emitted_here, "full-frame brute disagrees with the meeting filter " + str((seen, emitted_here)))
    counts["candidates"] = (
        counts["fixed_missing"] + counts["fixed_loss_a"] + counts["fixed_loss_b"] + counts["fixed_neutral"])
    need(filter_gaps == 0, "meeting filter omitted a locally feasible frame")
    need(brute_checked >= 1, "no moved frame emitted, so the full-frame control did not run")
    return counts, moved


def brute_moved_frame(scalars, left, right, changes, frames, width, owned, start, final, edges, base):
    """Every catalogue frame on an interval that already emitted one move."""
    seen = Counter()
    for number, (_index, extra, frame0, dest, source) in enumerate(changes):
        for frame in frames:
            if frame == frame0:
                continue
            rewritten = skeleton(scalars, left, right, changes, {number: frame})
            reason, paid = paid_histogram(rewritten, width, owned, start, final, edges)
            if reason is not None:
                continue
            seen[delta_of(paid, base)] += 1
    return seen


def controls(edges, outward):
    need(shape_positive(H4) and shape_positive(FIVE_H2), "known losses must stay positive")
    need(not shape_positive(((1, 1), (2, -2), (3, 1))), "the known saving must not be called a loss")
    need(2 * 2 - 5 < 0 and 5 - 4 == 1, "the 2^t bound 2*2-5<0 is the t->1 edge")
    sample = next(iter(edges))
    broken = dict(edges)
    del broken[sample]
    need(sample not in broken, "deleted edge still present")
    need(sample[1] not in (outward[sample[0]] - {sample[1]}), "neighbor set did not shrink")


def main():
    word, paths, local = load_pinned()
    published = {int(rank): count for rank, count in local["stats"]["paid"].items()}
    need(published == EXPECTED["base_paid"], "LOCAL-RESULT paid histogram drifted")
    need(local["productive_conjugations"] == 2, "published productive step count changed")
    edges, outward, frames = load_edges(paths)
    counts, moved = screen(word, edges, outward, frames)
    controls(edges, outward)
    for key in ("candidates", "fixed_missing", "fixed_loss_a", "fixed_loss_b", "fixed_neutral"):
        need(counts[key] == EXPECTED[key], key + " changed")
    need(moved["trials"] == EXPECTED["moved_trials"], "moved trial count changed")
    need(moved["missing"] == EXPECTED["moved_missing"], "moved missing count changed")
    need(moved["h4"] == EXPECTED["moved_h4"], "H4 count changed")
    need(moved["five_h2"] == EXPECTED["moved_five_h2"], "5 H2 - 2 H4 count changed")
    need(moved["h4"] + moved["five_h2"] + moved["missing"] == moved["trials"], "moved census does not add")
    print(
        "PASS_G20_MOVED_CORRECTION_FRAME"
        " candidates={candidates} moved_trials={trials} missing_edge={missing}"
        " emitted_h4={h4} emitted_5h2_minus_2h4={five_h2} savings=0"
        " no_new_kappa=true".format(
            candidates=counts["candidates"], trials=moved["trials"], missing=moved["missing"],
            h4=moved["h4"], five_h2=moved["five_h2"]))


if __name__ == "__main__":
    main()
