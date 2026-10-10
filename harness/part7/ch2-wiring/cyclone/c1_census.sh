#!/bin/bash
# CYCLONE-ARRAY C1 (OMNI-RENDER-GPU-0 plan § CYCLONE-ARRAY, J 10-08): census of every engine function ONE short school day executes under the
# school switches (cloud/school-round.sh env, warm from the r16 core) → the port list for the resident model (C2). gcov over a coverage build
# of OUR engine (omni_train.cpp, same source as the TRAIN-5x8 pod libs); the runtime binary is unchanged (it dlopens OMR_TRAIN_LIB).
#   c1_census.sh OUT_DIR
set -euo pipefail
O=${1:?OUT_DIR}; T=<workspace>/projects/thead-trial; E=$T/engine/omni_train; HERE=$(cd "$(dirname "$0")" && pwd)
rm -rf $O/build $O/run; mkdir -p $O/build/src $O/run
cp $E/omni_train.cpp $O/build/src/; cp $T/engine/trit_pack.hpp $O/build/
echo "== engine $(sha256sum $E/omni_train.cpp | cut -c1-12) · bin $(sha256sum $T/runtime/target/release/omni-render | cut -c1-12) · $(date -Is)"
( cd $O/build/src && g++ -O2 --coverage -fprofile-update=single -march=native -fopenmp -shared -fPIC -std=c++17 -o ../libomnitrain_cov.so omni_train.cpp )
cd $T/runtime
export THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 COPY=6
export T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=1 OMR_TRAIN_LIB=$O/build/libomnitrain_cov.so
# short day: every phase runs (wake · doing · study · sleep · retry), few steps each
export WAKE_STEPS=2 STUDY_STEPS=2 SLEEP_STEPS=2 DO_N=2 DO_REVIEW=1 OT_THREADS=1 WARM_FROM=$T/runtime/results/live-school/cores/r16
unset PLATE_PAGE ARC_AMP PAR_DIR BUS_DIR
B=../build-v4/tier1-prek-v4-s6400; HO=../build-v4/tier1-prek-v4-heldout; DO=../build-v4/tier1-prek-v4-doing
timeout --foreground 1500 ./target/release/omni-render thead-learn $B $HO $DO $O/run > $O/thead-learn.log 2>&1
echo "thead-learn exit 0 · $(date -Is)"
cd $O/build/src && gcov --json-format ../libomnitrain_cov.so-omni_train.gcda > $O/gcov.log 2>&1
python3 -I $HERE/c1_census.py $O/build/src/omni_train.cpp.gcov.json.gz $E/omni_train.cpp $O/run/state.json $O/census.json
