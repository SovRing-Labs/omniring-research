"""Parallel day training, stage 1 — the merge coordinator (J 10-08; DiLoCo day-merge). Waits for all N harnesses' day-end weights
(PAR_DIR/h<i>-d<day>.bin), averages them (float32 mean, same layout as ckpt.bin), writes PAR_DIR/merged-d<day>.bin atomically, logs the
spread between harnesses, and deletes the day's inputs once every harness has had time to load the merge. Stops when STOP exists in
PAR_DIR or no harness publishes for IDLE seconds.
python3 par_merge.py <PAR_DIR> <N> [IDLE=900]"""
import glob, json, os, sys, time
import numpy as np
D, N = sys.argv[1], int(sys.argv[2]); IDLE = float(sys.argv[3]) if len(sys.argv) > 3 else 900
log = open(os.path.join(D, "merge.log"), "a"); day, last = 1, time.time()
while not os.path.exists(os.path.join(D, "STOP")):
    fs = [os.path.join(D, f"h{i}-d{day}.bin") for i in range(N)]
    if all(os.path.exists(f) for f in fs):
        t = time.time(); W = [np.fromfile(f, dtype=np.float32) for f in fs]
        if len({w.size for w in W}) != 1: print(f"day {day}: size mismatch {[w.size for w in W]}", file=log, flush=True); break
        M = np.mean(W, axis=0, dtype=np.float64).astype(np.float32)
        spread = float(np.mean([np.sqrt(np.mean((w - M) ** 2)) for w in W]))
        M.tofile(os.path.join(D, f"merged-d{day}.bin.tmp")); os.replace(os.path.join(D, f"merged-d{day}.bin.tmp"), os.path.join(D, f"merged-d{day}.bin"))
        print(json.dumps({"day": day, "harnesses": N, "params": int(M.size), "rms_spread_to_mean": spread, "merge_s": round(time.time() - t, 2),
                          "at": time.strftime("%H:%M:%S")}), file=log, flush=True)
        for old in glob.glob(os.path.join(D, f"*-d{day - 2}.bin")): os.remove(old)
        day += 1; last = time.time(); continue
    if time.time() - last > IDLE: print(f"idle {IDLE}s at day {day} — stopping", file=log, flush=True); break
    time.sleep(0.3)
