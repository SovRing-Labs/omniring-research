#!/usr/bin/env python3
"""CYCLONE-ARRAY C2 S1 learning gate — DOES THE GPU STEP TRAIN LIKE THE CPU ENGINE? One THEAD model (plain trunk) created by the CPU engine;
K consecutive training steps on REAL curriculum batches: the CPU engine's om_train_step (forward, backward, AdamW + clip) vs the GPU step
(gen/train_step.build_train: the same K steps recorded back to back, resident). Compared per step: the training loss; at the end: every
weight (cosine, max |Δ| / max |w|) and a held-out loss of both final models measured by the SAME CPU engine (om_forward_loss).
  s1_train.py [--dims small|school] [--steps 20] [--lr 3e-3] [--device llvmpipe] [--out DIR]"""
import ctypes, json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import LIB, BIN, DIMS, batch

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "small"); dims = DIMS[dn]; dev = opt("--device", "llvmpipe"); K = int(opt("--steps", "20")); lr = float(opt("--lr", "3e-3"))
    out = opt("--out", f"{P}/results/cyclone/c2-s1"); os.makedirs(out, exist_ok=True)
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B"))
    Lb = ctypes.CDLL(LIB); vp = ctypes.c_void_p; ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    Lb.om_create.restype = vp; Lb.om_create.argtypes = [ctypes.c_int] * 5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
    Lb.om_train_step.restype = ctypes.c_float; Lb.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]
    Lb.om_forward_loss.restype = ctypes.c_float; Lb.om_forward_loss.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
    for fn, rt in (("om_param_ptr", ctypes.POINTER(ctypes.c_float)), ("om_param_size", ctypes.c_long), ("om_param_name", ctypes.c_char_p)):
        getattr(Lb, fn).restype = rt; getattr(Lb, fn).argtypes = [vp, ctypes.c_int]
    Lb.om_nparams.argtypes = [vp]; Lb.om_threads(4)
    PR = (ctypes.c_int * 32)(*train_step.PRIMES)
    mk = lambda: Lb.om_create(V, D, L, H, T, PR, (D // H) // 2, 1234)
    h = mk(); names = [Lb.om_param_name(h, i).decode() for i in range(Lb.om_nparams(h))]
    params = [(n, np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),)).copy()) for i, n in enumerate(names)]
    batches = [batch(V, T, B, seed=1000 + s) for s in range(K)]; hx, hy = batch(V, T, B, seed=999_999)      # held-out batch
    t0 = time.time(); cpu_loss = [float(Lb.om_train_step(h, x, y, B, T, lr)) for x, y in batches]; t_cpu = time.time() - t0
    w_cpu = {n: np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),)).copy() for i, n in enumerate(names)}
    held_cpu = float(Lb.om_forward_loss(h, hx, hy, B, T))
    with tempfile.TemporaryDirectory(prefix="omni-gpu-s1t-") as Tm:
        text, outs, npass, nbuf = train_step.build_train(dims, params, batches, [lr] * K, Tm)
        open(f"{Tm}/prog.txt", "w").write(text); od = f"{Tm}/o"; t1 = time.time()
        r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", "1", "--out", od], capture_output=True, text=True, timeout=14400)
        rec = {"gate": "CYCLONE-ARRAY C2 S1 learning: K training steps GPU vs the CPU engine (om_train_step)", "dims": dims, "steps": K, "lr": lr,
               "device": dev, "passes": npass, "buffers": nbuf, "cpu_s": round(t_cpu, 2), "lib": LIB}
        if r.returncode:
            rec.update({"pass": False, "error": r.stderr[-1500:]}); print(json.dumps(rec)); json.dump(rec, open(f"{out}/s1-train-{dn}-{dev.split()[0].lower()}.json", "w"), indent=1); sys.exit(1)
        info = json.loads(r.stdout.strip().splitlines()[-1])
        rd = lambda k: np.fromfile(f"{od}/buf{outs[k][0]}.bin", np.float32)
        gpu_loss = [float(rd(f"loss:{s}")[0]) for s in range(K)]
        w_gpu = {n: rd(f"w:{n}")[:w_cpu[n].size] for n in names}
        h2 = mk()                                                                                   # the GPU's final weights in a CPU model
        for i, n in enumerate(names): np.ctypeslib.as_array(Lb.om_param_ptr(h2, i), shape=(w_cpu[n].size,))[:] = w_gpu[n]
        held_gpu = float(Lb.om_forward_loss(h2, hx, hy, B, T))
        wcos = min(float(np.dot(w_gpu[n].astype(np.float64), w_cpu[n]) / (np.linalg.norm(w_gpu[n]) * np.linalg.norm(w_cpu[n]))) for n in names)
        wrel = max(float(np.max(np.abs(w_gpu[n] - w_cpu[n])) / max(np.max(np.abs(w_cpu[n])), 1e-30)) for n in names)
        dl = [abs(g - c) for g, c in zip(gpu_loss, cpu_loss)]
        ok = max(dl) <= 0.02 * max(cpu_loss) and abs(held_gpu - held_cpu) <= 0.02 * held_cpu and gpu_loss[-1] < gpu_loss[0]
        rec.update({"device_name": info["device"], "gpu_wall_s": round(time.time() - t1, 2), "gpu_ms_all_steps": info["gpu_ms_last"],
                    "gpu_ms_per_step": round(info["gpu_ms_last"] / K, 3) if info["gpu_ms_last"] else None, "loss_cpu": cpu_loss, "loss_gpu": gpu_loss,
                    "max_step_loss_diff": max(dl), "heldout_cpu": held_cpu, "heldout_gpu": held_gpu, "weights_min_cos": wcos, "weights_max_rel": wrel, "pass": bool(ok)})
        json.dump(rec, open(f"{out}/s1-train-{dn}-{dev.split()[0].lower()}.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in rec.items() if k not in ("loss_cpu", "loss_gpu")}))
        for s in range(K): print(f"  step {s:3d}  cpu {cpu_loss[s]:.5f}  gpu {gpu_loss[s]:.5f}")
        print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
