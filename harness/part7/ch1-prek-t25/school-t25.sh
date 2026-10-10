#!/bin/bash
# THE T25 MODEL — a NEW model with the T25 JIT core inside it, from pre-K (J 2026-10-07: "put the t25 core in the model … make a new
# model. begin from prek"; brief <notes>/worker/claude/THEAD-T25-CORE.brief.md, THEAD-TRIAL stage T25-CORE). Every token's event
# (position · token · plate · level · row) fires the rendered T25 core; its address turns the trunk's T25 clock rings (T25_CORE=1).
# Same school settings as school-repeat3.sh (pointer port, context copy pointer, voicing + harmony, 31 router vertices, supervised
# routing, J's day loop). Repeat 1 is FRESH (no warm start); each later repeat warm-starts from the one before on a fresh row seed,
# up to 3, until the pre-K copy gate (tier1_gate.py, copy top-1 ≥ 0.85) passes. SCHOOLS="prek k" continues into kindergarten.
# 10-07 R3 (J "plans approved"): pre-K = tier1-prek-v4 (babbling with equations and symbols); each repeat <= 20 min (J: no test over
# 20 min) = LEARN_MAX_DAYS days (default 3) under a hard `timeout 1200`; the next repeat warm-starts from the last saved day.
# Run under tritwatch:  systemd-run --user --unit=tw-school-t25 … bin/tw run --id school-t25 --owner claude -- results/school-t25.sh
set -e
cd <workspace>/projects/thead-trial/runtime
V=../build-v4; H1=../harness
export OT_THREADS=4 THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=${POINTER:-5} WAKE_STEPS=10
export DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=${COPY:-6}
export LEARN_MAX_DAYS=${LEARN_MAX_DAYS:-3}              # one repeat = 3 days, <= 20 min
export T25_CORE=1                                   # THE T25 JIT CORE IN THE MODEL (born with it; warm starts keep it)
export PLATES_ATTN=1                                # T25-REACTOR (rx tests 10-07): dense attention inside each row + page plates for older rows
unset WARM_FROM
prev=""; step=0
for school in ${SCHOOLS:-prek}; do
  id=$([ $school = prek ] && echo ${PREK_ID:-tier1-prek-v4} || echo tier1-k-v2)
  for rep in 1 2 3; do
    step=$((step + 1)); echo "@tw step=$step total=3"
    R=results/school-t25-$school-$rep; rm -rf $R; mkdir -p $R/bin
    seed=$((6000 + 100 * rep))
    (cd $H1 && python3 tier1_school.py compile tier1/$id.json --suffix s$seed --row-seed $seed | tail -1)
    cp target/release/omni-render ../engine/omni_train/libomnitrain_trial.so $R/bin/
    export OMR_TRAIN_LIB=$PWD/$R/bin/libomnitrain_trial.so
    if [ -n "$prev" ]; then export WARM_FROM=$prev; else unset WARM_FROM; fi
    echo "== T25 model · school $school repeat $rep start $(date -Is) warm=${prev:-none (fresh)} seed=$seed"
    rc=0; timeout 1200 $R/bin/omni-render thead-learn $V/$id-s$seed $V/$id-heldout $V/$id-doing $R || rc=$?
    echo "== repeat $rep exit $rc $(date -Is)"; [ -f $R/ckpt.bin ] || { echo "no checkpoint in $R"; exit 3; }
    python3 $H1/export_run.py $R > /dev/null || true
    OMNI_TRAIN_LIB=$OMR_TRAIN_LIB python3 $H1/tier1_eval.py $PWD/$R
    prev=$R
    if python3 $H1/tier1_gate.py $PWD/$R $school; then echo "== T25 model · school $school PASSED on repeat $rep"; break; fi
  done
done
echo SCHOOL-T25-DONE
