"""Check the one fixed R407 period profile against its authentic installer source."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from math import ceil, floor
from pathlib import Path
from subprocess import check_output
import tarfile

HEAD = "510113821774bb27f7ddaad4e8b94837a1c2cf52"
ARCHIVE = "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c"
IMAGE = "387e60913e375316d904d4489e5ea5e69c0ac5729250f27fe52ef23910a07e13"
H = (8192, 38102, 604363)
G = 18845934
CAP = 4354317571
TARGET = Q(".003898460000505")
STOP = Q(5, 10**18)
BIT = Q(4391986206293, 2**50)
GAUSSIAN = Q(17145637307, 2**42)
ORDINARY_DEBIT = Q(11239, 8192)
OLD_DEBIT = Q(64939, 524288)
NEW_DEBIT = Q(64934, 524288)


def bit_price(heights):
    previous = Q(0)
    for index, height in enumerate(heights, 1):
        booked = min(Q(39, 10000), (249 * (BIT - ORDINARY_DEBIT / height) + previous) / 250)
        if index < len(heights):
            previous = Q(floor(booked * 10**21) - 1, 10**21)
    return booked


def gaussian_price(height):
    return GAUSSIAN - NEW_DEBIT / height


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("peer8081", type=Path)
    args = parser.parse_args()
    git = lambda *items: check_output(["git", "-C", str(args.peer8081), *items])
    assert git("rev-parse", "HEAD").decode().strip() == HEAD and not git("status", "--porcelain")
    relative = "research/p104-expanded-budget-25bit/peer8057.tar.gz"
    archive = args.peer8081 / relative
    data = archive.read_bytes()
    assert sha256(data).hexdigest() == ARCHIVE and git("show", f"{HEAD}:{relative}") == data
    with tarfile.open(archive) as bundle:
        image = bundle.extractfile("research/tiered-native-multiplier/installations.py").read()
        typed = bundle.extractfile("research/frequency-weighted-native-multiplier/typed_transport.py").read()
    assert b"size = (e - 8) * k" in typed and b"period = 4 * ceil(Q(n, 4 * size))" in typed
    previous_line = b'TERMINAL = Profile((35327, 559005), 680000, Q(".0038982"))'
    assert image.count(previous_line) == 1
    image = image.replace(b"Q(2143194013, 2**39)", b"Q(17145637307, 2**42)", 1)
    predecessor = image.replace(previous_line, b'TERMINAL = Profile((8192, 38102, 604362), 18845936, Q(".00389846"))')
    assert sha256(predecessor).hexdigest() == "509c7ffec6f9bb26178a095ec9c9b219331b544a1ac7e6a53d0efe3fa17c8215"
    terminal = f'TERMINAL = Profile({H!r}, {G}, Q(".003898460000505"))'.encode()
    candidate = image.replace(previous_line, terminal)
    assert sha256(candidate).hexdigest() == IMAGE
    minimum_x = Q(1724 * 306, 2 * 4 * 258)
    assert 255 < minimum_x < 256 and 256 / minimum_x < Q(257, 256) < 1 + 1 / minimum_x
    paid = TARGET + STOP
    assert bit_price(H) > paid
    assert bit_price((H[0], H[1] - 1, H[2])) < paid
    assert bit_price((H[0], H[1], H[2] - 1)) < paid
    gaussian_floor = ceil(NEW_DEBIT / (GAUSSIAN - paid))
    ordinary_floor = ceil(ORDINARY_DEBIT / (BIT - paid))
    assert (ordinary_floor, gaussian_floor) == (569896, 18845933)
    assert gaussian_price(gaussian_floor - 1) < paid < gaussian_price(gaussian_floor)
    assert gaussian_price(G - 1) > paid
    assert GAUSSIAN - OLD_DEBIT / 18845936 - STOP < TARGET
    terminal_cost = 1731 + 320 * sum(H) + 220 * G
    assert terminal_cost == 4354317451 < CAP < terminal_cost + 220
    assert G.bit_length() == 25 and (1 << G).bit_length() == G + 1
    assert max(TARGET.numerator.bit_length(), TARGET.denominator.bit_length(), (10**18).bit_length()) <= 128
    # A concrete ordinary counterexample falsifies the old minimum-sum label.
    assert sum((8192, 38216, 604248)) == sum(H) - 1
    assert bit_price((8192, 38216, 604248)) > paid
    print("PASS_25BIT_LITERAL_PRICE", IMAGE, "floors", ordinary_floor, gaussian_floor)
    print("PASS_25BIT_FIXED_CASE", "terminal_cost", terminal_cost, "G_minus_one_funds", True)
    print("PASS_25BIT_ECONOMY_SCOPE_NEGATIVE", "old_ordinary_sum_has_funding", (8192, 38216, 604248))


if __name__ == "__main__":
    main()
