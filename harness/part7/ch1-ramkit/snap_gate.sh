#!/usr/bin/env bash
# RAM-KIT-0 #13: snapshot to /dev/shm, reload in a fresh process → next-step loss + params bit-identical (plain, and with all memories on).
set -euo pipefail
LIB=$1; HERE=$(cd "$(dirname "$0")" && pwd); OUT=$HERE/results/snap; mkdir -p "$OUT" /dev/shm/thead-snap/ramkit-gate
for m in 0 1; do
  F=/dev/shm/thead-snap/ramkit-gate/snap-m$m.bin
  RK_MEMS=$m python3 "$HERE/ramkit_snap.py" "$LIB" save "$F" 3 > "$OUT/save_m$m.json"
  RK_MEMS=$m python3 "$HERE/ramkit_snap.py" "$LIB" load "$F" 3 > "$OUT/load_m$m.json"
done
python3 - "$OUT" <<'EOF'
import json, os, sys
o = sys.argv[1]; r = {}
for m in (0, 1):
    a, b = (json.load(open(os.path.join(o, f"{k}_m{m}.json"))) for k in ("save", "load"))
    r[f"mems{m}"] = {"bytes": a["bytes"], "loaded": b["bytes"], "next_loss_equal": a["next_loss_bits"] == b["next_loss_bits"], "params_equal": a["sha_after"] == b["sha_after"], "loss": a["next_loss"]}
r["pass"] = all(v["next_loss_equal"] and v["params_equal"] and v["loaded"] > 0 for v in r.values())
json.dump(r, open(os.path.join(o, "verdict.json"), "w"), indent=1); print(json.dumps(r)); sys.exit(0 if r["pass"] else 1)
EOF
rm -f /dev/shm/thead-snap/ramkit-gate/snap-m*.bin
