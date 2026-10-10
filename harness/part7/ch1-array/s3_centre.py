#!/usr/bin/env python3
"""CYCLONE-ARRAY M1 — THE CYCLONE HOLDS THE MODEL (J 10-09, option 3; plan § Model form). One unit's R harness models on the GPU in one
recorded step, three ways:
  pull   — R models (option 1) + the hub every step: AdamW, then hub_mean (float64, replica order) and hub_pull w ← w + K·(mean − w)
  centre — option 3: the cyclone holds C once, each harness only Δ_h; step: W_h = C + Δ_h → forward / backward / AdamW → C = hub_mean of the
           updated models, Δ_h = (1 − K)·(W'_h − C)   (C + Δ_h = the hub pull; C stored once)
  CPU    — the reference: R CPU engine models (om_train_step each), then the SHM-BUS sync of runtime/src/shmbus.rs / cloud/bus_coord.py
           (np.mean float64 → float32, w + K·(mean − w) in float32) on om_param_ptr
Gates: pull vs CPU — every harness's held-out loss within 2 % (the S1 learning bar), spread of the models around their mean within 10 %;
centre vs pull — every harness's held-out within 0.5 % and per-step losses within 1 %. All harnesses start from ONE model (a school round
starts its harnesses from the round's core; --init distinct gives each its own seed) and read their own curriculum batches.
  s3_centre.py [--dims small|school] [--R 4] [--steps 30] [--K 0.1] [--lr 3e-3] [--init same|distinct] [--device llvmpipe] [--out DIR]"""
import json, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, f"{P}/gen"); sys.path.insert(0, HERE)
import train_step
from s1_grad import BIN, DIMS, batch
from s2_replica import engine, weights

def run_gpu(dims, params_R, batches_R, lr, dev, Tm, form, K):
    V = dims["V"]; R = len(params_R); K_ = len(batches_R[0]); names = [n for n, _ in params_R[0]]
    text, ix, npass, nbuf = train_step.build_loop(dims, params_R[0], Tm, params_R=params_R, form=form, K=K)
    for s in range(K_):
        xs, ys, os_, ss = [], [], [], []
        for r in range(R):
            x, y = batches_R[r][s]; o_, st = train_step.batch_index(x, V); xs.append(x); ys.append(y); os_.append(o_); ss.append(st)
        for nm, arr in (("x", xs), ("y", ys), ("eord", os_), ("est", ss), ("sc", [train_step.step_scalars(s, lr)] * R)):
            np.ascontiguousarray(np.stack(arr)).tofile(f"{Tm}/{nm}_{s}.bin")
    np.zeros(2 * R, np.uint32).tofile(f"{Tm}/acc0.bin")
    lines = [f"stepwrite {ix[k]} {Tm}/{k}_{{s}}.bin" for k in ("x", "y", "eord", "est", "sc")] + [f"stepwrite {ix['acc']} {Tm}/acc0.bin", f"stepread {ix['loss']}"]
    reads = [k for k in ix if k[:2] in ("w:", "C:", "D:")]; lines += [f"read {ix[k]}" for k in reads]
    open(f"{Tm}/prog.txt", "w").write(text + "\n".join(lines) + "\n"); od = f"{Tm}/o"; t1 = time.time()
    r_ = subprocess.run([BIN, "session", f"{Tm}/prog.txt", "--device", dev, "--steps", str(K_), "--out", od], capture_output=True, text=True, timeout=14400)
    if r_.returncode: raise RuntimeError(r_.stderr[-1500:])
    info = json.loads(r_.stdout.strip().splitlines()[-1]); info.update({"passes": npass, "buffers": nbuf, "wall_s": round(time.time() - t1, 2)})
    loss = np.fromfile(f"{od}/steps{ix['loss']}.bin", np.float32).reshape(K_, R)
    rd = lambda k: np.fromfile(f"{od}/buf{ix[k]}.bin", np.float32)
    W = [{} for _ in range(R)]
    for n, w in params_R[0]:
        if form == "centre": a = rd(f"C:{n}")[:w.size][None, :] + rd(f"D:{n}")[:R * w.size].reshape(R, w.size)     # W_h = C + Δ_h (float32, = wsum)
        else: a = rd(f"w:{n}")[:R * w.size].reshape(R, w.size)
        for r in range(R): W[r][n] = a[r].astype(np.float32)
    return loss, W, float(open(f"{od}/gpu_ms_sum.txt").read()) / K_, info

