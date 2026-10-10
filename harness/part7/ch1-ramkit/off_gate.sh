#!/usr/bin/env bash
# RAM-KIT-0 OFF gate: the ramkit lib with every new switch off (and once with every setter CALLED with its off value) == the live lib,
# bit-identical (loss bits, forward loss, sha256 over every parameter). Arms one per process. Usage: off_gate.sh <new lib> [steps] [threads]
set -euo pipefail
NEW=$1; STEPS=${2:-3}; THR=${3:-4}
HERE=$(cd "$(dirname "$0")" && pwd); OLD=$HOME/ai-stack/projects/thead-trial/engine/omni_train/libomnitrain_trial.so
OUT=$HERE/results/off_gate; mkdir -p "$OUT"
M2=$HOME/ai-stack/<notes>/GPU-RUN/lut5/m2_learn_ab.py
python3 "$M2" "$OLD" 1 "$STEPS" "$THR" > "$OUT/m2_old.json"
python3 "$M2" "$NEW" 1 "$STEPS" "$THR" > "$OUT/m2_new.json"
RK_P3=1 python3 "$HERE/ramkit_gate.py" "$OLD" "$STEPS" "$THR" > "$OUT/p3_old.json"
RK_P3=1 RK_CALL_OFF=1 python3 "$HERE/ramkit_gate.py" "$NEW" "$STEPS" "$THR" > "$OUT/p3_new_calloff.json"
python3 - "$OUT" <<'EOF'
import json, sys, os
o = sys.argv[1]; L = lambda f: json.load(open(os.path.join(o, f)))
keys = ["losses", "forward_loss", "params_sha256", "nparams"]
r = {}
for a, b, tag in [("m2_old.json", "m2_new.json", "m2_learn_ab"), ("p3_old.json", "p3_new_calloff.json", "p3_calloff")]:
    A, B = L(a), L(b); r[tag] = {k: A[k] == B[k] for k in keys}; r[tag]["pass"] = all(r[tag].values())
r["pass"] = all(v["pass"] for v in r.values() if isinstance(v, dict))
json.dump(r, open(os.path.join(o, "verdict.json"), "w"), indent=1); print(json.dumps(r))
sys.exit(0 if r["pass"] else 1)
EOF
