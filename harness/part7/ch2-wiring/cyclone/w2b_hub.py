#!/usr/bin/env python3
"""CYCLONE-ARRAY W2b/W2c gate — the coupling stream on the GPU: each unit's cyclone gathers its models' weights (hub_mean) and pulls them
toward the mean (hub_pull); on a floor, the ring carries the unit means one level up (outer hubs pull toward the centre hub, the centre
toward the mean of the 4 outer hubs) before the models pull toward their (ring-updated) unit mean. All passes resident, the step recorded
once and submitted twice (the second step starts from the first one's results, as training does).
Weights are REAL school checkpoints (ckpt.bin, 6,926,912 floats each):
  unit  — one live-school round's 8 harnesses (pod-cpu32b/live-r14/h0..h7), FULL size; harness 5 dropped by harmony (keep 0, re-seeded K = 1),
          the rest K = 0.35.
  floor — 5 units × 8 = 40 real checkpoints, first 1,048,576 floats of each (the laptop's memory; full size is the pod rung's job);
          ring K2 = 0.25 (outer → centre), K2c = 0.10 (centre → mean of the outer 4); model K = 0.35, unit 3's harness 2 dropped.
Oracle: numpy with the arithmetic of cloud/bus_coord.py (float64 mean in order, one rounding to float32) and runtime/src/shmbus.rs (float32,
each op rounded) — every float compared BIT FOR BIT.   w2b_hub.py [--devices llvmpipe,Intel] [--out DIR]"""
import glob, hashlib, json, os, subprocess, sys, tempfile
import numpy as np
P = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = f"{P}/target/release/omni-gpu"; KM, KP = f"{P}/kernels/hub_mean.spv", f"{P}/kernels/hub_pull.spv"
R = os.environ.get("CYCLONE_RESULTS", "<workspace>/projects/thead-trial/runtime/results"); NW = 6926912

def mean_ref(w, keep):                         # w [G, R, W], keep [G, R] → [G, W]
    out = np.zeros((w.shape[0], w.shape[2]), np.float32)
    for g in range(w.shape[0]):
        acc = np.zeros(w.shape[2], np.float64); c = 0
        for q in range(w.shape[1]):
            if keep[g, q]: acc = acc + w[g, q].astype(np.float64); c += 1
        out[g] = (acc / np.float64(c)).astype(np.float32) if c else 0
    return out

def pull_ref(w, mean, kf):                     # w [G, R, W] f32, mean [G, W], kf [G, R]
    o = w.copy()
    for g in range(w.shape[0]):
        for q in range(w.shape[1]):
            k = np.float32(kf[g, q])
            o[g, q] = mean[g] if k >= 1 else (w[g, q] + k * (mean[g] - w[g, q])).astype(np.float32)
    return o

