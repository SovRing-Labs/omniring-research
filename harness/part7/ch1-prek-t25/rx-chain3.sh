#!/bin/bash
# T25-REACTOR round 2 (J 10-07 "down the list, ensure 1 and 2 are compatible"): plates with the fast row-block kernel · plates paged by the
# T25 core (PLATE_PAGE) · integer backward WITHOUT flip counters. Each arm hard-stopped at 20 min (J).
cd <workspace>/projects/thead-trial/runtime
L=../engine/omni_train/libomnitrain_trial_rx5.so
for arm in "$@"; do
  case $arm in
    platesfast) RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh platesfast PLATES_ATTN=1 ;;
    t25page)    RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh t25page PLATES_ATTN=1 PLATE_PAGE=1 ;;
    intbwd0)    LEARN_MAX_DAYS=1 RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh intbwd0 INT_BWD=1 ;;
    *) echo "unknown arm $arm"; exit 2 ;;
  esac
  echo "== arm $arm exit $?"
done
echo RX-CHAIN3-DONE
