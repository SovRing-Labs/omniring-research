#!/usr/bin/env bash
# gate for core doctor.blackbox: probe the N5 driver's gcd (no source) → one spec row written, every probe defined.
set -euo pipefail
B="${DOCTOR_BIN:?DOCTOR_BIN}"; T="${CORE_TMP:?CORE_TMP}"
DRV=<workspace>/projects/omni-render/results/doctor-interp/n5/driver/target/release/bbdriver
"$B" core --abc blackbox --cmd "$DRV" --fn gcd --args int,int --out "$T/bb.jsonl" 2>"$T/bb.log"
python3 -I - "$T/bb.jsonl" "$T/bb.log" <<'P'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
ok = len(rows) == 1 and rows[0].get("need", "").startswith("s") and len(rows[0].get("examples", [])) == 8
print(open(sys.argv[2]).read().strip().splitlines()[-1] if ok else f"blackbox: {len(rows)} spec rows")
sys.exit(0 if ok else 1)
P
