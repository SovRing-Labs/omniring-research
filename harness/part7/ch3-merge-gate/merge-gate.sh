#!/bin/sh
# Merge gate for browser/body-0 ← main (BROWSER-FUNCTIONAL-0 M1–M3; recipe omni-render MANUAL:231). Run under tw.
# OLD = main's binary (target-doctor, built at main 23fd198); NEW = the merged browser worktree build.
set -u
R=<workspace>/projects/omni-ui/results/browser-functional-0
OUT=$R/merge-gate.$(date +%Y%m%d-%H%M)
mkdir -p "$OUT"
OLD=<workspace>/projects/omni-render/target-doctor/release/omni-render
NEW=<workspace>/projects/omni-render-browser/target/release/omni-render
echo "== M1 build"
cd <workspace>/projects/omni-render-browser && cargo build --release -j4 2>&1 | tail -3 || exit 1
cd <workspace>/projects/omni-render || exit 1
P="--program results/omr.program.json"
echo "== M2a baseline (old vs new must be equal)"
$OLD core corpus $P --max 0 > "$OUT/base-old.txt" 2>&1; tail -2 "$OUT/base-old.txt"
$NEW core corpus $P --max 0 > "$OUT/base-new.txt" 2>&1; tail -2 "$OUT/base-new.txt"
echo "== M2b check-compiled (0 different)"
$NEW core corpus $P --check-compiled > "$OUT/check-compiled.txt" 2>&1; tail -2 "$OUT/check-compiled.txt"
echo "== M2c binary gate (0 lost; gained 0 is expected for a merge)"
$OLD core corpus $P --agree-snapshot "$OUT/agree-old.json" 2>&1 | tail -1
$NEW core corpus $P --binary-gate "$OUT/agree-old.json" > "$OUT/binary-gate.json" 2>"$OUT/binary-gate.err"; tail -1 "$OUT/binary-gate.err"
echo "== M3 browser gates"
cd $R && (timeout 900 python3 server.py 8771 >/dev/null 2>&1 &) && sleep 1
printf 'jsprobe title: '; timeout 120 $NEW page http://127.0.0.1:8771/index.html 2>/dev/null | grep '^meta' | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()[5:]).get("title",""))'
BIN=$NEW sh $R/conn.sh > "$OUT/conn.txt" 2>&1; echo "conn.sh fails=$?"; grep -c '^PASS' "$OUT/conn.txt"
pkill -f "server.py 8771" || true
echo "MERGE-GATE-DONE $OUT"
