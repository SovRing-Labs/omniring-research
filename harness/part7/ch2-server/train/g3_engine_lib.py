#!/usr/bin/env python3
"""GROW-RUN-0 G3 gate 1 — the GPU engine library (engine-gpu: libomnitrain_gpu.so, the engine's C ABI with om_train_step on the GPU)
against the CPU engine, in ONE process, driven the way thead-learn drives the engine: om_create → the school's om_set_* calls → per step
om_set_port_data / om_set_stage_data / om_set_avoid → om_train_step. Model A is trained through the library (GPU), model B (same seed,
same calls, same batches) through the CPU engine directly; held-out of both measured by the CPU engine with their own weights.
  g3_engine_lib.py [--dims small4] [--steps 40] [--device llvmpipe] [--sw t25,voice,plates,…] [--out DIR]"""
import ctypes, json, os, shutil, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import LIB, DIMS, batch, switches_on, avoid_rows

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "small4"); dims = DIMS[dn]; K = int(opt("--steps", "40")); dev = opt("--device", "llvmpipe"); lr = 3e-3
    sw = [w for w in opt("--sw", "t25,voice,plates,spark=1.0,p3=0.3,harm,port,copy,local,roles,route=0.5,avoid").split(",") if w]
    out = opt("--out", f"{P}/results/grow/g3"); os.makedirs(out, exist_ok=True)
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B")); N = B * T
    with tempfile.TemporaryDirectory(prefix="g3-lib-") as Tm:
        shutil.copy(f"{P}/engine-gpu/target/release/libomnitrain_gpu.so", Tm); shutil.copy(LIB, f"{Tm}/libomnitrain_trial.so")
        os.environ["OMNI_GPU_DEVICE"] = dev; os.environ["OMNI_GPU_ROOT"] = P; os.environ["TMPDIR"] = Tm
        G = ctypes.CDLL(f"{Tm}/libomnitrain_gpu.so"); C = ctypes.CDLL(f"{Tm}/libomnitrain_trial.so")   # the same loaded CPU engine
        vp = ctypes.c_void_p; ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
        for Lb in (G, C):
            Lb.om_create.restype = vp; Lb.om_create.argtypes = [ctypes.c_int] * 5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
            Lb.om_train_step.restype = ctypes.c_float; Lb.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]
            Lb.om_forward_loss.restype = ctypes.c_float; Lb.om_forward_loss.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
            Lb.om_threads(4)
        PR = (ctypes.c_int * 32)(*train_step.PRIMES)
        hA = G.om_create(V, D, L, H, T, PR, (D // H) // 2, 1234); hB = C.om_create(V, D, L, H, T, PR, (D // H) // 2, 1234)
        auxA, kA = switches_on(G, hA, sw, D, H, L); auxB, kB = switches_on(C, hB, sw, D, H, L)
        WIN = "port" in sw or "local" in auxA
        batches = [batch(V, T, B, seed=1000 + s, port=WIN) for s in range(K)]; hb = batch(V, T, B, seed=999_999, port=WIN)
        AVS = [avoid_rows(bt[1], V, 50 + s) for s, bt in enumerate(batches)] if "avoid" in auxA else None
        def feed(Lb, h, bt, s):
            if "port" in sw: Lb.om_set_port_data(h, bt[2].ctypes.data, bt[3].ctypes.data, N)
            if "local" in auxA: Lb.om_set_stage_data(h, bt[4].ctypes.data, N)
            if AVS is not None: Lb.om_set_avoid(h, AVS[s].ctypes.data if s >= 0 else None, N if s >= 0 else 0)
        la, lb_ = [], []; ta = tb = 0.0
        for s, bt in enumerate(batches):
            feed(G, hA, bt, s); t0 = time.time(); la.append(float(G.om_train_step(hA, bt[0], bt[1], B, T, lr))); ta += time.time() - t0
            feed(C, hB, bt, s); t0 = time.time(); lb_.append(float(C.om_train_step(hB, bt[0], bt[1], B, T, lr))); tb += time.time() - t0
        feed(C, hA, hb, -1); feed(C, hB, hb, -1)
        hA_ = float(C.om_forward_loss(hA, hb[0], hb[1], B, T)); hB_ = float(C.om_forward_loss(hB, hb[0], hb[1], B, T))
    ok = abs(hA_ - hB_) <= 0.02 * hB_ and np.mean(la[-5:]) < np.mean(la[:5])
    rec = {"gate": "GROW-RUN-0 G3: libomnitrain_gpu.so (GPU step behind the engine's C ABI) vs the CPU engine, same calls + batches", "dims": dims,
           "steps": K, "switches": sw, "device": dev, "loss_lib": la, "loss_cpu": lb_, "heldout_lib": hA_, "heldout_cpu": hB_,
           "s_per_step_lib": round(ta / K, 3), "s_per_step_cpu": round(tb / K, 3), "pass": bool(ok)}
    json.dump(rec, open(f"{out}/g3-lib-{dn}-{dev}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k not in ("loss_lib", "loss_cpu")}))
    for s in list(range(0, K, max(1, K // 8))) + [K - 1]: print(f"  step {s:3d}  lib {la[s]:.5f}  cpu {lb_[s]:.5f}")
    print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