def grid(n): gx = min(65535, -(-n // 64)); return f"{gx},{-(-n // 64 // gx) + 1},1"

def run(dev, prog, steps, od):
    r = subprocess.run([BIN, "session", prog, "--device", dev, "--steps", str(steps), "--out", od], capture_output=True, text=True, timeout=1800)
    if r.returncode: raise RuntimeError(r.stderr[-500:])
    return json.loads(r.stdout.strip().splitlines()[-1])

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    devices = opt("--devices", "llvmpipe,Intel").split(","); out = opt("--out", f"{P}/results/cyclone/w2b"); os.makedirs(out, exist_ok=True)
    unit_files = [f"{R}/pod-cpu32b/live-r14/h{i}/ckpt.bin" for i in range(8)]
    pool = sorted(f for f in glob.glob(f"{R}/**/ckpt.bin", recursive=True) if os.path.getsize(f) == NW * 4)
    floor_files = (unit_files + [f for f in pool if f not in unit_files])[:40]
    assert len(floor_files) == 40, len(floor_files)
    fails, cases = [], []
    with tempfile.TemporaryDirectory(prefix="omni-gpu-w2b-") as T:
        # ── unit: 8 real harnesses, full size ─────────────────────────────────────────────────────────────────────────────────────
        w = np.stack([np.fromfile(f, np.float32) for f in unit_files])[None]          # [1, 8, W]
        keep = np.ones((1, 8), np.uint32); keep[0, 5] = 0; kf = np.full((1, 8), 0.35, np.float32); kf[0, 5] = 1.0
        ref = w.copy()
        for _ in range(2): m = mean_ref(ref, keep); ref = pull_ref(ref, m, kf)
        w.tofile(f"{T}/uw.bin"); keep.tofile(f"{T}/uk.bin"); kf.tofile(f"{T}/ukf.bin")
        open(f"{T}/unit.txt", "w").write("\n".join([f"buf file {T}/uw.bin", f"buf file {T}/uk.bin", f"buf zero {NW * 4}", f"buf file {T}/ukf.bin",
            f"pass {KM} {grid(NW)} spec 1=8 2={NW} bind 0 1 2", f"pass {KP} {grid(8 * NW)} spec 1=8 2={NW} bind 0 2 3", "read 0", "read 2"]) + "\n")
        # ── floor: 5 units × 8 real checkpoints, prefix ──────────────────────────────────────────────────────────────────────────
        W = 1 << 20; U = 5
        fw = np.stack([np.fromfile(f, np.float32, count=W) for f in floor_files]).reshape(U, 8, W)
        fkeep = np.ones((U, 8), np.uint32); fkeep[3, 2] = 0; fkf = np.full((U, 8), 0.35, np.float32); fkf[3, 2] = 1.0
        K2, K2c = 0.25, 0.10
        kout = np.array([[0, 1, 1, 1, 1]], np.uint32); kcen = np.array([[1, 0, 0, 0, 0]], np.uint32)
        rkf_out = np.array([[0, K2, K2, K2, K2]], np.float32); rkf_cen = np.array([[K2c, 0, 0, 0, 0]], np.float32)
        fref = fw.copy()
        for _ in range(2):
            means = mean_ref(fref, fkeep)                                              # A  unit cyclones
            tc = mean_ref(means[None], kout); cc = mean_ref(means[None], kcen)          # B, B'  the ring's two targets (old means)
            means = pull_ref(means[None], cc, rkf_out)                                 # C  outer hubs → centre
            means = pull_ref(means, tc, rkf_cen)[0]                                    # D  centre → mean of the outer 4
            fref = pull_ref(fref, means, fkf)                                          # E  models → their unit mean
        for nm, arr in (("fw", fw), ("fk", fkeep), ("fkf", fkf), ("ko", kout), ("kc", kcen), ("rko", rkf_out), ("rkc", rkf_cen)): arr.tofile(f"{T}/{nm}.bin")
        open(f"{T}/floor.txt", "w").write("\n".join([
            f"buf file {T}/fw.bin", f"buf file {T}/fk.bin", f"buf zero {U * W * 4}", f"buf file {T}/fkf.bin",          # 0 w · 1 keep · 2 means · 3 kf
            f"buf file {T}/ko.bin", f"buf file {T}/kc.bin", f"buf zero {W * 4}", f"buf zero {W * 4}",                  # 4 keep outer · 5 keep centre · 6 tc · 7 cc
            f"buf file {T}/rko.bin", f"buf file {T}/rkc.bin",                                                           # 8 ring K outer · 9 ring K centre
            f"pass {KM} {grid(U * W)} spec 1=8 2={W} bind 0 1 2",
            f"pass {KM} {grid(W)} spec 1=5 2={W} bind 2 4 6", f"pass {KM} {grid(W)} spec 1=5 2={W} bind 2 5 7",
            f"pass {KP} {grid(U * W)} spec 1=5 2={W} bind 2 7 8", f"pass {KP} {grid(U * W)} spec 1=5 2={W} bind 2 6 9",
            f"pass {KP} {grid(U * 8 * W)} spec 1=8 2={W} bind 0 2 3", "read 0", "read 2"]) + "\n")
        for dev in devices:
            for name, prog, refw, shape in (("unit (8 harnesses, full slabs)", f"{T}/unit.txt", ref, (1, 8, NW)), ("floor (5 units x 8, ring, prefix)", f"{T}/floor.txt", fref, (U, 8, W))):
                od = f"{T}/o-{dev}-{len(cases)}"; case = {"case": name, "device": dev, "slab_floats": shape[2], "models": shape[0] * shape[1], "steps": 2}
                try: info = run(dev, prog, 2, od)
                except RuntimeError as e: case["error"] = str(e); fails.append(f"{dev} {name}: {e}"); cases.append(case); continue
                got = np.fromfile(f"{od}/buf0.bin", np.float32).reshape(shape)
                diff = int((got.view(np.uint32) != refw.view(np.uint32)).sum())
                case.update({"device_name": info["device"], "passes": info["passes"], "bytes_resident": info["bytes"], "ms_per_step": info["ms_per_step"],
                             "gpu_ms_last": info["gpu_ms_last"], "weights_bit_mismatches": diff, "moved": int((refw != (w if shape[2] == NW else fw)).sum())})
                if diff: fails.append(f"{dev} {name}: {diff} weights differ from the oracle")
                cases.append(case); print(json.dumps(case), flush=True)
    rep = {"gate": "CYCLONE-ARRAY W2b/W2c coupling on the GPU (unit cyclone + floor ring)", "kernels": {k: hashlib.sha256(open(v, "rb").read()).hexdigest()[:12] for k, v in (("hub_mean", KM), ("hub_pull", KP))},
           "unit_files": unit_files, "floor_files": floor_files, "cases": cases, "fails": fails, "pass": not fails}
    json.dump(rep, open(f"{out}/hub.json", "w"), indent=1)
    print("PASS" if not fails else "FAIL: " + "; ".join(fails)); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
