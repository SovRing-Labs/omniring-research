#!/bin/bash
# T25 school — ONE run continues its ladder across 20-minute segments (J 10-07 "1-3 approved … instead of an a/b just look through our
# previous tests"; plan <notes>/worker/claude/<plan> § E). Fix 1: a segment RESUMES the same run dir and goes on to the
# next pass (the old repeats recompiled and restarted at pass 1, so passes 4–5 were never trained). Settings from lineage, no A/B:
#   STUDY_STEPS 20 — J 10-05 "approved: more doing + study (study writes the fix at the operand slip)" (school-repeat2.sh:10)
#   ARC_AMP off    — tested 10-04, thead-learn5-D: no measurable gain (<plan>:413-417)
# Each segment: timeout 1200 (J: no run over 20 min), then tier1_eval (kept per segment in probes/seg-N.json) and the copy gate
# (pk.meet out since 10-07). Stops when the gate passes, the ladder is finished, or after SEGMENTS (default 4).
#   school-t25-ladder.sh [SRC] [SEGMENTS]
set -e
cd <workspace>/projects/thead-trial/runtime
H1=../harness; SRC=${1:-results/school-t25-prek-3}; SEG=${2:-4}; R=results/school-t25-prek-ladder
export OT_THREADS=4 THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
export T25_CORE=1 PLATES_ATTN=1
unset WARM_FROM PLATE_PAGE ARC_AMP
if [ ! -f $R/state.json ]; then [ -f $SRC/state.json ] || { echo "no state in $SRC"; exit 2; }; rm -rf $R; cp -a $SRC $R; rm -rf $R/probes; echo "== ladder starts from $SRC"; fi
export OMR_TRAIN_LIB=$PWD/$R/bin/libomnitrain_trial.so
mkdir -p $R/probes
for seg in $(seq 1 $SEG); do
  echo "@tw step=$seg total=$SEG"
  read -r B HO DO DAYS STEP <<< "$(python3 -c "import json; s=json.load(open('$R/state.json')); c=s['config']; print(c['build'], c['heldout'], c['doing'], len(s['days']), s.get('step', 0))")"
  export LEARN_MAX_DAYS=$((DAYS + 20))
  echo "== segment $seg start $(date -Is) · days done $DAYS · step $STEP · build $B"
  rc=0; timeout 1200 $R/bin/omni-render thead-learn $B $HO $DO $R || rc=$?
  read -r DAYS2 STEP2 <<< "$(python3 -c "import json; s=json.load(open('$R/state.json')); print(len(s['days']), s.get('step', 0))")"
  echo "== segment $seg exit $rc · days $DAYS2 · step $STEP2 $(date -Is)"
  OMNI_TRAIN_LIB=$OMR_TRAIN_LIB python3 $H1/tier1_eval.py $PWD/$R | cut -c1-300
  cp $R/probes/tier1_eval.json $R/probes/seg-$seg.json
  if python3 $H1/tier1_gate.py $PWD/$R prek; then echo "== ladder PASSED the pre-K copy gate at segment $seg"; break; fi
  if [ $rc -eq 0 ]; then echo "== ladder finished (thead-learn ended on its own)"; break; fi
done
echo SCHOOL-LADDER-DONE
