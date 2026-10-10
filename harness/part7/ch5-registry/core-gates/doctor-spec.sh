#!/usr/bin/env bash
# gate for core doctor.spec (core-registry, contract §5): the A-B-C e-graph probe must PASS. Last stdout line = the summary.
set -euo pipefail
B="${DOCTOR_BIN:?DOCTOR_BIN}"
out=$("$B" core --abc probe 2>&1)
echo "$out" | grep -x 'abc probe: PASS'
