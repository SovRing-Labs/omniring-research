#!/bin/bash
# LIVE-SCHOOL-0 — compile one round's builds ON THE POD, in RAM, all at once, and make every harness's build CIRCULAR (J 10-08: "yes compile on
# pod. every curriculum should be circular and build on all previous layers"; TIER1-SYMBOL-SCHOOL-SPEC §8).
#   bash school-compile.sh <round> <plan-rN.json> <NM> <NH>        (plan + specs = absolute paths, same on the pod: <home> → /root)
# Per harness i (s = round*1000 + i*10, the laptop's seeds):
#   i <  NM (middle):  splice[ tier-1 REVIEW of every mastered tier-1 skill (REV_W, pass 1 = the schools before) → middle build ]
#   i >= NM (tier-1):  splice[ tier-1 build (frontier + review) → middle PREVIEW level 1 (PRE_W, the next school's format) ]
# Shared: tier-1 held-out (ho 9000+r) and doing (7000+r). Output dirs /dev/shm/thead-build/live-r<r>-c<s>, linked into build-v4/.
set -euo pipefail
R=$1; PJ=$2; NM=$3; NH=$4; REV_W=${REV_W:-0.3}; PRE_W=${PRE_W:-0.1}
T=$HOME/ai-stack/projects/thead-trial; H=$T/harness; SHM=/dev/shm/thead-build; mkdir -p $SHM $T/build-v4
LOG=$SHM/compile-r$R; rm -rf $LOG; mkdir -p $LOG; t0=$(date +%s)
spec() { python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['specs'].get(sys.argv[2], ''))" $PJ $1; }
B1=$(spec tier1); B1H=$(spec tier1_heldout); BM=$(spec middle); BRV=$(spec tier1_review); BPR=$(spec middle_preview)
for d in $SHM/live-*; do n=$(basename $d | sed -E 's/^live-([a-z]+-)?r([0-9]+).*/\2/'); [[ "$n" =~ ^[0-9]+$ ]] && [ "$n" -lt $((R - 1)) ] && rm -rf "$d" "$T/build-v4/$(basename $d)"; done 2>/dev/null || true
pids=(); names=()
t1job() { local name=$1; shift; (cd $H && nice -n 5 timeout 1200 python3 tier1_school.py compile "$@" --out-root $SHM > $LOG/$name.log 2>&1) & pids+=($!); names+=($name); }
cujob() { local name=$1 sfx=$2; shift 2; (cd $H && nice -n 5 timeout 3000 python3 curriculum.py compile "$@" --suffix $sfx --port --rows --procedure > $LOG/$name.log 2>&1 \
          && d=$(ls -d $H/curricula/build/*-$sfx) && rm -rf $SHM/$(basename $d) && mv $d $SHM/) & pids+=($!); names+=($name); }
for i in $(seq 0 $((NH - 1))); do s=$((R * 1000 + i * 10))
  if [ $i -lt $NM ]; then
    cujob m$i s$s $BM --tokens $(python3 -c "print(int(4e5 * (1 - $REV_W)))") --row-seed $s
    [ -n "$BRV" ] && t1job rv$i $BRV --suffix rv$s --row-seed $((s + 1)) --tokens $(python3 -c "print(int(4e5 * $REV_W))")
  else
    t1job t$i $B1 --suffix s$s --row-seed $s --tokens $(python3 -c "print(int(4e5 * (1 - $PRE_W)))")
    cujob p$i pv$s $BPR --tokens $(python3 -c "print(int(4e5 * $PRE_W))") --row-seed $((s + 2))
  fi
done
[ -n "$B1H" ] && t1job ho $B1H --row-seed $((9000 + R))
[ -n "$B1" ] && t1job doing $B1 --doing --suffix doing --row-seed $((7000 + R)) --tokens 200000
fail=0; for k in "${!pids[@]}"; do wait ${pids[$k]} || { echo "compile ${names[$k]} FAILED:"; tail -3 $LOG/${names[$k]}.log; fail=1; }; done
[ $fail = 0 ] || exit 1
# splice: one circular build per harness
sid() { python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['id'])" $1; }
for i in $(seq 0 $((NH - 1))); do s=$((R * 1000 + i * 10)); C=$SHM/live-r$R-c$s
  if [ $i -lt $NM ]; then
    if [ -n "$BRV" ]; then python3 $H/splice_build.py $C $SHM/$(sid $BRV)-rv$s:$REV_W $SHM/$(sid $BM)-s$s:$(python3 -c "print(1 - $REV_W)") > $LOG/splice$i.log
    else python3 $H/splice_build.py $C $SHM/$(sid $BM)-s$s:1 > $LOG/splice$i.log; fi
  else python3 $H/splice_build.py $C $SHM/$(sid $B1)-s$s:$(python3 -c "print(1 - $PRE_W)") $SHM/$(sid $BPR)-pv$s:$PRE_W > $LOG/splice$i.log; fi
done
# pad held-out + doing builds (splices are padded by splice_build): no row may end at a phase's last index (r16 crash, <devlog-entry>)
for d in $SHM/live-r$R-ho $SHM/live-r$R-doing; do [ -d "$d" ] && python3 $H/splice_build.py --pad $d > /dev/null; done
for d in $SHM/live-r$R-*; do L=$T/build-v4/$(basename $d); [ -d "$L" ] && [ ! -L "$L" ] && rm -rf "$L"; ln -sfn "$d" "$L"; done
echo "== pod compile r$R: ${#pids[@]} builds + $NH circular splices in $(( $(date +%s) - t0 ))s → $SHM ($(du -sh $SHM | cut -f1) in RAM)"
