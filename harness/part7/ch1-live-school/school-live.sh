#!/bin/bash
# LIVE-SCHOOL-0 — the live school orchestrator, ON THE LAPTOP (J 10-08: "do r1-8 all at once and do a full run"; high school A→J stacked,
# "2 stacks on 1"). Each round: school_graph plan (R1 graph + R3 learning-progress sampler + review + R5 level+1 held-out) → compile FRESH
# builds here (R2; tier-1 lessons incl. R4 mask, R6 bridge, R7 [revise] fixes, R8 rotation; middle / high-school depth via reason-gen) →
# rsync to the pod → school-round.sh (N harnesses, day merge) → skill.json back → school_graph update (gates; WALL after 3 flat rounds).
#   bash school-live.sh <pod_ip> <pod_port> [ROUNDS=12] [NH=8] [TH=4]        state: runtime/results/live-school/state.json
set -e
IP=$1; PORT=$2; ROUNDS=${3:-12}; NH=${4:-8}; TH=${5:-4}
T=$HOME/ai-stack/projects/thead-trial; H=$T/harness; L=$T/runtime/results/live-school; mkdir -p $L
SSH="ssh -o ConnectTimeout=20 -o ServerAliveInterval=30 -o ServerAliveCountMax=6 -i $HOME/.ssh/id_ed25519_runpod -p $PORT root@$IP"
RS="rsync -az -e \"ssh -o ConnectTimeout=20 -i $HOME/.ssh/id_ed25519_runpod -p $PORT\""
PT=/root/ai-stack/projects/thead-trial
CORE=${CORE:-results/pod-20261008/par-v5/h0}           # pod-relative start core (uploaded by the kit step)
ST=$L/state.json
. $T/cloud/ramkit-hooks.sh   # RAM-KIT-0 hooks (switch-guarded, non-fatal; BRANCHES stays 0 without J)
# ROUND GUARD (J 10-08): every round's core is backed up ($L/cores/rN, last 5 kept on disk, laptop + pod); a round whose tier-1 skills at the gate
# drop > 10 % or whose held-out rises > 30 % (cloud/round_guard.py, vs the last GOOD round) is discarded: fall back to the good core and redo the
# round with more review (SCHOOL_REVIEW 0.4, then 0.6); after GUARD_RETRIES failures the school stops for J.
r=${START_ROUND:-1}; GOOD=$((r - 1)); ATT=0; KEEP=${KEEP_CORES:-5}
while [ $r -le $ROUNDS ]; do
  echo "== round $r plan $(date -Is)"
  ramkit_watch $ST $L $r
  (cd $H && python3 school_graph.py plan $ST $r $L/r$r) | tee $L/r$r.plan.log
  PJ=$L/r$r/plan-r$r.json
  B1=$(python3 -c "import json; print(json.load(open('$PJ'))['specs'].get('tier1', ''))"); BM=$(python3 -c "import json; print(json.load(open('$PJ'))['specs'].get('middle', ''))")
  B1H=$(python3 -c "import json; print(json.load(open('$PJ'))['specs'].get('tier1_heldout', ''))")
  [ -n "$B1$BM" ] || { echo "== nothing left to train (frontier empty or only UNBUILT rungs)"; break; }
  # harness split: middle share of the frontier weight → that many harnesses on middle builds (at least 1 when present)
  NM=$(python3 -c "
import json; p=json.load(open('$PJ')); import sys; sys.path.insert(0, '$H'); import school_graph as g
N=g.nodes(); w=p['weights']; tm=sum(v for k, v in w.items() if N[k]['builder']=='middle'); tt=sum(w.values()) or 1
nm=round($NH*tm/tt); print(min($NH, max(1 if tm>0 else 0, nm)) if '$B1' else $NH)")
  # CIRCULAR + POD COMPILE (J 10-08): the laptop compiles NOTHING. The plan + specs go to the pod; school-compile.sh builds tier-1, middle, the
  # tier-1 review and the middle preview in parallel in /dev/shm and splices ONE circular build per harness (review → school → preview).
  SETS=""; HOS=""
  for i in $(seq 0 $((NH - 1))); do s=$((r * 1000 + i * 10))
    if [ $i -lt $NM ]; then SETS="$SETS ../build-v4/live-r$r-c$s|../build-v4/seed-v4-short-heldout|../build-v4/seed-v4-doing-bank"
    else SETS="$SETS ../build-v4/live-r$r-c$s|../build-v4/live-r$r-ho|../build-v4/live-r$r-doing"; fi
  done
  eval $RS --exclude __pycache__ --exclude "'*.pre-*'" $H/ root@$IP:$T/harness/
  eval $RS $HOME/ai-stack/bin/reason-gen root@$IP:/root/ai-stack/bin/
  eval $RS --exclude .git $HOME/ai-stack/projects/thead-generators/ root@$IP:/root/ai-stack/projects/thead-generators/
  eval $RS --exclude __pycache__ --exclude tests $T/ramkit/ root@$IP:$PT/ramkit/ ; eval $RS $T/cloud/ramkit-hooks.sh root@$IP:$PT/cloud/
  $SSH "mkdir -p $L/r$r"; eval $RS $L/r$r/ root@$IP:$L/r$r/
  eval $RS $T/cloud/school-compile.sh $T/cloud/school-round.sh root@$IP:$PT/cloud/
  $SSH "bash $PT/cloud/school-compile.sh $r $PJ $NM $NH" 2>&1 | tee $L/r$r/compile.log
  grep -q "^== pod compile r$r" $L/r$r/compile.log || { echo "== pod compile failed — stop"; break; }
  [ -n "$B1" ] && HOS="$HOS ../build-v4/live-r$r-ho"
  [ -n "$BM" ] && HOS="$HOS ../build-v4/seed-v4-short-heldout"
  echo "== round $r on the pod: $NH harnesses ($NM middle) $(date -Is)"
  # streamed through tee (J 10-08): laptop tw sees the pod heartbeat, so its STALL means a real silence; keepalive + wall cap end a dead ssh
  SPL=""; [ "${SCHOOL_SPLIT:-0}" = 1 ] && [ "$NM" -gt 0 ] && [ "$NM" -lt "$NH" ] && SPL="SPLIT_MID=$NM CORE_MID=${CORE_MID:-$CORE}"   # middle merges only with middle
  timeout ${ROUND_WALL:-7200} $SSH "cd $PT/runtime && HOS='$HOS' $SPL bash ../cloud/school-round.sh $CORE results/live-r$r $TH '$SETS'" 2>&1 | tee $L/r$r/round.log || true
  eval $RS root@$IP:$PT/runtime/results/live-r$r/skill.json $L/r$r/ || { echo "== no skill.json from the pod — stop"; break; }
  if ! python3 $T/cloud/round_guard.py $L $r $GOOD > $L/r$r/guard.json; then
    ATT=$((ATT + 1)); echo "== GUARD FAIL r$r attempt $ATT: $(cat $L/r$r/guard.json)"
    mv $L/r$r $L/r$r.fail$ATT; $SSH "mv $PT/runtime/results/live-r$r $PT/runtime/results/live-r$r-fail$ATT"
    [ $ATT -le ${GUARD_RETRIES:-2} ] || { echo "== GUARD: round $r failed $ATT times — fallback core $CORE kept; stop for J"; break; }
    export SCHOOL_REVIEW=$(python3 -c "print(min(0.6, 0.2 + 0.2 * $ATT))"); echo "== redo round $r from $CORE with review share $SCHOOL_REVIEW"
    continue
  fi
  echo "== GUARD PASS r$r: $(cat $L/r$r/guard.json | cut -c1-220)"; ATT=0; unset SCHOOL_REVIEW
  (cd $H && python3 school_graph.py update $ST $r $L/r$r/skill.json) | tee -a $L/rounds.jsonl
  ramkit_history $L; ( ramkit_memo_round $L $r $T/build-v4/live-mid-r$r-s* > $L/r$r/memo.log 2>&1 || true ) &   # memo off the critical path (it held the pod idle 10-08 r13)
  eval $RS root@$IP:$PT/runtime/results/live-r$r/h0/memdetect.json root@$IP:$PT/runtime/results/soup-r$r.log $L/r$r/ 2>/dev/null || true  # ramkit reports
  if [ -n "$SPL" ]; then CORE=results/live-r$r/h$NM; CORE_MID=results/live-r$r/h0      # tier-1 core continues tier-1; middle core continues middle
    mkdir -p $L/cores/r$r-mid; eval $RS --include "'ckpt*'" --include "'state.json'" --include "'t25_core*'" --exclude "'*'" root@$IP:$PT/runtime/results/live-r$r/h0/ $L/cores/r$r-mid/
  else CORE=results/live-r$r/h0; fi; GOOD=$r
  # backup: this round's core to the laptop; keep the last $KEEP cores (laptop $L/cores/, pod round dirs)
  mkdir -p $L/cores/r$r; eval $RS --include "'ckpt*'" --include "'state.json'" --include "'t25_core*'" --exclude "'*'" root@$IP:$PT/runtime/results/${CORE#results/}/ $L/cores/r$r/
  for d in $(ls -d $L/cores/r* 2>/dev/null | sort -V | head -n -$KEEP); do rm -rf "$d"; done
  python3 $T/cloud/reason_report.py $L $r 2>/dev/null | sed 's/^/== REASONING /' || true   # DOING, retry-fixed, novel answers, level+1 (J 10-08)
  $SSH "cd $PT/runtime/results && for d in live-r*; do n=\$(echo \$d | sed -E 's/^live-r([0-9]+).*/\\1/'); [ \$n -le $((r - KEEP)) ] && rm -rf \$d; done; true"
  if python3 -c "import json; import sys; sys.exit(0 if json.load(open('$ST'))['wall'] >= 3 else 1)"; then echo "== WALL at round $r (3 flat rounds) — stop for growth"; break; fi
  r=$((r + 1))
done
echo SCHOOL-LIVE-DONE
