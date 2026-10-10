#!/usr/bin/env python3
"""GROW-RUN-0 G3b-3 — THE ARRAY TRAINING RESIDENT: U units × `per` harness models in ONE recorded step, each unit's cyclone holding its C and
every harness its Δ (option 3, `build_loop(units=U)`: wsum_g / dset_g read the harness's own unit), the unit means on the cyclone's W2b
hub_mean, and with --ring the floor ring on the unit centres (W2c: per floor of 5 units, around-mean + centre-mean, then the two pulls, in
cyclone.rs order) — optionally with the school switches on (--sw, as s4_unit_school).
Gates:
  --exact (no ring): the U-unit array's per-step losses and final C + Δ == U separate one-unit runs (build_loop units=1), bit for bit
  learning: R CPU engines (switches on) → per unit mean (w2b_hub.mean_ref) → floor ring (mean_ref / pull_ref, rung.py's arithmetic) → each
            harness pulled to its unit (pull_ref): every harness's held-out within 2 % of the GPU's, loss falling. VRAM + ms recorded.
  s5_array.py [--dims small4|school] [--units 5] [--per 8] [--ring] [--k2 0.25] [--k2c 0.10] [--K 0.1] [--steps 10] [--sw …|none]
              [--exact] [--device A40] [--out DIR]"""
import ctypes, json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
sys.path.insert(0, f"{P}/tests/cyclone")
import train_step
from s1_grad import LIB, BIN, DIMS, batch, switches_on, t25_res, sw_dict, avoid_rows
from w2b_hub import mean_ref, pull_ref
SCHOOL_SW = "t25,voice,plates,spark=1.0,p3=0.3,harm,port,copy,local,roles,route=0.5,avoid"


