#!/bin/bash
# TRAIN-5x8 (OMNI-RENDER-GPU-0, J 10-08): N THEAD harnesses at once on THIS pod, school switches (school-round.sh), each warm from the r16
# core, one school day each (20 wake + 20 study + 12 sleep steps of B 4 × T 512 = 2,048 tokens), then a summary: per-harness seconds per
# phase (state.json days[0].seconds), aggregate training tokens/s, GPU utilisation + VRAM (nvidia-smi every 1 s), host RAM.
#   run.sh N THREADS LIB TAG          LIB = cpu | gpu | trial  (gpu/lib/build/libomnitrain_{cpu,gpu}.so from one engine source; trial = shipped)
# Layout: harness i belongs to unit i/8 (5 units × 8 = the 5×8 layout at N = 40). No merge (PAR_DIR unset): a speed run, not a school round.
set -euo pipefail
N=${1:?N}; TH=${2:?THREADS}; LIBK=${3:?cpu|gpu|trial}; TAG=${4:?TAG}
T=/root/ai-stack/projects/thead-trial; cd $T/runtime
case $LIBK in cpu) LIB=$T/gpu/lib/build/libomnitrain_cpu.so;; gpu) LIB=$T/gpu/lib/build/libomnitrain_gpu.so;; trial) LIB=$T/engine/omni_train/libomnitrain_trial.so;; esac
BIN=$T/runtime/target/release/omni-render; CORE=$T/runtime/results/live-school/cores/r16; O=/root/train5x8/$TAG
B=../build-v4/tier1-prek-v4-s6400; HO=../build-v4/tier1-prek-v4-heldout; DO=../build-v4/tier1-prek-v4-doing
export THEAD_D=256 THEAD_L=6 THEAD_H=4 CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
export T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=1 OMR_TRAIN_LIB=$LIB
unset PLATE_PAGE ARC_AMP PAR_DIR
rm -rf $O; mkdir -p $O
echo "== $TAG: $N harnesses × $TH threads · lib $LIBK $(sha256sum $LIB | cut -c1-12) · bin $(sha256sum $BIN | cut -c1-12) · $(nproc) vCPU · $(date -Is)"
nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader,nounits -l 1 > $O/nvsmi.csv 2>/dev/null & NV=$!
( while sleep 2; do echo "$(date +%s) $(free -m | awk '/Mem:/{print $3}') $(cat /proc/loadavg | cut -d' ' -f1)"; done ) > $O/host.txt & HM=$!
T0=$(date +%s.%N); pids=()
for i in $(seq 0 $((N - 1))); do
  R=$O/h$i; mkdir -p $R
  ( export OT_THREADS=$TH WARM_FROM=$CORE; timeout ${ROUND_SECS:-3600} $BIN thead-learn $B $HO $DO $R > $O/h$i.log 2>&1; echo "exit $?" >> $O/h$i.log ) &
  pids+=($!)
done
for p in "${pids[@]}"; do wait $p || true; done
T1=$(date +%s.%N); kill $NV $HM 2>/dev/null || true
python3 - "$O" "$N" "$TH" "$LIBK" "$T0" "$T1" <<'P'
import json, sys, glob, statistics as st
O, N, TH, LIB, t0, t1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], float(sys.argv[5]), float(sys.argv[6])
STEPS = {"wake": 20, "study": 20, "sleep": 12}; TOK = 2048
hs, bad = [], []
for i in range(N):
    try:
        d = json.load(open(f"{O}/h{i}/state.json"))["days"][0]["seconds"]
        hs.append({"h": i, "unit": i // 8, **{k: round(d[k], 2) for k in ("wake", "doing", "study", "sleep", "retry")}})
    except Exception as e: bad.append(f"h{i}: {e}")
wall = t1 - t0; train_steps = sum(STEPS.values())
gpu = [l.split(",") for l in open(f"{O}/nvsmi.csv") if l.count(",") == 2] if glob.glob(f"{O}/nvsmi.csv") else []
util = [float(x[1]) for x in gpu]; mem = [float(x[2]) for x in gpu]
host = [l.split() for l in open(f"{O}/host.txt")]; ram = [int(x[1]) for x in host if len(x) == 3]; load = [float(x[2]) for x in host if len(x) == 3]
s = {"tag": O.rsplit("/", 1)[1], "harnesses": N, "threads": TH, "lib": LIB, "units": (N + 7) // 8, "ok": len(hs), "failed": bad, "wall_s": round(wall, 1)}
if hs:
    w = [h["wake"] / STEPS["wake"] for h in hs]; tr = [(h["wake"] + h["study"] + h["sleep"]) for h in hs]
    s.update({"wake_s_per_step_median": round(st.median(w), 3), "wake_s_per_step_max": round(max(w), 3),
              "train_s_per_step_median": round(st.median(tr) / train_steps, 3),
              "tok_s_per_harness_median": round(train_steps * TOK / st.median(tr), 1),
              "tok_s_aggregate_train": round(len(hs) * train_steps * TOK / max(tr), 1),
              "tok_s_aggregate_wall": round(len(hs) * train_steps * TOK / wall, 1)})
s.update({"gpu_util_mean": round(st.mean(util), 1) if util else None, "gpu_util_max": max(util) if util else None,
          "vram_mib_max": max(mem) if mem else None, "host_ram_mib_max": max(ram) if ram else None, "load_max": max(load) if load else None,
          "per_harness": hs})
json.dump(s, open(f"{O}/summary.json", "w"), indent=1)
print(json.dumps({k: v for k, v in s.items() if k != "per_harness"}))
P
echo RUN-DONE $TAG
