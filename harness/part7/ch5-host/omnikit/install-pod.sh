#!/bin/bash
# omnikit install — runs ON a pod (or any x86-64 box): build omni-ring kernels natively (AVX2 always, AVX-512 when the CPU has
# avx512f/bw/vl/vpopcntdq/vnni), run the package tests, register the omnikit cores in cores.db (+ shard.search via ramkit when its
# snapshot is present), then the selftest (one PASS/FAIL line per core). the training pod: everything at nice 19 on the LAST 4 cpus of
# this process's affinity list (pod cpu ids are scattered host ids — never a fixed range), OMP_NUM_THREADS=4. Never touches corehostd.
#   install-pod.sh [--no-tests] [--no-register]
# Stops at the first error (PROCEDURES § When building and measuring); build logs in $LOG.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
AI=${CH_AI:-$(cd "$HERE/../../.." && pwd)}
PKG=$AI/packages/omni-ring
LOG=${OMNIKIT_LOG:-$HERE/install-logs/$(date -u +%Y%m%dT%H%M%SZ)}
TESTS=1; REGISTER=1
for a in "$@"; do case $a in --no-tests) TESTS=0;; --no-register) REGISTER=0;; *) echo "unknown arg $a"; exit 2;; esac; done
mkdir -p "$LOG"
CPUS=${OMNIKIT_CPUS:-$(python3 -c "import os; print(','.join(map(str, sorted(os.sched_getaffinity(0))[-4:])))")}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
RUN="nice -n 19 taskset -c $CPUS"
echo "omnikit: AI=$AI cpus=$CPUS omp=$OMP_NUM_THREADS log=$LOG"

# 1/5 kernels (rename-not-overwrite inside the build scripts)
$RUN sh "$PKG/build_kernel.sh" > "$LOG/build-avx2.log" 2>&1 || { cat "$LOG/build-avx2.log"; exit 1; }
echo "1/5 AVX2 kernel built"
if python3 -c "import sys; sys.path.insert(0,'$PKG'); from omni_ring.sift import cpu_has_avx512; sys.exit(0 if cpu_has_avx512() else 1)"; then
  $RUN sh "$PKG/build_kernel_avx512.sh" > "$LOG/build-avx512.log" 2>&1 || { cat "$LOG/build-avx512.log"; exit 1; }
  python3 -c "import sys; sys.path.insert(0,'$PKG'); from omni_ring import sift; sys.exit(0 if sift.has_avx512() else 1)" \
    || { echo "AVX-512 lib built but did not load"; exit 1; }
  echo "1/5 AVX-512 kernel built + loaded (backend auto = avx512)"
else
  echo "1/5 CPU has no AVX-512 (avx512f/bw/vl/vpopcntdq/vnni) — AVX2 only"
fi

# 2/5 package tests (pytest if present or installable, else the pytest-free kernel tests)
if [ $TESTS = 1 ]; then
  python3 -c "import pytest" 2>/dev/null || pip install -q pytest --break-system-packages > "$LOG/pip.log" 2>&1 || true
  if python3 -c "import pytest" 2>/dev/null; then
    (cd "$PKG" && $RUN timeout 1200 python3 -m pytest -q -p no:cacheprovider tests > "$LOG/pytest.log" 2>&1) \
      || { tail -30 "$LOG/pytest.log"; exit 1; }
    echo "2/5 package tests: $(tail -1 "$LOG/pytest.log")"
  else
    (cd "$PKG" && $RUN timeout 600 python3 tests/test_avx512.py > "$LOG/test_avx512.log" 2>&1) || { cat "$LOG/test_avx512.log"; exit 1; }
    echo "2/5 no pytest — kernel tests only: $(grep -c ^PASS "$LOG/test_avx512.log") PASS"
  fi
else
  echo "2/5 tests skipped (--no-tests)"
fi

# 3/5 registry rows (corehostd reads cores.db live — no restart)
if [ $REGISTER = 1 ]; then
  [ -f "${CORES_DB:-$AI/control-center/cores.db}" ] || (cd "$AI" && bin/core-registry init > /dev/null)
  python3 "$HERE/seed_omnikit.py"
  echo "3/5 omnikit cores registered"
  # 4/5 shard.search: owned by ramkit (#12) — register it only through its own script, only when its snapshot is here
  SS=$AI/projects/thead-trial/ramkit/shard_search.py
  if [ -f "$SS" ] && [ -f "$AI/data/shards/pod-snap/MANIFEST.json" ]; then python3 "$SS" register > /dev/null && echo "4/5 shard.search registered (ramkit)";
  else echo "4/5 shard.search skipped (ramkit/shard_search.py or data/shards/pod-snap missing)"; fi
else
  echo "3-4/5 registry skipped (--no-register)"
fi

# 5/5 selftest
$RUN bash "$HERE/selftest.sh" | tee "$LOG/selftest.log"
echo "5/5 omnikit selftest done — log $LOG"
