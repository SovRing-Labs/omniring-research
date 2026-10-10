#!/bin/bash
# GROW-RUN-0 G3b-4 gate — THE ARRAY SERVER drives unchanged thead-learn processes. One school day of harness h0:
#   solo   : thead-learn with OMR_TRAIN_LIB = libomnitrain_gpu.so (its own one-model session, G3)
#   array  : `omni-gpu serve DIR --slots N` + N thead-learn processes (client mode: OMR_GPU_SERVER / OMR_GPU_SLOT), h0 in slot 0, the others
#            training their own copies beside it in the SAME recorded step
# Gate: h0's day through the server == h0's day solo (state.json day metrics; the replica axis is bit-identical per model, C2 S2), and every
# array harness finishes its day; recorded: server steps, mean slots per step, GPU ms, VRAM.
#   g3b4_day.sh OUT [N=2] [DEVICE=A40] [DIMS="64 4 2"]        (paths: TT = thead-trial data root, OG = omni-gpu root, LIB = dir of both libs)
set -euo pipefail
OUT=$1; N=${2:-2}; DEV=${3:-A40}; read -r DD LL HH <<< "${4:-64 4 2}"
TT=${TT:-/root/ai-stack/projects/thead-trial}; OG=${OG:-/root/og/projects/omni-gpu}; LIB=${LIB:-/root/og/lib}
BIN=$TT/runtime/target/release/omni-render; B=${B:-$TT/build-v4/elementary-v1}; HO=${HO:-$TT/build-v4/elementary-v1-heldout}; DO=${DO:-$TT/build-v4/elementary-v1-doing}
[ -d $B ] || { echo "no build $B"; exit 2; }
rm -rf $OUT; mkdir -p $OUT; SRV=/dev/shm/omr-array-g3b4; rm -rf $SRV; mkdir -p $SRV
export THEAD_D=$DD THEAD_L=$LL THEAD_H=$HH CKPT_TOKENS=4e5 PLATES=31 ROUTER_SIMPLEX=1 ROUTER_CE=0.5
export VOICE=1 HARM=1 HARM_LAMBDA=0.05 HARM_KAPPA=0.9 LADDER=0 POINTER=5 WAKE_STEPS=10 DO_N=32 DO_REVIEW=8 STUDY_STEPS=20 COPY=6
export T25_CORE=1 PLATES_ATTN=1 P3=1 LEARN_MAX_DAYS=1 OT_THREADS=4 OMNI_GPU_DEVICE=$DEV OMNI_GPU_ROOT=$OG TMPDIR=$OUT OMR_TRAIN_LIB=$LIB/libomnitrain_gpu.so
unset PLATE_PAGE ARC_AMP
cd $TT/runtime
echo "== solo h0 $(date -Is)"; t0=$(date +%s)
timeout 3000 $BIN thead-learn $B $HO $DO $OUT/solo-h0 > $OUT/solo-h0.log 2>&1; echo "solo day $(( $(date +%s) - t0 )) s"
echo "== solo h0 again (the harness's own reproducibility) $(date -Is)"
timeout 3000 $BIN thead-learn $B $HO $DO $OUT/solo-h0b > $OUT/solo-h0b.log 2>&1
echo "== array: server + $N harnesses $(date -Is)"; t0=$(date +%s)
$OG/target/release/omni-gpu serve $SRV --slots $N --device $DEV > $OUT/server.log 2>&1 & SP=$!
pids=()
for i in $(seq 0 $((N - 1))); do
  ( OMR_GPU_SERVER=$SRV OMR_GPU_SLOT=$i timeout 3000 $BIN thead-learn $B $HO $DO $OUT/array-h$i > $OUT/array-h$i.log 2>&1; echo "exit $?" >> $OUT/array-h$i.log ) & pids+=($!)
done
for p in "${pids[@]}"; do wait $p || true; done
touch $SRV/stop; wait $SP || true; cp $SRV/stats.json $OUT/server-stats.json 2>/dev/null || true
echo "array day $(( $(date +%s) - t0 )) s"; tail -3 $OUT/server.log
grep -h "array server\|omnitrain_gpu" $OUT/array-h0.log | head -3
python3 - "$OUT" "$N" <<'PY'
import json, os, sys
o, N = sys.argv[1], int(sys.argv[2])
SKIP = ("sec", "secs", "seconds", "wall", "_ms", "ms_", "time", "elapsed", "build", "heldout", "doing", "out", "path", "control")
def flat(d, p=""):                                   # every leaf with its path; paths / wall-clock entries skipped (they differ by design)
    if isinstance(d, dict):
        for k, v in d.items():
            if any(t in k.lower() for t in SKIP): continue
            yield from flat(v, f"{p}.{k}")
    elif isinstance(d, list):
        for i, v in enumerate(d): yield from flat(v, f"{p}[{i}]")
    else: yield p, d
def diff(a, b):
    fa, fb = dict(flat(a)), dict(flat(b)); ks = sorted(set(fa) | set(fb))
    return [(k, fa.get(k), fb.get(k)) for k in ks if fa.get(k) != fb.get(k)], len(ks)
ld = lambda n: json.load(open(f"{o}/{n}/state.json"))
solo, solo2, arr = ld("solo-h0"), ld("solo-h0b"), [ld(f"array-h{i}") for i in range(N)]
d_rep, n_rep = diff(solo, solo2); d_arr, n_arr = diff(solo, arr[0])
fin = [json.load(open(f"{o}/array-h{i}/state.json")).get("day_n", 0) >= 1 for i in range(N)]
st = json.load(open(f"{o}/server-stats.json")) if os.path.exists(f"{o}/server-stats.json") else {}
res = {"gate": "G3b-4: h0's school day through the array server == h0's day solo (the GPU library alone)", "N": N,
       "leaves_compared": n_arr, "solo_vs_solo_differences": len(d_rep), "solo_vs_array_h0_differences": len(d_arr),
       "first_differences_solo_vs_array": d_arr[:12], "first_differences_solo_vs_solo": d_rep[:12],
       "all_harnesses_finished_day": all(fin), "day_n": [x.get("day_n") for x in arr], "server": st,
       "pass": len(d_arr) == 0 and all(fin) and bool(st.get("steps"))}
json.dump(res, open(f"{o}/g3b4.json", "w"), indent=1); print(json.dumps(res, indent=1, default=str)[:3500]); print("PASS" if res["pass"] else "FAIL")
PY
