#!/bin/bash
# omnikit selftest — one PASS/FAIL line per core (gate + registry fire + corehostd fire when up). Exit 0 = all PASS.
# Also checks shard.search (owned by ramkit/shard_search.py) when it is registered. Args pass through to selftest.py.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
AI=${CH_AI:-$(cd "$HERE/../../.." && pwd)}
rc=0
python3 "$HERE/selftest.py" "$@" || rc=1
DB=${CORES_DB:-$AI/control-center/cores.db}
SS=$(python3 -c "import sqlite3,sys;r=sqlite3.connect('$DB').execute(\"select gate from cores where core='shard.search'\").fetchone();print(r[0] if r else '')" 2>/dev/null)
if [ -n "$SS" ]; then
  if out=$(cd "$AI" && timeout 300 bash -c "$SS" 2>&1); then echo "PASS shard.search · gate ok (ramkit)"; else echo "FAIL shard.search · $(echo "$out" | tail -1)"; rc=1; fi
else
  echo "SKIP shard.search · not registered (ramkit/shard_search.py register, needs data/shards/pod-snap)"
fi
exit $rc