def spread(W, names):
    """rms distance of the models from their mean (bus_coord's spread), over every weight"""
    tot, cnt = 0.0, 0
    for n in names:
        st = np.stack([w[n] for w in W]).astype(np.float64); tot += float(((st - st.mean(axis=0)) ** 2).sum()); cnt += st.size
    return (tot / cnt) ** 0.5

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    dn = opt("--dims", "small"); dims = DIMS[dn]; dev = opt("--device", "llvmpipe"); S = int(opt("--steps", "30")); lr = float(opt("--lr", "3e-3"))
    R = int(opt("--R", "4")); K = float(opt("--K", "0.1")); init = opt("--init", "same"); out = opt("--out", f"{P}/results/cyclone/m1"); os.makedirs(out, exist_ok=True)
    V, D, L, H, T, B = (dims[k] for k in ("V", "D", "L", "H", "T", "B")); N = B * T
    Lb, mk = engine(dims)
    hs = [mk(1234 if init == "same" else 1234 + r) for r in range(R)]; params_R = [weights(Lb, h) for h in hs]; names = [n for n, _ in params_R[0]]
    batches_R = [[batch(V, T, B, seed=1000 + s + 100_000 * r) for s in range(S)] for r in range(R)]; hx, hy = batch(V, T, B, seed=999_999)
    rec = {"gate": "CYCLONE-ARRAY M1: the cyclone holds the model (option 3) — pull vs the CPU engines + SHM-BUS sync (held-out ≤ 2 %, spread ≤ 10 %); "
                   "centre vs pull (held-out ≤ 0.5 %, per-step loss ≤ 1 %)", "dims": dims, "R": R, "steps": S, "K": K, "lr": lr, "init": init, "device": dev}
    # CPU reference: om_train_step per harness, then the SHM-BUS sync over the R models' parameters
    ptr = lambda h, i, n: np.ctypeslib.as_array(Lb.om_param_ptr(h, i), shape=(Lb.om_param_size(h, i),))
    cpu_loss = np.zeros((S, R), np.float32); t0 = time.time(); k32 = np.float32(K)
    for s in range(S):
        for r in range(R): cpu_loss[s, r] = Lb.om_train_step(hs[r], batches_R[r][s][0], batches_R[r][s][1], B, T, lr)
        for i, n in enumerate(names):
            ws = [ptr(h, i, n) for h in hs]; mean = np.stack(ws).astype(np.float64).mean(axis=0).astype(np.float32)
            for w in ws: w[:] = w + k32 * (mean - w)
    t_cpu = time.time() - t0
    W_cpu = [{n: ptr(h, i, n).copy() for i, n in enumerate(names)} for h in hs]
    held = lambda W: [float(_held(Lb, mk, names, w, hx, hy, B, T)) for w in W]
    res = {"cpu": {"loss": cpu_loss, "W": W_cpu}}
    with tempfile.TemporaryDirectory(prefix="omni-gpu-m1-") as Tm:
        for form in ("pull", "centre"):
            os.makedirs(f"{Tm}/{form}")
            try: l, W, ms, info = run_gpu(dims, params_R, batches_R, lr, dev, f"{Tm}/{form}", form, K)
            except RuntimeError as e:
                rec.update({"pass": False, "error": f"{form}: {str(e)[-1500:]}"}); json.dump(rec, open(f"{out}/m1-{dn}-R{R}-{dev.split()[0].lower()}.json", "w"), indent=1)
                print(json.dumps(rec)); sys.exit(1)
            res[form] = {"loss": l, "W": W, "ms": ms, "info": info}
    for k in res: res[k]["held"] = held(res[k]["W"]); res[k]["spread"] = spread(res[k]["W"], names)
    hp, hc, hcpu = res["pull"]["held"], res["centre"]["held"], res["cpu"]["held"]
    ok_pull = all(abs(p - c) <= 0.02 * c for p, c in zip(hp, hcpu)) and abs(res["pull"]["spread"] - res["cpu"]["spread"]) <= 0.10 * res["cpu"]["spread"]
    dl = float(np.max(np.abs(res["centre"]["loss"] - res["pull"]["loss"]) / res["pull"]["loss"]))
    ok_centre = all(abs(c - p) <= 0.005 * p for c, p in zip(hc, hp)) and dl <= 0.01
    rec.update({"device_name": res["pull"]["info"]["device"], "cpu_ms_per_step_unit": round(1e3 * t_cpu / S, 2),
                "pull": {"gpu_ms_per_step": round(res["pull"]["ms"], 3), "bytes_resident": res["pull"]["info"]["bytes"], "passes": res["pull"]["info"]["passes"]},
                "centre": {"gpu_ms_per_step": round(res["centre"]["ms"], 3), "bytes_resident": res["centre"]["info"]["bytes"], "passes": res["centre"]["info"]["passes"]},
                "heldout": {"cpu": hcpu, "pull": hp, "centre": hc}, "spread": {k: res[k]["spread"] for k in ("cpu", "pull", "centre")},
                "max_rel_step_loss_centre_vs_pull": dl, "loss_first_last": {k: [res[k]["loss"][0].tolist(), res[k]["loss"][-1].tolist()] for k in ("cpu", "pull", "centre")},
                "pull_vs_cpu_pass": bool(ok_pull), "centre_vs_pull_pass": bool(ok_centre), "pass": bool(ok_pull and ok_centre)})
    json.dump(rec, open(f"{out}/m1-{dn}-R{R}-{dev.split()[0].lower()}.json", "w"), indent=1)
    print(json.dumps(rec))
    print("PASS" if rec["pass"] else "FAIL"); sys.exit(0 if rec["pass"] else 1)

def _held(Lb, mk, names, W, hx, hy, B, T):
    h2 = mk(1234)
    for i, n in enumerate(names): np.ctypeslib.as_array(Lb.om_param_ptr(h2, i), shape=(W[n].size,))[:] = W[n]
    return Lb.om_forward_loss(h2, hx, hy, B, T)

if __name__ == "__main__":
    main()
