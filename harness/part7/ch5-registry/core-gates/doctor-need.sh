#!/usr/bin/env bash
# gate for core doctor.need: emit on sketch0 walled specs → every need built and rustc-verified (10/10).
set -euo pipefail
B="${DOCTOR_BIN:?DOCTOR_BIN}"; T="${CORE_TMP:?CORE_TMP}"
R=<workspace>/projects/omni-render/results/doctor-interp
"$B" core --abc need --needs "$R/sketch0/specs.wall.jsonl" --emit --build-dir "$T/b" --out "$T/n.jsonl" >/dev/null 2>"$T/need.log"
python3 -I - "$T/n.jsonl" <<'P'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
ok = sum(1 for r in rows if (r.get("built") or {}).get("verified") is True)
print(f"need: {ok}/{len(rows)} verified")
sys.exit(0 if rows and ok == len(rows) else 1)
P
