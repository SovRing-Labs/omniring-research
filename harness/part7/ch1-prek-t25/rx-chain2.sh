#!/bin/bash
# T25-REACTOR short tests, second chain (1 day each, compared with the other arms at day 1; each hard-stopped at 20 min): fields · intbwd
cd <workspace>/projects/thead-trial/runtime
L=../engine/omni_train/libomnitrain_trial_rx3.so
for arm in "$@"; do
  case $arm in
    fields) LEARN_MAX_DAYS=1 RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh fields T25_FIELDS=1 ;;
    intbwd) LEARN_MAX_DAYS=1 RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh intbwd INT_BWD=1 OPT_MODE=1 ;;
    intbwd0) LEARN_MAX_DAYS=1 RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh intbwd0 INT_BWD=1 ;;
    *) echo "unknown arm $arm"; exit 2 ;;
  esac
  echo "== arm $arm exit $?"
done
echo RX-CHAIN2-DONE
