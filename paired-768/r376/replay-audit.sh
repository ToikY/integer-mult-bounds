#!/bin/sh
set -eu
if [ "$#" -ne 2 ]; then
    echo 'Usage: sh replay-audit.sh R374_PACKAGE R376_PACKAGE' >&2
    exit 2
fi
here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT HUP INT TERM
python3.12 -IB - "$1" "$tmp" <<'PY'
from pathlib import Path
from runpy import run_path
import sys

source, work = map(Path, sys.argv[1:])
peer, stage = work / 'peer', work / 'stage'
run_path(str(source / 'verify.py'))['restore'](peer)
run_path(str(source / 'prepare.py'))['materialize'](
    peer, source / 'COMPACT-PRICE.json', source / 'integer-prototype.py', stage,
)
(stage / 'RESULT.json').write_bytes((source / 'RESULT.json').read_bytes())
PY
coupling="$here/evidence/round375/independent"
python3.12 -IB "$here/accept.py" --inputs "$here/evidence" --literal "$2" --out "$tmp/accept.json"
cmp "$tmp/accept.json" "$here/verified.json"
python3.12 -IB "$here/audit/calendar.py" --stage "$tmp/stage" --coupling "$coupling" --out "$tmp/calendar.json"
cmp "$tmp/calendar.json" "$here/audit/receipt.json"
python3.12 -IB "$here/audit/setup.py" --coupling "$coupling/coupling.json" --setup "$tmp/stage/SETUP.md" --out "$tmp/setup.json"
cmp "$tmp/setup.json" "$here/audit/setup.json"
sha256sum "$tmp/accept.json" "$tmp/calendar.json" "$tmp/setup.json"
