#!/bin/bash
# THEAD T25 school on the cloud pod — LADDER CHAIN (J 10-07; plan T25-REACTOR-R3 § F). Measured on the pod 10-08: 1,800 tok/s vs the
# laptop's 134 (EPYC 4564P, 16 vCPU, no other load) → one full pre-K ladder (146 steps, 5 passes) takes minutes, not hours. So the run
# CHAINS ladders: each ladder is a fresh run on the next precompiled row seed, warm-started from the ladder before (the spiral again on
# new rows), then eval + copy gate. Stops when the gate passes, the seeds run out, or the time budget (TOTAL_SECS, default 3 h) is spent.
#   bash school-cloud-loop.sh [PREV_RUN=results/school-t25-prek-cloud1] [TOTAL_SECS=10800]
set -e
cd "$HOME/ai-stack/projects/thead-trial/runtime"
H1=../harness; PREV=${1:-results/school-t25-prek-cloud1}; TOTAL=${2:-10800}; T0=$(date +%s)
HO=../build-v4/tier1-prek-v4-heldout; DO=../build-v4/tier1-prek-v4-doing
SEEDS=${SEEDS:-"6500 6600 6700 6800 6900 7000 7100 7200 7300 7400 7500 7600"}
export OT_THREADS=${OT_THREADS:-$(nproc)} THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
export T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=0
unset PLATE_PAGE ARC_AMP
LIB=$PWD/../engine/omni_train/libomnitrain_trial.so; BIN=$PWD/target/release/omni-render; export OMR_TRAIN_LIB=$LIB
[ -f $PREV/ckpt.bin ] || { echo "no checkpoint in $PREV"; exit 2; }
echo "== chain from $PREV · seeds $SEEDS · budget ${TOTAL}s · $(nproc) cpus · OT_THREADS=$OT_THREADS · bin $(sha256sum $BIN | cut -c1-12) · lib $(sha256sum $LIB | cut -c1-12)"
for s in $SEEDS; do
  left=$((TOTAL - ($(date +%s) - T0))); [ $left -gt 120 ] || { echo "== budget spent"; break; }
  B=../build-v4/${BUILD:-tier1-prek-v4}-s$s; R=results/school-t25-${TAG:-prek}-cloud-s$s     # BUILD=tier1-prek-v5 TAG=prek5: the 5× curriculum
  [ -d $B ] || { echo "no build $B"; continue; }
  rm -rf $R; mkdir -p $R; export WARM_FROM=$PREV
  echo "== ladder seed $s start $(date -Is) · warm $PREV · ${left}s left"
  rc=0; timeout $left $BIN thead-learn $B $HO $DO $R || rc=$?
  python3 -c "import json; s=json.load(open('$R/state.json')); d=s['days']; print('   days', len(d), '· step', s.get('step'), '· day s', [round(sum(x.get('seconds', {}).values())) for x in d]); print('   held-out / canary', [(e['day'], round(e['heldout_loss_port'], 3), round(e['canary'], 3)) for e in s['log'] if e.get('day')][-2:])"
  OMNI_TRAIN_LIB=$LIB python3 $H1/tier1_eval.py $PWD/$R | cut -c1-200
  echo "== ladder seed $s exit $rc $(date -Is)"
  [ -f $R/ckpt.bin ] && PREV=$R
  if python3 $H1/tier1_gate.py $PWD/$R prek; then echo "== PASSED the pre-K copy gate on seed $s → $R"; break; fi
  [ $rc -eq 0 ] || { echo "== stopped by the budget mid-ladder"; break; }
done
echo "== last run: $PREV"
echo SCHOOL-CLOUD-LOOP-DONE
