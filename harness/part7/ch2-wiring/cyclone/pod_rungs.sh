#!/bin/bash
# CYCLONE-ARRAY pod rungs, POD side (started by pod_ship.sh under tritwatch on the pod). Every rung at FULL size: real weight slabs
# (6,926,912 floats per model) + every model's measured training state allocated (--full-state), then G40's wiring speed without the state.
# Each rung is the deployable's preset (omni-gpu cyclone) checked by rung.py; stops at the first failing rung.   pod_rungs.sh DEVICE
set -euo pipefail
DEV=${1:-L4}; R=/root/cyclone; H=$R/omni-gpu/tests/cyclone
export CYCLONE_THEAD=$R/thead CYCLONE_RESULTS=$R/results CYCLONE_CORE=$R/core
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
i=0; for r in G1 G4 G8 G40; do i=$((i + 1)); echo "@tw step=$i total=5 rung $r"; python3 $H/rung.py $r --device $DEV --slab full --full-state; done
echo "@tw step=5 total=5 rung G40 (no state)"
python3 $H/rung.py G40 --device $DEV --slab full
echo POD-RUNGS-DONE
