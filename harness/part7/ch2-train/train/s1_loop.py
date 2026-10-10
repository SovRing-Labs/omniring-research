#!/usr/bin/env python3
"""CYCLONE-ARRAY C2 S1 learning gate on THE TRAINING LOOP — one recorded step on fixed resident buffers (gen/train_step.build_loop), the host
feeding each step's batch + step scalars and reading the loss (`omni-gpu session` stepwrite / stepread), vs the CPU engine's om_train_step on
the same model + REAL curriculum batches. Compared per step: the training loss; at the end: the held-out loss of both final models measured
by the SAME CPU engine, and every weight (cosine). Timed: GPU ms per step (one model) vs the CPU engine (4 threads, as a school harness).
  s1_loop.py [--dims small|school] [--steps 100] [--lr 3e-3] [--device L4] [--out DIR]"""
import ctypes, json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import LIB, BIN, DIMS, BUILD, batch, switches_on, t25_res, sw_dict, avoid_rows

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "school"); dims = DIMS[dn]; dev = opt("--device", "L4"); K = int(opt("--steps", "100")); lr = float(opt("--lr", "3e-3"))
    sw = [w for w in opt("--sw", "").split(",") if w]
    out = opt("--out", f"{P}/results/cyclone/c2-s1"); os.makedirs(out, exist_ok=True)
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B"))
    Lb = ctypes.CDLL(LIB); vp = ctypes.c_void_p; ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    Lb.om_create.restype = vp; Lb.om_create.argtypes = [ctypes.c_int] * 5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
    Lb.om_train_step.restype = ctypes.c_float; Lb.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]
    Lb.om_forward_loss.restype = ctypes.c_float; Lb.om_forward_loss.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
    for fn, rt in (("om_param_ptr", ctypes.POINTER(ctypes.c_float)), ("om_param_size", ctypes.c_long), ("om_param_name", ctypes.c_char_p)):
        getattr(Lb, fn).restype = rt; getattr(Lb, fn).argtypes = [vp, ctypes.c_int]
    Lb.om_nparams.argtypes = [vp]; Lb.om_threads(4)
    PR = (ctypes.c_int * 32)(*train_step.PRIMES); mk = lambda: Lb.om_create(V, D, L, H, T, PR, (D // H) // 2, 1234)
    h = mk(); aux, keep = switches_on(Lb, h, sw, D, H, L); names = [Lb.om_param_name(h, i).decode() for i in range(Lb.om_nparams(h))]
    params = [(n, np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),)).copy()) for i, n in enumerate(names)]
    PORT = "port" in sw; LOCAL = "local" in aux; WIN = PORT or LOCAL
    batches = [batch(V, T, B, seed=1000 + s, port=WIN) for s in range(K)]; hb = batch(V, T, B, seed=999_999, port=WIN); hx, hy = hb[0], hb[1]
    AVS = [avoid_rows(bt[1], V, 50 + s) for s, bt in enumerate(batches)] if "avoid" in aux else None
    def feed(hh, bt):                                                  # the harness's per-window data to the CPU engine
        if PORT: Lb.om_set_port_data(hh, bt[2].ctypes.data, bt[3].ctypes.data, B * T)
        if LOCAL: Lb.om_set_stage_data(hh, bt[4].ctypes.data, B * T)
    t0 = time.time(); cpu_loss, res25 = [], []
    for si, bt in enumerate(batches):                                  # the T25 residues of each batch, as the engine computed them
        x, y = bt[0], bt[1]
        feed(h, bt)
        if AVS is not None: Lb.om_set_avoid(h, AVS[si].ctypes.data, B * T)
        cpu_loss.append(float(Lb.om_train_step(h, x, y, B, T, lr)))
        if "t25" in sw: res25.append(t25_res(Lb, h, B * T))
    t_cpu = time.time() - t0
    w_cpu = {n: np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),)).copy() for i, n in enumerate(names)}
    if WIN: feed(h, hb)
    if AVS is not None: Lb.om_set_avoid(h, None, 0)
    held_cpu = float(Lb.om_forward_loss(h, hx, hy, B, T))
    with tempfile.TemporaryDirectory(prefix="omni-gpu-loop-") as Tm:
        text, ix, npass, nbuf = train_step.build_loop(dims, params, Tm, sw=sw_dict(sw, aux), aux=aux)
        hostin = ["x", "y", "eord", "est", "sc"] + [k for k in ("t25res", "rsBH", "stepv", "pkind", "pprop", "pstage", "pavoid") if k in ix]
        for s, bt in enumerate(batches):
            x, y = bt[0], bt[1]
            o_, st = train_step.batch_index(x, V); extra = []
            if "t25res" in ix: extra.append(("t25res", res25[s].astype(np.int32)))
            if "rsBH" in ix: extra.append(("rsBH", train_step.row_starts(x, B, T, aux["eos"], H)))
            if "stepv" in ix: extra.append(("stepv", np.array([s], np.int32)))
            if "pkind" in ix: extra += [("pkind", bt[2]), ("pprop", bt[3])]
            if "pstage" in ix: extra.append(("pstage", bt[4]))
            if "pavoid" in ix: extra.append(("pavoid", AVS[s]))
            for nm, arr in [("x", x), ("y", y), ("eord", o_), ("est", st), ("sc", train_step.step_scalars(s, lr))] + extra: np.asarray(arr).tofile(f"{Tm}/{nm}_{s}.bin")
        np.zeros(2, np.uint32).tofile(f"{Tm}/acc0.bin")
        lines = [f"stepwrite {ix[k]} {Tm}/{k}_{{s}}.bin" for k in hostin] + [f"stepwrite {ix['acc']} {Tm}/acc0.bin", f"stepread {ix['loss']}"]
        lines += [f"read {ix[f'w:{n}']}" for n in names]
        open(f"{Tm}/prog.txt", "w").write(text + "\n".join(lines) + "\n"); od = f"{Tm}/o"; t1 = time.time()
        r = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", str(K), "--out", od], capture_output=True, text=True, timeout=14400)
        rec = {"gate": "CYCLONE-ARRAY C2 S1 learning on the training loop (one recorded step, re-submitted) vs the CPU engine", "dims": dims, "steps": K, "switches": sw,
               "lr": lr, "device": dev, "passes": npass, "buffers": nbuf, "cpu_s": round(t_cpu, 2), "cpu_ms_per_step": round(1e3 * t_cpu / K, 2), "lib": LIB}
        if r.returncode:
            rec.update({"pass": False, "error": r.stderr[-1500:]}); print(json.dumps(rec)); json.dump(rec, open(f"{out}/s1-loop-{dn}-{dev.split()[0].lower()}{'-' + '-'.join(sw) if sw else ''}.json", "w"), indent=1); sys.exit(1)
        info = json.loads(r.stdout.strip().splitlines()[-1])
        gpu_loss = [float(v) for v in np.fromfile(f"{od}/steps{ix['loss']}.bin", np.float32)]
        gsum = float(open(f"{od}/gpu_ms_sum.txt").read())
        w_gpu = {n: np.fromfile(f"{od}/buf{ix[f'w:{n}']}.bin", np.float32)[:w_cpu[n].size] for n in names}
        h2 = mk(); _, keep2 = switches_on(Lb, h2, sw, D, H, L)
        for i, n in enumerate(names): np.ctypeslib.as_array(Lb.om_param_ptr(h2, i), shape=(w_cpu[n].size,))[:] = w_gpu[n]
        if WIN: feed(h2, hb)
        held_gpu = float(Lb.om_forward_loss(h2, hx, hy, B, T))
        wcos = min(float(np.dot(w_gpu[n].astype(np.float64), w_cpu[n]) / (np.linalg.norm(w_gpu[n].astype(np.float64)) * np.linalg.norm(w_cpu[n].astype(np.float64)))) for n in names)
        dl = [abs(g - c) for g, c in zip(gpu_loss, cpu_loss)]
        ok = len(gpu_loss) == K and abs(held_gpu - held_cpu) <= 0.02 * held_cpu and np.mean(gpu_loss[-10:]) < np.mean(gpu_loss[:10])
        rec.update({"device_name": info["device"], "gpu_wall_s": round(time.time() - t1, 2), "gpu_ms_per_step": round(gsum / K, 3), "wall_ms_per_step": round(info["ms_per_step"], 3),
                    "speedup_vs_cpu_4threads": round((1e3 * t_cpu / K) / (gsum / K), 2), "loss_cpu": cpu_loss, "loss_gpu": gpu_loss, "max_step_loss_diff": max(dl),
                    "mean_last10_cpu": float(np.mean(cpu_loss[-10:])), "mean_last10_gpu": float(np.mean(gpu_loss[-10:])), "heldout_cpu": held_cpu, "heldout_gpu": held_gpu,
                    "weights_min_cos": wcos, "pass": bool(ok)})
        json.dump(rec, open(f"{out}/s1-loop-{dn}-{dev.split()[0].lower()}{'-' + '-'.join(sw) if sw else ''}.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in rec.items() if k not in ("loss_cpu", "loss_gpu")}))
        for s in list(range(0, K, max(1, K // 10))) + [K - 1]: print(f"  step {s:4d}  cpu {cpu_loss[s]:.5f}  gpu {gpu_loss[s]:.5f}")
        print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
