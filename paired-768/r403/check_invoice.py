"""Exact Round 403 invoice and restricted-family ceiling, from pinned #8071."""

from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import subprocess
import sys
import tarfile
from types import SimpleNamespace

HEAD = "9555f2df027f4a182722f736c97e5efafa5382c6"
ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
RECEIPT = "f5fa3269a242ed7cb4826ab03db0355dc7345caec8436f93eb53640afc53049d"
PACKAGE = Path("research/p104-weighted-ordinary-debit-11239")
TRIAL_O, TRIAL_G = Q(4391986206293, 2**50), Q(17145637307, 2**42)
DEBIT_O, DEBIT_G = Q(11239, 8192), Q(64939, 524288)
MIN_H, MAX_H, CAP = 8192, 524288, 318292071
ETA, STOP, SCALE = Q(39, 10000), Q(5, 10**18), 10**21
OLD_RATE, NEW_RATE = Q(".00389821412325"), Q(".003898214283192")
LOW, HIGH = 490949, 490950


def pinned_modules(repository, receipt_path):
    def git(*args):
        return subprocess.check_output(["git", "-C", repository, *args])
    assert git("rev-parse", "HEAD").strip().decode() == HEAD
    assert not git("status", "--porcelain")
    package = repository / PACKAGE
    for name in ("PEER-SOURCE.json", "peer8057.tar.gz", "RESULT.json"):
        assert (package / name).read_bytes() == git("show", f"{HEAD}:{PACKAGE / name}")
    receipt_data = receipt_path.read_bytes()
    assert sha256(receipt_data).hexdigest() == RECEIPT
    receipt = json.loads(receipt_data)
    assert receipt["head"] == HEAD and receipt["exit_code"] == 0 and receipt["clean_detached_checkout"]
    manifest = json.loads((package / "PEER-SOURCE.json").read_bytes())
    assert sha256((package / "peer8057.tar.gz").read_bytes()).hexdigest() == manifest["archive_sha256"] == ARCHIVE
    sources = {}
    with tarfile.open(package / "peer8057.tar.gz") as archive:
        for helper in ("outer_budget", "activation"):
            source = f"research/tiered-native-multiplier/source/{helper}.py"
            data = archive.extractfile(source).read()
            assert sha256(data).hexdigest() == manifest["files_sha256"][source]
            namespace = {"__name__": helper}
            exec(compile(data, source, "exec"), namespace)
            sources[helper] = namespace
    return sources, receipt, json.loads((package / "RESULT.json").read_bytes())


def ordinary(heights):
    value, stages = Q(0), []
    for i, height in enumerate(heights):
        unclamped = (249 * (TRIAL_O - DEBIT_O / height) + value) / 250
        assert unclamped < ETA
        value = unclamped if i == 2 else Q(floor(unclamped * SCALE) - 1, SCALE)
        stages.append(value)
    return value, stages


def best_policy(gaussian, cap):
    height_sum = (cap - 1731 - 220 * gaussian) // 320
    heights = (MIN_H, height_sum - MIN_H - MAX_H, MAX_H)
    assert sum(heights) == height_sum and MIN_H <= heights[1] <= MAX_H
    ordinary_rate, stages = ordinary(heights)
    return dict(gaussian_height=gaussian, heights=heights, ordinary=ordinary_rate,
                gaussian=TRIAL_G - DEBIT_G / gaussian, ordinary_stages=stages,
                complete_clock=1731 + 320 * sum(heights) + 220 * gaussian)


def fixed_cap_proof(upper):
    heights = upper["heights"]
    weights = Q(1, 250**2), Q(1, 250), Q(1)
    p = Q(249, 250)
    slopes = [w / height**2 for w, height in zip(weights, heights, strict=True)]
    a, b, c = slopes
    assert 0 < a < b < c
    relaxed = p * sum(w * (TRIAL_O - DEBIT_O / height)
                      for w, height in zip(weights, heights, strict=True))
    rounding_loss = relaxed - upper["ordinary"]
    tangent_loss = p * DEBIT_O * min(b-a, c-b, b)
    assert 0 < rounding_loss < tangent_loss
    return dict(relaxed_rate=relaxed, slopes=slopes, rounding_loss=rounding_loss,
                minimum_distinct_integer_tangent_loss=tangent_loss)


