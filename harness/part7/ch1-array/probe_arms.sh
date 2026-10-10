#!/bin/bash
# PROBE-2G31 arms A/B on the pod. set -e off so arm B runs even if A fails; each arm has its own timeout + record.
R=/root/probe; OG=$R/omni-gpu; OUT=$R/out; mkdir -p $OUT
export CYCLONE_LIB=$R/thead/engine/omni_train/libomnitrain_trial.so CYCLONE_BUILD=$R/thead/build-v4/tier1-prek-v4-s6400 CYCLONE_T25=$R/thead/growth-base/r12-elem
SW="t25,voice,plates,spark=1.0,p3=0.3,harm,port,copy,local,roles,route=0.5,avoid"
cd $OG
echo "ARM A start $(date -u +%T) cap=default(3.5GiB)"; timeout 1200 python3 tests/train/s5_array.py --dims school --units 5 --per 8 --ring --steps 6 --device A40 --sw "$SW" --out $OUT/A > $OUT/A.log 2>&1; echo "ARM A exit $? $(date -u +%T)"
echo "ARM B start $(date -u +%T) cap=2147483392"; OMNI_TRAIN_ARENA_MAX=2147483392 timeout 1200 python3 tests/train/s5_array.py --dims school --units 5 --per 8 --ring --steps 6 --device A40 --sw "$SW" --out $OUT/B > $OUT/B.log 2>&1; echo "ARM B exit $? $(date -u +%T)"
echo DONE
