#!/bin/sh
# Merge gate (PROCEDURES § When merging engine work), parameterised copy of
# projects/omni-ui/results/browser-functional-0/merge-gate.sh for a seat worktree:
#   OLD = main's exact commit built in a throwaway worktree, NEW = the seat branch build.
# Gates: baseline equal, check-compiled 0 different, binary gate 0 lost, JS probe title, connectivity 13/13.
# Server runs under tritwatch by name and is stopped by name (no pkill -f, PROCEDURES 10-07).
set -u
OLD=${OLD:?OLD binary}; NEW=${NEW:?NEW binary}
B=<workspace>/projects/omni-ui/results/browser-functional-0
OUT=${OUT:-$(dirname "$0")/gate.$(date +%Y%m%d-%H%M)}; mkdir -p "$OUT"
echo "OLD $OLD ($("$OLD" --version 2>/dev/null | head -1)) · NEW $NEW" | tee "$OUT/binaries.txt"
sha256sum "$OLD" "$NEW" >> "$OUT/binaries.txt"
cd <workspace>/projects/omni-render || exit 1
P="--program results/omr.program.json"
echo "== M2a baseline (old vs new must be equal)"
timeout 900 "$OLD" core corpus $P --max 0 > "$OUT/base-old.txt" 2>&1; tail -2 "$OUT/base-old.txt"
timeout 900 "$NEW" core corpus $P --max 0 > "$OUT/base-new.txt" 2>&1; tail -2 "$OUT/base-new.txt"
echo "== M2b check-compiled (0 different)"
timeout 900 "$NEW" core corpus $P --check-compiled > "$OUT/check-compiled.txt" 2>&1; tail -2 "$OUT/check-compiled.txt"
echo "== M2c binary gate (0 lost)"
timeout 900 "$OLD" core corpus $P --agree-snapshot "$OUT/agree-old.json" 2>&1 | tail -1
timeout 900 "$NEW" core corpus $P --binary-gate "$OUT/agree-old.json" > "$OUT/binary-gate.json" 2>"$OUT/binary-gate.err"; tail -1 "$OUT/binary-gate.err"
echo "== M3 browser gates"
cd $B && <workspace>/bin/tw start --id gate-srv-8771 -- timeout 900 python3 server.py 8771 >/dev/null 2>&1; sleep 2
printf 'jsprobe title: '; timeout 120 "$NEW" page http://127.0.0.1:8771/index.html 2>/dev/null | grep '^meta' | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()[5:]).get("title",""))' | tee "$OUT/jsprobe.txt"
BIN=$NEW sh $B/conn.sh > "$OUT/conn.txt" 2>&1; echo "conn.sh fails=$?"; grep -c '^PASS' "$OUT/conn.txt"
<workspace>/bin/tw kill gate-srv-8771 >/dev/null 2>&1 || true
echo "MERGE-GATE-DONE $OUT"
