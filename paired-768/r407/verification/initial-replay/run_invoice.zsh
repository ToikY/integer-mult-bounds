#!/bin/zsh
set -u
idir=${0:A:h}
py=${1:-python3.12}
label=${2:-independent-invoice}
date -u +%FT%TZ > "$idir/$label.start.utc"
"$py" -IB "$idir/independent_check.py" "$idir/checkout" "$idir/../../round406/peer8081/checkout" "$idir/working-images" "$idir/../CANDIDATE-INPUTS.json" "$idir/../../round406/peer8081/REPLAY-RECEIPT.json" > "$idir/$label.json" 2> "$idir/$label.err"
rc=$?
date -u +%FT%TZ > "$idir/$label.end.utc"
printf '%s\n' "$rc" > "$idir/$label.exit"
cat "$idir/$label.err"
exit "$rc"
