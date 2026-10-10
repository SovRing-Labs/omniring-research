#!/usr/bin/env bash
# RAM-KIT-0 #1 gate: (a) grads LUT5_BWD on vs off on one batch (error, cosine, bit-identity); (b) 6 real steps per arm, one arm per process,
# 4 threads: loss bits + params sha (bit-identical?), bl_bwd_dx seconds (engine prof[3]) and wall seconds. Usage: lut5bwd_gate.sh <lib> [steps] [thr]
set -euo pipefail
LIB=$1; STEPS=${2:-6}; THR=${3:-4}
HERE=$(cd "$(dirname "$0")" && pwd); OUT=$HERE/results/lut5bwd; mkdir -p "$OUT"
python3 "$HERE/ramkit_lut5bwd.py" "$LIB" "$THR" > "$OUT/grads.json"
for rep in 1 2; do
  RK_LUT5BWD=0 python3 "$HERE/ramkit_gate.py" "$LIB" "$STEPS" "$THR" > "$OUT/off_$rep.json"
  RK_LUT5BWD=1 python3 "$HERE/ramkit_gate.py" "$LIB" "$STEPS" "$THR" > "$OUT/on_$rep.json"
done
python3 - "$OUT" <<'EOF'
import json, os, sys
o = sys.argv[1]; L = lambda f: json.load(open(os.path.join(o, f)))
g = L("grads.json"); off = [L(f"off_{r}.json") for r in (1, 2)]; on = [L(f"on_{r}.json") for r in (1, 2)]
dx = lambda a: min(x["prof_s"]["bl_bwd_dx"] for x in a); wall = lambda a: min(x["seconds"] for x in a)
r = {"grads_bit_identical": g["bit_identical_grads"], "grads_worst_max_rel": g["worst_max_rel"], "grads_min_cos": g["min_cos"],
     "losses_bit_identical": off[0]["losses"] == on[0]["losses"], "params_bit_identical": off[0]["params_sha256"] == on[0]["params_sha256"],
     "loss_off": off[0]["loss_values"], "loss_on": on[0]["loss_values"],
     "bl_bwd_dx_s": {"off": dx(off), "on": dx(on)}, "wall_s": {"off": wall(off), "on": wall(on)}}
r["bl_bwd_dx_speedup"] = r["bl_bwd_dx_s"]["off"] / max(r["bl_bwd_dx_s"]["on"], 1e-9); r["step_speedup"] = r["wall_s"]["off"] / r["wall_s"]["on"]
r["default_on_allowed"] = r["losses_bit_identical"] and r["params_bit_identical"]
json.dump(r, open(os.path.join(o, "verdict.json"), "w"), indent=1); print(json.dumps(r))
EOF
