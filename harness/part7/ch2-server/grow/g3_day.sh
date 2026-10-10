#!/bin/bash
# GROW-RUN-0 G3 gate 2 — ONE SCHOOL DAY through thead-learn (the harness, unchanged) with the GPU engine library vs the CPU engine: same
# binary, same builds (elementary-v1 + heldout + doing), same school env (cloud/school-round.sh) — a small model (THEAD_D 64, L 4, H 2) so the
# day fits the laptop. Compares the runs' state.json (held-out, losses, day metrics).   g3_day.sh OUT [DEVICE]
set -euo pipefail
OUT=$1; DEV=${2:-Intel}; TT=<workspace>/projects/thead-trial; OG=<projects>/ai-stack-opus-gpu/projects/omni-gpu
BIN=$TT/runtime/target/release/omni-render; B=$TT/build-v4/elementary-v1; HO=$TT/build-v4/elementary-v1-heldout; DO=$TT/build-v4/elementary-v1-doing
mkdir -p $OUT/lib; cp $OG/engine-gpu/target/release/libomnitrain_gpu.so $OUT/lib/; cp $TT/engine/omni_train/libomnitrain_trial.so $OUT/lib/
export THEAD_D=64 THEAD_L=4 THEAD_H=2 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
export T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=1 OT_THREADS=4 OMNI_GPU_DEVICE=$DEV OMNI_GPU_ROOT=$OG TMPDIR=$OUT
unset PLATE_PAGE ARC_AMP
cd $TT/runtime
echo "== CPU engine day"; t0=$(date +%s); OMR_TRAIN_LIB=$OUT/lib/libomnitrain_trial.so timeout 3000 $BIN thead-learn $B $HO $DO $OUT/cpu > $OUT/cpu.log 2>&1; echo "cpu day $(( $(date +%s) - t0 )) s"
echo "== GPU engine library day"; t0=$(date +%s); OMR_TRAIN_LIB=$OUT/lib/libomnitrain_gpu.so timeout 3000 $BIN thead-learn $B $HO $DO $OUT/gpu > $OUT/gpu.log 2>&1; echo "gpu day $(( $(date +%s) - t0 )) s"
grep -h "omnitrain_gpu" $OUT/gpu.log | head -5
python3 - "$OUT" <<'PY'
import json, sys
o = sys.argv[1]; r = {}
for k in ("cpu", "gpu"):
    st = json.load(open(f"{o}/{k}/state.json")); r[k] = st
keys = sorted(set(r["cpu"]) & set(r["gpu"]))
print(json.dumps({k: [r["cpu"][k], r["gpu"][k]] for k in keys if isinstance(r["cpu"][k], (int, float, str))}, indent=0)[:3000])
PY
echo G3-DAY-DONE
