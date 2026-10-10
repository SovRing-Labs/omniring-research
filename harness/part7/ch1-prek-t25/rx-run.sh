#!/bin/bash
# T25-REACTOR short tests (J 2026-10-07: "do a few SHORT 1-3 day tests and implement the improvements"; scope = the four reactor
# programs: vocab head on the T25 token rings · attention plates · integer backward · provenance + direction). One arm = a FRESH
# T25 model, 3 pre-K days on the same curriculum seed (tier1-prek-v3-s6100) with the school settings, held-out every day.
# Hard cap 20 min (J): launch inside `systemd-run … -p RuntimeMaxSec=1200`.   rx-run.sh <arm> [ENV=VAL …]
set -e
cd <workspace>/projects/thead-trial/runtime
arm=$1; shift; for kv in "$@"; do export "$kv"; done
V=../build-v4
export OT_THREADS=4 THEAD_D=256 THEAD_L=6 THEAD_H=4 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 COPY=6
# light day so 2 days fit the 20-min cap on a shared box (same for every arm): study 5, sleep 4, doing 16 + 4 review
export DO_N=16 DO_REVIEW=4 STUDY_STEPS=5 SLEEP_STEPS=4
export T25_CORE=1 LEARN_MAX_DAYS=${LEARN_MAX_DAYS:-2} CKPT_TOKENS=4e4
unset WARM_FROM
R=results/rx-$arm; rm -rf $R; mkdir -p $R/bin
cp target/release/omni-render ${RX_LIB:-../engine/omni_train/libomnitrain_trial.so} $R/bin/
export OMR_TRAIN_LIB=$PWD/$R/bin/$(basename ${RX_LIB:-libomnitrain_trial.so})
echo "@tw step=1 total=1"
echo "== rx $arm start $(date -Is) env: $*"
$R/bin/omni-render thead-learn $V/tier1-prek-v3-s6100 $V/tier1-prek-v3-heldout $V/tier1-prek-v3-doing $R
echo "== rx $arm done $(date -Is)"
echo RX-DONE
