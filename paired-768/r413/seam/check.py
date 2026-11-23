"""Audit all seven #8094 ordinary recipe slots using integer exponents."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from math import ceil
from pathlib import Path
from tarfile import open as open_tar
import json
import signal

SOURCES = {
    "RESULT.json": "915e124475494b08e786eb433e6591d85f2bdedebd624a45b49504c63bbb30e6",
    "prepare.py": "bc401e5c47d275617f3c7d162d56ea4c604ef3d4c6637ab2a8aa8627a570a9f6",
    "check_stage_seam.py": "b790eb6855afa255a609eaaf88a46ed9e8b04232671cca4d0f8bd0bad27f11ac",
}
ARCHIVE_SHA256 = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
INHERITED = "research/tiered-native-multiplier/installations.py"
HEAD = "c20a08dc0a79a989e3515068560d5da371c0a2a8"


def checked_file(path, digest):
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"Source hash mismatch for {path.name}")
    return data


def admission_cuts(heights):
    cuts = []
    for height in heights:
        cut = ceil(Q(250 * (height + 64), 249))
        if cuts:
            cut = max(cut, height + cuts[-1] + 64)
        cuts.append(cut)
    return cuts


def dyadic_direct(s, height, prev_cut):
    """Decide ceil(2**s / width) <= 2**(8*H) without materializing the width."""
    t = s - 8 * height
    if t <= 0 or (prev_cut is not None and t <= prev_cut):
        return True
    if t < 10:
        return s >= ((2**t - 1)**250).bit_length()
    # Direct via the root iff 2**s > (2**t-1)**250. Bernoulli gives
    # (1-2**(-t))**250 > 1/2 for t>=10, leaving one integer boundary.
    return s >= 250 * t


def recipe(heights, cuts, eta, index):
    height, cut = heights[index], cuts[index]
    prev_cut = cuts[index - 1] if index else None
    next_cut = cuts[index + 1] if index + 1 < len(cuts) else None
    prev_gap = height - prev_cut - 2 if prev_cut is not None else None
    assert prev_gap is None or prev_gap > 0
    root_margin = Q(249 * cut, 250) - height - 64
    floor_margin = cut - height - prev_cut - 64 if prev_cut is not None else None
    assert root_margin >= 0 and (floor_margin is None or floor_margin >= 0)

    # At e=2**cut the root is <=2**ceil(cut/250). The other branch
    # is <=2**(prev_cut+1). Subtract the larger bound to get true stock.
    width_upper_log = ceil(Q(cut, 250))
    if prev_cut is not None:
        width_upper_log = max(width_upper_log, prev_cut + 1)
    stock_lo = cut - width_upper_log
    assert stock_lo >= height + 63

    # (2**p+1)**250 lies strictly between 2**(250*p) and
    # 2**(250*p+1) by the common p>=10 bound below.
    floor_last = 250 * prev_cut if prev_cut is not None else None
    assert prev_cut is None or prev_cut >= 10
    floor_at_entry = floor_last is not None and cut <= floor_last

    last_direct = max(2000 * height // 249, 8 * height + (prev_cut or 0))
    first_compiled = last_direct + 1
    assert dyadic_direct(cut, height, prev_cut)
    assert dyadic_direct(last_direct, height, prev_cut)
    assert not dyadic_direct(first_compiled, height, prev_cut)
    quotient_bound = ceil(Q(2 * height + 64, 1 - eta))
    assert quotient_bound < 3 * height < 8 * height < first_compiled
    assert eta * quotient_bound > 23
    assert 2 * eta > Q(1, 250) and eta > Q(1, 258)
    if next_cut is not None and first_compiled >= next_cut:
        # This checks absence among dyadic anchors in the uncapped
        # stage's dispatch domain. It is not a claim about caller reach.
        assert dyadic_direct(next_cut - 1, height, prev_cut)

    # Common finite raw lower fence and maximum possible public input cut.
    calendar_lower = 4474
    assert (calendar_lower * 1024 * 134).bit_length() <= height
    return {
        "stage": index + 1, "rank_log": height, "entry_cut": cut,
        "previous_cut": prev_cut, "next_cut": next_cut,
        "predecessor_rank_gap_after_two_bits": prev_gap,
        "cut_root_margin_above_H_plus_64": str(root_margin),
        "cut_floor_margin_above_H_plus_64": floor_margin,
        "entry_stock_lower_log": stock_lo,
        "predecessor_floor_at_entry": floor_at_entry,
        "previous_full_width_log_if_called_at_admission": prev_cut if floor_at_entry else None,
        "last_predecessor_floor_dyadic_log": floor_last,
        "last_direct_dyadic_log": last_direct,
        "first_compiled_dyadic_log_if_stage_capped": first_compiled,
        "compiled_dyadic_anchor_in_uncapped_stage": next_cut is None or first_compiled < next_cut,
        "quotient_stock_log_bound": quotient_bound,
    }


def stop(*_):
    raise TimeoutError("Seven-case finite seam reached the 60-second cap")


def run(package_root, archive):
    source = {name: checked_file(package_root / name, h) for name, h in SOURCES.items()}
    profile = json.loads(source["RESULT.json"])
    prepare, seam = (source[name].decode() for name in ("prepare.py", "check_stage_seam.py"))
    assert 'Q(".003900857267786"), Q(1, 256)' in prepare
    assert "level_floor=4474" in prepare
    assert "width = max(prev+1, power)" in seam
    assert "expect_direct = -(-base//width) <= 1 <<" in seam
    with open_tar(fileobj=BytesIO(checked_file(archive, ARCHIVE_SHA256)), mode="r:gz") as inputs:
        installation = inputs.extractfile(INHERITED).read()
    assert b"eta: Q = Q(39, 10000)" in installation
    assert b'ENTRY = Profile((3000, 3080), 1024, Q(".00345"))' in installation
    assert (1 + Q(1, 1024))**250 < 2
    assert 1 - Q(250, 1024) > Q(1, 2)

    results = {}
    for name, eta in (("entry", Q(39, 10000)), ("terminal", Q(1, 256))):
        row = profile[name]
        heights = row["ordinary_H"]
        assert heights == ([3000, 3080] if name == "entry" else [31808, 502922, 7951907, 125730703, 134217727])
        cuts = admission_cuts(heights)
        assert row["stock"]["binary_cuts"] == cuts
        assert all(Q(b) < eta < Q(1, 250) for b in row["ordinary_rates"])
        results[name] = {
            "eta": str(eta),
            "fits_old_eta": Q(row["ordinary_rates"][-1]) < Q(39, 10000),
            "recipes": [recipe(heights, cuts, eta, i) for i in range(len(heights))],
        }
    assert results["entry"]["fits_old_eta"] and not results["terminal"]["fits_old_eta"]
    first_cut_terminal = results["terminal"]["recipes"][-2]["entry_cut"]
    assert first_cut_terminal + 2 < results["terminal"]["recipes"][-1]["rank_log"]
    bad_heights = profile["terminal"]["ordinary_H"][:-1] + [first_cut_terminal + 2]
    try:
        recipe(bad_heights, admission_cuts(bad_heights), Q(1, 256), len(bad_heights) - 1)
    except AssertionError:
        pass
    else:
        raise AssertionError("Predecessor-clearance negative control was admitted")
    return {
        "head": HEAD, "cases": 7, "elapsed_cap_seconds": 60,
        "sources_sha256": SOURCES, "archive_sha256": ARCHIVE_SHA256,
        "archived_entry_path": INHERITED,
        "archived_entry_sha256": sha256(installation).hexdigest(),
        "scope": "Exact dyadic dispatch, floor, stock and cut arithmetic only. No native action, all-size clock or signed caller reach was executed.",
        "controls": {"terminal_old_eta_rejected": True, "neighbor_at_predecessor_cut_plus_2_rejected": True},
        "tiers": results,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    assert __debug__
    signal.signal(signal.SIGALRM, stop)
    signal.alarm(60)
    print(json.dumps(run(args.package_root, args.archive), indent=2))


if __name__ == "__main__":
    main()
