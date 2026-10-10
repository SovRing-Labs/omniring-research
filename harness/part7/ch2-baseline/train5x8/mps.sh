#!/bin/bash
# TRAIN-5x8 probe 1 (J 10-08 "why is it single threaded and serialized instead of parallel?"): the same runs with NVIDIA MPS on, so the
# harness processes' CUDA work shares the GPU concurrently instead of time-slicing between 40 contexts. No code change.
set -uo pipefail
D=$(cd "$(dirname "$0")" && pwd)
export CUDA_MPS_PIPE_DIRECTORY=/tmp/mps-pipe CUDA_MPS_LOG_DIRECTORY=/tmp/mps-log; mkdir -p $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
nvidia-cuda-mps-control -d && echo "MPS daemon up"
for spec in "8 4 gpu unit8-gpu-mps" "40 1 gpu layout5x8-gpu-mps"; do set -- $spec; bash $D/run.sh $1 $2 $3 $4 2>&1 | tail -3; done
echo quit | nvidia-cuda-mps-control; echo "MPS daemon down"
echo MPS-DONE