def full_invoice(selected, old_late, entry, source):
    heights, gauss = selected["heights"], selected["gaussian_height"]
    cuts = []
    for h in heights:
        cuts.append(max(ceil(Q(250 * (h + 64), 249)), cuts[-1] + h + 64 if cuts else 0))
    required = cuts[-1] + gauss + 102
    width = next(s for s in range(required, required + 150) if s - 7 * (s-1).bit_length() >= required)
    exponent, offset = width - 1, (-pow(2, width - 1, 6)) % 6
    assert (1 << (width-1).bit_length()) + 1 - 7 * ((width-1).bit_length() + 1) >= required
    stock = source["activation"]["resource_receipt"](
        SimpleNamespace(rank_logs=heights, complex_log=gauss, eta=ETA))
    assert (stock["public_exponent_A"], stock["first_public_offset"], stock["binary_cuts"]) == (exponent, offset, cuts)
    assert all(a < b for a, b in zip([0, *selected["ordinary_stages"][:2]],
                                     [*selected["ordinary_stages"][:2], NEW_RATE + STOP], strict=True))
    margins = []
    for rate, ordinary_rate, gaussian_rate in (
        (Q(".00345"), Q(".00345") + STOP, TRIAL_G - DEBIT_G / 1024),
        (NEW_RATE, NEW_RATE + STOP, selected["gaussian"]),
    ):
        strict, functional, paid = source["outer_budget"]["margins"](rate, Q(1,10**18), ordinary_rate, gaussian_rate)
        assert (len(strict), len(functional)) == (54, 4)
        assert min(*strict, *functional, paid) > 0
        margins.append(dict(strict_count=54, functional_count=4, minimum_strict=min(strict),
                            minimum_functional=min(functional), paid_margin=paid))
    descriptor_bits = max(*heights,gauss).bit_length()
    envelope = 1024 * max(*heights,gauss) + (len(heights) + 1).bit_length()
    assert stock["absolute_log2_private_control_envelope"] == envelope
    assert descriptor_bits == max(*old_late["ordinary_H"], old_late["numerical_H"]).bit_length() == 20
    assert envelope == old_late["stock"]["absolute_log2_private_control_envelope"] == 536870915
    binary_bill = 128 + 320 * sum(heights)
    gauss_bill = 220 * gauss
    entry_premium = ceil((NEW_RATE - Q(entry["kappa"])) * exponent)
    final = 1 + max(entry["log2_C"] + entry_premium, max(84500001, 1602 + gauss_bill + binary_bill))
    assert final == selected["complete_clock"] == 318292011 and entry_premium == 515
    # The signed Gaussian provider retains its exact two physical scales and upper divisor.
    # Verify the literal upper-width parameter precondition at the new H.
    carrier = 1 << gauss
    upper = 2 * (carrier // (1724 * 306))
    assert upper > 2 * (carrier // (2048 * 306)) and 4 * 258 * (upper-8) < carrier
    assert upper % 2 == 0 and (68 + 83 * gauss) < 92 * gauss
    funding_o = ceil(DEBIT_O / (TRIAL_O - NEW_RATE - STOP))
    funding_g = ceil(DEBIT_G / (TRIAL_G - NEW_RATE - STOP))
    assert funding_o <= sum(heights) and funding_g <= gauss
    width_min = 128 * (4 * (width+1) + 6)
    q = (6 * width_min - 1).bit_length()
    assert exponent - q >= (6 * exponent).bit_length()
    largest_axis = ((1 << q)+5)//6
    return dict(final_recurring_clock=final, entry_premium=entry_premium,
                entry_clock_before_premium=entry["log2_C"], binary_clock=binary_bill,
                gaussian_clock=gauss_bill, stage_cuts=cuts, activation_exponent=exponent,
                activation_offset=offset, minimum_width_at_activation=width_min,
                log2_axis_count=exponent-q, largest_axis_width=largest_axis,
                private_scalar_clock_upper=(1 << 10)*(largest_axis+width+67)+width,
                stock=stock, height_descriptor_bits=descriptor_bits, fixed_setup_exponent_bound=228,
                family_stage_count_total=len(heights)+len(entry["ordinary_H"])+2,
                gaussian_funding_height=funding_g, ordinary_standalone_funding_height=funding_o,
                signed_margins=margins)


def main():
    repository, receipt_path = map(Path, sys.argv[1:])
    sources, old_replay, old_result = pinned_modules(repository, receipt_path)
    old, old_next = old_result["terminal"], old_result["entry"]
    assert Q(old["kappa"]) == OLD_RATE and old_result["complete_log2_C"] == CAP
    old_gaussian = TRIAL_G - DEBIT_G / old["numerical_H"]
    old_ordinary, _ = ordinary(tuple(old["ordinary_H"]))
    old_ceiling = min(old_ordinary, old_gaussian) - STOP
    assert old_ceiling == Q(old_replay["candidate_fixed_profile_ceiling"])
    low, high, negative = [best_policy(g, CAP) for g in (LOW, HIGH, HIGH+1)]
    assert low["gaussian"] < high["ordinary"] < high["gaussian"]
    assert negative["ordinary"] < NEW_RATE + STOP
    negative_proof = fixed_cap_proof(negative)
    proof = fixed_cap_proof(high)
    ceiling = high["ordinary"] - STOP
    assert ceiling > NEW_RATE > old_ceiling > OLD_RATE
    assert high["heights"] == tuple(best_policy(HIGH, high["complete_clock"])["heights"])
    invoice = full_invoice(high, old, old_next, sources)
    print(json.dumps({
        "prior_head": HEAD, "gaussian_height_range": [1024, MAX_H],
        "ordinary_height_range": [MIN_H, MAX_H], "terminal_three_stage_cap": CAP,
        "same_ceiling_at_installed_cap": high["complete_clock"],
        "lower_adjacent": low, "upper_adjacent": high, "new_budgeted_negative": negative,
        "adjacent_integer_proof": proof, "negative_integer_proof": negative_proof,
        "candidate_fixed_and_capped_family_ceiling": ceiling, "candidate_kappa": NEW_RATE,
        "prior_fixed_profile_ceiling": old_ceiling,
        "gain_above_prior_booking": NEW_RATE-OLD_RATE,
        "gain_above_prior_ceiling": NEW_RATE-old_ceiling,
        "slack_below_new_ceiling": ceiling-NEW_RATE,
        "old_gaussian_height_shortfall": NEW_RATE + STOP - old_gaussian,
        "lower_crossing_gaussian_shortfall": NEW_RATE + STOP - low["gaussian"],
        "higher_gaussian_ordinary_shortfall": NEW_RATE + STOP - negative["ordinary"],
        "complete_invoice": invoice,
    }, default=str, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
