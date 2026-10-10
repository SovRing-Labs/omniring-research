#!/bin/bash
# GROW-RUN-0 step 3 gate (board GROW-RUN-0-WIRE) — GROW mode wired into the live school, ONE small local round (laptop, no ssh: school-live.sh
# local): from the frozen growth-base r12 core + its planner state, stage mode (GROW_GATE 1.0) plans, the pod-side scripts compile + train + eval
# HERE (code = this worktree's harness / cloud, data = <home>/ai-stack thead-trial runtime + build-v4), then grow_ctl writes the growth row, keep and
# ledger. Small on purpose (1 harness, 1 day, PAC ε 0.1 → 30 rows) — it gates the WIRING, not learning.
#   g3w_local_round.sh OUT [TRAIN_LIB]      (TRAIN_LIB empty = the CPU engine)
#   POD="IP PORT" g3w_local_round.sh OUT /root/og/lib/libomnitrain_gpu.so   → the same round with compile + training + eval ON the pod (J 10-09:
#   "boot up a pod and have this run on there"); POD_TH threads (default 8); POD_ENV passes the GPU library's environment
set -euo pipefail
OUT=$1; LIB=${2:-}
W=$(cd "$(dirname "$0")/../.." && pwd); D=$HOME/ai-stack/projects/thead-trial; GB=$D/runtime/results/growth-base/r12-elem
rm -rf $OUT; mkdir -p $OUT; cp $GB/school-state-r12.json $OUT/state.json; chmod u+w $OUT/state.json   # growth-base files are read-only; the copy must be writable
(cd $GB && sha256sum -c --quiet MANIFEST.sha256) && echo "== growth-base intact before"
T3=${G3W_TAG:-grow-wire}; rm -rf $D/runtime/results/$T3-r13* /dev/shm/thead-build/$T3-* $D/build-v4/$T3-*   # this gate's own names only
export GROW=1 GROW_GATE=1.0 GROW_EPS=0.1 GROW_KEEP_EVERY=1 GROW_TIER=laptop-wire GROW_RUN=$OUT/grow
export LIVE_TAG=${G3W_TAG:-grow-wire} LIVE_DIR=$OUT THEAD_T=$W THEAD_DATA=$D START_ROUND=13 CORE=$GB GUARD_BASE=$D/runtime/results/live-school/r12 ROUND_DAYS=1 KEEP_CORES=5 TRAIN_LIB=$LIB
t0=$(date +%s)
if [ -n "${POD:-}" ]; then TGT="$POD"; TH=${POD_TH:-8}; else TGT="local -"; TH=4; fi
bash $W/cloud/school-live.sh $TGT 13 ${G3W_NH:-1} $TH 2>&1 | tee $OUT/live.log   # G3W_NH harnesses (8 = one unit through the array server)
echo "== round wall $(( $(date +%s) - t0 )) s"
(cd $GB && sha256sum -c --quiet MANIFEST.sha256) && echo "== growth-base intact after"
python3 - "$OUT" <<'PY'
import json, os, sys
o = sys.argv[1]; r = f"{o}/r13"; ck = {}
up = json.load(open(f"{r}/update.json")); sk = json.load(open(f"{r}/skill.json")); gw = json.load(open(f"{r}/grow.json")); vf = json.load(open(f"{r}/grow-verify.json"))
plan = json.load(open(f"{r}/plan-r13.json"))
ck["plan_stage_mode_frontier"] = len(plan["frontier"]) > 0
ck["skill_json_has_rows"] = bool(sk.get("rows")) and all(isinstance(v, int) for v in sk["rows"].values())
ck["update_has_stage_fields"] = all(k in up for k in ("gate", "min_rows", "at_gate", "stage", "stage_passed", "stages")) and up["gate"] == 1.0 and up["min_rows"] == 30
ck["grow_row_written"] = os.path.exists(f"{o}/grow/growth.jsonl") and gw["round"] == 13 and gw["mode"] in ("skills", "params", "generators")
ck["keep_with_manifest"] = bool(gw.get("keep")) and os.path.exists(os.path.join(gw["keep"], "MANIFEST.sha256"))
ck["ledger_verifies"] = vf["ok"] and vf["rows"] >= 1
row = json.loads(open(f"{o}/grow/growth.jsonl").read().splitlines()[-1])
res = {"checks": ck, "pass": all(ck.values()), "update": up, "grow": gw, "growth_row": row, "skills_scored": len(sk["skill"]),
       "skills_with_30_rows": sum(v >= 30 for v in sk["rows"].values())}
json.dump(res, open(f"{o}/g3w.json", "w"), indent=1); print(json.dumps(res, indent=1)[:3000]); sys.exit(0 if res["pass"] else 1)
PY
echo G3W-DONE
