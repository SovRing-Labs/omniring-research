#!/bin/bash
# CYCLONE-ARRAY local ladder (J 10-08: "get the layout and wiring first … local", no pod): every rung that fits this laptop, on both devices.
# G1 / G4 / G8 with FULL real weight slabs, G40 (one floor, ring, routing) with the first 1,048,576 floats of each slab, G1 with its full
# measured training state, G120 (3 floors, routing across floors) with 262,144-float slabs. Stops at the first failing rung (set -e); each rung writes results/cyclone/<rung>/<tag>.json.
set -euo pipefail
H=$(cd "$(dirname "$0")" && pwd)
for dev in llvmpipe Intel; do
  for r in G1 G4 G8; do python3 $H/rung.py $r --device $dev --slab full; done
  python3 $H/rung.py G40 --device $dev --slab 1048576
  python3 $H/rung.py G1 --device $dev --slab full --full-state
  python3 $H/rung.py G120 --device $dev --slab 262144
done
echo RUNGS-LOCAL-DONE
