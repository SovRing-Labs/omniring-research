#!/usr/bin/env python3
"""CYCLONE-ARRAY C2 S2 — THE REPLICA AXIS: R THEAD models trained in ONE recorded step (every pass one launch for all R: T0B / T2B
kernels, replica = gid.z / WorkgroupId.z, each model's weights / moments / activations at its own slice; float64 reductions per replica).
Each model has its own seed and its own curriculum batches. Gates, per replica r:
  A (exactness of the axis): the batched run's per-step losses and final weights are BIT-IDENTICAL to model r trained alone (R = 1) on the GPU;
  B (learning): model r vs the CPU engine's om_train_step on the same model + batches — held-out loss within 2 %, loss falling (= s1_loop).
Timed: GPU ms per step for the R-batch vs R single-model steps → tokens/s.
  s2_replica.py [--dims small|school] [--R 3] [--steps 20] [--lr 3e-3] [--device llvmpipe] [--single all|first|none] [--out DIR]"""
import ctypes, json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import LIB, BIN, DIMS, batch

def engine(dims):
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B"))
    Lb = ctypes.CDLL(LIB); vp = ctypes.c_void_p; ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    Lb.om_create.restype = vp; Lb.om_create.argtypes = [ctypes.c_int] * 5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
    Lb.om_train_step.restype = ctypes.c_float; Lb.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]
    Lb.om_forward_loss.restype = ctypes.c_float; Lb.om_forward_loss.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
    for fn, rt in (("om_param_ptr", ctypes.POINTER(ctypes.c_float)), ("om_param_size", ctypes.c_long), ("om_param_name", ctypes.c_char_p)):
        getattr(Lb, fn).restype = rt; getattr(Lb, fn).argtypes = [vp, ctypes.c_int]
    Lb.om_nparams.argtypes = [vp]; Lb.om_threads(4)
    PR = (ctypes.c_int * 32)(*train_step.PRIMES)
    return Lb, (lambda seed: Lb.om_create(V, D, L, H, T, PR, (D // H) // 2, seed))

def weights(Lb, h):
    return [(Lb.om_param_name(h, i).decode(), np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),)).copy()) for i in range(Lb.om_nparams(h))]

