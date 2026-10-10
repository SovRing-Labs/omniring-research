#!/usr/bin/env bash
# RAM-KIT-0 runtime OFF gate: thead-learn, 1 day, school env, same seed — (A) shipped binary target/release/omni-render + live lib,
# (B) the ramkit binary + ramkit lib, no switches, (C) ramkit binary + lib with the observers on (ROW_MAP=1, SNAP_EVERY=5): state.json logs,
# day records and ckpt.bin must be identical (C may only ADD its ramkit day field + row_map.bin / snapshots).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); R=$HOME/ai-stack/projects/thead-trial/runtime; E=$HOME/ai-stack/projects/thead-trial/engine/omni_train
OUT=$HERE/results/learn_off; mkdir -p "$OUT"; export DAYS=${DAYS:-1}
"$HERE/learn_arm.sh" "$OUT/A" "$R/target/release/omni-render" "$E/libomnitrain_trial.so" > "$OUT/A.log" 2>&1 &
"$HERE/learn_arm.sh" "$OUT/B" "$R/target-ramkit/release/omni-render" "$E/libomnitrain_trial_ramkit.so" > "$OUT/B.log" 2>&1 &
wait
"$HERE/learn_arm.sh" "$OUT/C" "$R/target-ramkit/release/omni-render" "$E/libomnitrain_trial_ramkit.so" ROW_MAP=1 SNAP_EVERY=5 SNAP_DIR=/dev/shm/thead-snap/ramkit-offC > "$OUT/C.log" 2>&1
ls /dev/shm/thead-snap/ramkit-offC > "$OUT/C.snaps.txt"; rm -rf /dev/shm/thead-snap/ramkit-offC
python3 "$HERE/learn_compare.py" "$OUT/A" "$OUT/B" "$OUT/C" > "$OUT/compare.json"
python3 -c "import json; d=json.load(open('$OUT/compare.json')); r={a['dir'].split('/')[-1]: a['identical_to_ref'] for a in d['arms']}; r['pass']=all(r.values()); print(json.dumps(r)); json.dump(r, open('$OUT/verdict.json','w'))"
