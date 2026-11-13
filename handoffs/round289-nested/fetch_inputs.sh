#!/bin/sh
set -eu
target=${1:?Usage: sh fetch_inputs.sh replay-root}
base=https://raw.githubusercontent.com/ToikY/integer-mult-bounds/d6be7d620c9c8337104daeb09fe01196eced5fe3/research/p104-funded-producer-rung-composition/bench/inputs
mkdir -p "$target/inputs"
for file in 7113-CALLER.json 7481-APPLICATION.json pricing.py; do
    curl --fail --silent --show-error --location "$base/$file" --output "$target/inputs/$file"
done
