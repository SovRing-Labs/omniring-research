#!/usr/bin/env bash
# RAM-KIT-0 laptop A/B (#4 ring memory, #5 episodic memory, #9 A-GEM) vs off: one arm per process, same seed and env (learn_arm.sh, school
# env, pre-K v4 s6400, warm from the laptop ladder end), DAYS days each (≤ 20 min, learn_arm's timeout), two arms at a time × 4 threads.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); R=$HOME/ai-stack/projects/thead-trial/runtime; E=$HOME/ai-stack/projects/thead-trial/engine/omni_train
BIN=$R/target-ramkit/release/omni-render; LIB=$E/libomnitrain_trial_ramkit.so; OUT=$HERE/results/ab; mkdir -p "$OUT"; export DAYS=${DAYS:-2}
"$HERE/learn_arm.sh" "$OUT/off" "$BIN" "$LIB" > "$OUT/off.log" 2>&1 &
"$HERE/learn_arm.sh" "$OUT/ring" "$BIN" "$LIB" RING_MEM=65536 > "$OUT/ring.log" 2>&1 &
wait
"$HERE/learn_arm.sh" "$OUT/epi" "$BIN" "$LIB" EPI_MEM=2048 > "$OUT/epi.log" 2>&1 &
"$HERE/learn_arm.sh" "$OUT/gem" "$BIN" "$LIB" GEM=2 > "$OUT/gem.log" 2>&1 &
wait
python3 "$HERE/learn_compare.py" "$OUT/off" "$OUT/ring" "$OUT/epi" "$OUT/gem" > "$OUT/compare.json"
python3 -c "
import json; d=json.load(open('$OUT/compare.json')); f=lambda a: [(e['step'], round(e['heldout_loss_port'],4), round(e['canary'],4)) for e in a['log']]
r={'off': f(d['ref'])}; r.update({a['dir'].split('/')[-1]: {'log': f(a), 'heldout_delta_last': round(a['heldout_delta_last'],4), 'canary_delta_last': round(a['canary_delta_last'],4)} for a in d['arms']})
print(json.dumps(r)); json.dump(r, open('$OUT/verdict.json','w'), indent=1)"
