#!/bin/bash
# T25-REACTOR short tests, one arm after another; each arm hard-stopped at 20 min (J: no test over 20 minutes). Arms: base · head · plates
cd <workspace>/projects/thead-trial/runtime
L=../engine/omni_train/libomnitrain_trial_rx.so
for arm in "$@"; do
  case $arm in
    base)   RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh base ;;
    head)   RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh head LEARN_RING=1 RING_ADDR=../build-v4/ring/ring_addr_t25.json ;;
    plates) RX_LIB=$L timeout 1200 /bin/bash results/rx-run.sh plates PLATES_ATTN=1 ;;
    *) echo "unknown arm $arm"; exit 2 ;;
  esac
  echo "== arm $arm exit $?"
done
echo RX-CHAIN-DONE
