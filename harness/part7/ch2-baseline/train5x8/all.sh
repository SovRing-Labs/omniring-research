#!/bin/bash
# TRAIN-5x8 driver ON THE POD (J 10-08): single harness → one unit (8) → the 5×8 layout (40), CPU lib vs GPU lib, one school day each.
set -uo pipefail
D=$(cd "$(dirname "$0")" && pwd)
for spec in "1 4 cpu one-cpu" "1 4 gpu one-gpu" "8 4 cpu unit8-cpu" "8 4 gpu unit8-gpu" "40 1 gpu layout5x8-gpu" "40 1 cpu layout5x8-cpu"; do
  set -- $spec; bash $D/run.sh $1 $2 $3 $4 2>&1 | tail -3
done
echo ALL-DONE