def gpu_run(dims, params, params_R, Tm, K, units, ring, sw, aux, hostin_fn, S, dev):
    text, ix, npass, nbuf = train_step.build_loop(dims, params, Tm, params_R=params_R, form="centre", K=K, sw=sw_dict(sw, aux) if sw else None,
                                                  aux=aux if sw else None, units=units, ring=ring)
    hostin = ["x", "y", "eord", "est", "sc"] + [k for k in ("t25res", "rsBH", "stepv", "pkind", "pprop", "pstage", "pavoid") if k in ix]
    R = len(params_R)
    for s in range(S):
        cols = {k: [] for k in hostin}
        for r in range(R):
            v = hostin_fn(r, s, ix)
            for k in hostin: cols[k].append(np.asarray(v[k]))
        for k in hostin: np.ascontiguousarray(np.stack(cols[k])).tofile(f"{Tm}/{k}_{s}.bin")
    np.zeros(2 * R, np.uint32).tofile(f"{Tm}/acc0.bin")
    lines = [f"stepwrite {ix[k]} {Tm}/{k}_{{s}}.bin" for k in hostin] + [f"stepwrite {ix['acc']} {Tm}/acc0.bin", f"stepread {ix['loss']}"]
    lines += [f"read {ix[k]}" for k in ix if k[:2] in ("C:", "D:")]
    open(f"{Tm}/prog.txt", "w").write(text + "\n".join(lines) + "\n"); od = f"{Tm}/o"; t1 = time.time()
    r_ = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", str(S), "--out", od], capture_output=True, text=True, timeout=7200)
    if r_.returncode: raise RuntimeError(r_.stderr[-1500:])
    info = json.loads(r_.stdout.strip().splitlines()[-1]); info.update(passes=npass, buffers=nbuf, wall_s=round(time.time() - t1, 1))
    loss = np.fromfile(f"{od}/steps{ix['loss']}.bin", np.float32).reshape(S, R); gms = float(open(f"{od}/gpu_ms_sum.txt").read()) / S
    per = R // units; W = [{} for _ in range(R)]; raw = {}
    for n, w in params:
        c = np.fromfile(f"{od}/buf{ix[f'C:{n}']}.bin", np.float32)[:units * w.size].reshape(units, w.size)
        d = np.fromfile(f"{od}/buf{ix[f'D:{n}']}.bin", np.float32)[:R * w.size].reshape(R, w.size); raw[n] = (c, d)
        for r in range(R): W[r][n] = (c[r // per] + d[r]).astype(np.float32)
    return loss, W, raw, gms, info


def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "small4"); dims = DIMS[dn]; dev = opt("--device", "llvmpipe"); S = int(opt("--steps", "10")); lr = float(opt("--lr", "3e-3"))
    U = int(opt("--units", "5")); per = int(opt("--per", "8")); R = U * per; K = float(opt("--K", "0.1"))
    ring = {"k2": float(opt("--k2", "0.25")), "k2c": float(opt("--k2c", "0.10"))} if "--ring" in a else None
    swa = opt("--sw", "none"); sw = [] if swa == "none" else [w for w in (SCHOOL_SW if swa == "school" else swa).split(",") if w]
    GO = "--gpu-only" in a   # no CPU reference — only "does every model's GPU loss fall" (fast size sweeps)
    exact = "--exact" in a; out = opt("--out", f"{P}/results/cyclone/g3b"); os.makedirs(out, exist_ok=True)
    assert not ring or U % 5 == 0, "the floor ring needs 5 units per floor"
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B"))
    Lb = ctypes.CDLL(LIB); vp = ctypes.c_void_p; ip = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    Lb.om_create.restype = vp; Lb.om_create.argtypes = [ctypes.c_int] * 5 + [vp, ctypes.c_int, ctypes.c_ulonglong]
    Lb.om_train_step.restype = ctypes.c_float; Lb.om_train_step.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int, ctypes.c_float]
    Lb.om_forward_loss.restype = ctypes.c_float; Lb.om_forward_loss.argtypes = [vp, ip, ip, ctypes.c_int, ctypes.c_int]
    for fn, rt in (("om_param_ptr", ctypes.POINTER(ctypes.c_float)), ("om_param_size", ctypes.c_long), ("om_param_name", ctypes.c_char_p)):
        getattr(Lb, fn).restype = rt; getattr(Lb, fn).argtypes = [vp, ctypes.c_int]
    Lb.om_nparams.argtypes = [vp]; Lb.om_threads(4)
    PR = (ctypes.c_int * 32)(*train_step.PRIMES); mk = lambda seed: Lb.om_create(V, D, L, H, T, PR, (D // H) // 2, seed)
    hs = [mk(1234 + r // per) for r in range(R)]                                 # every unit starts from its own model; a unit's harnesses from one
    keeps = [switches_on(Lb, h, sw, D, H, L) if sw else ({}, None) for h in hs]; aux = keeps[0][0]
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
    rec = {"gate": "GROW-RUN-0 G3b-3: the array (U units × per harnesses, each unit's cyclone holds C, floor ring) training in one GPU step",
           "dims": dims, "units": U, "per": per, "R": R, "ring": ring, "switches": sw, "steps": S, "K": K, "lr": lr, "device": dev, "lib": LIB}
    tag = f"g3b3-{dn}-U{U}x{per}{'-ring' if ring else ''}{'-sw' if sw else ''}{'-exact' if exact else ''}-{dev.split()[0].lower()}"
    # CPU reference (its T25 residues feed the GPU's t25res input, as s1_loop)
    cpu_loss = np.zeros((S, R), np.float32); res25 = [[None] * S for _ in range(R)]; t0 = time.time()
    ko = np.tile([0, 1, 1, 1, 1], (U // 5, 1)).astype(np.uint32) if ring else None; kc = np.tile([1, 0, 0, 0, 0], (U // 5, 1)).astype(np.uint32) if ring else None
    rko = np.tile([0.0] + [ring["k2"]] * 4, (U // 5, 1)).astype(np.float32) if ring else None
    rkc = np.tile([ring["k2c"], 0, 0, 0, 0], (U // 5, 1)).astype(np.float32) if ring else None
    keep = np.ones((U, per), np.uint32); kf = np.full((U, per), K, np.float32)
    for s in (range(0) if GO else range(S)):
        for r in range(R):
            bt = bat[r][s]; feed(hs[r], bt)
            if AVS is not None: Lb.om_set_avoid(hs[r], AVS[r][s].ctypes.data, B * T)
            cpu_loss[s, r] = Lb.om_train_step(hs[r], bt[0], bt[1], B, T, lr)
            if "t25" in sw: res25[r][s] = t25_res(Lb, hs[r], B * T)
        for i in range(len(names)):
            w = np.stack([ptr(h, i) for h in hs]).reshape(U, per, -1).astype(np.float32); m = mean_ref(w, keep)
            if ring:
                for f in range(U // 5):
                    mf = m[f * 5:(f + 1) * 5][None]; tc = mean_ref(mf, ko[f:f + 1]); cc = mean_ref(mf, kc[f:f + 1])
                    m[f * 5:(f + 1) * 5] = pull_ref(pull_ref(mf, cc, rko[f:f + 1]), tc, rkc[f:f + 1])[0]
            w2 = pull_ref(w, m, kf).reshape(R, -1)
            for r, h in enumerate(hs): ptr(h, i)[:] = w2[r]
    t_cpu = time.time() - t0
    W_cpu = [{n: ptr(h, i).copy() for i, n in enumerate(names)} for h in hs]
    def hostin_fn(r, s, ix):
        bt = bat[r][s]; x, y = bt[0], bt[1]; o_, st = train_step.batch_index(x, V)
        v = {"x": x, "y": y, "eord": o_, "est": st, "sc": train_step.step_scalars(s, lr)}
        if "t25res" in ix: v["t25res"] = res25[r][s].astype(np.int32)
        if "rsBH" in ix: v["rsBH"] = train_step.row_starts(x, B, T, aux["eos"], H)
        if "stepv" in ix: v["stepv"] = np.array([s], np.int32)
        if "pkind" in ix: v["pkind"], v["pprop"] = bt[2], bt[3]
        if "pstage" in ix: v["pstage"] = bt[4]
        if "pavoid" in ix: v["pavoid"] = AVS[r][s]
        return v
    try:
        with tempfile.TemporaryDirectory(prefix="omni-gpu-g3b3-") as Tm:
            gl, W_gpu, raw, gms, info = gpu_run(dims, params, params_R, Tm, K, U, ring, sw, aux, hostin_fn, S, dev)
            if exact:                                                          # U separate one-unit runs: losses + C + Δ bit for bit
                bad = 0
                for u in range(U):
                    sub = params_R[u * per:(u + 1) * per]; T2 = f"{Tm}/u{u}"; os.makedirs(T2)
                    lu, _, ru, _, _ = gpu_run(dims, params, sub, T2, K, 1, None, sw, aux, lambda r, s, ix: hostin_fn(u * per + r, s, ix), S, dev)
                    bad += int((lu.view(np.uint32) != gl[:, u * per:(u + 1) * per].view(np.uint32)).sum())
                    for n, _ in params:
                        bad += int((ru[n][0][0].view(np.uint32) != raw[n][0][u].view(np.uint32)).sum())
                        bad += int((ru[n][1].view(np.uint32) != raw[n][1][u * per:(u + 1) * per].view(np.uint32)).sum())
                rec["exact_mismatched_words"] = bad
    except RuntimeError as e:
        rec.update({"pass": False, "error": str(e)[-1500:]}); json.dump(rec, open(f"{out}/{tag}.json", "w"), indent=1); print(json.dumps(rec)); sys.exit(1)
    if GO:
        fall = [float(gl[-1, r] / gl[0, r]) for r in range(R)]
        rec.update({"gpu_only": True, "gb_resident": round((info.get("bytes") or 0) / 1e9, 3), "gpu_ms_per_array_step": round(gms, 2),
                    "loss_first_gpu": gl[0].tolist(), "loss_last_gpu": gl[-1].tolist(), "loss_ratio_max": max(fall), "pass": max(fall) < 0.95})
        json.dump(rec, open(f"{out}/{tag}-gpuonly.json", "w"), indent=1)
        print(json.dumps({k: rec[k] for k in ("R", "units", "per", "gb_resident", "gpu_ms_per_array_step", "loss_ratio_max", "pass")})); sys.exit(0 if rec["pass"] else 1)
    def held(W):
        h2 = mk(1234); k2_ = switches_on(Lb, h2, sw, D, H, L) if sw else None    # k2_: buffers the engine points into (must stay alive)
        if WIN: feed(h2, hb)
        o_ = []
        for w in W:
            for i, n in enumerate(names): ptr(h2, i)[:] = w[n]
            o_.append(float(Lb.om_forward_loss(h2, hx, hy, B, T)))
        return o_
    hc, hg = held(W_cpu), held(W_gpu)
    ok = all(abs(g - c) <= 0.02 * c for g, c in zip(hg, hc)) and all(gl[-3:, r].mean() < gl[:3, r].mean() for r in range(R))
    if exact: ok = ok and rec["exact_mismatched_words"] == 0
    rec.update({"device_name": info["device"], "passes_per_step": info["passes"], "buffers": info["buffers"], "bytes_resident": info.get("bytes"),
                "gb_resident": round((info.get("bytes") or 0) / 1e9, 3), "gpu_ms_per_array_step": round(gms, 2), "cpu_ms_per_array_step": round(1e3 * t_cpu / S, 1),
                "speedup_vs_cpu_engines": round(1e3 * t_cpu / S / gms, 1) if gms else None, "heldout_cpu": hc, "heldout_gpu": hg,
                "max_rel_heldout_gap": max(abs(g - c) / c for g, c in zip(hg, hc)), "loss_first_gpu": gl[0].tolist(), "loss_last_gpu": gl[-1].tolist(),
                "pass": bool(ok)})
    json.dump(rec, open(f"{out}/{tag}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k not in ("heldout_cpu", "heldout_gpu", "loss_first_gpu", "loss_last_gpu")}))
    print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
