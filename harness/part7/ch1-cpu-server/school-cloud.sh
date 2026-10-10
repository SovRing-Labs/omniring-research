#!/bin/bash
# THEAD T25 school on a cloud CPU server (J 10-07: "let's do it on the runpod"; plan <notes>/worker/claude/<plan> § F).
# One run, warm-started from the finished pre-K ladder (results/school-t25-prek-ladder, 146/146 steps, gate 0.627) on a FRESH row seed
# (tier1-prek-v4-s6400, precompiled), then resumed segment after segment. J 10-07: segments of 30 min – 1 h (SEG_SECS, default 3600);
# eval + copy gate after each segment (probes/seg-N.json). Settings = the laptop ladder (STUDY 20 J 10-05; ARC_AMP off, 10-04 lineage;
# P3=1 from 10-07) — only OT_THREADS follows the server's cores. Stops when the gate passes, the ladder ends, or after SEG segments.
#   bash school-cloud.sh [SEG=3] [SEG_SECS=3600]      log: results/school-cloud.log (the install script prints the nohup line)
set -e
cd "$HOME/ai-stack/projects/thead-trial/runtime"
H1=../harness; SEG=${1:-${SEG:-3}}; SEG_SECS=${2:-${SEG_SECS:-3600}}
SRC=results/school-t25-prek-ladder; R=${RUN:-results/school-t25-prek-cloud1}
B=../build-v4/tier1-prek-v4-s6400; HO=../build-v4/tier1-prek-v4-heldout; DO=../build-v4/tier1-prek-v4-doing
NT=${OT_THREADS:-$(nproc)}
export OT_THREADS=$NT THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
export T25_CORE=1 PLATES_ATTN=1 P3=1
unset PLATE_PAGE ARC_AMP
LIB=$PWD/../engine/omni_train/libomnitrain_trial.so; BIN=$PWD/target/release/omni-render
export OMR_TRAIN_LIB=$LIB
echo "== host $(hostname) · $(nproc) cpus · $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2) · OT_THREADS=$NT · bin $(sha256sum $BIN | cut -c1-12) · lib $(sha256sum $LIB | cut -c1-12)"
mkdir -p $R/probes
for seg in $(seq 1 $SEG); do
  if [ -f $R/state.json ]; then unset WARM_FROM; read -r DAYS STEP <<< "$(python3 -c "import json; s=json.load(open('$R/state.json')); print(len(s['days']), s.get('step', 0))")"
  else export WARM_FROM=$SRC; DAYS=0; STEP=0; fi
  export LEARN_MAX_DAYS=$((DAYS + 40))
  echo "== segment $seg start $(date -Is) · days done $DAYS · step $STEP · warm ${WARM_FROM:-resume}"
  rc=0; timeout $SEG_SECS $BIN thead-learn $B $HO $DO $R || rc=$?
  read -r DAYS2 STEP2 <<< "$(python3 -c "import json; s=json.load(open('$R/state.json')); print(len(s['days']), s.get('step', 0))")"
  echo "== segment $seg exit $rc · days $DAYS2 · step $STEP2 $(date -Is)"
  python3 -c "import json; s=json.load(open('$R/state.json')); [print('  day', d['day'], 'pass', d.get('pass'), {k: round(v) for k, v in d.get('seconds', {}).items()}) for d in s['days'][$DAYS:]]"
  OMNI_TRAIN_LIB=$LIB python3 $H1/tier1_eval.py $PWD/$R | cut -c1-300
  cp $R/probes/tier1_eval.json $R/probes/seg-$seg.json
  if python3 $H1/tier1_gate.py $PWD/$R prek; then echo "== PASSED the pre-K copy gate at segment $seg"; break; fi
  if [ $rc -eq 0 ]; then echo "== ladder finished (thead-learn ended on its own)"; break; fi
done
echo SCHOOL-CLOUD-DONE
