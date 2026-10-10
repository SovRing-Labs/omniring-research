#!/bin/bash
# CYCLONE-ARRAY pod rungs with routing (W3), POD side: G40 with every model's training state + routing, G40 wiring speed, G120 (3 floors,
# 120 models, full real weight slabs; its full training state needs 64.6 GB = an 80 GB card) — each the deployable's preset, gated by rung.py.
set -euo pipefail
DEV=${1:-L4}; R=/root/cyclone; H=$R/omni-gpu/tests/cyclone
export CYCLONE_THEAD=$R/thead CYCLONE_RESULTS=$R/results CYCLONE_CORE=$R/core
echo "@tw step=1 total=3 G40 full state + routing"; python3 $H/rung.py G40 --device $DEV --slab full --full-state
echo "@tw step=2 total=3 G40 wiring + routing";     python3 $H/rung.py G40 --device $DEV --slab full
echo "@tw step=3 total=3 G120 3 floors full slabs"; python3 $H/rung.py G120 --device $DEV --slab full
echo POD-RUNGS-ROUTE-DONE
