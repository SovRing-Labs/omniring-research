#!/bin/bash
# Probe (RAM-KIT-0 / omnitech brainstorm, 10-08): does compiling the training engine ON the pod (-march=native → AVX-512 on EPYC 9575F)
# beat the laptop-built AVX2 lib? Same source (the kit's omni_train.cpp), same probe (<notes>/GPU-RUN/lut5/m2_ab.py 6 steps, 4 threads), nice 19.
set -euo pipefail
cd /root/ai-stack/projects/thead-trial/engine/omni_train
echo "src $(sha256sum omni_train.cpp | cut -c1-12) · shipped lib $(sha256sum libomnitrain_trial.so | cut -c1-12)"
[ -f /root/libomnitrain_native.so ] || nice -n 19 g++ -O3 -march=native -fopenmp -shared -fPIC -std=c++17 -o /root/libomnitrain_native.so omni_train.cpp
for L in $PWD/libomnitrain_trial.so /root/libomnitrain_native.so; do
  echo "== $L"; nice -n 19 timeout 300 python3 <workspace>/<notes>/GPU-RUN/lut5/m2_ab.py $L 6 4 > /root/probe-$(basename $L .so).json 2>&1; python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(json.dumps({k: d[k] for k in (\"loss_bit_identical\", \"params_differing\", \"bl_fwd_s_median\", \"step_wall_s_median\", \"step_speedup\", \"pass\")}))" /root/probe-$(basename $L .so).json
done
echo PROBE-DONE