def run_gpu(dims, params_R, batches_R, lr, dev, Tm):
    """R models in one recorded step, K steps host-fed → (losses (K, R), [{name: final weights}] per replica, GPU ms per step, wall ms, info)"""
    V = dims["V"]; R = len(params_R); K = len(batches_R[0]); names = [n for n, _ in params_R[0]]
    text, ix, npass, nbuf = train_step.build_loop(dims, params_R[0], Tm, params_R=params_R if R > 1 else None)
    for s in range(K):
        xs, ys, os_, ss = [], [], [], []
        for r in range(R):
            x, y = batches_R[r][s]; o_, st = train_step.batch_index(x, V); xs.append(x); ys.append(y); os_.append(o_); ss.append(st)
        for nm, arr in (("x", xs), ("y", ys), ("eord", os_), ("est", ss), ("sc", [train_step.step_scalars(s, lr)] * R)):
            np.ascontiguousarray(np.stack(arr)).tofile(f"{Tm}/{nm}_{s}.bin")
    np.zeros(2 * R, np.uint32).tofile(f"{Tm}/acc0.bin")
    lines = [f"stepwrite {ix[k]} {Tm}/{k}_{{s}}.bin" for k in ("x", "y", "eord", "est", "sc")] + [f"stepwrite {ix['acc']} {Tm}/acc0.bin", f"stepread {ix['loss']}"]
    lines += [f"read {ix[f'w:{n}']}" for n in names]
    open(f"{Tm}/prog.txt", "w").write(text + "\n".join(lines) + "\n"); od = f"{Tm}/o"; t1 = time.time()
    r_ = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", str(K), "--out", od], capture_output=True, text=True, timeout=14400)
    if r_.returncode: raise RuntimeError(r_.stderr[-1500:])
    info = json.loads(r_.stdout.strip().splitlines()[-1]); info.update({"passes": npass, "buffers": nbuf, "wall_s": round(time.time() - t1, 2)})
    loss = np.fromfile(f"{od}/steps{ix['loss']}.bin", np.float32).reshape(K, R)
    W = [{} for _ in range(R)]
    for n, w in params_R[0]:
        a = np.fromfile(f"{od}/buf{ix[f'w:{n}']}.bin", np.float32)[:R * w.size].reshape(R, w.size)
        for r in range(R): W[r][n] = a[r].copy()
    gsum = float(open(f"{od}/gpu_ms_sum.txt").read())
    return loss, W, gsum / K, info

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "small"); dims = DIMS[dn]; dev = opt("--device", "llvmpipe"); K = int(opt("--steps", "20")); lr = float(opt("--lr", "3e-3"))
    R = int(opt("--R", "3")); single = opt("--single", "all"); CK = int(opt("--cpu-check", str(R)))   # CPU engine reference: first CK replicas
    out = opt("--out", f"{P}/results/cyclone/c2-s2"); os.makedirs(out, exist_ok=True)
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B")); N = B * T
    Lb, mk = engine(dims)
    hs = [mk(1234 + r) for r in range(R)]; params_R = [weights(Lb, h) for h in hs]; names = [n for n, _ in params_R[0]]
    batches_R = [[batch(V, T, B, seed=1000 + s + 100_000 * r) for s in range(K)] for r in range(R)]; hx, hy = batch(V, T, B, seed=999_999)
    rec = {"gate": "CYCLONE-ARRAY C2 S2 replica axis: R models in one recorded training step — A: each replica bit-identical to its own R=1 GPU run; "
                   "B: each replica learns like the CPU engine (held-out within 2 %, loss falling)", "dims": dims, "R": R, "steps": K, "lr": lr, "device": dev, "lib": LIB}
    # CPU engine: each model trained alone
    t0 = time.time(); cpu_loss = [[float(Lb.om_train_step(hs[r], x, y, B, T, lr)) for x, y in batches_R[r]] for r in range(CK)]; t_cpu = time.time() - t0
    held_cpu = [float(Lb.om_forward_loss(h, hx, hy, B, T)) for h in hs[:CK]]
    S = sys.argv[0]
    with tempfile.TemporaryDirectory(prefix="omni-gpu-s2-") as Tm:
        os.makedirs(f"{Tm}/R")
        try: lossR, WR, msR, infoR = run_gpu(dims, params_R, batches_R, lr, dev, f"{Tm}/R")
        except RuntimeError as e:                                              # keep a record of a failed GPU run (e.g. device lost)
            rec.update({"pass": False, "error": str(e)[-1500:]}); json.dump(rec, open(f"{out}/s2-replica-{dn}-R{R}-{dev.split()[0].lower()}.json", "w"), indent=1)
            print(json.dumps(rec)); sys.exit(1)
        singles = range(R) if single == "all" else range(1) if single == "first" else range(0)
        one = {}
        for r in singles:
            os.makedirs(f"{Tm}/s{r}"); l1, W1, ms1, info1 = run_gpu(dims, [params_R[r]], [batches_R[r]], lr, dev, f"{Tm}/s{r}"); one[r] = (l1[:, 0], W1[0], ms1, info1)
    per = []; okA = okB = True
    for r in range(CK):
        h2 = mk(1234 + r)
        for i, n in enumerate(names): np.ctypeslib.as_array(Lb.om_param_ptr(h2, i), shape=(WR[r][n].size,))[:] = WR[r][n]
        held_gpu = float(Lb.om_forward_loss(h2, hx, hy, B, T)); gl = [float(v) for v in lossR[:, r]]
        b = abs(held_gpu - held_cpu[r]) <= 0.02 * held_cpu[r] and np.mean(gl[-max(1, K // 10):]) < np.mean(gl[:max(1, K // 10)])
        row = {"replica": r, "seed": 1234 + r, "loss_gpu": gl, "loss_cpu": cpu_loss[r], "max_step_loss_diff_vs_cpu": max(abs(g - c) for g, c in zip(gl, cpu_loss[r])),
               "heldout_gpu": held_gpu, "heldout_cpu": held_cpu[r], "B_learning": bool(b)}
        if r in one:
            l1, W1 = one[r][0], one[r][1]
            same_loss = bool(np.array_equal(l1.view(np.uint32), lossR[:, r].view(np.uint32)))
            wdiff = sum(int((W1[n].view(np.uint32) != WR[r][n].view(np.uint32)).sum()) for n in names)
            row.update({"A_loss_bit_identical": same_loss, "A_weight_words_different": wdiff, "A_exact": bool(same_loss and wdiff == 0)})
            okA &= row["A_exact"]
        okB &= b; per.append(row)
    ms1 = float(np.mean([v[2] for v in one.values()])) if one else None
    rec.update({"device_name": infoR["device"], "passes_per_step": infoR["passes"], "buffers": infoR["buffers"], "bytes_resident_R": infoR["bytes"],
                "bytes_resident_1": one[0][3]["bytes"] if 0 in one else None,
                "gpu_ms_per_step_R": round(msR, 3), "gpu_ms_per_step_1": round(ms1, 3) if ms1 else None,
                "tokens_per_s_R": round(R * N / (msR / 1e3), 1), "tokens_per_s_1": round(N / (ms1 / 1e3), 1) if ms1 else None,
                "speedup_vs_R_singles": round(R * ms1 / msR, 2) if ms1 else None, "cpu_ms_per_step_per_model": round(1e3 * t_cpu / (K * max(1, CK)), 2), "cpu_checked": CK,
                "A_pass": bool(okA) if one else None, "B_pass": bool(okB), "pass": bool(okA and okB), "replicas": per})
    tag = f"s2-replica-{dn}-R{R}-{dev.split()[0].lower()}"
    json.dump(rec, open(f"{out}/{tag}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != "replicas"}))
    for row in per:
        print(f"  replica {row['replica']}  A {row.get('A_exact', '-')}  (weights differ {row.get('A_weight_words_different', '-')})  "
              f"held-out gpu {row['heldout_gpu']:.4f} cpu {row['heldout_cpu']:.4f}  loss {row['loss_gpu'][0]:.3f}→{row['loss_gpu'][-1]:.3f}  B {row['B_learning']}")
    print("PASS" if rec["pass"] else "FAIL"); sys.exit(0 if rec["pass"] else 1)

if __name__ == "__main__":
    main()
