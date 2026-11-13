#!/bin/sh
set -eu
src=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target=${1:?Usage: sh fetch_inputs.sh replay-root}
mkdir -p "$target/inputs"
base=https://raw.githubusercontent.com/ToikY/integer-mult-bounds/d6be7d620c9c8337104daeb09fe01196eced5fe3/research/p104-funded-producer-rung-composition
curl -fsSL "$base/expected/COMPOSED-WORD.json.gz" -o "$target/inputs/COMPOSED-WORD.json.gz"
curl -fsSL "$base/expected/FINAL.json" -o "$target/inputs/COMPOSED-APPLICATION.json"
curl -fsSL "$base/bench/inputs/7113-CALLER.json" -o "$target/inputs/7113-CALLER.json"
cp "$src/inputs/suffix_readout.py" "$target/inputs/suffix_readout.py"
cp "$src/inputs/pricing.py" "$target/inputs/pricing.py"
