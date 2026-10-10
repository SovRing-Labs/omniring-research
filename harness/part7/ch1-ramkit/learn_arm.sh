#!/usr/bin/env bash
# RAM-KIT-0: one thead-learn arm on the laptop (≤ 20 min), school env (cloud/school-round.sh) on pre-K v4 seed 6400, warm from the laptop
# ladder end (results/school-t25-prek-ladder), LEARN_MAX_DAYS days of WAKE_STEPS×2 steps, held-out eval every day (CKPT_TOKENS 4e4).
# Usage: learn_arm.sh <out_dir> <bin> <lib> [KEY=VAL ...]   (extra env = the arm's switches)
set -euo pipefail
OUT=$1; BIN=$2; LIB=$3; shift 3
cd "$HOME/ai-stack/projects/thead-trial/runtime"
B=$PWD/../build-v4/tier1-prek-v4-s6400; HO=$PWD/../build-v4/tier1-prek-v4-heldout; DO=$PWD/../build-v4/tier1-prek-v4-doing
rm -rf "$OUT"; mkdir -p "$OUT"
env THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e4 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5 \
    VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6 \
    T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=${DAYS:-2} OT_THREADS=${TH:-4} WARM_FROM=$PWD/results/school-t25-prek-ladder \
    OMR_TRAIN_LIB=$LIB "$@" timeout 1200 "$BIN" thead-learn "$B" "$HO" "$DO" "$OUT"
