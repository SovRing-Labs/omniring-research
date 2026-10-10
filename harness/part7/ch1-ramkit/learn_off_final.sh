#!/usr/bin/env bash
# RAM-KIT-0 runtime OFF gate, final binary (after SHM-BUS B2 + GEM=2): arm B2 = target-ramkit binary + ramkit lib, no switches, 1 day,
# compared with arm A of learn_off_gate.sh (shipped binary + live lib). Pass = identical logs, day records and ckpt.bin.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); R=$HOME/ai-stack/projects/thead-trial/runtime; E=$HOME/ai-stack/projects/thead-trial/engine/omni_train
OUT=$HERE/results/learn_off; export DAYS=1
"$HERE/learn_arm.sh" "$OUT/B2" "$R/target-ramkit/release/omni-render" "$E/libomnitrain_trial_ramkit.so" > "$OUT/B2.log" 2>&1
python3 "$HERE/learn_compare.py" "$OUT/A" "$OUT/B2" > "$OUT/compare_final.json"
python3 -c "import json; d=json.load(open('$OUT/compare_final.json')); r={'B2_final_binary': d['arms'][0]['identical_to_ref'], 'bin_sha': '$(sha256sum $R/target-ramkit/release/omni-render | cut -c1-16)', 'lib_sha': '$(sha256sum $E/libomnitrain_trial_ramkit.so | cut -c1-16)'}; r['pass']=r['B2_final_binary']; print(json.dumps(r)); json.dump(r, open('$OUT/verdict_final.json','w'))"
