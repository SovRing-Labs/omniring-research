#!/bin/bash
# GROW-RUN-0 G6 — THE GROWTH RUN on the A40 (48 GB tier; J 10-09: "run the real growth round"). 40 harnesses, each its own model, training in
# 2 resident array sessions × 20 (omni-gpu serve), decode + held-out eval on the GPU, from the frozen r12 core; stage mode (GROW_GATE 1.0, PAC
# 300 rows per skill), grow_ctl every round (growth-rate rows, keeps, hash-chained ledger), auto curriculum each round. Stops itself at a WALL
# after middle school (parameter growth = G4, not built) or at ROUNDS. Orchestrator on the laptop, everything else on the pod.
#   run_a40.sh RUN_DIR [IP PORT] [ROUNDS=40] [NH=40]
set -euo pipefail
OUT=$1; IP=${2:-<pod-ip>}; PORT=${3:-22071}; ROUNDS=${4:-40}; NH=${5:-40}
W=$(cd "$(dirname "$0")/../.." && pwd); D=$HOME/ai-stack/projects/thead-trial; GB=$D/runtime/results/growth-base/r12-elem
mkdir -p $OUT; [ -f $OUT/state.json ] || { cp $GB/school-state-r12.json $OUT/state.json; chmod u+w $OUT/state.json; }
(cd $GB && sha256sum -c --quiet MANIFEST.sha256) && echo "== growth-base intact"
export GROW=1 GROW_GATE=1.0 GROW_TIER=a40-48gb GROW_RUN=$OUT/grow LIVE_TAG=grow-a40 LIVE_DIR=$OUT THEAD_T=$W THEAD_DATA=$D
export START_ROUND=${START_ROUND:-13} CORE=${CORE:-$GB} GUARD_BASE=$D/runtime/results/live-school/r12 KEEP_CORES=2
export TRAIN_LIB=/root/og/lib/libomnitrain_gpu.so SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
export POD_ENV="OMNI_GPU_ROOT=/root/og/projects/omni-gpu OMNI_GPU_DEVICE=A40 ARRAY_SERVER=1 ARRAY_MAX_SLOTS=20 PAR_TIMEOUT=3600"
exec bash $W/cloud/school-live.sh $IP $PORT $ROUNDS $NH 1
