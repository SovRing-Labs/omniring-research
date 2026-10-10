#!/bin/bash
# PARALLEL DAY TRAINING, stage 1 (J 10-08: "let's get parallel day training set up, once that's running we'll do swarm"; scope confirmed:
# 4 harnesses × 4 threads on the pod, each a pre-K v5 seed, warm from the same core, merge every day, no engine change).
# N harnesses each run their own full school day on their own row seed; at every day end they publish weights, par_merge.py averages
# them into ONE core, every harness loads it and continues (own optimizer moments kept in-process — DiLoCo's inner optimizer).
# After the ladders end: eval + copy gate on the merged core (harness 0's dir holds it).
#   bash school-parallel.sh [CORE=results/school-t25-prek-cloud1] [N=4] [SEEDS="6500 6600 6700 6800"] [BUDGET=7200]
set -e
cd "$HOME/ai-stack/projects/thead-trial/runtime"
H1=../harness; CORE=${1:-results/school-t25-prek-cloud1}; N=${2:-4}; BUDGET=${4:-7200}
read -r -a SEEDS <<< "${3:-6500 6600 6700 6800}"
BUILD=${BUILD:-tier1-prek-v5}; HO=../build-v4/tier1-prek-v4-heldout; DO=../build-v4/tier1-prek-v4-doing
TH=${TH:-$(( $(nproc) / N ))}; P=results/par-${TAG:-v5}; PD=$P/merge
export THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
export T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=0 PAR_TIMEOUT=${PAR_TIMEOUT:-1800}
unset PLATE_PAGE ARC_AMP
LIB=$PWD/../engine/omni_train/libomnitrain_trial.so; BIN=$PWD/target/release/omni-render; export OMR_TRAIN_LIB=$LIB
[ -f $CORE/ckpt.bin ] || { echo "no checkpoint in $CORE"; exit 2; }
rm -rf $P; mkdir -p $PD
echo "== parallel day training · core $CORE · $N harnesses × $TH threads · seeds ${SEEDS[*]} · build $BUILD · budget ${BUDGET}s · bin $(sha256sum $BIN | cut -c1-12) · lib $(sha256sum $LIB | cut -c1-12) · $(date -Is)"
python3 ../cloud/par_merge.py $PD $N 1200 &
MP=$!
pids=()
for i in $(seq 0 $((N - 1))); do
  R=$P/h$i; mkdir -p $R; s=${SEEDS[$i]}
  ( export OT_THREADS=$TH PAR_DIR=$PD PAR_ID=$i WARM_FROM=$CORE
    timeout $BUDGET $BIN thead-learn ../build-v4/$BUILD-s$s $HO $DO $R > $P/h$i.log 2>&1; echo "exit $?" >> $P/h$i.log ) &
  pids+=($!)
done
for p in "${pids[@]}"; do wait $p || true; done
touch $PD/STOP; wait $MP || true
echo "== harnesses done $(date -Is)"; for i in $(seq 0 $((N - 1))); do echo "   h$i: $(tail -1 $P/h$i.log) · $(grep -c '\[par\]' $P/h$i.log) merges"; done
tail -3 $PD/merge.log
python3 -c "import json; s=json.load(open('$P/h0/state.json')); d=s['days']; print('   days', len(d), '· day s', [round(sum(x.get('seconds', {}).values())) for x in d][-6:]); print('   held-out / canary', [(e['day'], round(e['heldout_loss_port'], 3), round(e['canary'], 3)) for e in s['log'] if e.get('day')][-2:])"
OMNI_TRAIN_LIB=$LIB python3 $H1/tier1_eval.py $PWD/$P/h0 | cut -c1-200
python3 $H1/tier1_gate.py $PWD/$P/h0 prek || true
echo SCHOOL-PARALLEL-DONE
