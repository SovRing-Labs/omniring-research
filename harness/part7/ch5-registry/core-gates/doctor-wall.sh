#!/usr/bin/env bash
# gate for core doctor.wall: clean types0 layout specs + --seed-leaks → every seeded leak refused (refused == tried > 0).
set -euo pipefail
B="${DOCTOR_BIN:?DOCTOR_BIN}"; T="${CORE_TMP:?CORE_TMP}"
TREE=$(dirname "$(dirname "$(dirname "$B")")")       # …/target/release/omni-render → source tree (src/layout.rs)
R=<workspace>/projects/omni-render/results/doctor-interp
"$B" core --abc wall --specs "$R/types0/specs.layout.jsonl" --src "$TREE/src/layout.rs" --out "$T/w.jsonl" --seed-leaks 2>/dev/null > "$T/wall.json"
python3 -I - "$T/wall.json" <<'P'
import json, sys
j = json.load(open(sys.argv[1])); s = j["seeded"]
print(f"wall: passed {j['passed']}/{j['rows']}, seeded {s['refused']}/{s['tried']} refused")
sys.exit(0 if s["tried"] > 0 and s["refused"] == s["tried"] else 1)
P
