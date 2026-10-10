#!/usr/bin/env python3
"""GROW-RUN-0 G3b-2 — ONE UNIT TRAINING RESIDENT WITH THE SCHOOL SWITCHES: R harness models in one recorded step in the cyclone's form
(option 3: the cyclone holds C, each harness Δ_h; s3_centre) with the school step's switches on (G2: s1_loop --sw), vs the reference: R CPU
engines with the same switches, each fed its own windows' extras, then the SHM-BUS sync (runtime/src/shmbus.rs / cloud/bus_coord.py).
Gate: every harness's held-out (the same CPU engine, switches on, measures both) within 2 %, loss falling. Recorded: VRAM, GPU ms per unit
step vs the CPU engines' ms per step, every harness's held-out + losses.
  s4_unit_school.py [--dims school] [--R 8] [--steps 30] [--K 0.1] [--lr 3e-3] [--sw t25,voice,plates,…] [--device A40] [--out DIR]"""
import ctypes, json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import LIB, BIN, DIMS, batch, switches_on, t25_res, sw_dict, avoid_rows
SCHOOL_SW = "t25,voice,plates,spark=1.0,p3=0.3,harm,port,copy,local,roles,route=0.5,avoid"   # G2's all-switches set (thresholds that fire)


def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "school"); dims = DIMS[dn]; dev = opt("--device", "A40"); S = int(opt("--steps", "30")); lr = float(opt("--lr", "3e-3"))
    R = int(opt("--R", "8")); K = float(opt("--K", "0.1")); sw = [w for w in opt("--sw", SCHOOL_SW).split(",") if w]
    out = opt("--out", f"{P}/results/cyclone/g3b"); os.makedirs(out, exist_ok=True)
    TB = int(opt("--cpu-twice", "0"))   # > 0: NO GPU — the CPU reference twice (4 threads, then TB threads): the engine's own noise floor per harness
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B"))
    Lb = ctypes.CDLL(LIB); vp = ctypes.c_void_p; ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    Lb.om_create.restype = vp; Lb.om_create.argtypes = [ctypes.c_int] * 5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
    Lb.om_train_step.restype = ctypes.c_float; Lb.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]
    Lb.om_forward_loss.restype = ctypes.c_float; Lb.om_forward_loss.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
    for fn, rt in (("om_param_ptr", ctypes.POINTER(ctypes.c_float)), ("om_param_size", ctypes.c_long), ("om_param_name", ctypes.c_char_p)):
        getattr(Lb, fn).restype = rt; getattr(Lb, fn).argtypes = [vp, ctypes.c_int]
    Lb.om_nparams.argtypes = [vp]; Lb.om_threads(4)
    PR = (ctypes.c_int * 32)(*train_step.PRIMES); mk = lambda: Lb.om_create(V, D, L, H, T, PR, (D // H) // 2, 1234)
    hs = [mk() for _ in range(R)]; auxs = [switches_on(Lb, h, sw, D, H, L) for h in hs]; aux = auxs[0][0]
    names = [Lb.om_param_name(hs[0], i).decode() for i in range(Lb.om_nparams(hs[0]))]
    ptr = lambda h, i: np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),))
    params = [(n, ptr(hs[0], i).copy()) for i, n in enumerate(names)]; params_R = [[(n, ptr(h, i).copy()) for i, n in enumerate(names)] for h in hs]
    PORT = "port" in sw; LOCAL = "local" in aux; WIN = PORT or LOCAL
    bat = [[batch(V, T, B, seed=1000 + s + 100_000 * r, port=WIN) for s in range(S)] for r in range(R)]
    hb = batch(V, T, B, seed=999_999, port=WIN); hx, hy = hb[0], hb[1]
    AVS = [[avoid_rows(bat[r][s][1], V, 50 + s + 1000 * r) for s in range(S)] for r in range(R)] if "avoid" in aux else None
    def feed(hh, bt):
        if PORT: Lb.om_set_port_data(hh, bt[2].ctypes.data, bt[3].ctypes.data, B * T)
        if LOCAL: Lb.om_set_stage_data(hh, bt[4].ctypes.data, B * T)
    # CPU reference: R engines (switches on), each its own batches + extras, then the SHM-BUS sync
    cpu_loss = np.zeros((S, R), np.float32); res25 = [[None] * S for _ in range(R)]; k32 = np.float32(K); t0 = time.time()
    for s in range(S):
        for r in range(R):
            bt = bat[r][s]; feed(hs[r], bt)
            if AVS is not None: Lb.om_set_avoid(hs[r], AVS[r][s].ctypes.data, B * T)
            cpu_loss[s, r] = Lb.om_train_step(hs[r], bt[0], bt[1], B, T, lr)
            if "t25" in sw: res25[r][s] = t25_res(Lb, hs[r], B * T)
        for i in range(len(names)):
            ws = [ptr(h, i) for h in hs]; mean = np.stack(ws).astype(np.float64).mean(axis=0).astype(np.float32)
            for w in ws: w[:] = w + k32 * (mean - w)
    t_cpu = time.time() - t0
    W_cpu = [{n: ptr(h, i).copy() for i, n in enumerate(names)} for h in hs]
    if TB:                                                                              # the same R engines again, other thread count (summation order)
        Lb.om_threads(TB); hs2 = [mk() for _ in range(R)]; aux2 = [switches_on(Lb, h, sw, D, H, L) for h in hs2]
        cl2 = np.zeros((S, R), np.float32)
        for s_ in range(S):
            for r in range(R):
                bt = bat[r][s_]; feed(hs2[r], bt)
                if AVS is not None: Lb.om_set_avoid(hs2[r], AVS[r][s_].ctypes.data, B * T)
                cl2[s_, r] = Lb.om_train_step(hs2[r], bt[0], bt[1], B, T, lr)
            for i in range(len(names)):
                ws = [ptr(h, i) for h in hs2]; mean = np.stack(ws).astype(np.float64).mean(axis=0).astype(np.float32)
                for w in ws: w[:] = w + k32 * (mean - w)
        W2 = [{n: ptr(h, i).copy() for i, n in enumerate(names)} for h in hs2]; Lb.om_threads(4)
    def held(W):                                                                       # one CPU engine, switches on, measures every model
        h2 = mk(); keep2 = switches_on(Lb, h2, sw, D, H, L)                          # keep2: buffers the engine points into (must stay alive)
        if WIN: feed(h2, hb)
        out_ = []
        for w in W:
            for i, n in enumerate(names): ptr(h2, i)[:] = w[n]
            out_.append(float(Lb.om_forward_loss(h2, hx, hy, B, T)))
        return out_
    if TB:
        h1, h2_ = held(W_cpu), held(W2); gap = [abs(a_ - b_) / a_ for a_, b_ in zip(h1, h2_)]
        div = [int(np.argmax(np.abs(cpu_loss[:, r] - cl2[:, r]) > 1e-3 * np.abs(cpu_loss[:, r]))) for r in range(R)]
        r_ = {"probe": "CPU engine vs itself (threads 4 vs %d), same harnesses, batches, switches" % TB, "dims": dims, "R": R, "steps": S, "switches": sw,
              "heldout_t4": h1, "heldout_tb": h2_, "rel_gap": gap, "max_rel_gap": max(gap), "first_step_loss_differs_1e-3": div,
              "loss_t4": cpu_loss.tolist(), "loss_tb": cl2.tolist()}
        json.dump(r_, open(f"{out}/g3b2-cpu-noise-{dn}-R{R}.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in r_.items() if not k.startswith("loss_")})); sys.exit(0)
    rec = {"gate": "GROW-RUN-0 G3b-2: one unit (R harness models, option 3 centre form) with the school switches on the GPU vs R CPU engines + SHM-BUS sync",
           "dims": dims, "R": R, "steps": S, "K": K, "lr": lr, "switches": sw, "device": dev, "lib": LIB,
           "cpu_ms_per_unit_step": round(1e3 * t_cpu / S, 1)}
    with tempfile.TemporaryDirectory(prefix="omni-gpu-g3b-") as Tm:
        try:
            text, ix, npass, nbuf = train_step.build_loop(dims, params, Tm, params_R=params_R, form="centre", K=K, sw=sw_dict(sw, aux), aux=aux)
        except Exception as e:
            rec.update({"pass": False, "error": f"build_loop: {type(e).__name__}: {e}"}); json.dump(rec, open(f"{out}/g3b2-{dn}-R{R}-{dev.lower()}.json", "w"), indent=1)
            print(json.dumps(rec)); sys.exit(1)
        hostin = ["x", "y", "eord", "est", "sc"] + [k for k in ("t25res", "rsBH", "stepv", "pkind", "pprop", "pstage", "pavoid") if k in ix]
        for s in range(S):
            cols = {k: [] for k in hostin}
            for r in range(R):
                bt = bat[r][s]; x, y = bt[0], bt[1]; o_, st = train_step.batch_index(x, V)
                v = {"x": x, "y": y, "eord": o_, "est": st, "sc": train_step.step_scalars(s, lr)}
                if "t25res" in ix: v["t25res"] = res25[r][s].astype(np.int32)
                if "rsBH" in ix: v["rsBH"] = train_step.row_starts(x, B, T, aux["eos"], H)
                if "stepv" in ix: v["stepv"] = np.array([s], np.int32)
                if "pkind" in ix: v["pkind"], v["pprop"] = bt[2], bt[3]
                if "pstage" in ix: v["pstage"] = bt[4]
                if "pavoid" in ix: v["pavoid"] = AVS[r][s]
                for k in hostin: cols[k].append(np.asarray(v[k]))
            for k in hostin: np.ascontiguousarray(np.stack(cols[k])).tofile(f"{Tm}/{k}_{s}.bin")
        np.zeros(2 * R, np.uint32).tofile(f"{Tm}/acc0.bin")
        lines = [f"stepwrite {ix[k]} {Tm}/{k}_{{s}}.bin" for k in hostin] + [f"stepwrite {ix['acc']} {Tm}/acc0.bin", f"stepread {ix['loss']}"]
        lines += [f"read {ix[k]}" for k in ix if k[:2] in ("C:", "D:")]
        open(f"{Tm}/prog.txt", "w").write(text + "\n".join(lines) + "\n"); od = f"{Tm}/o"; t1 = time.time()
        r_ = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", str(S), "--out", od], capture_output=True, text=True, timeout=7200)
        if r_.returncode:
            rec.update({"pass": False, "error": r_.stderr[-1500:]}); json.dump(rec, open(f"{out}/g3b2-{dn}-R{R}-{dev.lower()}.json", "w"), indent=1)
            print(json.dumps(rec)); sys.exit(1)
        info = json.loads(r_.stdout.strip().splitlines()[-1])
        gl = np.fromfile(f"{od}/steps{ix['loss']}.bin", np.float32).reshape(S, R); gms = float(open(f"{od}/gpu_ms_sum.txt").read()) / S
        rd = lambda k: np.fromfile(f"{od}/buf{ix[k]}.bin", np.float32)
        W_gpu = [{} for _ in range(R)]
        for n, w in params:
            arr = rd(f"C:{n}")[:w.size][None, :] + rd(f"D:{n}")[:R * w.size].reshape(R, w.size)
            for r in range(R): W_gpu[r][n] = arr[r].astype(np.float32)
    hc, hg = held(W_cpu), held(W_gpu)
    ok = all(abs(g - c) <= 0.02 * c for g, c in zip(hg, hc)) and all(gl[-5:, r].mean() < gl[:5, r].mean() for r in range(R))
    rec.update({"device_name": info["device"], "passes_per_step": npass, "buffers": nbuf, "bytes_resident": info.get("bytes"),
                "gb_resident": round((info.get("bytes") or 0) / 1e9, 3), "gpu_ms_per_unit_step": round(gms, 2), "gpu_wall_s": round(time.time() - t1, 1),
                "speedup_vs_cpu_engines": round(rec["cpu_ms_per_unit_step"] / gms, 1) if gms else None,
                "heldout_cpu": hc, "heldout_gpu": hg, "loss_first_last_cpu": [cpu_loss[0].tolist(), cpu_loss[-1].tolist()],
                "loss_first_last_gpu": [gl[0].tolist(), gl[-1].tolist()], "pass": bool(ok)})
    json.dump(rec, open(f"{out}/g3b2-{dn}-R{R}-{dev.lower()}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if not k.startswith("loss_")}))
    for r in range(R): print(f"  harness {r}  held-out gpu {hg[r]:.4f} cpu {hc[r]:.4f}  loss {gl[0, r]:.3f}→{gl[-1, r]:.3f}")
    print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
