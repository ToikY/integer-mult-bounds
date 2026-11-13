#!/bin/sh
set -eu
bundle=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
root=${1:?replay root required}
mkdir -p "$root/inputs" "$root/compiler"
caller=https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/replay/supplier7112/short-caller
signed=https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/89eaa9d8cae37c1540de98f2d29a3abaabb96a2b/research/p104-funded-485-1455-return/producer54/validation_signed
copied=https://raw.githubusercontent.com/ToikY/integer-mult-bounds/0d86bd1e4ae98624ef75123b93bb49e93801e872/research/p104-owned1548-early-encoding-bound/inputs
for f in 7113-CALLER.json 7481-APPLICATION.json 7481-WORD.json.gz
do
    curl -fsSL "$copied/$f" -o "$root/inputs/$f"
done
for f in upstream_application.py DATA-PHASES.json
do
    curl -fsSL "$caller/$f" -o "$root/compiler/$f"
done
for f in check_odd_physical_binding.py check_odd_fixed_tape_counts.py check_odd_partial_admission.py
do
    curl -fsSL "$signed/adapted/$f" -o "$root/compiler/$f"
done
curl -fsSL "$signed/RESULT.json" -o "$root/compiler/SIGNED-RESULT.json"
cp "$bundle/pricing.py" "$root/inputs/pricing.py"
cd "$root"
shasum -a 256 -c "$bundle/INPUT-SHA256"
