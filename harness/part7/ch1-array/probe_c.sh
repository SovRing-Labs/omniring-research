#!/bin/bash
R=/root/probe; OG=$R/omni-gpu; OUT=$R/out; mkdir -p $OUT; cd $OG
export CYCLONE_LIB=$R/thead/engine/omni_train/libomnitrain_trial.so CYCLONE_BUILD=$R/thead/build-v4/tier1-prek-v4-s6400 CYCLONE_T25=$R/thead/growth-base/r12-elem
SW="t25,voice,plates,spark=1.0,p3=0.3,harm,port,copy,local,roles,route=0.5,avoid"
echo "ARM C start $(date -u +%T) R=20 (5x4)"; timeout 1500 python3 tests/train/s5_array.py --dims school --units 5 --per 4 --ring --steps 6 --device A40 --sw "$SW" --out $OUT/C > $OUT/C.log 2>&1; echo "ARM C exit $? $(date -u +%T)"; echo DONE
