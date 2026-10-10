#!/bin/bash
# T25-REACTOR R3 (J 10-07 accepted: PLATE_PAGE off by default; one more short test): days 3–4 of the t25page and platesfast arms,
# RESUMED from their day-2 checkpoints (copies -d34, same binary + lib as days 1–2 = the arm's own bin/). Question: does t25page's
# canary (3.02 vs platesfast 2.864 vs base 2.605 at day 2) recover while its answer loss holds? Each arm hard-stopped at 20 min (J).
# Plan <notes>/worker/claude/<plan> step A2.   rx-days34.sh [arms…]  (default: platesfast t25page)
set -e
cd <workspace>/projects/thead-trial/runtime
V=../build-v4
export OT_THREADS=4 THEAD_D=256 THEAD_L=6 THEAD_H=4 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 COPY=6
export DO_N=16 DO_REVIEW=4 STUDY_STEPS=5 SLEEP_STEPS=4
export T25_CORE=1 LEARN_MAX_DAYS=4 CKPT_TOKENS=4e4 PLATES_ATTN=1
unset WARM_FROM
arms=${*:-platesfast t25page}; n=0; total=$(echo $arms | wc -w)
for arm in $arms; do
  n=$((n + 1)); echo "@tw step=$n total=$total"
  S=results/rx-$arm; R=results/rx-$arm-d34
  [ -f $S/state.json ] || { echo "no day-2 state in $S"; exit 2; }
  rm -rf $R; cp -a $S $R
  export OMR_TRAIN_LIB=$PWD/$R/bin/libomnitrain_trial_rx5.so
  if [ $arm = t25page ]; then export PLATE_PAGE=1; else unset PLATE_PAGE; fi
  echo "== rx $arm days 3-4 start $(date -Is) PLATE_PAGE=${PLATE_PAGE:-0} bin=$(sha256sum $R/bin/omni-render | cut -c1-12)"
  rc=0; timeout 1200 $R/bin/omni-render thead-learn $V/tier1-prek-v3-s6100 $V/tier1-prek-v3-heldout $V/tier1-prek-v3-doing $R || rc=$?
  echo "== rx $arm days 3-4 exit $rc $(date -Is)"
done
echo RX-DAYS34-DONE
