#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target=${1:?Usage: sh fetch_inputs.sh replay-root}
mkdir -p "$target/inputs"
base=https://raw.githubusercontent.com/ToikY/integer-mult-bounds/0d86bd1e4ae98624ef75123b93bb49e93801e872/research/p104-owned1548-early-encoding-bound/inputs
for name in 7481-WORD.json.gz 7481-APPLICATION.json 7113-CALLER.json
do
    curl --fail --silent --show-error --location "$base/$name" --output "$target/inputs/$name"
done
cp "$root/pricing.py" "$target/inputs/pricing.py"
cp "$root/gate.py" "$target/inputs/gate.py"
(
    cd "$target"
    shasum -a 256 -c "$root/INPUT-SHA256"
)
