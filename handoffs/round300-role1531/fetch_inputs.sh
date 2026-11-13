#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target=${1:?Usage: sh fetch_inputs.sh replay-root}
mkdir -p "$target/inputs"
base=https://raw.githubusercontent.com/ToikY/integer-mult-bounds/99438c43df7aac1e5dbcc43c1578fcd886c119ec/research/p104-role902-direct-lift
curl -fsSL "$base/expected/FINAL.json" -o "$target/inputs/ROLE902-APPLICATION.json"
curl -fsSL "$base/bench/inputs/7113-CALLER.json" -o "$target/inputs/7113-CALLER.json"
curl -fsSL "$base/expected/role902-WORD.json.gz" -o "$target/inputs/ROLE902-WORD.json.gz"
cp "$here/inputs/pricing.py" "$here/inputs/gate.py" "$target/inputs/"
old=https://raw.githubusercontent.com/ToikY/integer-mult-bounds/d6be7d620c9c8337104daeb09fe01196eced5fe3/research/p104-funded-producer-rung-composition/compose
curl -fsSL "$old/7334-WORD.json.gz" -o "$target/inputs/7334-WORD.json.gz"
