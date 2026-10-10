#!/bin/bash
# LIVE-SCHOOL-0 — one round ON THE POD (J 10-08). N harnesses train ONE core (day merge, par_merge.py), each on its own fresh build of
# this round; then the per-skill eval on the merged core over the round's held-out build(s).
#   bash school-round.sh <core_dir> <round_dir> <TH> "<build>|<heldout>|<doing> ..."  (one triple per harness; paths relative to runtime/)
#   heldouts to evaluate: HOS="<heldout> ..." (env)
set -e
cd "$HOME/ai-stack/projects/thead-trial/runtime"
CORE=$1; P=$2; TH=$3; read -r -a SETS <<< "$4"; N=${#SETS[@]}; PD=$P/merge
export THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
# equal days (J 10-08 r15: a bigger spliced build ran h2 into a day 11 alone while 7 harnesses sat done) — every harness stops at ROUND_DAYS
export T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=${ROUND_DAYS:-10} PAR_TIMEOUT=${PAR_TIMEOUT:-1800}
unset PLATE_PAGE ARC_AMP
LIB=$PWD/../engine/omni_train/libomnitrain_trial.so; BIN=$PWD/target/release/omni-render; export OMR_TRAIN_LIB=$LIB
[ -f $CORE/ckpt.bin ] || { echo "no checkpoint in $CORE"; exit 2; }
rm -rf $P; mkdir -p $PD
echo "== round · core $CORE · $N harnesses × $TH threads · bin $(sha256sum $BIN | cut -c1-12) · lib $(sha256sum $LIB | cut -c1-12) · $(date -Is)"
# SPLIT_MID=k (J 10-08 middle runs): harnesses 0..k-1 (middle builds) merge ONLY with each other in $P/merge-mid from CORE_MID; harnesses
# k..N-1 (tier-1) merge in $P/merge from CORE — so middle cannot wipe tier-1 (the r9 collapse). Tier-1 core = h<k>, middle core = h0.
K=${SPLIT_MID:-0}; CORE_MID=${CORE_MID:-$CORE}
if [ "$K" -gt 0 ] && [ "$K" -lt "$N" ]; then
  mkdir -p $P/merge-mid; python3 ../cloud/par_merge.py $P/merge-mid $K 1200 & MPM=$!
  python3 ../cloud/par_merge.py $PD $((N - K)) 1200 &
else K=0; python3 ../cloud/par_merge.py $PD $N 1200 & fi
MP=$!; pids=()
# tritwatch ON THE POD (J 10-08): each harness runs under `tw run` where the work is, so STALL / ERR are real (laptop tw only saw ssh).
# A harness silent + idle for TW_STALL is killed (its round continues with the rest); nudges land in $TW_DIR/inbox/pod.log.
TW=$PWD/../../tritwatch/tw; export TW_DIR=${TW_DIR:-$HOME/tw}; RN=$(basename $P)
for i in $(seq 0 $((N - 1))); do
  IFS='|' read -r B HO DO <<< "${SETS[$i]}"; R=$P/h$i; mkdir -p $R
  if [ $i -lt $K ]; then PDI=$P/merge-mid; PID=$i; WF=$CORE_MID; else PDI=$PD; PID=$((i - K)); WF=$CORE; fi
  ( export OT_THREADS=$TH PAR_DIR=$PDI PAR_ID=$PID WARM_FROM=$WF
    rc=0; timeout ${ROUND_SECS:-5400} python3 $TW run --id $RN-h$i --owner pod --class thead-learn.round --stall ${TW_STALL:-15m} \
      --on stall=kill -- $BIN thead-learn $B $HO $DO $R || rc=$?
    cp $TW_DIR/jobs/$RN-h$i/raw $P/h$i.log 2>/dev/null; echo "exit $rc" >> $P/h$i.log ) &
  pids+=($!)
done
# heartbeat: one line per harness every 2 min, so the laptop's tw (and anyone tailing round.log) sees the pod's own state
( while sleep 120; do for i in $(seq 0 $((N - 1))); do echo "   pod-tw $(python3 $TW peek $RN-h$i 2>&1 | head -1 | cut -c1-160)"; done; done ) &
HB=$!
# straggler cut: once the first harness finishes, the rest get STRAGGLE_SECS, then they are stopped (no merge partner is left anyway)
while :; do left=0; for p in "${pids[@]}"; do kill -0 $p 2>/dev/null && left=$((left + 1)); done
  [ $left -eq 0 ] && break
  if [ $left -lt ${#pids[@]} ]; then [ -z "${T_FIRST:-}" ] && T_FIRST=$(date +%s)
    if [ $(( $(date +%s) - T_FIRST )) -ge ${STRAGGLE_SECS:-180} ]; then
      echo "== straggler cut: $left harness(es) still running $(( $(date +%s) - T_FIRST ))s after the first finished — stopping them"
      for i in $(seq 0 $((N - 1))); do ps -eo pid,args | grep -F "thead-learn" | grep -F "$P/h$i" | grep -v grep | grep -v "tw run" | grep -v timeout | awk '{print $1}' | xargs -r kill; done
      break; fi; fi
  sleep 5; done
for p in "${pids[@]}"; do wait $p || true; done
kill $HB 2>/dev/null || true
touch $PD/STOP; wait $MP || true
[ $K -gt 0 ] && { touch $P/merge-mid/STOP; wait $MPM || true; }
EH=h$K   # the tier-1 core (h0 when not split)
echo "== pod tw nudges ($RN)"; grep -E "TW-(STALL|ERR|OOM|RULE|EXIT) $RN-" $TW_DIR/inbox/pod.log 2>/dev/null | cut -c1-200 | tail -24 || true
echo "== harnesses done $(date -Is)"; for i in $(seq 0 $((N - 1))); do echo "   h$i: $(tail -1 $P/h$i.log) · $(grep -c '\[par\]' $P/h$i.log) merges"; done
python3 -c "import json; s=json.load(open('$P/$EH/state.json')); d=s['days']; print('   days', len(d), '· held-out / canary', [(e['day'], round(e['heldout_loss_port'], 3), round(e['canary'], 3)) for e in s['log'] if e.get('day')][-1:])"
i=0; for H in $HOS; do bash ../cloud/skill-eval-par.sh $PWD/$P/$EH $H $PWD/$P/skill-$i.json; i=$((i + 1)); done
if [ $K -gt 0 ]; then   # the middle core on the same held-outs: its middle skills go into skill.json; its tier-1 retention is reported
  mkdir -p $P/mid-eval; i=0; for H in $HOS; do bash ../cloud/skill-eval-par.sh $PWD/$P/h0 $H $PWD/$P/mid-eval/skill-$i.json; i=$((i + 1)); done
  python3 -c "
import json, glob
mid = {}
for f in sorted(glob.glob('$P/mid-eval/skill-*.json')): mid.update(json.load(open(f))['skill'])
json.dump({'skill': mid}, open('$P/skill-midcore.json', 'w'), indent=1)
t1 = {k: v for k, v in mid.items() if not k.startswith(('mid.', 'hs.'))}
print('MID-CORE tier-1 retention: %d of %d at >= 0.85 · middle skills %d at >= 0.85' % (sum(v >= 0.85 for v in t1.values()), len(t1), sum(v >= 0.85 for k, v in mid.items() if k.startswith(('mid.', 'hs.')))))"
fi
python3 -c "
import json, glob
sk = {}; n = {}
for f in sorted(glob.glob('$P/skill-[0-9]*.json')): j = json.load(open(f)); sk.update(j['skill']); n.update(j['n'])
try:   # split: middle skills come from the middle core
    mid = json.load(open('$P/skill-midcore.json'))['skill']; sk.update({k: v for k, v in mid.items() if k.startswith(('mid.', 'hs.'))})
except OSError: pass
json.dump({'skill': sk, 'n': n}, open('$P/skill.json', 'w'), indent=1); print('ROUND-SKILLS', len(sk), sum(v >= 0.85 for v in sk.values()))"
# RAM-KIT-0 reports (non-fatal): checkpoint soup + time machine (#7), memorisation detector (#11) over this round's first build
if [ -f ../cloud/ramkit-hooks.sh ]; then export RAMKIT=$PWD/../ramkit; . ../cloud/ramkit-hooks.sh; ramkit_soup results $(basename $P) || true; ramkit_memdetect $P/h0 "${SETS[0]%%|*}" || true; fi
echo SCHOOL-ROUND-DONE
