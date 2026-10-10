#!/bin/bash
# School-end idle window (J 10-08 approved): with NO training on the pod, (1) native vs shipped engine lib (m2_ab, 6 steps × 4 threads),
# (2) omnikit sift bench at 1/4/8 threads. Same probes as under load, now clean.
set -euo pipefail
echo "training procs: $(ps -eo args | grep -v grep | grep -c 'omni-render thead-learn' || true) · load $(cut -d' ' -f1-3 /proc/loadavg)"
CP=$(python3 -c "import os; print(','.join(map(str, sorted(os.sched_getaffinity(0))[:8])))")
cd /root/ai-stack/projects/thead-trial/engine/omni_train
for L in $PWD/libomnitrain_trial.so /root/libomnitrain_native.so; do
  taskset -c $CP timeout 300 python3 <workspace>/<notes>/GPU-RUN/lut5/m2_ab.py $L 6 4 > /root/idle-$(basename $L .so).json 2>&1
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1], json.dumps({k: d[k] for k in ('bl_fwd_s_median','step_wall_s_median','pass')}))" /root/idle-$(basename $L .so).json
done
cd /root/ai-stack/projects/thead-trial/omnikit
for t in 1 4 8; do OMP_NUM_THREADS=$t taskset -c $CP timeout 600 python3 bench_sift.py --out results/bench-pod-idle-t$t.json 2>&1 | tail -4; done
echo IDLE-WINDOW-DONE
